"""
WebLogic Monitoring Dashboard - SECURE Backend API
FastAPI server con todas las medidas de seguridad implementadas
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator, constr
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
import subprocess
import json
import time
import secrets
import hashlib
import logging
import re
from pathlib import Path
from cryptography.fernet import Fernet
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from jose import JWTError, jwt
from passlib.context import CryptContext

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password encryption key (debe estar en variable de entorno)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS - SOLO ORÍGENES PERMITIDOS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
    ALLOWED_ORIGINS = ["https://weblogic-monitor.ejemplo.com"]

# Trusted hosts
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "weblogic-monitor.ejemplo.com,localhost").split(",")

# ============================================================================
# CONFIGURACIÓN DE LOGGING SEGURO
# ============================================================================

# Logger principal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/weblogic-monitor/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Logger de auditoría
audit_logger = logging.getLogger("audit")
audit_handler = logging.FileHandler("/var/log/weblogic-monitor/audit.log")
audit_handler.setFormatter(logging.Formatter('%(message)s'))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)


def sanitize_log_message(message: str) -> str:
    """Elimina información sensible de logs"""
    message = re.sub(r'password[=:]\s*\S+', 'password=***', message, flags=re.IGNORECASE)
    message = re.sub(r'token[=:]\s*\S+', 'token=***', message, flags=re.IGNORECASE)
    message = re.sub(r'(api[_-]?key)[=:]\s*\S+', r'\1=***', message, flags=re.IGNORECASE)
    return message


def log_audit(event_type: str, user: str, resource: str, 
              action: str, status: str, ip: str, details: dict = None):
    """Registra evento de auditoría"""
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user": user,
        "resource": resource,
        "action": action,
        "status": status,
        "ip_address": ip,
        "details": details or {}
    }
    audit_logger.info(json.dumps(audit_entry))


# ============================================================================
# INICIALIZACIÓN DE FASTAPI
# ============================================================================

app = FastAPI(
    title="WebLogic Monitor API - SECURE",
    version="2.0.0-secure",
    docs_url=None,  # Desactivar docs en producción
    redoc_url=None
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# MIDDLEWARES DE SEGURIDAD
# ============================================================================

# CORS restringido
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)


# Headers de seguridad
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Prevenir XSS
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # CSP
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com;"
    )
    
    # HSTS
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


# ============================================================================
# MODELOS DE DATOS CON VALIDACIÓN
# ============================================================================

class ServerMetrics(BaseModel):
    name: constr(regex=r'^[a-zA-Z0-9_-]+$', max_length=50)
    state: str
    health_state: str
    uptime: int
    thread_pool: Dict[str, int]
    jvm: Dict[str, Any]
    timestamp: datetime


class ApplicationMetrics(BaseModel):
    name: constr(max_length=100)
    state: str
    open_sessions: int
    avg_response_time: Optional[float]


class DatasourceMetrics(BaseModel):
    name: constr(max_length=100)
    active_connections: int
    available_connections: int
    waiters: int
    capacity: int
    failures: int


class JMSMetrics(BaseModel):
    destination: constr(max_length=100)
    current_messages: int
    pending_messages: int
    delayed_messages: int
    consumers: int


class DomainStatus(BaseModel):
    name: constr(regex=r'^[a-zA-Z0-9_-]+$', max_length=50)
    admin_url: str
    last_update: datetime
    servers: List[ServerMetrics]
    applications: List[ApplicationMetrics]
    datasources: List[DatasourceMetrics]
    jms_destinations: List[JMSMetrics]
    overall_health: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    disabled: Optional[bool] = None


# ============================================================================
# AUTENTICACIÓN Y AUTORIZACIÓN
# ============================================================================

# Base de datos de usuarios (EN PRODUCCIÓN: usar DB real)
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("changeme123"),
        "disabled": False,
        "roles": ["admin", "read:metrics", "write:config"]
    }
}

security_bearer = HTTPBearer()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    
    return user


def has_permission(user: dict, permission: str) -> bool:
    """Verifica si usuario tiene permiso"""
    return permission in user.get("roles", [])


# ============================================================================
# FUNCIONES DE SEGURIDAD PARA PASSWORDS
# ============================================================================

def encrypt_password(password: str) -> str:
    """Encripta password usando Fernet"""
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted: str) -> str:
    """Desencripta password"""
    try:
        decrypted = fernet.decrypt(encrypted.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Error decrypting password: {e}")
        raise HTTPException(status_code=500, detail="Password decryption failed")


# ============================================================================
# VALIDACIÓN Y SANITIZACIÓN
# ============================================================================

def validate_domain_name(name: str) -> bool:
    """Valida nombre de dominio"""
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, name)) and 1 <= len(name) <= 50


def create_safe_script_path(domain_name: str) -> Path:
    """Crea path seguro para script WLST"""
    if not validate_domain_name(domain_name):
        raise HTTPException(status_code=400, detail="Invalid domain name")
    
    # Usar directorio seguro
    script_dir = Path("/tmp/wlst_scripts_secure")
    script_dir.mkdir(exist_ok=True, mode=0o700)
    
    # Nombre de archivo sanitizado
    script_path = script_dir / f"collect_{domain_name}.py"
    
    # Verificar path traversal
    if not str(script_path.resolve()).startswith(str(script_dir.resolve())):
        raise HTTPException(status_code=400, detail="Path traversal detected")
    
    return script_path


# ============================================================================
# CONFIGURACIÓN DE CACHE
# ============================================================================

CACHE_TTL = int(os.getenv("CACHE_TTL", "15"))
metrics_cache = {}


# ============================================================================
# CONFIGURACIÓN DE DOMINIOS
# ============================================================================

DOMAINS_CONFIG = [
    # Cargar desde archivo de configuración o variable de entorno
    # En producción: cargar desde base de datos o archivo config seguro
]


# ============================================================================
# ENDPOINTS CON SEGURIDAD
# ============================================================================

@app.post("/api/auth/token", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, username: str, password: str):
    """Login y generación de token JWT"""
    user = authenticate_user(username, password)
    if not user:
        log_audit(
            event_type="LOGIN_FAILED",
            user=username,
            resource="auth/token",
            action="LOGIN",
            status="FAILURE",
            ip=request.client.host
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    log_audit(
        event_type="LOGIN_SUCCESS",
        user=username,
        resource="auth/token",
        action="LOGIN",
        status="SUCCESS",
        ip=request.client.host
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    return {"message": "WebLogic Monitoring API - SECURE", "version": "2.0.0"}


@app.get("/api/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint (sin autenticación para monitoring)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "cache_size": len(metrics_cache),
        "version": "2.0.0-secure"
    }


@app.get("/api/domains", response_model=List[Dict[str, Any]])
@limiter.limit("30/minute")
async def get_domains(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get list of all domains - REQUIRES AUTH"""
    if not has_permission(current_user, "read:metrics"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    log_audit(
        event_type="DOMAINS_LIST",
        user=current_user["username"],
        resource="domains",
        action="READ",
        status="SUCCESS",
        ip=request.client.host
    )
    
    domains = []
    for config in DOMAINS_CONFIG:
        domains.append({
            "name": config['name'],
            "admin_url": config['admin_url'],
            "server_count": len(config['servers'])
        })
    return domains


@app.get("/api/domain/{domain_name}/metrics", response_model=DomainStatus)
@limiter.limit("30/minute")
async def get_domain_metrics(
    domain_name: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed metrics for a specific domain - REQUIRES AUTH"""
    # Validar nombre de dominio
    if not validate_domain_name(domain_name):
        raise HTTPException(status_code=400, detail="Invalid domain name")
    
    # Verificar permisos
    if not has_permission(current_user, "read:metrics"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Verificar que el dominio existe
    domain_config = next((d for d in DOMAINS_CONFIG if d['name'] == domain_name), None)
    if not domain_config:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    try:
        metrics = await collect_domain_metrics(domain_config)
        
        log_audit(
            event_type="METRICS_ACCESS",
            user=current_user["username"],
            resource=f"domain/{domain_name}",
            action="READ",
            status="SUCCESS",
            ip=request.client.host
        )
        
        if not metrics:
            raise HTTPException(status_code=500, detail="Failed to collect metrics")
        
        return metrics
        
    except Exception as e:
        log_audit(
            event_type="METRICS_ACCESS",
            user=current_user["username"],
            resource=f"domain/{domain_name}",
            action="READ",
            status="FAILURE",
            ip=request.client.host,
            details={"error": sanitize_log_message(str(e))}
        )
        logger.error(sanitize_log_message(f"Error collecting metrics: {e}"))
        raise HTTPException(status_code=500, detail="Failed to collect metrics")


@app.get("/api/metrics/all")
@limiter.limit("10/minute")  # Límite más bajo por ser operación costosa
async def get_all_metrics(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get metrics for all domains - REQUIRES AUTH - EXPENSIVE OPERATION"""
    if not has_permission(current_user, "read:metrics"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tasks = [collect_domain_metrics(config) for config in DOMAINS_CONFIG]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_results = []
    failed_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, DomainStatus):
            valid_results.append(result)
        else:
            failed_count += 1
            logger.error(sanitize_log_message(
                f"Failed to collect metrics for {DOMAINS_CONFIG[i]['name']}: {result}"
            ))
    
    log_audit(
        event_type="METRICS_ALL",
        user=current_user["username"],
        resource="metrics/all",
        action="READ",
        status="SUCCESS",
        ip=request.client.host,
        details={"successful": len(valid_results), "failed": failed_count}
    )
    
    return {
        "total_domains": len(DOMAINS_CONFIG),
        "successful": len(valid_results),
        "failed": failed_count,
        "domains": valid_results
    }


# ============================================================================
# FUNCIÓN DE COLECCIÓN DE MÉTRICAS (con seguridad mejorada)
# ============================================================================

async def collect_domain_metrics(domain_config: dict) -> Optional[DomainStatus]:
    """Execute WLST script and parse results - SECURE VERSION"""
    cache_key = domain_config['name']
    
    # Check cache
    if cache_key in metrics_cache:
        cached_data, cached_time = metrics_cache[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            return cached_data
    
    # Create secure script path
    script_path = create_safe_script_path(domain_config['name'])
    
    # Read and decrypt password
    try:
        with open(domain_config['password_file'], 'r') as f:
            encrypted_password = f.read().strip()
        password = decrypt_password(encrypted_password)
    except Exception as e:
        logger.error(f"Error reading password file: {e}")
        return None
    
    # Generate WLST script (similar al original pero con password ya desencriptado)
    script = create_wlst_script_secure(domain_config, password)
    
    # Write script to secure path
    with open(script_path, 'w') as f:
        f.write(script)
    os.chmod(script_path, 0o600)
    
    # Validate WLST command path
    wlst_cmd = os.getenv("WLST_PATH", "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh")
    if not Path(wlst_cmd).exists():
        logger.error(f"WLST command not found: {wlst_cmd}")
        return None
    
    # Execute WLST with timeout
    try:
        process = await asyncio.create_subprocess_exec(
            wlst_cmd, str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
        
        # Parse JSON output (igual que antes)
        output = stdout.decode()
        if 'METRICS_JSON_START' in output:
            json_start = output.index('METRICS_JSON_START') + len('METRICS_JSON_START')
            json_end = output.index('METRICS_JSON_END')
            json_str = output[json_start:json_end].strip()
            
            data = json.loads(json_str)
            
            domain_status = DomainStatus(
                name=data['domain'],
                admin_url=domain_config['admin_url'],
                last_update=datetime.fromisoformat(data['timestamp']),
                servers=[ServerMetrics(**s) for s in data['servers']],
                applications=[ApplicationMetrics(**a) for a in data['applications']],
                datasources=[DatasourceMetrics(**d) for d in data['datasources']],
                jms_destinations=[JMSMetrics(**j) for j in data['jms_destinations']],
                overall_health='HEALTHY'
            )
            
            # Calculate overall health
            health_states = [s.health_state for s in domain_status.servers]
            if any('CRITICAL' in h for h in health_states):
                domain_status.overall_health = 'CRITICAL'
            elif any('WARNING' in h for h in health_states):
                domain_status.overall_health = 'WARNING'
            
            # Cache result
            metrics_cache[cache_key] = (domain_status, time.time())
            
            # Clean up script
            script_path.unlink()
            
            return domain_status
            
    except asyncio.TimeoutError:
        logger.error(f"Timeout collecting metrics for {domain_config['name']}")
        return None
    except Exception as e:
        logger.error(sanitize_log_message(f"Error collecting metrics: {e}"))
        return None
    finally:
        # Always cleanup
        if script_path.exists():
            script_path.unlink()


def create_wlst_script_secure(domain_config: dict, password: str) -> str:
    """Generate WLST Jython script - mismo que antes pero con password ya desencriptado"""
    # ... (mismo código que create_wlst_script original)
    pass


if __name__ == "__main__":
    import uvicorn
    # EN PRODUCCIÓN: usar HTTPS
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="/etc/ssl/private/key.pem",  # Configurar certificados
        ssl_certfile="/etc/ssl/certs/cert.pem"
    )
