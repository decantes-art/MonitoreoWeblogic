#!/bin/bash
#
# encrypt_passwords.sh
# Encripta archivos de contraseñas existentes usando Fernet
#

set -e

SECURE_DIR="/secure/weblogic-monitor"
BACKUP_DIR="/secure/weblogic-monitor-backup-$(date +%Y%m%d_%H%M%S)"
ENCRYPTION_KEY_FILE="/opt/weblogic-monitor/.encryption_key"

echo "=========================================="
echo "Password Encryption Tool"
echo "=========================================="
echo ""

# Verificar que existe el directorio
if [ ! -d "$SECURE_DIR" ]; then
    echo "Error: Directorio $SECURE_DIR no existe"
    exit 1
fi

# Crear backup
echo "Creando backup de passwords en: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$SECURE_DIR"/*.txt "$BACKUP_DIR/" 2>/dev/null || true
chmod 700 "$BACKUP_DIR"

# Generar o usar key de encriptación existente
if [ -f "$ENCRYPTION_KEY_FILE" ]; then
    echo "Usando key de encriptación existente"
    ENCRYPTION_KEY=$(cat "$ENCRYPTION_KEY_FILE")
else
    echo "Generando nueva key de encriptación..."
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    echo "$ENCRYPTION_KEY" > "$ENCRYPTION_KEY_FILE"
    chmod 600 "$ENCRYPTION_KEY_FILE"
    chown oracle:oinstall "$ENCRYPTION_KEY_FILE"
    echo "Key guardada en: $ENCRYPTION_KEY_FILE"
    echo ""
    echo "⚠️  IMPORTANTE: Guarda esta key en un lugar seguro!"
    echo "⚠️  Sin ella, no podrás desencriptar las contraseñas"
    echo ""
fi

# Script Python para encriptar
ENCRYPT_SCRIPT=$(mktemp)
cat > "$ENCRYPT_SCRIPT" << 'PYTHON_EOF'
import sys
from cryptography.fernet import Fernet

key = sys.argv[1].encode()
password = sys.argv[2]

f = Fernet(key)
encrypted = f.encrypt(password.encode())
print(encrypted.decode())
PYTHON_EOF

# Encriptar todos los archivos
echo "Encriptando archivos de password..."
for file in "$SECURE_DIR"/*.txt; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo -n "  Procesando $filename... "
        
        # Leer password actual
        password=$(cat "$file")
        
        # Verificar si ya está encriptado (contiene caracteres no imprimibles)
        if [[ $password =~ [^[:print:]] ]] || [[ $password =~ ^gAAAAA ]]; then
            echo "ya encriptado (saltando)"
            continue
        fi
        
        # Encriptar
        encrypted=$(python3 "$ENCRYPT_SCRIPT" "$ENCRYPTION_KEY" "$password")
        
        # Guardar
        echo "$encrypted" > "$file"
        
        echo "✓ OK"
    fi
done

# Cleanup
rm -f "$ENCRYPT_SCRIPT"

echo ""
echo "=========================================="
echo "Encriptación completada"
echo "=========================================="
echo ""
echo "Backup guardado en: $BACKUP_DIR"
echo "Key de encriptación: $ENCRYPTION_KEY_FILE"
echo ""
echo "Próximos pasos:"
echo "1. Agregar key a variables de entorno:"
echo "   export ENCRYPTION_KEY='$ENCRYPTION_KEY'"
echo ""
echo "2. O agregarlo al service de systemd:"
echo "   Environment=\"ENCRYPTION_KEY=$ENCRYPTION_KEY\""
echo ""
echo "3. Actualizar backend para usar passwords encriptadas"
echo ""
echo "⚠️  GUARDA LA KEY DE FORMA SEGURA!"
