# 🚀 Inicio Rápido - WebLogic Monitor

## Instalación en 5 Pasos

### 1️⃣ Despliegue Automático (Recomendado)

```bash
# Descargar y ejecutar script de instalación
cd weblogic_monitor
sudo ./deployment/deploy.sh
```

### 2️⃣ Configurar Dominios

```bash
# Editar configuración de dominios
vi /opt/weblogic-monitor/backend/app.py

# O usar archivo de ejemplo
cp /opt/weblogic-monitor/backend/domains_config_example.py \
   /opt/weblogic-monitor/backend/domains_config.py
```

Agregar tus 90 dominios en `DOMAINS_CONFIG`:

```python
DOMAINS_CONFIG = [
    {
        "name": "ProdDomain01",
        "admin_url": "t3://wls-prod01.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod01_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    # ... agregar los 89 restantes
]
```

### 3️⃣ Crear Archivos de Contraseñas

```bash
# Opción A: Script interactivo
cd /opt/weblogic-monitor
./scripts/setup_passwords.sh

# Opción B: Manual
echo "tu_password_prod01" > /secure/weblogic-monitor/prod01_pass.txt
chmod 600 /secure/weblogic-monitor/prod01_pass.txt
chown oracle:oinstall /secure/weblogic-monitor/prod01_pass.txt
```

### 4️⃣ Iniciar Servicios

```bash
# Iniciar backend
systemctl start weblogic-monitor
systemctl status weblogic-monitor

# Reiniciar Nginx
systemctl restart nginx

# Verificar
curl http://localhost:8000/api/health
```

### 5️⃣ Acceder al Dashboard

Abrir navegador en: **http://tu-servidor**

---

## 🧪 Pruebas de Conexión

Antes de agregar los 90 dominios, prueba con uno:

```bash
./scripts/test_domain_connection.sh \
    t3://wls-admin01.ejemplo.com:7001 \
    weblogic \
    /secure/weblogic-monitor/prod01_pass.txt
```

---

## 📊 Verificar que Todo Funciona

### Backend Funcionando

```bash
# Health check
curl http://localhost:8000/api/health

# Respuesta esperada:
{
  "status": "healthy",
  "timestamp": "2025-02-08T10:30:00",
  "cache_size": 0
}
```

### Obtener Métricas

```bash
# Lista de dominios
curl http://localhost:8000/api/domains

# Métricas de un dominio
curl http://localhost:8000/api/domain/ProdDomain01/metrics

# Todas las métricas
curl http://localhost:8000/api/metrics/all
```

---

## 🎨 Configuración del Frontend

Editar `/var/www/weblogic-monitor/index.html`:

```javascript
// Línea ~828
const API_BASE_URL = 'http://tu-servidor:8000';  // Cambiar a tu servidor

// Línea ~829  
const REFRESH_INTERVAL = 15000;  // Ajustar intervalo (ms)
```

---

## 🔧 Troubleshooting Rápido

### Backend no inicia

```bash
# Ver logs
journalctl -u weblogic-monitor -f

# Verificar Python
/opt/weblogic-monitor/backend/venv/bin/python --version

# Verificar dependencias
/opt/weblogic-monitor/backend/venv/bin/pip list
```

### Conexión falla a WebLogic

```bash
# Verificar red
telnet wls-admin01.ejemplo.com 7001

# Verificar credenciales
cat /secure/weblogic-monitor/prod01_pass.txt

# Test manual con script
./scripts/test_domain_connection.sh t3://... weblogic /secure/.../pass.txt
```

### Dashboard no carga

```bash
# Verificar Nginx
nginx -t
systemctl status nginx

# Verificar archivo frontend
ls -la /var/www/weblogic-monitor/index.html

# Ver logs
tail -f /var/log/nginx/weblogic-monitor-error.log
```

---

## 📈 Métricas Disponibles

### ✅ Por Dominio
- Estado general (HEALTHY/WARNING/CRITICAL)
- Servidores activos vs totales
- Aplicaciones desplegadas
- Uso promedio de Heap
- Threads stuck
- DataSources configurados

### ✅ Por Servidor
- Estado (RUNNING/SHUTDOWN/FAILED)
- Health state
- Uptime
- Heap: usado/máximo/libre/porcentaje
- Threads: total/activos/stuck/hogging
- Pending requests

### ✅ Por Aplicación
- Estado de despliegue
- Sesiones activas
- Tiempo de respuesta promedio

### ✅ Por DataSource
- Conexiones activas
- Conexiones disponibles
- Waiters
- Capacity
- Failures

### ✅ Por Destino JMS
- Mensajes actuales
- Mensajes pendientes
- Mensajes delayed
- Consumers activos

---

## 🔄 Actualización de Métricas

El dashboard se actualiza automáticamente cada **15 segundos**.

Para cambiar el intervalo:

**Frontend** (`index.html`):
```javascript
const REFRESH_INTERVAL = 30000;  // 30 segundos
```

**Backend** (`app.py`):
```python
CACHE_TTL = 30  # 30 segundos
```

---

## 🎯 Próximos Pasos

1. **Producción**: Configurar HTTPS en Nginx
2. **Seguridad**: Agregar autenticación al API
3. **Monitoreo**: Integrar con Prometheus/Grafana
4. **Alertas**: Configurar notificaciones (email, Slack)
5. **Backup**: Configurar respaldo de configuración

Ver documentación completa en: **README.md**

---

## 📞 Soporte

- 📖 Documentación: `README.md`
- 🐛 Reportar bugs: GitHub Issues
- 💬 Preguntas: soporte@ejemplo.com

---

**¡Listo para monitorear 90 dominios de WebLogic en tiempo real!** 🎉
