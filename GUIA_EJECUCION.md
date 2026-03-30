# 🚀 Guía Completa de Ejecución - WebLogic Monitor

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Conectividad Necesaria](#conectividad-necesaria)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Configuración de Dominios](#configuración-de-dominios)
5. [Ejecución](#ejecución)
6. [Verificación](#verificación)
7. [Troubleshooting](#troubleshooting)

---

## 1️⃣ Requisitos Previos

### Servidor donde se Instalará el Dashboard

**Hardware Mínimo:**
- CPU: 2 cores
- RAM: 4 GB
- Disco: 10 GB libre
- Red: 100 Mbps

**Software Necesario:**
- Sistema Operativo: Linux (RHEL 7/8, CentOS 7/8, Ubuntu 18.04+)
- Python 3.8 o superior
- WebLogic Server instalado (para tener WLST disponible)
- Nginx (se instala automáticamente)
- Acceso root o sudo

**Verificar Python:**
```bash
python3 --version
# Debe mostrar: Python 3.8.x o superior
```

**Verificar WLST:**
```bash
# Ubicación típica en instalaciones Oracle
ls -la /u01/oracle/middleware/oracle_common/common/bin/wlst.sh

# O buscar en tu instalación
find / -name "wlst.sh" 2>/dev/null
```

---

## 2️⃣ Conectividad Necesaria

### 🌐 Diagrama de Conectividad

```
┌─────────────────────────────────────────────────────────────┐
│                Servidor Dashboard                            │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │ ◄─────► │   Backend    │                 │
│  │   (Nginx)    │         │   (FastAPI)  │                 │
│  │   :80/:443   │         │   :8000      │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                   │                          │
└───────────────────────────────────┼──────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │  Dominio 1  │ │  Dominio 2  │ │  Dominio 90 │
            │             │ │             │ │             │
            │ AdminServer │ │ AdminServer │ │ AdminServer │
            │   :7001     │ │   :7001     │ │   :7001     │
            │   (T3)      │ │   (T3)      │ │   (T3)      │
            └─────────────┘ └─────────────┘ └─────────────┘
```

### 📡 Puertos y Protocolos Requeridos

#### Desde el Servidor Dashboard HACIA los Dominios WebLogic:

| Origen | Destino | Puerto | Protocolo | Descripción |
|--------|---------|--------|-----------|-------------|
| Dashboard Server | AdminServer Dominio 1 | 7001 | T3 | Conexión WLST |
| Dashboard Server | AdminServer Dominio 2 | 7001 | T3 | Conexión WLST |
| Dashboard Server | AdminServer Dominio N | 7001 | T3 | Conexión WLST |

**Nota:** El puerto puede variar. Comúnmente:
- AdminServer: 7001 (T3) o 7002 (T3S/SSL)
- Puede ser cualquier puerto configurado en tu WebLogic

#### Acceso de Usuarios AL Dashboard:

| Origen | Destino | Puerto | Protocolo | Descripción |
|--------|---------|--------|-----------|-------------|
| Navegador Usuario | Dashboard Server | 80 | HTTP | Acceso web |
| Navegador Usuario | Dashboard Server | 443 | HTTPS | Acceso web seguro (recomendado) |

### 🔐 Credenciales Necesarias

Para CADA dominio necesitas:
- **URL del AdminServer** (ejemplo: `t3://wls-admin01.ejemplo.com:7001`)
- **Usuario WebLogic** (típicamente: `weblogic` o `admin`)
- **Contraseña** del usuario
- **Lista de Managed Servers** del dominio (opcional, para mejor visualización)

### 🧪 Verificar Conectividad

**Antes de instalar, verifica que puedes alcanzar los AdminServers:**

```bash
# Prueba 1: Ping
ping wls-admin01.ejemplo.com

# Prueba 2: Telnet al puerto T3
telnet wls-admin01.ejemplo.com 7001

# Prueba 3: Conexión WLST manual
/u01/oracle/middleware/oracle_common/common/bin/wlst.sh
# Dentro de WLST:
>>> connect('weblogic','password','t3://wls-admin01.ejemplo.com:7001')
>>> serverRuntime()
>>> ls()
>>> disconnect()
>>> exit()
```

### 🔥 Reglas de Firewall Necesarias

**En el Servidor del Dashboard (Salida):**
```bash
# Permitir salida a todos los AdminServers en puerto 7001
# Ejemplo para iptables:
iptables -A OUTPUT -p tcp --dport 7001 -j ACCEPT
```

**En cada Servidor WebLogic (Entrada):**
```bash
# Permitir entrada desde el servidor Dashboard al puerto AdminServer
# Ejemplo (reemplazar 192.168.1.100 con IP del Dashboard):
iptables -A INPUT -s 192.168.1.100 -p tcp --dport 7001 -j ACCEPT
```

**En el Servidor del Dashboard (Entrada - para acceso web):**
```bash
# Permitir acceso HTTP/HTTPS desde la red interna
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

---

## 3️⃣ Instalación Paso a Paso

### Opción A: Instalación Automática (Recomendada)

```bash
# 1. Descargar y extraer
cd /tmp
tar -xzf weblogic_monitor.tar.gz
cd weblogic_monitor

# 2. Ejecutar instalación (como root)
sudo ./deployment/deploy.sh
```

El script automáticamente:
- ✅ Instala dependencias
- ✅ Crea directorios
- ✅ Configura Python virtual environment
- ✅ Configura Nginx
- ✅ Crea servicio systemd
- ✅ Establece permisos

### Opción B: Instalación Manual

```bash
# 1. Crear directorios
sudo mkdir -p /opt/weblogic-monitor/backend
sudo mkdir -p /var/www/weblogic-monitor
sudo mkdir -p /secure/weblogic-monitor
sudo chown oracle:oinstall /opt/weblogic-monitor
sudo chown oracle:oinstall /secure/weblogic-monitor
sudo chmod 700 /secure/weblogic-monitor

# 2. Copiar archivos backend
cd weblogic_monitor
sudo cp -r backend/* /opt/weblogic-monitor/backend/

# 3. Configurar Python
cd /opt/weblogic-monitor/backend
sudo -u oracle python3 -m venv venv
sudo -u oracle venv/bin/pip install -r requirements.txt

# 4. Copiar frontend
sudo cp frontend/index.html /var/www/weblogic-monitor/

# 5. Configurar systemd
sudo cp deployment/weblogic-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weblogic-monitor

# 6. Configurar Nginx
sudo cp deployment/nginx.conf /etc/nginx/conf.d/weblogic-monitor.conf
sudo nginx -t
```

---

## 4️⃣ Configuración de Dominios

### Paso 1: Editar Configuración

```bash
sudo vi /opt/weblogic-monitor/backend/app.py
```

### Paso 2: Localizar DOMAINS_CONFIG (línea ~21)

Reemplazar el array vacío con tus dominios:

```python
DOMAINS_CONFIG = [
    {
        "name": "ProdDomain01",
        "admin_url": "t3://wls-prod-admin01.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod01_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    {
        "name": "ProdDomain02",
        "admin_url": "t3://wls-prod-admin02.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod02_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    # ... continuar con los 88 dominios restantes
]
```

### Paso 3: Ajustar Ruta de WLST (línea ~180)

```python
# Buscar esta línea:
wlst_cmd = "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"

# Reemplazar con tu ruta real (la que encontraste en los requisitos previos)
wlst_cmd = "/tu/ruta/real/wlst.sh"
```

### Paso 4: Crear Archivos de Contraseñas

**Opción A: Script Interactivo**
```bash
cd /opt/weblogic-monitor
sudo ./scripts/setup_passwords.sh
```

**Opción B: Manual**
```bash
# Para cada dominio:
sudo bash -c 'echo "tu_password_prod01" > /secure/weblogic-monitor/prod01_pass.txt'
sudo chown oracle:oinstall /secure/weblogic-monitor/prod01_pass.txt
sudo chmod 600 /secure/weblogic-monitor/prod01_pass.txt

# Repetir para cada dominio...
```

**Opción C: Desde CSV**
```bash
# Crear archivo CSV con formato: nombre_dominio,password
cat > /tmp/passwords.csv << EOF
prod01,Password123
prod02,Password456
prod03,Password789
EOF

# Ejecutar script
sudo ./scripts/setup_passwords.sh
# Seleccionar opción 2 y proporcionar: /tmp/passwords.csv
```

### Paso 5: Verificar Archivos Creados

```bash
ls -la /secure/weblogic-monitor/
# Debe mostrar archivos con permisos 600 (rw-------)
```

---

## 5️⃣ Ejecución

### Iniciar Backend

```bash
# Opción 1: Con systemd (producción)
sudo systemctl start weblogic-monitor
sudo systemctl status weblogic-monitor

# Opción 2: Manual (desarrollo/testing)
cd /opt/weblogic-monitor/backend
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Iniciar Nginx

```bash
sudo systemctl start nginx
sudo systemctl status nginx
```

### Verificar que Están Corriendo

```bash
# Backend
curl http://localhost:8000/api/health
# Respuesta esperada: {"status":"healthy","timestamp":"...","cache_size":0}

# Nginx
curl http://localhost/
# Debe devolver el HTML del dashboard
```

---

## 6️⃣ Verificación Completa

### Test 1: Health Check del API

```bash
curl http://localhost:8000/api/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-08T10:30:00",
  "cache_size": 0
}
```

### Test 2: Lista de Dominios

```bash
curl http://localhost:8000/api/domains
```

**Respuesta esperada:**
```json
[
  {
    "name": "ProdDomain01",
    "admin_url": "t3://wls-prod-admin01.ejemplo.com:7001",
    "server_count": 3
  },
  ...
]
```

### Test 3: Métricas de un Dominio

```bash
curl http://localhost:8000/api/domain/ProdDomain01/metrics
```

**Si funciona:** Verás JSON con todas las métricas  
**Si falla:** Verás error 500 - revisar logs

### Test 4: Dashboard en Navegador

1. Abrir navegador
2. Ir a: `http://IP_DEL_SERVIDOR`
3. Deberías ver el dashboard cargando
4. Después de ~30-40 segundos verás las métricas de todos los dominios

---

## 7️⃣ Troubleshooting

### ❌ Error: "Connection refused to AdminServer"

**Causa:** No hay conectividad de red al AdminServer

**Solución:**
```bash
# 1. Verificar que el AdminServer está corriendo
# En el servidor WebLogic:
ps -ef | grep java | grep AdminServer

# 2. Verificar conectividad de red
telnet wls-admin01.ejemplo.com 7001

# 3. Verificar firewall
sudo iptables -L -n | grep 7001

# 4. Probar conexión WLST manual
/u01/oracle/middleware/oracle_common/common/bin/wlst.sh
>>> connect('weblogic','password','t3://wls-admin01.ejemplo.com:7001')
```

### ❌ Error: "Authentication failed"

**Causa:** Credenciales incorrectas

**Solución:**
```bash
# 1. Verificar archivo de password
cat /secure/weblogic-monitor/prod01_pass.txt

# 2. Verificar sin espacios o caracteres extra
# El archivo debe tener SOLO la password, sin saltos de línea al final

# 3. Recrear archivo
echo -n "tu_password" > /secure/weblogic-monitor/prod01_pass.txt
chmod 600 /secure/weblogic-monitor/prod01_pass.txt

# 4. Probar con WLST manual
```

### ❌ Error: "WLST command not found"

**Causa:** Ruta incorrecta de WLST

**Solución:**
```bash
# 1. Buscar WLST
find / -name "wlst.sh" 2>/dev/null

# 2. Actualizar app.py con la ruta correcta
sudo vi /opt/weblogic-monitor/backend/app.py
# Línea ~180: wlst_cmd = "/ruta/correcta/wlst.sh"

# 3. Reiniciar servicio
sudo systemctl restart weblogic-monitor
```

### ❌ Error: "Timeout collecting metrics"

**Causa:** WLST toma más de 30 segundos

**Solución:**
```bash
# Aumentar timeout en app.py
sudo vi /opt/weblogic-monitor/backend/app.py

# Buscar línea ~182:
stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)

# Cambiar a:
stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)

# Reiniciar
sudo systemctl restart weblogic-monitor
```

### ❌ Dashboard no carga / pantalla blanca

**Causa:** Frontend no puede conectar al backend

**Solución:**
```bash
# 1. Verificar URL del backend en frontend
sudo vi /var/www/weblogic-monitor/index.html

# Buscar línea ~828:
const API_BASE_URL = 'http://localhost:8000';

# Cambiar a la IP/hostname correcto:
const API_BASE_URL = 'http://192.168.1.100:8000';
# O si está detrás de Nginx:
const API_BASE_URL = 'http://tu-servidor.ejemplo.com';

# 2. Verificar CORS
curl -H "Origin: http://ejemplo.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/health

# 3. Ver errores en navegador
# Presionar F12 → Console
```

### ❌ Error: "Port 8000 already in use"

**Solución:**
```bash
# Encontrar proceso
sudo lsof -i :8000

# Matar proceso
sudo kill -9 PID

# O cambiar puerto en app.py y systemd service
```

### 📊 Ver Logs en Tiempo Real

```bash
# Backend
sudo journalctl -u weblogic-monitor -f

# Nginx access
sudo tail -f /var/log/nginx/weblogic-monitor-access.log

# Nginx errors
sudo tail -f /var/log/nginx/weblogic-monitor-error.log

# Todos juntos
sudo journalctl -u weblogic-monitor -f & \
sudo tail -f /var/log/nginx/weblogic-monitor-error.log
```

---

## 📝 Checklist de Instalación

```
☐ 1. Servidor Linux con Python 3.8+
☐ 2. WebLogic instalado (para tener WLST)
☐ 3. Conectividad de red a los 90 AdminServers (puerto 7001)
☐ 4. Credenciales de WebLogic para cada dominio
☐ 5. Firewall configurado
☐ 6. Proyecto descargado y extraído
☐ 7. Instalación ejecutada (deploy.sh)
☐ 8. DOMAINS_CONFIG editado con los 90 dominios
☐ 9. Ruta de WLST ajustada en app.py
☐ 10. Archivos de contraseñas creados
☐ 11. Backend iniciado y respondiendo
☐ 12. Nginx iniciado
☐ 13. Health check OK
☐ 14. Dashboard accesible desde navegador
☐ 15. Métricas apareciendo correctamente
```

---

## 🎯 Flujo de Ejecución Normal

```
1. Usuario abre http://servidor-dashboard
                    ↓
2. Nginx sirve index.html (Frontend React)
                    ↓
3. Frontend hace request a /api/metrics/all cada 15 segundos
                    ↓
4. Backend recibe request
                    ↓
5. Backend verifica cache (TTL: 15s)
        ↓                           ↓
    Cache HIT                   Cache MISS
        ↓                           ↓
   Retorna datos            Genera script WLST
                                    ↓
                            Ejecuta WLST contra AdminServer
                                    ↓
                            Obtiene métricas de MBeans
                                    ↓
                            Parsea JSON
                                    ↓
                            Guarda en cache
                                    ↓
                            Retorna datos
                                    ↓
6. Frontend recibe JSON y actualiza visualización
                    ↓
7. Espera 15 segundos → vuelve al paso 3
```

---

## 🚀 Comandos Rápidos de Referencia

```bash
# Iniciar todo
sudo systemctl start weblogic-monitor nginx

# Detener todo
sudo systemctl stop weblogic-monitor nginx

# Reiniciar después de cambios
sudo systemctl restart weblogic-monitor

# Ver estado
sudo systemctl status weblogic-monitor nginx

# Ver logs
sudo journalctl -u weblogic-monitor -n 50

# Health check
curl http://localhost:8000/api/health

# Test de un dominio
curl http://localhost:8000/api/domain/ProdDomain01/metrics | jq

# Todas las métricas
curl http://localhost:8000/api/metrics/all | jq
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs
2. Verifica conectividad de red
3. Prueba conexión WLST manual
4. Consulta la documentación completa en README.md

**¡Listo para monitorear tus 90 dominios WebLogic en tiempo real!** 🎉
