#!/bin/bash
#
# deploy_secure.sh
# Despliega la versión SEGURA del WebLogic Monitor
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}WebLogic Monitor - SECURE Deployment${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Este script debe ejecutarse como root${NC}"
    exit 1
fi

INSTALL_DIR="/opt/weblogic-monitor"
FRONTEND_DIR="/var/www/weblogic-monitor"

# ============================================
# 1. Instalación base (si no existe)
# ============================================
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[1/10] Ejecutando instalación base...${NC}"
    ./deployment/deploy.sh
else
    echo -e "${GREEN}[1/10] Instalación base ya existe${NC}"
fi

# ============================================
# 2. Instalar dependencias de seguridad
# ============================================
echo -e "${YELLOW}[2/10] Instalando dependencias de seguridad...${NC}"
cd "$INSTALL_DIR/backend"
sudo -u oracle venv/bin/pip install -r requirements_secure.txt

# ============================================
# 3. Generar secret key para JWT
# ============================================
echo -e "${YELLOW}[3/10] Generando JWT secret key...${NC}"
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "JWT_SECRET_KEY=$JWT_SECRET" >> /opt/weblogic-monitor/.env
chmod 600 /opt/weblogic-monitor/.env

# ============================================
# 4. Generar encryption key para passwords
# ============================================
echo -e "${YELLOW}[4/10] Generando encryption key...${NC}"
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> /opt/weblogic-monitor/.env

echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Keys generadas${NC}"
echo "JWT_SECRET_KEY: ${JWT_SECRET:0:20}..."
echo "ENCRYPTION_KEY: ${ENCRYPTION_KEY:0:20}..."
echo ""
echo "Guardadas en: /opt/weblogic-monitor/.env"
echo ""

# ============================================
# 5. Encriptar passwords existentes
# ============================================
echo -e "${YELLOW}[5/10] Encriptando passwords...${NC}"
if [ -d "/secure/weblogic-monitor" ] && [ "$(ls -A /secure/weblogic-monitor/*.txt 2>/dev/null)" ]; then
    read -p "¿Encriptar passwords existentes? (s/N): " encrypt_now
    if [ "$encrypt_now" = "s" ] || [ "$encrypt_now" = "S" ]; then
        ./scripts/encrypt_passwords.sh
    fi
else
    echo "No hay passwords para encriptar aún"
fi

# ============================================
# 6. Configurar ALLOWED_ORIGINS
# ============================================
echo -e "${YELLOW}[6/10] Configurando CORS...${NC}"
read -p "Ingresa los orígenes permitidos (separados por coma): " origins
echo "ALLOWED_ORIGINS=$origins" >> /opt/weblogic-monitor/.env

# ============================================
# 7. Configurar ALLOWED_HOSTS
# ============================================
echo -e "${YELLOW}[7/10] Configurando hosts permitidos...${NC}"
read -p "Ingresa los hosts permitidos (separados por coma): " hosts
echo "ALLOWED_HOSTS=$hosts" >> /opt/weblogic-monitor/.env

# ============================================
# 8. Configurar HTTPS con Let's Encrypt
# ============================================
echo -e "${YELLOW}[8/10] Configurando HTTPS...${NC}"
read -p "¿Configurar HTTPS con Let's Encrypt? (s/N): " setup_https

if [ "$setup_https" = "s" ] || [ "$setup_https" = "S" ]; then
    # Instalar certbot
    if ! command -v certbot &> /dev/null; then
        echo "Instalando certbot..."
        yum install -y certbot python3-certbot-nginx || apt-get install -y certbot python3-certbot-nginx
    fi
    
    read -p "Ingresa tu dominio (ej: weblogic-monitor.ejemplo.com): " domain
    read -p "Ingresa tu email: " email
    
    # Obtener certificado
    certbot --nginx -d "$domain" --non-interactive --agree-tos --email "$email"
    
    echo -e "${GREEN}✓ HTTPS configurado${NC}"
else
    echo "Saltando configuración HTTPS"
    echo "⚠️  RECUERDA: Configurar HTTPS manualmente antes de producción"
fi

# ============================================
# 9. Actualizar systemd service
# ============================================
echo -e "${YELLOW}[9/10] Actualizando servicio systemd...${NC}"

cat > /etc/systemd/system/weblogic-monitor.service << EOF
[Unit]
Description=WebLogic Monitor Backend API - SECURE
After=network.target

[Service]
Type=simple
User=oracle
Group=oinstall
WorkingDirectory=/opt/weblogic-monitor/backend
EnvironmentFile=/opt/weblogic-monitor/.env
Environment="PATH=/opt/weblogic-monitor/backend/venv/bin:/u01/oracle/middleware/oracle_common/common/bin"
Environment="ORACLE_HOME=/u01/oracle/middleware"
Environment="MW_HOME=/u01/oracle/middleware"
Environment="WLS_HOME=/u01/oracle/middleware/wlserver"
ExecStart=/opt/weblogic-monitor/backend/venv/bin/uvicorn app_secure:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/tmp /var/log/weblogic-monitor

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=weblogic-monitor

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# ============================================
# 10. Configurar logs de auditoría
# ============================================
echo -e "${YELLOW}[10/10] Configurando logs...${NC}"
mkdir -p /var/log/weblogic-monitor
chown oracle:oinstall /var/log/weblogic-monitor
chmod 750 /var/log/weblogic-monitor

# Configurar logrotate
cat > /etc/logrotate.d/weblogic-monitor << EOF
/var/log/weblogic-monitor/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 oracle oinstall
    sharedscripts
    postrotate
        systemctl reload weblogic-monitor > /dev/null 2>&1 || true
    endscript
}
EOF

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Despliegue SEGURO completado${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Resumen de configuración:${NC}"
echo "✓ Dependencias de seguridad instaladas"
echo "✓ JWT secret key generado"
echo "✓ Encryption key para passwords generado"
echo "✓ CORS configurado"
echo "✓ Hosts permitidos configurados"
if [ "$setup_https" = "s" ] || [ "$setup_https" = "S" ]; then
    echo "✓ HTTPS configurado"
else
    echo "⚠ HTTPS NO configurado"
fi
echo "✓ Servicio systemd actualizado"
echo "✓ Logs de auditoría configurados"
echo ""
echo -e "${YELLOW}Variables de entorno guardadas en:${NC}"
echo "/opt/weblogic-monitor/.env"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo ""
echo "1. Crear usuario administrador:"
echo "   cd /opt/weblogic-monitor/backend"
echo "   source venv/bin/activate"
echo "   python3 -c 'from app_secure import get_password_hash; print(get_password_hash(\"tu_password\"))'"
echo ""
echo "2. Agregar hash al código (fake_users_db en app_secure.py)"
echo ""
echo "3. Reiniciar servicios:"
echo "   systemctl restart weblogic-monitor nginx"
echo ""
echo "4. Obtener token de acceso:"
echo "   curl -X POST http://localhost:8000/api/auth/token \\"
echo "     -d 'username=admin&password=tu_password'"
echo ""
echo "5. Usar token en requests:"
echo "   curl -H 'Authorization: Bearer TOKEN' \\"
echo "     http://localhost:8000/api/domains"
echo ""
echo -e "${GREEN}¡Sistema seguro listo!${NC}"
echo ""
echo -e "${RED}⚠️  IMPORTANTE:${NC}"
echo "   - Guarda las keys de /opt/weblogic-monitor/.env en un lugar seguro"
echo "   - Cambia las contraseñas por defecto"
echo "   - Revisa los logs regularmente: /var/log/weblogic-monitor/"
echo "   - Configura HTTPS si no lo hiciste aún"
