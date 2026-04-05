# 🚀 INSTRUCCIONES FINALES - GitHub y Servidor

## ✅ ARCHIVO LISTO: MonitoreoWeblogic-LISTO-PARA-GITHUB.zip

Este archivo YA tiene TODO corregido:
- ✅ app.py con decrypt_password()
- ✅ requirements.txt con cryptography
- ✅ setup_secure_password.sh
- ✅ DOMAINS_CONFIG con PRO1LADMS
- ✅ Toda la documentación

---

## 📤 PASO 1: SUBIR A GITHUB (5 minutos)

### 1. Descargar el ZIP
- Descargar: `MonitoreoWeblogic-LISTO-PARA-GITHUB.zip`

### 2. Extraer en tu PC
- Extraer el ZIP
- Verás carpeta: `MonitoreoWeblogic-main/`

### 3. Subir TODO a GitHub

**Opción A - Via Web:**
1. Ir a: https://github.com/decantes-art/MonitoreoWeblogic
2. Click **"Add file"** → **"Upload files"**
3. Arrastrar TODO de la carpeta `MonitoreoWeblogic-main/`
4. Mensaje: `Setup completo con password encriptado`
5. Click **"Commit changes"**

**Opción B - GitHub Desktop:**
1. Clone repository
2. Copiar todos los archivos de `MonitoreoWeblogic-main/` a la carpeta clonada
3. Commit: "Setup completo con password encriptado"
4. Push

---

## ✅ VERIFICAR EN GITHUB

Debes ver:
```
MonitoreoWeblogic/
├── setup_secure_password.sh
├── INSTALACION_PASO_A_PASO.md
├── weblogic_monitor/
│   ├── backend/
│   │   ├── app.py
│   │   └── requirements.txt (con cryptography)
│   ├── frontend/
│   ├── deployment/
│   └── secure/
└── [Más documentación]
```

---

## 🖥️ PASO 2: SUBIR AL SERVIDOR (20 minutos)

### 2.1 Descargar desde GitHub

1. En GitHub, click **"Code"** → **"Download ZIP"**
2. Guardar como: `MonitoreoWeblogic-main.zip`

### 2.2 Subir al Servidor

**Con WinSCP/FileZilla:**
```
Host: 172.21.12.73
Usuario: appuser
Password: [tu password SSH]
Destino: /tmp/
```

Arrastrar: `MonitoreoWeblogic-main.zip` → `/tmp/`

---

## 🚀 PASO 3: INSTALACIÓN EN SERVIDOR

### Conectar y Preparar

```bash
# 1. Conectar
ssh appuser@172.21.12.73

# 2. Extraer
cd /tmp
unzip MonitoreoWeblogic-main.zip
cd MonitoreoWeblogic-main/weblogic_monitor

# 3. Verificar archivos
ls -la
# Debes ver: setup_secure_password.sh, backend/, frontend/, etc.
```

---

### Encriptar Password

```bash
# Hacer ejecutable
chmod +x setup_secure_password.sh

# Ejecutar
./setup_secure_password.sh
```

**Te pedirá:**
```
Ingresa el password de WebLogic (usuario: uamonmidkio): [ESCRIBIR]
Confirma el password: [ESCRIBIR NUEVAMENTE]
```

**Resultado:**
```
✅ Password encriptado exitosamente!
Archivos creados:
  - secure/.encryption_key
  - secure/pro1_pass.txt

Key: gAAAAABl... [GUARDAR]
```

⚠️ **IMPORTANTE:** Guarda la encryption key que te muestra

---

### Encontrar WLST

```bash
# Buscar WLST en el servidor
find / -name "wlst.sh" 2>/dev/null

# Anotar la ruta que te muestre
```

**Rutas comunes:**
- `/u01/oracle/middleware/oracle_common/common/bin/wlst.sh`
- `/opt/oracle/middleware/oracle_common/common/bin/wlst.sh`
- `/app/oracle/middleware/oracle_common/common/bin/wlst.sh`

---

### Editar Ruta WLST (si es necesaria)

```bash
# Editar app.py
vi backend/app.py

# Buscar línea ~378 (presionar: /wlst_cmd)
# Cambiar:
wlst_cmd = "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"

# Por tu ruta real que encontraste

# Guardar: ESC + :wq + ENTER
```

---

### Instalar

```bash
# Dar permisos
chmod +x deployment/deploy.sh

# Instalar (toma ~5 minutos)
sudo ./deployment/deploy.sh
```

**Verás:**
```
[1/8] Instalando dependencias del sistema...
[2/8] Creando directorios...
[3/8] Copiando archivos del backend...
[4/8] Configurando entorno virtual de Python...
[5/8] Copiando archivos del frontend...
[6/8] Configurando servicio systemd...
[7/8] Configurando Nginx...
[8/8] Configurando directorio seguro...

✅ Instalación completada!
```

---

### Verificar

```bash
# Estado del servicio
sudo systemctl status weblogic-monitor
# Debe mostrar: "active (running)"

# Test del API
curl http://localhost:8000/api/health
# Debe responder: {"status":"healthy",...}

# Ver dominios
curl http://localhost:8000/api/domains
# Debe mostrar: PRO1LADMS

# Ver logs en tiempo real
sudo journalctl -u weblogic-monitor -f
```

---

## 🌐 PASO 4: ABRIR DASHBOARD

### En tu navegador:
```
http://172.21.12.73
```

### Deberías ver:
- ✅ Dashboard visual
- ✅ Dominio PRO1LADMS
- ✅ Estado del servidor
- ✅ Gráficas de Heap
- ✅ Threads
- ✅ Actualización cada 15 segundos

---

## 🔍 TROUBLESHOOTING

### ❌ Error: "cryptography not found"
```bash
pip3 install cryptography --break-system-packages
sudo systemctl restart weblogic-monitor
```

### ❌ Error: "Password decryption failed"
```bash
# Recrear password
cd /tmp/MonitoreoWeblogic-main/weblogic_monitor
./setup_secure_password.sh
sudo systemctl restart weblogic-monitor
```

### ❌ Error: "Connection refused to WebLogic"
```bash
# Verificar conectividad
telnet 192.168.1.166 7004

# Verificar que WebLogic esté corriendo
# En servidor WebLogic:
ps -ef | grep AdminServer
```

### ❌ Error: "WLST not found"
```bash
# Buscar ruta correcta
find / -name "wlst.sh" 2>/dev/null

# Editar app.py con la ruta correcta
vi backend/app.py
# Línea ~378
```

---

## 📊 Ver Logs

```bash
# Logs del backend
sudo journalctl -u weblogic-monitor -n 100

# Logs en tiempo real
sudo journalctl -u weblogic-monitor -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## ✅ CHECKLIST COMPLETO

```
☐ Descargar MonitoreoWeblogic-LISTO-PARA-GITHUB.zip
☐ Extraer en tu PC
☐ Subir TODO a GitHub
☐ Verificar en GitHub que todo se subió
☐ Descargar ZIP nuevo de GitHub
☐ Subir a servidor 172.21.12.73 via WinSCP
☐ SSH al servidor
☐ Extraer ZIP
☐ Ejecutar setup_secure_password.sh
☐ Guardar encryption key
☐ Encontrar ruta de WLST
☐ Editar app.py (si es necesario)
☐ Ejecutar deploy.sh
☐ Verificar servicio activo
☐ Abrir dashboard en navegador
☐ Ver métricas de PRO1LADMS
```

---

## 🎯 RESUMEN

```
GITHUB ────> SERVIDOR ────> DASHBOARD
  ↓            ↓              ↓
Upload     Extraer       http://172.21.12.73
  ↓            ↓              ↓
Commit     Setup Pass    Ver métricas
  ↓            ↓              ↓
Done       Deploy.sh     ¡Funciona!
```

---

## 🚀 ¡LISTO!

**Tiempo total estimado: 30 minutos**

1. GitHub: 5 minutos
2. Subir a servidor: 5 minutos
3. Instalación: 15 minutos
4. Verificación: 5 minutos

---

**Cualquier duda en el proceso, me avisas.** 🎯
