#!/bin/bash
#
# setup_secure_password.sh
# Script para encriptar el password de WebLogic de forma segura
#

set -e

echo "=========================================="
echo "Setup Password Encriptado - WebLogic"
echo "=========================================="
echo ""

# Crear directorio secure si no existe
mkdir -p secure

# Verificar si cryptography está instalado
echo "Verificando dependencias..."
python3 -c "from cryptography.fernet import Fernet" 2>/dev/null || {
    echo "Instalando cryptography..."
    pip3 install cryptography --break-system-packages 2>/dev/null || \
    pip3 install cryptography --user 2>/dev/null || \
    pip3 install cryptography
}

# Pedir password de forma segura
echo ""
read -sp "Ingresa el password de WebLogic (usuario: uamonmidkio): " WEBLOGIC_PASS
echo ""
read -sp "Confirma el password: " WEBLOGIC_PASS_CONFIRM
echo ""

# Verificar que coincidan
if [ "$WEBLOGIC_PASS" != "$WEBLOGIC_PASS_CONFIRM" ]; then
    echo "ERROR: Los passwords no coinciden"
    exit 1
fi

if [ -z "$WEBLOGIC_PASS" ]; then
    echo "ERROR: El password no puede estar vacío"
    exit 1
fi

# Generar key y encriptar
echo ""
echo "Encriptando password..."

python3 << EOF
from cryptography.fernet import Fernet
import sys

try:
    # Generar key de encriptación
    key = Fernet.generate_key()
    
    # Guardar key
    with open('secure/.encryption_key', 'wb') as f:
        f.write(key)
    
    # Encriptar password
    fernet = Fernet(key)
    encrypted = fernet.encrypt(b"$WEBLOGIC_PASS")
    
    # Guardar password encriptado
    with open('secure/pro1_pass.txt', 'wb') as f:
        f.write(encrypted)
    
    print("")
    print("✅ Password encriptado exitosamente!")
    print("")
    print("Archivos creados:")
    print("  - secure/.encryption_key  (key de encriptación)")
    print("  - secure/pro1_pass.txt    (password encriptado)")
    print("")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF

# Proteger archivos
chmod 600 secure/pro1_pass.txt
chmod 600 secure/.encryption_key
chmod 700 secure

echo "🔒 Permisos configurados:"
ls -la secure/

echo ""
echo "=========================================="
echo "✅ Configuración completada!"
echo "=========================================="
echo ""
echo "IMPORTANTE: Guarda la encryption key en un lugar seguro:"
echo ""
cat secure/.encryption_key
echo ""
echo ""
echo "Próximo paso: Ejecutar ./deployment/deploy.sh"
