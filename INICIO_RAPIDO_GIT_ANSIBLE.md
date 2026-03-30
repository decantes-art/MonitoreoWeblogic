# 🚀 Inicio Rápido - Git + Ansible

## 📍 Por Dónde Empezar

### Opción 1: Solo quiero desplegar (SIN Git/GitHub)

```bash
# 1. Extraer archivos
tar -xzf weblogic_monitor_COMPLETO_SEGURO.tar.gz
cd weblogic_monitor

# 2. Ir a Ansible
cd ansible

# 3. Editar inventario con tu servidor
vi inventory/production.ini
# Cambiar: ansible_host=192.168.1.100  (tu IP real)

# 4. Configurar SSH
ssh-copy-id oracle@192.168.1.100

# 5. Test
ansible dashboard_servers -i inventory/production.ini -m ping

# 6. Deploy!
ansible-playbook -i inventory/production.ini playbooks/deploy.yml
```

**✅ LISTO! No necesitas Git para esto.**

---

### Opción 2: Quiero usar Git/GitHub (Recomendado)

```bash
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: CONFIGURAR GIT LOCAL (5 minutos)                   │
└─────────────────────────────────────────────────────────────┘

# 1. Extraer proyecto
tar -xzf weblogic_monitor_COMPLETO_SEGURO.tar.gz
cd weblogic_monitor

# 2. Inicializar Git
git init
git add .
git commit -m "Initial commit"

┌─────────────────────────────────────────────────────────────┐
│  PASO 2: CREAR REPO EN GITHUB (3 minutos)                   │
└─────────────────────────────────────────────────────────────┘

# Via Web:
1. Ir a: https://github.com/new
2. Nombre: weblogic-monitor
3. Privado: ✅ (IMPORTANTE)
4. NO inicializar con README
5. Click "Create repository"

# Copiar los comandos que GitHub muestra:
git remote add origin https://github.com/TU_USUARIO/weblogic-monitor.git
git branch -M main
git push -u origin main

┌─────────────────────────────────────────────────────────────┐
│  PASO 3: CONFIGURAR ANSIBLE (10 minutos)                    │
└─────────────────────────────────────────────────────────────┘

# 1. Instalar Ansible (si no lo tienes)
pip3 install ansible

# 2. Ir a directorio Ansible
cd ansible

# 3. Editar inventario
vi inventory/production.ini
# Actualizar con tus servidores

# 4. Editar variables
vi inventory/group_vars/production.yml
# Actualizar dominios permitidos

# 5. Configurar SSH
ssh-copy-id oracle@TU_SERVIDOR

# 6. Test de conectividad
ansible all -i inventory/production.ini -m ping

┌─────────────────────────────────────────────────────────────┐
│  PASO 4: PRIMER DEPLOYMENT (5 minutos)                      │
└─────────────────────────────────────────────────────────────┘

# Deploy a producción
ansible-playbook -i inventory/production.ini playbooks/deploy.yml

# Verificar
curl http://TU_SERVIDOR:8000/api/health
```

---

## 🎯 Decisión Rápida

### ¿Cuándo usar cada opción?

| Criterio | Sin Git | Con Git/GitHub |
|----------|---------|----------------|
| **Equipo** | 1 persona | 2+ personas |
| **Servidores** | 1-2 | 3+ |
| **Cambios** | Pocos | Frecuentes |
| **Versionado** | No necesito | Sí necesito |
| **CI/CD** | No | Sí |
| **Tiempo setup** | 10 min | 30 min |
| **Complejidad** | Baja | Media |

### Recomendación:

```
👤 Solo tú → Empezar sin Git (Opción 1)
         → Migrar a Git después si lo necesitas

👥 Equipo → Git desde el inicio (Opción 2)
```

---

## 📂 Estructura de Archivos - Dónde Está Qué

```
weblogic_monitor/
│
├── 📖 README.md                    ← Documentación principal
├── 📖 GUIA_ANSIBLE_GITHUB.md       ← Esta guía (completa)
├── 📖 INICIO_RAPIDO_GIT_ANSIBLE.md ← Esta guía (resumen)
│
├── backend/                        ← Código Python
│   ├── app.py                      ← Versión básica
│   └── app_secure.py               ← Versión segura ✅
│
├── frontend/                       ← Dashboard React
│   └── index.html
│
├── ansible/                        ← 🎯 CONFIGURAR ESTO
│   ├── ansible.cfg                 ← Configuración Ansible
│   ├── inventory/                  ← 🎯 EDITAR ESTO PRIMERO
│   │   ├── production.ini          ← Servidores de producción
│   │   ├── development.ini         ← Servidores de desarrollo
│   │   └── group_vars/             ← Variables por ambiente
│   │       ├── all.yml
│   │       ├── production.yml      ← 🎯 Dominios, HTTPS
│   │       └── development.yml
│   │
│   ├── playbooks/                  ← Scripts de deployment
│   │   └── deploy.yml              ← Playbook principal
│   │
│   └── roles/                      ← Lógica de instalación
│       └── weblogic-monitor/
│
└── deployment/                     ← Scripts standalone
    ├── deploy.sh                   ← Deploy básico (sin Ansible)
    └── deploy_secure.sh            ← Deploy seguro (sin Ansible)
```

---

## 🔧 Configuraciones Mínimas Necesarias

### 1. Inventario (OBLIGATORIO)

**Archivo:** `ansible/inventory/production.ini`

```ini
[dashboard_servers]
weblogic-monitor-prod ansible_host=TU_IP_AQUI ansible_user=oracle
```

### 2. Variables (OBLIGATORIO para producción)

**Archivo:** `ansible/inventory/group_vars/production.yml`

```yaml
allowed_origins: "https://TU_DOMINIO.com"
allowed_hosts: "TU_DOMINIO.com"
letsencrypt_email: TU_EMAIL@ejemplo.com
```

### 3. SSH (OBLIGATORIO)

```bash
# Copiar tu SSH key al servidor
ssh-copy-id oracle@TU_SERVIDOR

# Verificar
ssh oracle@TU_SERVIDOR "echo OK"
```

**✅ Con esto ya puedes desplegar!**

---

## 🚦 Comandos Esenciales

```bash
# ============================================
# Git (si usas GitHub)
# ============================================

# Guardar cambios
git add .
git commit -m "descripción del cambio"
git push

# Obtener cambios del equipo
git pull

# Ver estado
git status

# ============================================
# Ansible
# ============================================

# Test de conectividad
ansible all -i inventory/production.ini -m ping

# Deploy a desarrollo
ansible-playbook -i inventory/development.ini playbooks/deploy.yml

# Deploy a producción
ansible-playbook -i inventory/production.ini playbooks/deploy.yml

# Ver qué haría sin ejecutar (dry-run)
ansible-playbook -i inventory/production.ini playbooks/deploy.yml --check

# Ver detalles de ejecución
ansible-playbook -i inventory/production.ini playbooks/deploy.yml -vvv

# ============================================
# Verificación post-deploy
# ============================================

# Health check
curl http://TU_SERVIDOR:8000/api/health

# Ver logs
ssh oracle@TU_SERVIDOR "tail -50 /var/log/weblogic-monitor/app.log"

# Ver estado del servicio
ssh oracle@TU_SERVIDOR "systemctl status weblogic-monitor"
```

---

## ❓ FAQ - Preguntas Frecuentes

### P: ¿Necesito GitHub para usar Ansible?
**R:** NO. Ansible funciona independiente de Git/GitHub.

### P: ¿Puedo empezar sin Git y agregarlo después?
**R:** SÍ. Puedes iniciar con Ansible solamente y agregar Git cuando lo necesites.

### P: ¿Dónde pongo las contraseñas de WebLogic?
**R:** En `/secure/weblogic-monitor/` en cada servidor. Ansible puede copiarlas con el playbook.

### P: ¿Puedo tener múltiples ambientes?
**R:** SÍ. Crea un inventario por ambiente (dev, qa, prod).

### P: ¿Cómo actualizo el código?
**R:** Con Git: `git pull` + `ansible-playbook deploy.yml`  
Sin Git: Reemplaza archivos + `ansible-playbook deploy.yml`

### P: ¿Qué hago si algo falla?
**R:** Ejecuta con `-vvv` para ver detalles:
```bash
ansible-playbook playbooks/deploy.yml -vvv
```

---

## 📞 Próximos Pasos

Una vez que funcione, considera:

1. **Agregar más playbooks:**
   - `update.yml` - Actualizar solo el código
   - `rollback.yml` - Volver a versión anterior
   - `backup.yml` - Backup de configuración

2. **Ansible Vault para secretos:**
   ```bash
   ansible-vault create secrets.yml
   ```

3. **CI/CD con GitHub Actions:**
   - Deploy automático en cada push
   - Tests automáticos

4. **Monitoreo:**
   - Configurar alertas
   - Dashboard de Grafana

---

## 🎓 Recursos de Aprendizaje

- **Ansible:** https://docs.ansible.com/ansible/latest/user_guide/index.html
- **Git Basics:** https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
- **GitHub:** https://docs.github.com/en/get-started

---

## ✅ Checklist de Verificación

```bash
☐ Archivos extraídos
☐ Inventario editado con mi servidor
☐ Variables actualizadas con mi dominio
☐ SSH configurado y probado
☐ Ansible instalado
☐ Test de conectividad OK
☐ Primer deployment exitoso
☐ Health check pasa
☐ Dashboard accesible

# Opcional (Git/GitHub)
☐ Git inicializado
☐ Repositorio creado en GitHub
☐ Código subido a GitHub
☐ .gitignore configurado (no subir secretos)
```

---

**¡Empieza por lo simple y crece según necesites!** 🚀

Para documentación completa, ver: `GUIA_ANSIBLE_GITHUB.md`
