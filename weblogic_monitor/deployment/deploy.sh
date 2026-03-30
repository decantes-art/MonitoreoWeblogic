#!/bin/bash
#
# WebLogic Monitor - Deployment Script
# Automatiza la instalación y configuración del dashboard
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/weblogic-monitor"
FRONTEND_DIR="/var/www/weblogic-monitor"
SECURE_DIR="/secure/weblogic-monitor"
SERVICE_NAME="weblogic-monitor"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}WebLogic Monitor - Deployment Script${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Este script debe ejecutarse como root${NC}"
    exit 1
fi

# Step 1: Install system dependencies
echo -e "${YELLOW}[1/8] Instalando dependencias del sistema...${NC}"
yum install -y python38 python38-pip nginx || apt-get install -y python3.8 python3-pip nginx

# Step 2: Create directories
echo -e "${YELLOW}[2/8] Creando directorios...${NC}"
mkdir -p $INSTALL_DIR/backend
mkdir -p $FRONTEND_DIR
mkdir -p $SECURE_DIR
mkdir -p /var/log/weblogic-monitor

# Step 3: Copy backend files
echo -e "${YELLOW}[3/8] Copiando archivos del backend...${NC}"
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: No se encuentra el directorio 'backend'${NC}"
    echo "Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

cp -r backend/* $INSTALL_DIR/backend/
chown -R oracle:oinstall $INSTALL_DIR

# Step 4: Setup Python virtual environment
echo -e "${YELLOW}[4/8] Configurando entorno virtual de Python...${NC}"
cd $INSTALL_DIR/backend
sudo -u oracle python3 -m venv venv
sudo -u oracle venv/bin/pip install --upgrade pip
sudo -u oracle venv/bin/pip install -r requirements.txt

# Step 5: Copy frontend files
echo -e "${YELLOW}[5/8] Copiando archivos del frontend...${NC}"
if [ ! -f "frontend/index.html" ]; then
    echo -e "${RED}Error: No se encuentra frontend/index.html${NC}"
    exit 1
fi

cp frontend/index.html $FRONTEND_DIR/
chown -R nginx:nginx $FRONTEND_DIR

# Step 6: Configure systemd service
echo -e "${YELLOW}[6/8] Configurando servicio systemd...${NC}"
cp deployment/weblogic-monitor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Step 7: Configure Nginx
echo -e "${YELLOW}[7/8] Configurando Nginx...${NC}"
cp deployment/nginx.conf /etc/nginx/conf.d/weblogic-monitor.conf

# Validate Nginx configuration
nginx -t
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Configuración de Nginx inválida${NC}"
    exit 1
fi

# Step 8: Setup secure directory for passwords
echo -e "${YELLOW}[8/8] Configurando directorio seguro...${NC}"
chmod 700 $SECURE_DIR
chown oracle:oinstall $SECURE_DIR

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Instalación completada exitosamente${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo ""
echo "1. Configurar dominios en: $INSTALL_DIR/backend/app.py"
echo "   - Editar DOMAINS_CONFIG con tus 90 dominios"
echo ""
echo "2. Crear archivos de contraseña en: $SECURE_DIR"
echo "   Ejemplo:"
echo "   echo 'tu_password' > $SECURE_DIR/domain1_pass.txt"
echo "   chmod 600 $SECURE_DIR/domain1_pass.txt"
echo ""
echo "3. Actualizar URL del backend en: $FRONTEND_DIR/index.html"
echo "   - Buscar API_BASE_URL y configurar la URL correcta"
echo ""
echo "4. Configurar certificados SSL (opcional pero recomendado)"
echo "   - Editar /etc/nginx/conf.d/weblogic-monitor.conf"
echo "   - Actualizar rutas de certificados SSL"
echo ""
echo "5. Iniciar servicios:"
echo "   systemctl start $SERVICE_NAME"
echo "   systemctl restart nginx"
echo ""
echo "6. Verificar estado:"
echo "   systemctl status $SERVICE_NAME"
echo "   curl http://localhost:8000/api/health"
echo ""
echo "7. Acceder al dashboard:"
echo "   http://$(hostname):80"
echo ""
echo -e "${GREEN}¡Listo para usar!${NC}"
