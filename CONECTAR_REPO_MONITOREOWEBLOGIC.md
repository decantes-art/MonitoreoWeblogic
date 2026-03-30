# 🚀 Conectar con tu Repositorio "MonitoreoWeblogic"

## ✅ Ya tienes el repo creado - Excelente!

Ahora solo necesitas conectar tu código local con GitHub.

---

## 📋 Pasos para Conectar

### Opción A: Repositorio Vacío (Recomendado)

**Si tu repo en GitHub está vacío (sin archivos):**

```bash
# 1. Ir a tu directorio del proyecto
cd /ruta/donde/extraiste/weblogic_monitor

# 2. Inicializar Git (si no lo has hecho)
git init

# 3. Agregar todos los archivos
git add .

# 4. Primer commit
git commit -m "Initial commit: WebLogic Monitor Dashboard"

# 5. Conectar con tu repo (CAMBIAR TU_USUARIO por tu usuario real)
git remote add origin https://github.com/TU_USUARIO/MonitoreoWeblogic.git

# 6. Cambiar a branch main (si está en master)
git branch -M main

# 7. Push inicial
git push -u origin main
```

---

### Opción B: Repositorio con Archivos

**Si ya tiene README.md u otros archivos:**

```bash
# 1. Ir a tu directorio del proyecto
cd /ruta/donde/extraiste/weblogic_monitor

# 2. Inicializar Git
git init

# 3. Conectar con tu repo
git remote add origin https://github.com/TU_USUARIO/MonitoreoWeblogic.git

# 4. Bajar lo que ya existe
git pull origin main --allow-unrelated-histories

# 5. Agregar tus archivos
git add .

# 6. Commit
git commit -m "Add WebLogic Monitor complete code and documentation"

# 7. Push
git push -u origin main
```

---

## 🔧 Comandos Exactos para Tu Caso

### Paso 1: Preparar el Proyecto

```bash
# Extraer el proyecto
tar -xzf weblogic_monitor_FINAL.tar.gz

# Entrar al directorio
cd weblogic_monitor

# Ver archivos
ls -la
```

### Paso 2: Inicializar Git

```bash
# Inicializar repositorio local
git init

# Verificar que .gitignore existe (protege secretos)
cat .gitignore

# Agregar todos los archivos
git add .

# Ver qué se agregará
git status

# Primer commit
git commit -m "Initial commit: WebLogic Monitor Dashboard con Ansible"
```

### Paso 3: Conectar con GitHub

```bash
# Conectar con tu repositorio
# IMPORTANTE: Reemplaza TU_USUARIO con tu usuario real de GitHub
git remote add origin https://github.com/TU_USUARIO/MonitoreoWeblogic.git

# Verificar que se agregó correctamente
git remote -v
# Debe mostrar:
# origin  https://github.com/TU_USUARIO/MonitoreoWeblogic.git (fetch)
# origin  https://github.com/TU_USUARIO/MonitoreoWeblogic.git (push)

# Configurar branch principal como main
git branch -M main
```

### Paso 4: Push a GitHub

```bash
# Subir todo a GitHub
git push -u origin main

# Si te pide autenticación:
# - Usuario: tu_usuario_github
# - Password: usa un Personal Access Token (NO tu password de GitHub)
```

---

## 🔑 Autenticación en GitHub

GitHub ya no acepta passwords normales. Necesitas un **Personal Access Token**.

### Crear Token:

1. Ir a: https://github.com/settings/tokens
2. Click en "Generate new token" → "Generate new token (classic)"
3. Nombre: "WebLogic Monitor Access"
4. Permisos: Marcar "repo" (todos los sub-checkboxes)
5. Click "Generate token"
6. **COPIAR EL TOKEN** (no lo volverás a ver)

### Usar el Token:

```bash
# Cuando hagas push y pida password, usar el TOKEN (no tu password)
git push -u origin main
Username: tu_usuario
Password: ghp_xxxxxxxxxxxxxxxxxxxx  ← PEGAR TOKEN AQUÍ
```

### Guardar Credenciales (opcional):

```bash
# Para no pedir el token cada vez
git config --global credential.helper store

# Ahora en el próximo push, guarda las credenciales
git push
# Pide usuario/token una vez y lo guarda
```

---

## ✅ Verificar que Funcionó

```bash
# 1. Ver el remote configurado
git remote -v

# 2. Ver el log
git log --oneline

# 3. Ver en GitHub
# Ir a: https://github.com/TU_USUARIO/MonitoreoWeblogic
# Deberías ver todos tus archivos
```

---

## 📁 Estructura que Verás en GitHub

```
MonitoreoWeblogic/
├── .gitignore
├── .env.example
├── README.md
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   │   ├── production.ini
│   │   └── group_vars/
│   └── playbooks/
│       └── deploy.yml
├── backend/
│   ├── app.py
│   ├── app_secure.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── deployment/
│   ├── deploy.sh
│   └── deploy_secure.sh
└── docs/
    ├── ARQUITECTURA_RED.md
    ├── AUDITORIA_SEGURIDAD.md
    └── ...
```

---

## 🔄 Flujo de Trabajo Diario

Una vez conectado, el flujo normal es:

```bash
# 1. Hacer cambios en archivos
vi ansible/inventory/production.ini

# 2. Ver qué cambió
git status
git diff

# 3. Agregar cambios
git add ansible/inventory/production.ini
# O agregar todo:
git add .

# 4. Commit con mensaje descriptivo
git commit -m "Update production inventory with new servers"

# 5. Push a GitHub
git push

# 6. (Opcional) Si trabajas en equipo, primero pull
git pull
# Luego continuar con tus cambios
```

---

## 🌿 Trabajar con Branches (Recomendado)

```bash
# Crear branch para nuevas features
git checkout -b feature/add-new-domains

# Hacer cambios y commit
git add .
git commit -m "Add 10 new WebLogic domains"

# Push del branch
git push -u origin feature/add-new-domains

# En GitHub: Crear Pull Request
# Después de merge, volver a main
git checkout main
git pull
```

---

## 🚨 Solución de Problemas

### Error: "remote origin already exists"

```bash
# Ver qué remote tienes
git remote -v

# Si está mal, eliminarlo
git remote remove origin

# Agregar el correcto
git remote add origin https://github.com/TU_USUARIO/MonitoreoWeblogic.git
```

### Error: "failed to push some refs"

```bash
# Significa que hay cambios en GitHub que no tienes local
# Solución: hacer pull primero
git pull origin main --allow-unrelated-histories

# Resolver conflictos si hay
# Luego push
git push -u origin main
```

### Error: "Authentication failed"

```bash
# Necesitas Personal Access Token (no password)
# Ver sección "Autenticación en GitHub" arriba
```

---

## 📖 Configurar README en GitHub

Una vez que hayas hecho push, el README.md se mostrará automáticamente.

Si quieres personalizar la página principal:

```bash
# Editar README
vi README.md

# Agregar información específica de tu organización
# Por ejemplo:
# - Contactos internos
# - Procedimientos específicos
# - Links a documentación interna

# Commit y push
git add README.md
git commit -m "Customize README for our organization"
git push
```

---

## 🔒 Proteger el Repositorio

### En GitHub → Settings:

1. **General**
   - Hacer el repo "Private" (si no lo es)
   
2. **Branches**
   - Branch protection rules para "main"
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   
3. **Secrets and variables**
   - Agregar secrets para CI/CD:
     - `ANSIBLE_VAULT_PASSWORD`
     - `SSH_PRIVATE_KEY`
     - `PROD_SERVER_IP`

---

## 🎯 Siguiente Paso: Configurar Ansible

Una vez que tu código esté en GitHub:

```bash
# 1. Clonar en otro servidor o máquina
git clone https://github.com/TU_USUARIO/MonitoreoWeblogic.git
cd MonitoreoWeblogic

# 2. Configurar Ansible
cd ansible
vi inventory/production.ini

# 3. Deploy
ansible-playbook -i inventory/production.ini playbooks/deploy.yml
```

---

## ✅ Checklist Final

```bash
☐ Proyecto extraído
☐ Git inicializado (git init)
☐ Archivos agregados (git add .)
☐ Commit inicial (git commit)
☐ Remote configurado (git remote add origin)
☐ Push exitoso (git push -u origin main)
☐ Verificado en GitHub (https://github.com/TU_USUARIO/MonitoreoWeblogic)
☐ README.md visible en GitHub
☐ .gitignore funcionando (no se subieron .env, passwords, etc)
```

---

## 🆘 Ayuda Rápida

```bash
# Ver estado
git status

# Ver historial
git log --oneline --graph --all

# Ver remotes
git remote -v

# Ver diferencias
git diff

# Deshacer último commit (mantiene cambios)
git reset --soft HEAD~1

# Deshacer cambios en archivo
git checkout -- archivo.txt

# Ver branches
git branch -a

# Ayuda
git help
git help push
```

---

## 📞 Comandos Resumen

```bash
# Setup inicial (una sola vez)
cd weblogic_monitor
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/MonitoreoWeblogic.git
git branch -M main
git push -u origin main

# Flujo diario
git pull                    # Obtener cambios
# ... hacer cambios ...
git add .                   # Agregar cambios
git commit -m "mensaje"     # Guardar cambios
git push                    # Subir a GitHub
```

---

**¡Listo! Tu código estará en GitHub en minutos.** 🚀

**Recuerda:** Reemplaza `TU_USUARIO` con tu usuario real de GitHub en todos los comandos.
