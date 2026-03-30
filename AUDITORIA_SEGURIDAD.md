# 🔐 Auditoría de Seguridad - WebLogic Monitor

## ⚠️ ESTADO ACTUAL DE SEGURIDAD

### ❌ VULNERABILIDADES IDENTIFICADAS

```
┌────────────────────────────────────────────────────────────────┐
│  SEVERIDAD CRÍTICA                                              │
├────────────────────────────────────────────────────────────────┤
│  ✗ Sin autenticación en el API                                 │
│  ✗ Sin autenticación en el dashboard                           │
│  ✗ Contraseñas en texto plano en archivos                      │
│  ✗ CORS configurado con allow_origins=["*"]                    │
│  ✗ Sin rate limiting                                            │
│  ✗ Sin validación de entrada                                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  SEVERIDAD ALTA                                                 │
├────────────────────────────────────────────────────────────────┤
│  ✗ Sin HTTPS configurado por defecto                           │
│  ✗ Sin encriptación de datos en tránsito                       │
│  ✗ Sin logging de auditoría                                    │
│  ✗ Sin protección contra ataques de fuerza bruta               │
│  ✗ Ejecución de comandos shell sin sanitización               │
│  ✗ Sin validación de rutas de archivos (path traversal)       │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  SEVERIDAD MEDIA                                                │
├────────────────────────────────────────────────────────────────┤
│  ⚠ Sin headers de seguridad en API                             │
│  ⚠ Sin protección CSRF                                          │
│  ⚠ Información sensible en logs                                │
│  ⚠ Sin rotación de logs                                        │
│  ⚠ Sin monitoreo de seguridad                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ PLAN DE HARDENING DE SEGURIDAD

### Nivel 1: BÁSICO (Mínimo Viable)
- ✅ HTTPS obligatorio
- ✅ Autenticación básica HTTP
- ✅ Contraseñas encriptadas
- ✅ CORS restringido
- ✅ Rate limiting básico

### Nivel 2: RECOMENDADO (Producción)
- ✅ Todo lo de Nivel 1
- ✅ Autenticación con tokens JWT
- ✅ Logging de auditoría
- ✅ Validación de entrada
- ✅ Headers de seguridad
- ✅ Protección CSRF

### Nivel 3: ENTERPRISE (Alta Seguridad)
- ✅ Todo lo de Nivel 2
- ✅ Integración LDAP/Active Directory
- ✅ OAuth2 / SAML
- ✅ Encriptación de datos en reposo
- ✅ IDS/IPS
- ✅ SIEM integration
- ✅ Segmentación de red

---

## 📋 EVALUACIÓN DETALLADA

### 1. Autenticación y Autorización

#### ❌ ESTADO ACTUAL
```python
# backend/app.py - INSEGURO
@app.get("/api/metrics/all")
async def get_all_metrics():
    # Cualquiera puede acceder sin autenticación
    return metrics
```

#### ✅ RIESGO
- **Severidad:** CRÍTICA
- **Impacto:** Exposición de información sensible de infraestructura
- **Explotación:** Trivial (acceso directo)
- **CVSS Score:** 7.5 (High)

#### 🔒 SOLUCIÓN
```python
# Implementar autenticación JWT
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

@app.get("/api/metrics/all")
async def get_all_metrics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validar token
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verificar permisos
    if not has_permission(payload.get("user"), "read:metrics"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return metrics
```

---

### 2. Almacenamiento de Credenciales

#### ❌ ESTADO ACTUAL
```bash
# /secure/weblogic-monitor/prod01_pass.txt
Password123    # ← TEXTO PLANO!
```

#### ✅ RIESGO
- **Severidad:** CRÍTICA
- **Impacto:** Compromiso total de dominios WebLogic
- **Explotación:** Lectura de archivo
- **CVSS Score:** 9.1 (Critical)

#### 🔒 SOLUCIÓN 1: Encriptación con Fernet
```python
from cryptography.fernet import Fernet
import base64
import os

def encrypt_password(password: str, key: bytes) -> str:
    """Encripta password usando Fernet"""
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted: str, key: bytes) -> str:
    """Desencripta password"""
    f = Fernet(key)
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()

# Uso:
# Generar key una vez: Fernet.generate_key()
# Guardar en variable de entorno: export ENCRYPTION_KEY=...
```

#### 🔒 SOLUCIÓN 2: Oracle Wallet (RECOMENDADO para WebLogic)
```bash
# Crear wallet
mkstore -wrl /secure/wallet -create

# Agregar credenciales
mkstore -wrl /secure/wallet -createCredential \
    ProdDomain01 weblogic Password123

# Usar en WLST
connect(username=username, password=password, url=url, 
        walletPath='/secure/wallet')
```

#### 🔒 SOLUCIÓN 3: HashiCorp Vault (Enterprise)
```python
import hvac

client = hvac.Client(url='https://vault.ejemplo.com:8200')
client.token = os.getenv('VAULT_TOKEN')

# Leer password
secret = client.secrets.kv.v2.read_secret_version(
    path='weblogic/prod01'
)
password = secret['data']['data']['password']
```

---

### 3. CORS (Cross-Origin Resource Sharing)

#### ❌ ESTADO ACTUAL
```python
# backend/app.py - INSEGURO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← PERMITE CUALQUIER ORIGEN!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### ✅ RIESGO
- **Severidad:** ALTA
- **Impacto:** XSS, CSRF, robo de datos
- **Explotación:** Sitio malicioso puede consumir API
- **CVSS Score:** 6.5 (Medium)

#### 🔒 SOLUCIÓN
```python
# Solo permitir orígenes conocidos
ALLOWED_ORIGINS = [
    "https://weblogic-monitor.ejemplo.com",
    "https://dashboard.ejemplo.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Solo métodos necesarios
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### 4. Inyección de Comandos

#### ❌ ESTADO ACTUAL
```python
# backend/app.py - VULNERABLE A COMMAND INJECTION
wlst_cmd = "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"
process = await asyncio.create_subprocess_exec(
    wlst_cmd, script_path,  # ← Sin validación de script_path
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
```

#### ✅ RIESGO
- **Severidad:** CRÍTICA
- **Impacto:** Ejecución remota de código
- **Explotación:** Manipulación de domain_config
- **CVSS Score:** 9.8 (Critical)

#### 🔒 SOLUCIÓN
```python
import re
from pathlib import Path

def validate_domain_name(name: str) -> bool:
    """Valida nombre de dominio"""
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, name)) and len(name) <= 50

def create_safe_script_path(domain_name: str) -> Path:
    """Crea path seguro para script"""
    if not validate_domain_name(domain_name):
        raise ValueError("Invalid domain name")
    
    # Usar directorio seguro
    script_dir = Path("/tmp/wlst_scripts")
    script_dir.mkdir(exist_ok=True, mode=0o700)
    
    # Nombre de archivo sanitizado
    script_path = script_dir / f"collect_{domain_name}.py"
    
    # Verificar path traversal
    if not str(script_path.resolve()).startswith(str(script_dir.resolve())):
        raise ValueError("Path traversal detected")
    
    return script_path

# Uso
script_path = create_safe_script_path(domain_config['name'])
```

---

### 5. Rate Limiting

#### ❌ ESTADO ACTUAL
```python
# Sin protección contra abuso
@app.get("/api/metrics/all")
async def get_all_metrics():
    # Puede ser llamado infinitas veces
    return metrics
```

#### ✅ RIESGO
- **Severidad:** MEDIA
- **Impacto:** DoS, consumo excesivo de recursos
- **Explotación:** Requests automatizados
- **CVSS Score:** 5.3 (Medium)

#### 🔒 SOLUCIÓN
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/metrics/all")
@limiter.limit("10/minute")  # Máximo 10 requests por minuto
async def get_all_metrics(request: Request):
    return metrics

@app.get("/api/domain/{domain_name}/metrics")
@limiter.limit("30/minute")  # Límite más permisivo para consultas específicas
async def get_domain_metrics(request: Request, domain_name: str):
    return metrics
```

---

### 6. Validación de Entrada

#### ❌ ESTADO ACTUAL
```python
@app.get("/api/domain/{domain_name}/metrics")
async def get_domain_metrics(domain_name: str):
    # Sin validación de domain_name
    domain_config = next((d for d in DOMAINS_CONFIG 
                         if d['name'] == domain_name), None)
```

#### ✅ RIESGO
- **Severidad:** MEDIA
- **Impacto:** Path traversal, SQL injection (si se agrega DB)
- **Explotación:** Parámetros maliciosos
- **CVSS Score:** 6.1 (Medium)

#### 🔒 SOLUCIÓN
```python
from pydantic import BaseModel, validator, constr

class DomainNameParam(BaseModel):
    name: constr(regex=r'^[a-zA-Z0-9_-]+$', min_length=1, max_length=50)
    
    @validator('name')
    def validate_domain_exists(cls, v):
        if v not in [d['name'] for d in DOMAINS_CONFIG]:
            raise ValueError('Domain not found')
        return v

@app.get("/api/domain/{domain_name}/metrics")
async def get_domain_metrics(domain_name: str):
    # Validar
    validated = DomainNameParam(name=domain_name)
    
    domain_config = next((d for d in DOMAINS_CONFIG 
                         if d['name'] == validated.name), None)
    # ...
```

---

### 7. Headers de Seguridad

#### ❌ ESTADO ACTUAL
```python
# Sin headers de seguridad
```

#### ✅ RIESGO
- **Severidad:** MEDIA
- **Impacto:** XSS, clickjacking, MIME sniffing
- **Explotación:** Ataques del lado del cliente
- **CVSS Score:** 5.4 (Medium)

#### 🔒 SOLUCIÓN
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

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
        "script-src 'self' 'unsafe-inline' https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com;"
    )
    
    # HSTS
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )
    
    return response

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["weblogic-monitor.ejemplo.com", "localhost"]
)
```

---

### 8. Logging de Auditoría

#### ❌ ESTADO ACTUAL
```python
# Sin logging de auditoría
# No se registra quién accede a qué
```

#### ✅ RIESGO
- **Severidad:** MEDIA
- **Impacto:** Imposible rastrear accesos maliciosos
- **Explotación:** Falta de accountability
- **CVSS Score:** 4.3 (Medium)

#### 🔒 SOLUCIÓN
```python
import logging
from datetime import datetime
import json

# Configurar logger de auditoría
audit_logger = logging.getLogger("audit")
audit_handler = logging.FileHandler("/var/log/weblogic-monitor/audit.log")
audit_handler.setFormatter(logging.Formatter('%(message)s'))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

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

@app.get("/api/domain/{domain_name}/metrics")
async def get_domain_metrics(
    domain_name: str,
    request: Request,
    user: dict = Depends(get_current_user)
):
    try:
        metrics = await collect_domain_metrics(domain_name)
        
        # Log exitoso
        log_audit(
            event_type="METRICS_ACCESS",
            user=user['username'],
            resource=f"domain/{domain_name}",
            action="READ",
            status="SUCCESS",
            ip=request.client.host
        )
        
        return metrics
        
    except Exception as e:
        # Log fallo
        log_audit(
            event_type="METRICS_ACCESS",
            user=user['username'],
            resource=f"domain/{domain_name}",
            action="READ",
            status="FAILURE",
            ip=request.client.host,
            details={"error": str(e)}
        )
        raise
```

---

### 9. HTTPS y Certificados

#### ❌ ESTADO ACTUAL
```nginx
# deployment/nginx.conf
server {
    listen 80;  # ← HTTP SIN ENCRIPTACIÓN
    # ...
}
```

#### ✅ RIESGO
- **Severidad:** ALTA
- **Impacto:** Man-in-the-middle, robo de credenciales
- **Explotación:** Sniffing de red
- **CVSS Score:** 7.4 (High)

#### 🔒 SOLUCIÓN
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name weblogic-monitor.ejemplo.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    server_name weblogic-monitor.ejemplo.com;
    
    # Certificados SSL (Let's Encrypt recomendado)
    ssl_certificate /etc/letsencrypt/live/weblogic-monitor.ejemplo.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/weblogic-monitor.ejemplo.com/privkey.pem;
    
    # SSL Settings (Mozilla Modern)
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/weblogic-monitor.ejemplo.com/chain.pem;
    
    # ...resto de configuración
}
```

---

### 10. Información Sensible en Logs

#### ❌ ESTADO ACTUAL
```python
# Passwords y tokens pueden aparecer en logs
print(f"Error connecting to {url} with password {password}")
```

#### ✅ RIESGO
- **Severidad:** ALTA
- **Impacto:** Exposición de credenciales en logs
- **Explotación:** Lectura de archivos de log
- **CVSS Score:** 7.5 (High)

#### 🔒 SOLUCIÓN
```python
import re

def sanitize_log_message(message: str) -> str:
    """Elimina información sensible de logs"""
    # Remover passwords
    message = re.sub(r'password[=:]\s*\S+', 'password=***', message, flags=re.IGNORECASE)
    
    # Remover tokens
    message = re.sub(r'token[=:]\s*\S+', 'token=***', message, flags=re.IGNORECASE)
    
    # Remover API keys
    message = re.sub(r'(api[_-]?key)[=:]\s*\S+', r'\1=***', message, flags=re.IGNORECASE)
    
    return message

# Logger personalizado
class SanitizingLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, message):
        self.logger.info(sanitize_log_message(str(message)))
    
    def error(self, message):
        self.logger.error(sanitize_log_message(str(message)))

# Uso
logger = SanitizingLogger(logging.getLogger(__name__))
logger.info(f"Connecting to {url} with password {password}")
# Log: "Connecting to t3://... with password=***"
```

---

## 📊 MATRIZ DE RIESGOS

| Vulnerabilidad | Severidad | Probabilidad | Impacto | Risk Score |
|----------------|-----------|--------------|---------|------------|
| Sin autenticación API | Crítica | Alta | Crítico | 9.5 |
| Passwords texto plano | Crítica | Media | Crítico | 9.1 |
| Command injection | Crítica | Baja | Crítico | 7.8 |
| Sin HTTPS | Alta | Alta | Alto | 7.4 |
| CORS abierto | Alta | Media | Medio | 6.5 |
| Sin rate limiting | Media | Alta | Medio | 5.3 |
| Sin validación entrada | Media | Media | Medio | 6.1 |
| Info en logs | Alta | Media | Alto | 7.5 |

**Risk Score = (Severidad × Probabilidad × Impacto) / 3**

---

## ✅ CHECKLIST DE SEGURIDAD PARA PRODUCCIÓN

```bash
☐ CRÍTICO - Implementar autenticación (JWT/OAuth2)
☐ CRÍTICO - Encriptar passwords (Fernet/Vault/Wallet)
☐ CRÍTICO - Validar todas las entradas
☐ CRÍTICO - Configurar HTTPS con certificados válidos
☐ CRÍTICO - Restringir CORS a orígenes conocidos

☐ ALTO - Implementar rate limiting
☐ ALTO - Agregar headers de seguridad
☐ ALTO - Logging de auditoría
☐ ALTO - Sanitizar logs
☐ ALTO - Validar paths de archivos

☐ MEDIO - Implementar protección CSRF
☐ MEDIO - Rotación de logs
☐ MEDIO - Monitoreo de seguridad
☐ MEDIO - Backup encriptado
☐ MEDIO - Actualizar dependencias

☐ BAJO - Implementar 2FA
☐ BAJO - Análisis de vulnerabilidades periódico
☐ BAJO - Penetration testing
☐ BAJO - Security training del equipo
```

---

## 🎯 ROADMAP DE IMPLEMENTACIÓN

### Fase 1 (Semana 1): CRÍTICO
1. Implementar autenticación básica HTTP
2. Configurar HTTPS
3. Encriptar passwords con Fernet
4. Restringir CORS
5. Validación de entrada

### Fase 2 (Semana 2): ALTO
6. Migrar a JWT
7. Rate limiting
8. Headers de seguridad
9. Logging de auditoría
10. Sanitización de logs

### Fase 3 (Semana 3): MEDIO
11. Integración LDAP (opcional)
12. Protección CSRF
13. Rotación de logs
14. Monitoreo de seguridad

### Fase 4 (Semana 4): ENTERPRISE
15. OAuth2/SAML
16. HashiCorp Vault
17. SIEM integration
18. Pen testing

---

## 📞 CONTACTO DE SEGURIDAD

En caso de detectar una vulnerabilidad:
- Email: security@ejemplo.com
- PGP Key: [fingerprint]
- Bugcrowd: [URL si aplica]

---

**CONCLUSIÓN:** El portal en su estado actual **NO es seguro para producción**. 
Se requiere implementar **mínimo las correcciones de Nivel 1-2** antes de deployment.
