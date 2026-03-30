#!/bin/bash
#
# setup_passwords.sh
# Script para crear archivos de contraseñas de forma segura
#

SECURE_DIR="/secure/weblogic-monitor"

echo "======================================"
echo "WebLogic Monitor - Password Setup"
echo "======================================"
echo ""

# Check if running as root or oracle user
if [ "$EUID" -eq 0 ]; then
    TARGET_USER="oracle"
    TARGET_GROUP="oinstall"
elif [ "$USER" == "oracle" ]; then
    TARGET_USER="oracle"
    TARGET_GROUP="oinstall"
else
    echo "Error: Este script debe ejecutarse como root o usuario oracle"
    exit 1
fi

# Create secure directory if it doesn't exist
if [ ! -d "$SECURE_DIR" ]; then
    echo "Creando directorio seguro: $SECURE_DIR"
    mkdir -p $SECURE_DIR
    chown $TARGET_USER:$TARGET_GROUP $SECURE_DIR
    chmod 700 $SECURE_DIR
fi

echo "Este script te ayudará a crear archivos de contraseñas para tus dominios."
echo "Las contraseñas se almacenarán de forma segura con permisos 600."
echo ""

# Function to create password file
create_password_file() {
    local domain_name=$1
    local password_file="$SECURE_DIR/${domain_name}_pass.txt"
    
    echo ""
    echo "Configurando: $domain_name"
    echo "Archivo: $password_file"
    
    # Check if file already exists
    if [ -f "$password_file" ]; then
        read -p "El archivo ya existe. ¿Sobrescribir? (s/N): " overwrite
        if [ "$overwrite" != "s" ] && [ "$overwrite" != "S" ]; then
            echo "Saltando $domain_name..."
            return
        fi
    fi
    
    # Read password (hidden)
    read -sp "Ingresa la contraseña para $domain_name: " password1
    echo ""
    read -sp "Confirma la contraseña: " password2
    echo ""
    
    if [ "$password1" != "$password2" ]; then
        echo "Error: Las contraseñas no coinciden"
        return 1
    fi
    
    if [ -z "$password1" ]; then
        echo "Error: La contraseña no puede estar vacía"
        return 1
    fi
    
    # Write password to file
    echo "$password1" > "$password_file"
    chown $TARGET_USER:$TARGET_GROUP "$password_file"
    chmod 600 "$password_file"
    
    echo "✓ Contraseña guardada exitosamente"
}

# Interactive mode
echo "Opciones:"
echo "1. Configurar un dominio individual"
echo "2. Configurar múltiples dominios desde archivo CSV"
echo "3. Configurar todos los dominios con la misma contraseña"
echo ""
read -p "Selecciona una opción (1-3): " option

case $option in
    1)
        # Single domain
        read -p "Nombre del dominio (ej: prod01): " domain_name
        create_password_file "$domain_name"
        ;;
        
    2)
        # CSV file
        read -p "Ruta del archivo CSV (formato: nombre_dominio,password): " csv_file
        
        if [ ! -f "$csv_file" ]; then
            echo "Error: Archivo no encontrado: $csv_file"
            exit 1
        fi
        
        while IFS=',' read -r domain_name password || [ -n "$domain_name" ]; do
            # Skip comments and empty lines
            [[ "$domain_name" =~ ^#.*$ ]] && continue
            [[ -z "$domain_name" ]] && continue
            
            password_file="$SECURE_DIR/${domain_name}_pass.txt"
            echo "$password" > "$password_file"
            chown $TARGET_USER:$TARGET_GROUP "$password_file"
            chmod 600 "$password_file"
            echo "✓ Creado: $password_file"
        done < "$csv_file"
        
        echo ""
        echo "Todos los archivos de contraseña creados exitosamente"
        ;;
        
    3)
        # Same password for all
        read -p "Ingresa los nombres de dominio separados por espacio: " -a domains
        
        read -sp "Ingresa la contraseña para todos los dominios: " common_password
        echo ""
        read -sp "Confirma la contraseña: " confirm_password
        echo ""
        
        if [ "$common_password" != "$confirm_password" ]; then
            echo "Error: Las contraseñas no coinciden"
            exit 1
        fi
        
        for domain_name in "${domains[@]}"; do
            password_file="$SECURE_DIR/${domain_name}_pass.txt"
            echo "$common_password" > "$password_file"
            chown $TARGET_USER:$TARGET_GROUP "$password_file"
            chmod 600 "$password_file"
            echo "✓ Creado: $password_file"
        done
        
        echo ""
        echo "Todos los archivos de contraseña creados exitosamente"
        ;;
        
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "Resumen de archivos creados:"
echo "======================================"
ls -lh $SECURE_DIR/*.txt 2>/dev/null || echo "No hay archivos en $SECURE_DIR"

echo ""
echo "Nota: Los archivos tienen permisos 600 (solo lectura para el propietario)"
echo "      Ubicación: $SECURE_DIR"
