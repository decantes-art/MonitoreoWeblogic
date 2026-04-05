# 🚀 Guía de Instalación - WebLogic Monitor con Password Encriptado

## 📋 Información Configurada

```
Servidor Dashboard: 172.21.12.73
Usuario SSH: appuser

Dominio WebLogic: PRO1LADMS
IP: 192.168.1.166:7004
Usuario WebLogic: uamonmidkio
Password: [ENCRIPTADO]
```

---

## ⚡ PASOS DE INSTALACIÓN (30 minutos)

### 1️⃣ Subir Código al Servidor

**Opción A - WinSCP/FileZilla:**
1. Descargar ZIP de GitHub
2. Conectar a 172.21.12.73 con WinSCP/FileZilla
3. Subir archivo a `/tmp/`

**Opción B - SCP:**
```bash
scp MonitoreoWeblogic-main.zip appuser@172.21.12.73:/tmp/
```

---

### 2️⃣ Conectar al Servidor y Extraer

```bash
# Conectar
ssh appuser@172.21.12.73

# Ir a /tmp
cd /tmp

# Extraer ZIP
unzip MonitoreoWeblogic-main.zip

# Entrar al directorio
cd MonitoreoWeblogic-main/weblogic_monitor

# Verificar que todo está
ls -la
# Debes ver: backend/, frontend/, deployment/, etc.
```

---

### 3️⃣ Configurar Password Encriptado

```bash
# Hacer el script ejecutable
chmod +x setup_secure_password.sh

# Ejecutar
./setup_secure_password.sh
```

**El script te pedirá:**
```
Ingresa el password de WebLogic (usuario: uamonmidkio): [ESCRIBIR PASSWORD]
Confirma el password: [ESCRIBIR PASSWORD NUEVAMENTE]
```

**Resultado:**
```
✅ Password encriptado exitosamente!

Archivos creados:
  - secure/.encryption_key  (key de encriptación)
  - secure/pro1_pass.txt    (password encriptado)

🔒 Permisos configurados
Key: gAAAAABl...  [GUARDAR ESTA KEY]
```

⚠️ **IMPORTANTE:** Guarda la encryption key en un lugar seguro

---

### 4️⃣ Verificar Configuración

```bash
# Ver que los archivos se crearon
ls -la secure/

# Debe mostrar:
# drwx------  secure/
# -rw-------  .encryption_key
# -rw-------  pro1_pass.txt

# Ver configuración del dominio
cat backend/app.py | grep -A 8 "DOMAINS_CONFIG"

# Debe mostrar PRO1LADMS configurado
```

---

### 5️⃣ Encontrar Ruta de WLST

```bash
# Buscar WLST en el servidor
find / -name "wlst.sh" 2>/dev/null

# O si sabes dónde está WebLogic:
ls /u01/oracle/middleware/oracle_common/common/bin/wlst.sh
```

**Anotar la ruta que encuentres:** `__________________`

**Editar app.py con la ruta correcta:**
```bash
vi backend/app.py

# Buscar línea ~314 (presiona: /wlst_cmd)
# Cambiar:
wlst_cmd = "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"
# Por tu ruta real

# Guardar: ESC + :wq + Enter
```

---

### 6️⃣ Ejecutar Instalación

```bash
# Dar permisos de ejecución
chmod +x deployment/deploy.sh

# Ejecutar instalación
sudo ./deployment/deploy.sh
```

**Esto instalará:**
- ✅ Python y dependencias (incluye cryptography)
- ✅ Backend FastAPI
- ✅ Frontend React
- ✅ Nginx
- ✅ Servicio systemd

**Tiempo estimado:** ~5 minutos

**Ver progreso:**
```
[1/8] Instalando dependencias del sistema...
[2/8] Creando directorios...
[3/8] Copiando archivos del backend...
[4/8] Configurando entorno virtual de Python...
[5/8] Copiando archivos del frontend...
[6/8] Configurando servicio systemd...
[7/8] Configurando Nginx...
[8/8] Configurando directorio seguro...
```

---

### 7️⃣ Verificar Instalación

```bash
# Ver estado del servicio
sudo systemctl status weblogic-monitor

# Debe mostrar: "active (running)"

# Ver logs en tiempo real
sudo journalctl -u weblogic-monitor -f

# En otra terminal, probar el API
curl http://localhost:8000/api/health

# Debe responder:
# {"status":"healthy","timestamp":"...","cache_size":0}

# Probar endpoint de dominios
curl http://localhost:8000/api/domains

# Debe mostrar PRO1LADMS

# Probar métricas (tomará ~10 segundos)
curl http://localhost:8000/api/domain/PRO1LADMS/metrics
```

---

### 8️⃣ Abrir Dashboard en Navegador

**URL:** `http://172.21.12.73`

**Deberías ver:**
- ✅ Dashboard visual
- ✅ Dominio PRO1LADMS
- ✅ Estado (RUNNING/SHUTDOWN/etc)
- ✅ Gráficas de Heap, Threads
- ✅ Métricas en tiempo real
- ✅ Actualización cada 15 segundos

---

## 🔍 Troubleshooting

### ❌ Error: "Password desencriptado fallido"

```bash
# Verificar que existan los archivos
ls -la secure/

# Recrear password
./setup_secure_password.sh
```

### ❌ Error: "WLST command not found"

```bash
# Buscar WLST
find / -name "wlst.sh" 2>/dev/null

# Editar app.py con ruta correcta
vi backend/app.py
# Línea ~314
```

### ❌ Error: "Connection refused to WebLogic"

```bash
# Verificar conectividad
telnet 192.168.1.166 7004

# Verificar que AdminServer esté corriendo
# En el servidor WebLogic:
ps -ef | grep java | grep AdminServer
```

### ❌ Error: "ModuleNotFoundError: No module named 'cryptography'"

```bash
# Instalar manualmente
pip3 install cryptography --break-system-packages

# O reinstalar requirements
cd /tmp/MonitoreoWeblogic-main/weblogic_monitor/backend
pip3 install -r requirements.txt --break-system-packages
```

---

## 📊 Ver Logs

```bash
# Logs del backend
sudo journalctl -u weblogic-monitor -n 100

# Logs en tiempo real
sudo journalctl -u weblogic-monitor -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs de instalación
sudo tail -f /var/log/weblogic-monitor/app.log
```

---

## ✅ Checklist de Instalación

```
☐ Código subido al servidor
☐ ZIP extraído en /tmp/
☐ setup_secure_password.sh ejecutado
☐ Password encriptado creado
☐ Encryption key guardada
☐ Ruta de WLST verificada y configurada
☐ deploy.sh ejecutado exitosamente
☐ Servicio weblogic-monitor activo
☐ Health check responde OK
☐ Dashboard accesible en http://172.21.12.73
☐ Métricas de PRO1LADMS visibles
```

---

## 🔐 Archivos de Seguridad

```
/tmp/MonitoreoWeblogic-main/weblogic_monitor/
└── secure/
    ├── .encryption_key        ← KEY (GUARDAR EN LUGAR SEGURO)
    └── pro1_pass.txt          ← PASSWORD ENCRIPTADO
```

**Permisos correctos:**
```bash
drwx------  2 appuser appuser   secure/
-rw-------  1 appuser appuser   .encryption_key
-rw-------  1 appuser appuser   pro1_pass.txt
```

---

## 🎯 Después de Instalar

### Agregar Más Dominios

```bash
# Editar configuración
vi backend/app.py

# Agregar en DOMAINS_CONFIG:
{
    "name": "NUEVODOMAIN",
    "admin_url": "t3://ip:puerto",
    "username": "usuario",
    "password_file": "secure/nuevodomain_pass.txt",
    "servers": ["AdminServer"]
}

# Crear password para nuevo dominio
python3 << EOF
from cryptography.fernet import Fernet

with open('secure/.encryption_key', 'rb') as f:
    key = f.read()

fernet = Fernet(key)
encrypted = fernet.encrypt(b"PASSWORD_NUEVO_DOMINIO")

with open('secure/nuevodomain_pass.txt', 'wb') as f:
    f.write(encrypted)
EOF

# Reiniciar servicio
sudo systemctl restart weblogic-monitor
```

---

## 🚀 ¡Listo!

Dashboard funcionando en: **http://172.21.12.73**

**Características:**
- ✅ Password encriptado (seguro)
- ✅ Métricas en tiempo real
- ✅ Actualización cada 15 segundos
- ✅ Dashboard visual completo
- ✅ Accesible desde cualquier navegador

---

**Cualquier problema, revisar los logs:**
```bash
sudo journalctl -u weblogic-monitor -n 50
```
