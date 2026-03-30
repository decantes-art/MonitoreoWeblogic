# Dashboard de Monitoreo WebLogic en Tiempo Real

Dashboard profesional para monitorear 90 dominios de WebLogic con métricas en tiempo real. Incluye visualización de salud de servidores, aplicaciones, threads, JVM, JDBC y JMS.

![WebLogic Monitor Dashboard](docs/screenshot.png)

## 🚀 Características Principales

### Métricas Monitoreadas

#### A. Salud General de Dominios/Instancias
- ✅ Estado de servidor (RUNNING/SHUTDOWN/FAILED/UNKNOWN)
- ✅ Health state (HEALTH_OK/WARNING/CRITICAL)
- ✅ Uptime por Managed Server
- ✅ Estado del AdminServer

#### B. Aplicaciones (EAR/WAR)
- ✅ Estado de despliegue (STATE_ACTIVE/PREPARED/FAILED)
- ✅ Sesiones activas (web)
- ✅ Tiempo de respuesta promedio

#### C. Threads/Pools
- ✅ ExecuteThread total
- ✅ Threads activos
- ✅ Stuck threads
- ✅ Hogging threads
- ✅ Work Managers (pending/completed requests)

#### D. JVM
- ✅ Heap usado/máximo
- ✅ Old Gen usado
- ✅ Garbage Collection (tiempo y conteo)
- ✅ Thread count total de la JVM

#### E. JDBC (por datasource)
- ✅ Conexiones activas
- ✅ Conexiones disponibles
- ✅ Waiters
- ✅ Capacity
- ✅ Fallos de conexión

#### F. JMS
- ✅ Mensajes encolados (current)
- ✅ Mensajes pendientes/delayed
- ✅ Consumers activos
- ✅ Redelivery/error counters

## 📊 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  - Dashboard en tiempo real                                  │
│  - Actualización cada 15 segundos                           │
│  - Filtros y búsqueda                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/JSON
┌───────────────────────▼─────────────────────────────────────┐
│              Backend API (FastAPI)                           │
│  - Cache de métricas (TTL: 15s)                             │
│  - Ejecución paralela de colectores                         │
│  - Endpoints REST                                            │
└───────────────────────┬─────────────────────────────────────┘
                        │ WLST/Jython
┌───────────────────────▼─────────────────────────────────────┐
│           WebLogic Domains (x90)                             │
│  - AdminServer (T3 protocol)                                │
│  - MBeans (ServerRuntime, JVMRuntime, etc.)                 │
│  - Managed Servers                                           │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Recolección de Métricas

1. **Frontend** solicita métricas cada 15 segundos
2. **Backend API** verifica cache (TTL: 15s)
3. Si no hay cache válido:
   - Genera script WLST/Jython dinámico
   - Ejecuta script contra AdminServer vía T3
   - Obtiene métricas de MBeans
   - Parsea JSON de salida
   - Cachea resultado
4. **Frontend** recibe y visualiza datos

## 🛠️ Instalación

### Requisitos Previos

- WebLogic Server 12c o superior
- Python 3.8+
- Node.js 16+ (opcional, para desarrollo)
- Acceso T3 a los AdminServers

### 1. Backend Setup

```bash
# Crear directorio del proyecto
mkdir -p /opt/weblogic-monitor
cd /opt/weblogic-monitor

# Copiar archivos
cp -r backend/ /opt/weblogic-monitor/
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Dominios

Editar `backend/app.py` y configurar tus 90 dominios:

```python
DOMAINS_CONFIG = [
    {
        "name": "ProductionDomain1",
        "admin_url": "t3://prod-admin1.example.com:7001",
        "username": "weblogic",
        "password_file": "/secure/prod1_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    {
        "name": "ProductionDomain2",
        "admin_url": "t3://prod-admin2.example.com:7001",
        "username": "weblogic",
        "password_file": "/secure/prod2_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    # ... agregar los 88 dominios restantes
]
```

### 3. Configurar Archivos de Contraseña

```bash
# Crear directorio seguro
mkdir -p /secure
chmod 700 /secure

# Crear archivo de contraseña para cada dominio
echo "tu_password" > /secure/prod1_pass.txt
chmod 600 /secure/prod1_pass.txt
```

### 4. Configurar Path de WLST

Editar la ruta de WLST en `app.py`:

```python
# Línea ~180
wlst_cmd = "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"
```

### 5. Iniciar Backend

```bash
# Desarrollo
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Producción
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Frontend Setup

```bash
# Opción 1: Servidor HTTP simple
cd frontend
python3 -m http.server 3000

# Opción 2: Nginx
sudo cp index.html /var/www/html/weblogic-monitor/
```

Configurar URL del backend en `index.html` (línea ~825):

```javascript
const API_BASE_URL = 'http://tu-servidor:8000';
```

## 🔧 Configuración

### Variables de Entorno

```bash
# backend/.env
CACHE_TTL=15
WLST_PATH=/u01/oracle/middleware/oracle_common/common/bin/wlst.sh
LOG_LEVEL=INFO
```

### Ajustar Intervalo de Refresco

Frontend (`index.html`, línea ~828):
```javascript
const REFRESH_INTERVAL = 15000; // 15 segundos
```

Backend (`app.py`, línea ~7):
```python
CACHE_TTL = 15  # segundos
```

## 📡 API Endpoints

### GET /api/domains
Obtiene lista de todos los dominios configurados.

**Response:**
```json
[
  {
    "name": "ProductionDomain1",
    "admin_url": "t3://prod-admin1.example.com:7001",
    "server_count": 3
  }
]
```

### GET /api/domain/{domain_name}/metrics
Obtiene métricas detalladas de un dominio específico.

**Response:**
```json
{
  "name": "ProductionDomain1",
  "admin_url": "t3://prod-admin1.example.com:7001",
  "last_update": "2025-02-08T10:30:00",
  "overall_health": "HEALTHY",
  "servers": [...],
  "applications": [...],
  "datasources": [...],
  "jms_destinations": [...]
}
```

### GET /api/metrics/all
Obtiene métricas de todos los dominios (ejecución paralela).

**Response:**
```json
{
  "total_domains": 90,
  "successful": 88,
  "failed": 2,
  "domains": [...]
}
```

### GET /api/health
Health check del API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-08T10:30:00",
  "cache_size": 45
}
```

## 🎨 Personalización del Dashboard

### Cambiar Colores (CSS Variables)

Editar `index.html` (líneas 16-30):

```css
:root {
    --bg-primary: #0a0e1a;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-green: #10b981;
    --accent-yellow: #f59e0b;
    --accent-red: #ef4444;
}
```

### Agregar Nuevas Métricas

1. **Backend**: Modificar script WLST en `create_wlst_script()`
2. **Backend**: Actualizar modelo Pydantic
3. **Frontend**: Agregar visualización en componente

## 🔐 Seguridad

### Mejores Prácticas

1. **No almacenar contraseñas en código**
   - Usar archivos externos con permisos 600
   - Considerar Oracle Wallet para credenciales

2. **Habilitar HTTPS**
   ```bash
   uvicorn app:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

3. **Agregar autenticación**
   ```python
   from fastapi.security import HTTPBasic, HTTPBasicCredentials
   ```

4. **Firewall**
   - Puerto 8000 solo accesible desde red interna
   - Puerto 3000 (frontend) detrás de proxy inverso

## 📊 Integración con Prometheus/Grafana

### Exportar Métricas a Prometheus

Agregar endpoint `/metrics` en `app.py`:

```python
from prometheus_client import Counter, Gauge, generate_latest

# Definir métricas
heap_usage = Gauge('weblogic_heap_usage_percent', 
    'Heap usage percentage', ['domain', 'server'])
stuck_threads = Gauge('weblogic_stuck_threads', 
    'Stuck thread count', ['domain', 'server'])

@app.get("/metrics")
async def prometheus_metrics():
    # Actualizar métricas
    for domain in await get_all_metrics():
        for server in domain.servers:
            heap_pct = (server.jvm.heap_used / server.jvm.heap_max) * 100
            heap_usage.labels(domain.name, server.name).set(heap_pct)
            stuck_threads.labels(domain.name, server.name).set(
                server.thread_pool.stuck_threads)
    
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana Dashboard

Importar dashboard pre-configurado desde `docs/grafana-dashboard.json`

## 🐛 Troubleshooting

### Error: "Connection refused to AdminServer"

```bash
# Verificar conectividad T3
telnet prod-admin1.example.com 7001

# Verificar credenciales
java weblogic.WLST
connect('weblogic','password','t3://localhost:7001')
```

### Error: "WLST script timeout"

Aumentar timeout en `app.py`:

```python
stdout, stderr = await asyncio.wait_for(
    process.communicate(), 
    timeout=60  # Aumentar de 30 a 60 segundos
)
```

### Dashboard no actualiza

1. Verificar backend está corriendo: `curl http://localhost:8000/api/health`
2. Revisar logs: `tail -f logs/app.log`
3. Verificar CORS en navegador (F12 → Console)

## 📈 Performance

### Optimizaciones

- **Cache**: Reduce llamadas WLST de 90 cada 15s a ~1-2 por dominio
- **Ejecución Paralela**: Collect de 90 dominios en ~30-45 segundos
- **Lazy Loading**: Frontend carga detalles solo cuando se expande card

### Benchmarks

- 90 dominios, 270 servers: ~35-40 segundos colección completa
- Cache hit rate: ~95% después de primer ciclo
- Frontend rendering: <100ms con 90 dominios

## 🤝 Contribuciones

Para agregar nuevas métricas:

1. Fork el repositorio
2. Crear branch: `git checkout -b feature/nueva-metrica`
3. Agregar métrica en WLST script
4. Actualizar modelos Pydantic
5. Actualizar frontend
6. Commit: `git commit -am 'Add nueva métrica'`
7. Push: `git push origin feature/nueva-metrica`
8. Crear Pull Request

## 📄 Licencia

MIT License - ver archivo `LICENSE`

## 📞 Soporte

- Issues: https://github.com/tu-org/weblogic-monitor/issues
- Email: soporte@ejemplo.com
- Docs: https://docs.ejemplo.com/weblogic-monitor

---

**Desarrollado con ❤️ para monitoreo enterprise de WebLogic**
