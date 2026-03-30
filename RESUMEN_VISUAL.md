# 🚀 WebLogic Monitor - Resumen Visual de Ejecución

## ⚡ Instalación en 3 Pasos

```
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: INSTALAR                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  tar -xzf weblogic_monitor.tar.gz                           │
│  cd weblogic_monitor                                         │
│  sudo ./deployment/deploy.sh                                 │
│                                                              │
│  ⏱️  Tiempo: ~5 minutos                                      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: CONFIGURAR                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  A. Editar dominios:                                         │
│     vi /opt/weblogic-monitor/backend/app.py                  │
│                                                              │
│  B. Ajustar ruta WLST (línea ~180):                          │
│     wlst_cmd = "/tu/ruta/wlst.sh"                            │
│                                                              │
│  C. Crear passwords:                                         │
│     ./scripts/setup_passwords.sh                             │
│                                                              │
│  ⏱️  Tiempo: ~15-30 minutos (dependiendo de cuántos dominios)│
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: INICIAR                                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  systemctl start weblogic-monitor nginx                      │
│  systemctl status weblogic-monitor                           │
│                                                              │
│  ✅ Verificar: http://tu-servidor                            │
│                                                              │
│  ⏱️  Tiempo: ~1 minuto                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Conectividad Requerida

```
┌────────────────────┐
│  Servidor          │
│  Dashboard         │  Necesita SALIR hacia:
│  192.168.1.100     │  ────────────────────────────────┐
└─────────┬──────────┘                                   │
          │                                              │
          ├──────────────────────────────────────────────┤
          │                                              │
          │  T3 Protocol (Puerto 7001)                   │
          │                                              │
          ▼                                              ▼
    ┌──────────┐                                  ┌──────────┐
    │ Dominio 1│                                  │Dominio 90│
    │ AdminSrv │                                  │ AdminSrv │
    │  :7001   │  ...  (90 dominios total)  ...  │  :7001   │
    └──────────┘                                  └──────────┘

    wls-admin01      wls-admin02      ...      wls-admin90
    .ejemplo.com     .ejemplo.com              .ejemplo.com
```

### ✅ Checklist de Conectividad

```bash
# 1. Ping a los AdminServers
ping wls-admin01.ejemplo.com

# 2. Telnet al puerto
telnet wls-admin01.ejemplo.com 7001

# 3. Test WLST manual
/ruta/a/wlst.sh
>>> connect('weblogic','pass','t3://wls-admin01.ejemplo.com:7001')
>>> serverRuntime()
>>> disconnect()
>>> exit()
```

---

## 📝 Configuración de Dominios

### Formato del DOMAINS_CONFIG

```python
DOMAINS_CONFIG = [
    {
        "name": "ProdDomain01",                          # Nombre único
        "admin_url": "t3://wls-prod01.ejemplo.com:7001", # URL T3
        "username": "weblogic",                          # Usuario WebLogic
        "password_file": "/secure/wl-monitor/prod01.txt",# Archivo password
        "servers": ["AdminServer", "MS1", "MS2"]         # Lista de servers
    },
    {
        "name": "ProdDomain02",
        "admin_url": "t3://wls-prod02.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/wl-monitor/prod02.txt",
        "servers": ["AdminServer", "MS1", "MS2", "MS3"]
    },
    # ... continuar hasta 90 dominios
]
```

### 🔐 Archivos de Password

```bash
# Estructura:
/secure/weblogic-monitor/
├── prod01_pass.txt  (contiene: Password123)
├── prod02_pass.txt  (contiene: Password456)
├── prod03_pass.txt
└── ...

# Permisos:
-rw------- oracle oinstall prod01_pass.txt

# Crear:
echo "tu_password" > /secure/weblogic-monitor/prod01_pass.txt
chmod 600 /secure/weblogic-monitor/prod01_pass.txt
chown oracle:oinstall /secure/weblogic-monitor/prod01_pass.txt
```

---

## 🎯 Puertos Utilizados

| Componente | Puerto | Protocolo | Dirección | Para qué |
|------------|--------|-----------|-----------|----------|
| **Frontend (Nginx)** | 80 | HTTP | Entrada | Acceso web usuarios |
| **Frontend (Nginx)** | 443 | HTTPS | Entrada | Acceso web seguro |
| **Backend (FastAPI)** | 8000 | HTTP | Interna | API REST |
| **AdminServers WebLogic** | 7001 | T3 | Salida | Consulta métricas |

---

## 🔧 Comandos Esenciales

### Iniciar/Detener

```bash
# Iniciar
sudo systemctl start weblogic-monitor nginx

# Detener
sudo systemctl stop weblogic-monitor nginx

# Reiniciar
sudo systemctl restart weblogic-monitor

# Estado
sudo systemctl status weblogic-monitor nginx
```

### Verificar Funcionamiento

```bash
# Health check del API
curl http://localhost:8000/api/health

# Respuesta esperada:
# {"status":"healthy","timestamp":"2025-02-08T...","cache_size":0}

# Ver lista de dominios
curl http://localhost:8000/api/domains

# Métricas de un dominio
curl http://localhost:8000/api/domain/ProdDomain01/metrics

# Acceder al dashboard
# Navegador: http://IP_DEL_SERVIDOR
```

### Ver Logs

```bash
# Backend
sudo journalctl -u weblogic-monitor -f

# Nginx
sudo tail -f /var/log/nginx/weblogic-monitor-error.log

# Últimas 50 líneas
sudo journalctl -u weblogic-monitor -n 50
```

---

## 📊 Métricas Monitoreadas

```
┌─────────────────────────────────────────────────────┐
│  POR DOMINIO                                         │
├─────────────────────────────────────────────────────┤
│  ✓ Estado general (HEALTHY/WARNING/CRITICAL)        │
│  ✓ Número de servidores activos                     │
│  ✓ Aplicaciones desplegadas                         │
│  ✓ Uso promedio de Heap                             │
│  ✓ Threads stuck totales                            │
│  ✓ DataSources configurados                         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  POR SERVIDOR                                        │
├─────────────────────────────────────────────────────┤
│  ✓ Estado (RUNNING/SHUTDOWN/FAILED)                 │
│  ✓ Health state                                      │
│  ✓ Uptime                                            │
│  ✓ Heap: usado/máximo/libre/porcentaje              │
│  ✓ Threads: total/activos/stuck/hogging             │
│  ✓ Pending requests                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  POR APLICACIÓN                                      │
├─────────────────────────────────────────────────────┤
│  ✓ Estado de despliegue                             │
│  ✓ Sesiones activas                                 │
│  ✓ Tiempo de respuesta promedio                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  POR DATASOURCE                                      │
├─────────────────────────────────────────────────────┤
│  ✓ Conexiones activas                               │
│  ✓ Conexiones disponibles                           │
│  ✓ Waiters (esperando conexión)                     │
│  ✓ Capacity                                          │
│  ✓ Failures                                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  POR DESTINO JMS                                     │
├─────────────────────────────────────────────────────┤
│  ✓ Mensajes actuales                                │
│  ✓ Mensajes pendientes                              │
│  ✓ Mensajes delayed                                 │
│  ✓ Consumers activos                                │
└─────────────────────────────────────────────────────┘
```

---

## 🚨 Troubleshooting Rápido

### ❌ "Backend no inicia"

```bash
# Ver error
sudo journalctl -u weblogic-monitor -n 20

# Verificar Python
/opt/weblogic-monitor/backend/venv/bin/python --version

# Verificar dependencias
/opt/weblogic-monitor/backend/venv/bin/pip list
```

### ❌ "No puedo conectar a AdminServer"

```bash
# 1. Verificar AdminServer corriendo
ps -ef | grep java | grep AdminServer

# 2. Verificar red
telnet wls-admin01.ejemplo.com 7001

# 3. Test WLST manual
/ruta/a/wlst.sh
>>> connect('user','pass','t3://wls-admin01.ejemplo.com:7001')
```

### ❌ "Dashboard no carga"

```bash
# 1. Verificar Nginx
sudo systemctl status nginx
sudo nginx -t

# 2. Verificar archivo
ls -la /var/www/weblogic-monitor/index.html

# 3. Ver logs Nginx
sudo tail -f /var/log/nginx/weblogic-monitor-error.log

# 4. Verificar URL del backend en frontend
grep API_BASE_URL /var/www/weblogic-monitor/index.html
```

### ❌ "Timeout collecting metrics"

```bash
# Aumentar timeout en app.py
sudo vi /opt/weblogic-monitor/backend/app.py

# Línea ~182, cambiar de 30 a 60:
timeout=60

# Reiniciar
sudo systemctl restart weblogic-monitor
```

---

## 📈 Performance Esperado

```
┌────────────────────────────────────────────┐
│  90 DOMINIOS                                │
├────────────────────────────────────────────┤
│  Primera colección:     30-45 segundos     │
│  Con cache (95% hits):   5-10 segundos     │
│  Consumo RAM:           200-300 MB         │
│  Tráfico red/día:       1.5-3 GB           │
│  Auto-refresh:          Cada 15 segundos   │
└────────────────────────────────────────────┘
```

---

## 🎨 Características del Dashboard

```
┌─────────────────────────────────────────────────────┐
│  🎯 ESTADÍSTICAS GLOBALES                            │
│  • Total dominios                                    │
│  • Servidores activos/totales                        │
│  • Aplicaciones desplegadas                          │
│  • Threads stuck                                     │
│  • Uso promedio de Heap                              │
│  • Dominios en estado crítico                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  🔍 FILTROS                                           │
│  • Todos                                             │
│  • Saludables                                        │
│  • Con advertencias                                  │
│  • Críticos                                          │
│  • Búsqueda por nombre                               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  📊 CARDS POR DOMINIO                                │
│  • Indicador de salud (color)                        │
│  • Servidores activos                                │
│  • Uso de Heap (barra progreso)                      │
│  • Threads stuck                                     │
│  • Detalle expandible de servidores                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  🔄 AUTO-REFRESH                                      │
│  • Cada 15 segundos                                  │
│  • Sin recargar página                               │
│  • Timestamp de última actualización                 │
└─────────────────────────────────────────────────────┘
```

---

## 📂 Ubicaciones Importantes

```
/opt/weblogic-monitor/          # Instalación principal
├── backend/
│   ├── app.py                  # ← CONFIGURAR dominios aquí
│   ├── venv/
│   └── requirements.txt

/var/www/weblogic-monitor/      # Frontend
└── index.html                  # ← CONFIGURAR URL backend aquí

/secure/weblogic-monitor/       # Passwords
├── prod01_pass.txt
├── prod02_pass.txt
└── ...

/etc/systemd/system/
└── weblogic-monitor.service    # Servicio systemd

/etc/nginx/conf.d/
└── weblogic-monitor.conf       # Configuración web

/var/log/nginx/
├── weblogic-monitor-access.log
└── weblogic-monitor-error.log
```

---

## 🎓 Próximos Pasos Post-Instalación

```
1. ✓ Configurar HTTPS con certificados SSL
2. ✓ Agregar autenticación (OAuth2/LDAP)
3. ✓ Configurar alertas (email, Slack)
4. ✓ Integrar con Prometheus/Grafana
5. ✓ Configurar backup de configuración
6. ✓ Documentar procedimientos operativos
7. ✓ Capacitar al equipo
```

---

## 📞 Recursos

- **Documentación Completa:** README.md
- **Guía de Ejecución:** GUIA_EJECUCION.md
- **Arquitectura de Red:** ARQUITECTURA_RED.md
- **Estructura del Proyecto:** PROJECT_STRUCTURE.md
- **Inicio Rápido:** QUICKSTART.md

---

## ✅ Checklist Final

```bash
# Antes de poner en producción, verifica:

☐ Backend responde: curl http://localhost:8000/api/health
☐ Frontend carga: http://IP_SERVIDOR
☐ Métricas aparecen en dashboard
☐ Logs sin errores: journalctl -u weblogic-monitor
☐ Firewall configurado correctamente
☐ Passwords con permisos 600
☐ Auto-start habilitado: systemctl is-enabled weblogic-monitor
☐ Nginx habilitado: systemctl is-enabled nginx
☐ Todos los 90 dominios configurados
☐ Prueba de conectividad a todos los AdminServers
```

---

🎉 **¡Listo para monitorear 90 dominios WebLogic en tiempo real!** 🎉
