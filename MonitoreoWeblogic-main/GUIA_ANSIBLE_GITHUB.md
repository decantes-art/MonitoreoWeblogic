# 🚀 Automatización con Ansible - WebLogic Monitor

## 📋 Tabla de Contenidos
1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Setup de Git/GitHub](#setup-de-gitgithub)
3. [Configuración de Ansible](#configuración-de-ansible)
4. [Playbooks de Deployment](#playbooks-de-deployment)
5. [Ejecución](#ejecución)
6. [CI/CD Pipeline](#cicd-pipeline)

---

## 1️⃣ Estructura del Proyecto para Git/Ansible

```
weblogic-monitor/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # GitHub Actions CI
│       └── deploy.yml                # GitHub Actions Deploy
│
├── ansible/
│   ├── inventory/
│   │   ├── development.ini          # Inventario para DEV
│   │   ├── production.ini           # Inventario para PROD
│   │   └── group_vars/
│   │       ├── all.yml              # Variables globales
│   │       ├── development.yml      # Variables DEV
│   │       └── production.yml       # Variables PROD
│   │
│   ├── roles/
│   │   ├── weblogic-monitor/
│   │   │   ├── tasks/
│   │   │   │   ├── main.yml
│   │   │   │   ├── install.yml
│   │   │   │   ├── configure.yml
│   │   │   │   └── secure.yml
│   │   │   ├── templates/
│   │   │   │   ├── nginx.conf.j2
│   │   │   │   ├── systemd.service.j2
│   │   │   │   └── app_config.py.j2
│   │   │   ├── files/
│   │   │   │   └── requirements.txt
│   │   │   ├── handlers/
│   │   │   │   └── main.yml
│   │   │   ├── defaults/
│   │   │   │   └── main.yml
│   │   │   └── vars/
│   │   │       └── main.yml
│   │   │
│   │   ├── nginx/
│   │   │   └── ...
│   │   │
│   │   └── ssl-certs/
│   │       └── ...
│   │
│   ├── playbooks/
│   │   ├── deploy.yml               # Deploy principal
│   │   ├── deploy-secure.yml        # Deploy con seguridad
│   │   ├── update.yml               # Actualización
│   │   └── rollback.yml             # Rollback
│   │
│   └── ansible.cfg                  # Configuración Ansible
│
├── backend/
│   ├── app.py                       # Versión básica
│   ├── app_secure.py                # Versión segura
│   ├── requirements.txt
│   └── requirements_secure.txt
│
├── frontend/
│   └── index.html
│
├── scripts/
│   ├── test_domain_connection.sh
│   ├── setup_passwords.sh
│   └── encrypt_passwords.sh
│
├── docs/
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── ARQUITECTURA_RED.md
│   └── AUDITORIA_SEGURIDAD.md
│
├── .gitignore
├── .env.example                     # Ejemplo de variables de entorno
├── README.md
└── VERSION

```

---

## 2️⃣ Setup de Git/GitHub

### Paso 1: Inicializar Repositorio Local

```bash
# Extraer el proyecto
cd /tmp
tar -xzf weblogic_monitor_COMPLETO_SEGURO.tar.gz
cd weblogic_monitor

# Inicializar Git
git init

# Crear .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Logs
*.log
logs/

# Secrets - NUNCA subir esto a Git
.env
*.pem
*.key
*.crt
*_pass.txt
/secure/
.encryption_key

# Ansible
*.retry
.vault_pass

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temp
/tmp/
*.tmp
EOF

# Crear .env.example (sin valores reales)
cat > .env.example << 'EOF'
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# Encryption
ENCRYPTION_KEY=your-encryption-key-here

# CORS
ALLOWED_ORIGINS=https://your-domain.com

# Hosts
ALLOWED_HOSTS=your-domain.com,localhost

# WebLogic
WLST_PATH=/u01/oracle/middleware/oracle_common/common/bin/wlst.sh

# Cache
CACHE_TTL=15
EOF

# Primer commit
git add .
git commit -m "Initial commit: WebLogic Monitor Dashboard"
```

### Paso 2: Crear Repositorio en GitHub

**Opción A: Via Web (Recomendado para principiantes)**

1. Ir a https://github.com
2. Click en "New repository"
3. Nombre: `weblogic-monitor`
4. Descripción: "Real-time monitoring dashboard for 90 WebLogic domains"
5. Privado/Público: **PRIVADO** (contiene infraestructura crítica)
6. NO inicializar con README (ya lo tenemos)
7. Click "Create repository"

**Opción B: Via GitHub CLI**

```bash
# Instalar GitHub CLI
# RHEL/CentOS: sudo yum install gh
# Ubuntu: sudo apt install gh

# Login
gh auth login

# Crear repo
gh repo create weblogic-monitor --private --source=. --remote=origin

# Push
git push -u origin main
```

**Opción C: Via Git manual**

```bash
# En GitHub web, crear el repo vacío
# Luego ejecutar:

git remote add origin https://github.com/TU_USUARIO/weblogic-monitor.git
git branch -M main
git push -u origin main
```

### Paso 3: Proteger el Repositorio

**En GitHub → Settings → Branches:**

```
Branch protection rules:
✅ Require pull request reviews before merging
✅ Require status checks to pass before merging
✅ Require branches to be up to date before merging
✅ Include administrators
```

**En GitHub → Settings → Secrets:**

Agregar secrets para CI/CD:
```
ANSIBLE_VAULT_PASSWORD
SSH_PRIVATE_KEY
PROD_SERVER_IP
ENCRYPTION_KEY
JWT_SECRET_KEY
```

---

## 3️⃣ Configuración de Ansible

### Paso 1: Instalar Ansible

```bash
# En tu máquina de control (laptop o servidor de deployment)

# RHEL/CentOS
sudo yum install epel-release
sudo yum install ansible

# Ubuntu
sudo apt update
sudo apt install ansible

# O via pip (cualquier OS)
pip3 install ansible

# Verificar
ansible --version
```

### Paso 2: Crear Estructura de Ansible

```bash
cd weblogic_monitor
mkdir -p ansible/{inventory,roles,playbooks}
mkdir -p ansible/roles/weblogic-monitor/{tasks,templates,files,handlers,defaults,vars}
mkdir -p ansible/inventory/group_vars
```

### Paso 3: Configurar Inventarios

**ansible/inventory/production.ini:**

```ini
# Inventario de Producción

[dashboard_servers]
weblogic-monitor-prod01 ansible_host=192.168.1.100 ansible_user=oracle

[dashboard_servers:vars]
environment=production
install_dir=/opt/weblogic-monitor
frontend_dir=/var/www/weblogic-monitor
secure_dir=/secure/weblogic-monitor
use_secure_version=true
enable_https=true
domain_count=90

# WebLogic Domains (opcional, para validación)
[weblogic_domains]
wls-prod-admin01 ansible_host=10.1.1.10
wls-prod-admin02 ansible_host=10.1.1.11
# ... más dominios
```

**ansible/inventory/development.ini:**

```ini
# Inventario de Desarrollo

[dashboard_servers]
weblogic-monitor-dev01 ansible_host=192.168.1.200 ansible_user=oracle

[dashboard_servers:vars]
environment=development
install_dir=/opt/weblogic-monitor
frontend_dir=/var/www/weblogic-monitor
secure_dir=/secure/weblogic-monitor
use_secure_version=false  # Versión básica para dev
enable_https=false
domain_count=10  # Menos dominios en dev
```

**ansible/inventory/group_vars/all.yml:**

```yaml
---
# Variables globales para todos los ambientes

# Versiones
app_version: "2.0.0"
python_version: "3.8"

# Paths
wlst_path: "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"

# Configuración de aplicación
cache_ttl: 15
refresh_interval: 15000

# Usuario y grupo
app_user: oracle
app_group: oinstall

# Puertos
backend_port: 8000
nginx_http_port: 80
nginx_https_port: 443

# Logging
log_dir: /var/log/weblogic-monitor
log_retention_days: 30
```

**ansible/inventory/group_vars/production.yml:**

```yaml
---
# Variables específicas de producción

# Dominios permitidos
allowed_origins: "https://weblogic-monitor.ejemplo.com,https://dashboard.ejemplo.com"
allowed_hosts: "weblogic-monitor.ejemplo.com"

# SSL
ssl_certificate: "/etc/letsencrypt/live/weblogic-monitor.ejemplo.com/fullchain.pem"
ssl_certificate_key: "/etc/letsencrypt/live/weblogic-monitor.ejemplo.com/privkey.pem"

# Seguridad
enable_rate_limiting: true
max_requests_per_minute: 30

# Workers
uvicorn_workers: 4
```

**ansible/inventory/group_vars/development.yml:**

```yaml
---
# Variables específicas de desarrollo

allowed_origins: "*"
allowed_hosts: "localhost,192.168.1.200"

ssl_certificate: ""
ssl_certificate_key: ""

enable_rate_limiting: false
max_requests_per_minute: 100

uvicorn_workers: 2
```

### Paso 4: Configurar ansible.cfg

**ansible/ansible.cfg:**

```ini
[defaults]
inventory = ./inventory
roles_path = ./roles
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

# Logging
log_path = /var/log/ansible/weblogic-monitor.log

# SSH
remote_user = oracle
private_key_file = ~/.ssh/id_rsa

# Performance
forks = 10
timeout = 30

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

---

## 4️⃣ Playbooks de Ansible

### Playbook Principal: deploy.yml

**ansible/playbooks/deploy.yml:**

```yaml
---
- name: Deploy WebLogic Monitor Dashboard
  hosts: dashboard_servers
  become: yes
  
  vars_prompt:
    - name: "deployment_version"
      prompt: "¿Qué versión quieres desplegar? (basic/secure)"
      private: no
      default: "secure"
  
  pre_tasks:
    - name: Validate deployment environment
      assert:
        that:
          - environment is defined
          - environment in ['development', 'production']
        fail_msg: "Environment must be 'development' or 'production'"
    
    - name: Display deployment info
      debug:
        msg: |
          Deploying WebLogic Monitor to {{ environment }}
          Version: {{ deployment_version }}
          Target: {{ ansible_host }}
  
  roles:
    - role: weblogic-monitor
      tags: ['install', 'configure']

  post_tasks:
    - name: Verify deployment
      uri:
        url: "http://localhost:{{ backend_port }}/api/health"
        method: GET
        status_code: 200
      register: health_check
      retries: 3
      delay: 5
      
    - name: Display health check result
      debug:
        var: health_check.json
```

### Role Principal

**ansible/roles/weblogic-monitor/tasks/main.yml:**

```yaml
---
# Main tasks for weblogic-monitor role

- name: Include installation tasks
  include_tasks: install.yml
  tags: install

- name: Include configuration tasks
  include_tasks: configure.yml
  tags: configure

- name: Include security tasks
  include_tasks: secure.yml
  when: use_secure_version | bool
  tags: secure

- name: Start and enable services
  systemd:
    name: "{{ item }}"
    state: started
    enabled: yes
  loop:
    - weblogic-monitor
    - nginx
  tags: service
```

**ansible/roles/weblogic-monitor/tasks/install.yml:**

```yaml
---
- name: Install system dependencies
  package:
    name:
      - python38
      - python38-pip
      - nginx
      - git
    state: present

- name: Create application directories
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0755'
  loop:
    - "{{ install_dir }}"
    - "{{ install_dir }}/backend"
    - "{{ frontend_dir }}"
    - "{{ secure_dir }}"
    - "{{ log_dir }}"

- name: Create secure directory with restricted permissions
  file:
    path: "{{ secure_dir }}"
    state: directory
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0700'

- name: Copy backend application files
  copy:
    src: "{{ playbook_dir }}/../../backend/"
    dest: "{{ install_dir }}/backend/"
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0644'

- name: Copy frontend files
  copy:
    src: "{{ playbook_dir }}/../../frontend/index.html"
    dest: "{{ frontend_dir }}/index.html"
    owner: nginx
    group: nginx
    mode: '0644'

- name: Create Python virtual environment
  pip:
    requirements: "{{ install_dir }}/backend/{{ 'requirements_secure.txt' if use_secure_version else 'requirements.txt' }}"
    virtualenv: "{{ install_dir }}/backend/venv"
    virtualenv_command: python3 -m venv
  become_user: "{{ app_user }}"
```

**ansible/roles/weblogic-monitor/tasks/configure.yml:**

```yaml
---
- name: Generate JWT secret key
  command: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  register: jwt_secret
  changed_when: false
  when: use_secure_version | bool

- name: Generate encryption key
  command: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  register: encryption_key
  changed_when: false
  when: use_secure_version | bool

- name: Create .env file
  template:
    src: env.j2
    dest: "{{ install_dir }}/.env"
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0600'
  when: use_secure_version | bool

- name: Configure systemd service
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/weblogic-monitor.service
    owner: root
    group: root
    mode: '0644'
  notify: reload systemd

- name: Configure Nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/conf.d/weblogic-monitor.conf
    owner: root
    group: root
    mode: '0644'
  notify: reload nginx

- name: Test Nginx configuration
  command: nginx -t
  changed_when: false
```

**ansible/roles/weblogic-monitor/tasks/secure.yml:**

```yaml
---
- name: Setup SSL certificates with Let's Encrypt
  block:
    - name: Install certbot
      package:
        name:
          - certbot
          - python3-certbot-nginx
        state: present
    
    - name: Obtain SSL certificate
      command: >
        certbot --nginx
        -d {{ allowed_hosts.split(',')[0] }}
        --non-interactive
        --agree-tos
        --email {{ letsencrypt_email }}
      when: enable_https | bool
  when: environment == 'production'

- name: Setup log rotation
  copy:
    dest: /etc/logrotate.d/weblogic-monitor
    content: |
      {{ log_dir }}/*.log {
          daily
          rotate {{ log_retention_days }}
          compress
          delaycompress
          notifempty
          create 0640 {{ app_user }} {{ app_group }}
          sharedscripts
          postrotate
              systemctl reload weblogic-monitor > /dev/null 2>&1 || true
          endscript
      }
    owner: root
    group: root
    mode: '0644'

- name: Configure firewall rules
  firewalld:
    port: "{{ item }}"
    permanent: yes
    state: enabled
    immediate: yes
  loop:
    - "{{ nginx_http_port }}/tcp"
    - "{{ nginx_https_port }}/tcp"
  when: ansible_facts['os_family'] == 'RedHat'
```

### Templates

**ansible/roles/weblogic-monitor/templates/systemd.service.j2:**

```ini
[Unit]
Description=WebLogic Monitor Backend API
After=network.target

[Service]
Type=simple
User={{ app_user }}
Group={{ app_group }}
WorkingDirectory={{ install_dir }}/backend
{% if use_secure_version %}
EnvironmentFile={{ install_dir }}/.env
{% endif %}
Environment="PATH={{ install_dir }}/backend/venv/bin:{{ wlst_path | dirname }}"
Environment="ORACLE_HOME=/u01/oracle/middleware"
Environment="MW_HOME=/u01/oracle/middleware"
Environment="WLS_HOME=/u01/oracle/middleware/wlserver"
ExecStart={{ install_dir }}/backend/venv/bin/uvicorn {{ 'app_secure' if use_secure_version else 'app' }}:app --host 0.0.0.0 --port {{ backend_port }} --workers {{ uvicorn_workers }}
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
{% if use_secure_version %}
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/tmp {{ log_dir }}
{% endif %}

StandardOutput=journal
StandardError=journal
SyslogIdentifier=weblogic-monitor

[Install]
WantedBy=multi-user.target
```

**ansible/roles/weblogic-monitor/templates/env.j2:**

```bash
# WebLogic Monitor Environment Variables
# Generated by Ansible

JWT_SECRET_KEY={{ jwt_secret.stdout }}
ENCRYPTION_KEY={{ encryption_key.stdout }}
ALLOWED_ORIGINS={{ allowed_origins }}
ALLOWED_HOSTS={{ allowed_hosts }}
WLST_PATH={{ wlst_path }}
CACHE_TTL={{ cache_ttl }}
```

**ansible/roles/weblogic-monitor/templates/nginx.conf.j2:**

```nginx
{% if enable_https %}
server {
    listen {{ nginx_http_port }};
    server_name {{ allowed_hosts.split(',')[0] }};
    return 301 https://$server_name$request_uri;
}
{% endif %}

server {
{% if enable_https %}
    listen {{ nginx_https_port }} ssl http2;
    ssl_certificate {{ ssl_certificate }};
    ssl_certificate_key {{ ssl_certificate_key }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
{% else %}
    listen {{ nginx_http_port }};
{% endif %}
    
    server_name {{ allowed_hosts.split(',')[0] }};

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
{% if enable_https %}
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
{% endif %}

    # Frontend
    location / {
        root {{ frontend_dir }};
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:{{ backend_port }}/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    access_log {{ log_dir }}/nginx-access.log;
    error_log {{ log_dir }}/nginx-error.log;
}
```

### Handlers

**ansible/roles/weblogic-monitor/handlers/main.yml:**

```yaml
---
- name: reload systemd
  systemd:
    daemon_reload: yes

- name: restart weblogic-monitor
  systemd:
    name: weblogic-monitor
    state: restarted

- name: reload nginx
  systemd:
    name: nginx
    state: reloaded

- name: restart nginx
  systemd:
    name: nginx
    state: restarted
```

---

## 5️⃣ Ejecución

### Desde Tu Máquina Local

```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/weblogic-monitor.git
cd weblogic-monitor/ansible

# 2. Configurar SSH
ssh-copy-id oracle@192.168.1.100

# 3. Test de conectividad
ansible dashboard_servers -i inventory/production.ini -m ping

# 4. Deploy a Desarrollo
ansible-playbook -i inventory/development.ini playbooks/deploy.yml

# 5. Deploy a Producción (versión segura)
ansible-playbook -i inventory/production.ini playbooks/deploy.yml \
  -e "deployment_version=secure"

# 6. Con verbose para debugging
ansible-playbook -i inventory/production.ini playbooks/deploy.yml -vvv

# 7. Dry-run (verificar sin ejecutar)
ansible-playbook -i inventory/production.ini playbooks/deploy.yml --check

# 8. Solo tags específicos
ansible-playbook -i inventory/production.ini playbooks/deploy.yml --tags "configure"
```

### Con Ansible Vault (para secretos)

```bash
# 1. Crear archivo de vault para passwords
ansible-vault create ansible/inventory/group_vars/production_vault.yml

# Contenido:
# vault_jwt_secret: "tu_secret_real"
# vault_encryption_key: "tu_key_real"
# vault_letsencrypt_email: "tu@email.com"

# 2. Usar vault en playbook
ansible-playbook -i inventory/production.ini playbooks/deploy.yml \
  --ask-vault-pass

# 3. O con archivo de password
echo "tu_vault_password" > .vault_pass
chmod 600 .vault_pass
ansible-playbook -i inventory/production.ini playbooks/deploy.yml \
  --vault-password-file .vault_pass
```

---

## 6️⃣ CI/CD con GitHub Actions

**.github/workflows/ci.yml:**

```yaml
name: CI - Test and Lint

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install flake8 pylint
          pip install -r backend/requirements.txt
      
      - name: Lint with flake8
        run: |
          flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Lint Ansible
        run: |
          pip install ansible-lint
          cd ansible
          ansible-lint playbooks/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements_secure.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**.github/workflows/deploy.yml:**

```yaml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - development
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install Ansible
        run: |
          pip install ansible
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.PROD_SERVER_IP }} >> ~/.ssh/known_hosts
      
      - name: Create vault password file
        run: |
          echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}" > .vault_pass
          chmod 600 .vault_pass
      
      - name: Deploy with Ansible
        run: |
          cd ansible
          ansible-playbook \
            -i inventory/${{ github.event.inputs.environment }}.ini \
            playbooks/deploy.yml \
            --vault-password-file ../.vault_pass \
            -e "deployment_version=secure"
      
      - name: Verify deployment
        run: |
          sleep 10
          curl -f http://${{ secrets.PROD_SERVER_IP }}/api/health || exit 1
```

---

## 🎯 Flujo de Trabajo Completo

```
┌─────────────────────────────────────────────────────────────┐
│  FLUJO DE TRABAJO GITHUB + ANSIBLE                           │
└─────────────────────────────────────────────────────────────┘

1. DESARROLLO LOCAL
   ├─ Hacer cambios en código
   ├─ Commit local: git commit -m "feature: nueva funcionalidad"
   └─ Push a branch: git push origin feature/nueva-feature

2. GITHUB - PULL REQUEST
   ├─ Crear PR en GitHub
   ├─ CI ejecuta automáticamente (tests, lint)
   ├─ Code review del equipo
   └─ Merge a main

3. GITHUB ACTIONS - CI
   ├─ Tests automáticos
   ├─ Linting
   ├─ Build verification
   └─ ✅ Pass → Continuar

4. DEPLOY MANUAL (via GitHub Actions)
   ├─ Ir a Actions tab en GitHub
   ├─ Seleccionar "Deploy to Production"
   ├─ Click "Run workflow"
   ├─ Elegir environment (dev/prod)
   └─ Ansible despliega automáticamente

5. ANSIBLE DEPLOYMENT
   ├─ Conecta via SSH al servidor
   ├─ Ejecuta playbooks
   ├─ Instala/actualiza aplicación
   ├─ Configura servicios
   └─ Verifica deployment

6. VERIFICACIÓN
   ├─ Health check automático
   ├─ Smoke tests
   └─ ✅ Producción actualizada
```

---

## 📝 Comandos Rápidos de Referencia

```bash
# Git
git status                              # Ver cambios
git add .                               # Agregar todos los cambios
git commit -m "mensaje"                 # Commit
git push origin main                    # Push a GitHub
git pull origin main                    # Pull desde GitHub

# Ansible - Testing
ansible all -i inventory/production.ini -m ping
ansible-playbook playbooks/deploy.yml --check --diff

# Ansible - Deployment
ansible-playbook -i inventory/development.ini playbooks/deploy.yml
ansible-playbook -i inventory/production.ini playbooks/deploy.yml -e "use_secure_version=true"

# Ansible - Troubleshooting
ansible-playbook playbooks/deploy.yml -vvv
ansible-playbook playbooks/deploy.yml --start-at-task="Configure Nginx"

# Ansible - Ad-hoc commands
ansible dashboard_servers -i inventory/production.ini -a "systemctl status weblogic-monitor"
ansible dashboard_servers -i inventory/production.ini -m shell -a "tail -50 /var/log/weblogic-monitor/app.log"
```

---

## ✅ Checklist de Setup Inicial

```bash
☐ 1. Instalar Git localmente
☐ 2. Crear cuenta en GitHub
☐ 3. Crear repositorio en GitHub (privado)
☐ 4. Inicializar Git local y push
☐ 5. Configurar .gitignore (no subir secretos)
☐ 6. Instalar Ansible en máquina de control
☐ 7. Crear estructura de directorios de Ansible
☐ 8. Configurar inventarios (dev/prod)
☐ 9. Crear playbooks y roles
☐ 10. Configurar SSH keys para Ansible
☐ 11. Test de conectividad con Ansible
☐ 12. Primer deployment a dev
☐ 13. Configurar GitHub Actions (opcional)
☐ 14. Deployment a producción
☐ 15. Documentar proceso
```

---

**¡Listo para automatizar tus deployments!** 🚀
