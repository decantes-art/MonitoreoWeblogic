#!/bin/bash
#
# test_domain_connection.sh
# Script de utilidad para probar la conexión a un dominio WebLogic
#

usage() {
    echo "Uso: $0 <admin_url> <username> <password_file>"
    echo ""
    echo "Ejemplo:"
    echo "  $0 t3://localhost:7001 weblogic /secure/prod1_pass.txt"
    exit 1
}

if [ $# -ne 3 ]; then
    usage
fi

ADMIN_URL=$1
USERNAME=$2
PASSWORD_FILE=$3

if [ ! -f "$PASSWORD_FILE" ]; then
    echo "Error: Archivo de password no encontrado: $PASSWORD_FILE"
    exit 1
fi

# Read password
PASSWORD=$(cat $PASSWORD_FILE)

# WebLogic environment
if [ -z "$WLS_HOME" ]; then
    export WLS_HOME="/u01/oracle/middleware/wlserver"
fi

WLST_CMD="$WLS_HOME/../oracle_common/common/bin/wlst.sh"

if [ ! -f "$WLST_CMD" ]; then
    echo "Error: WLST no encontrado en: $WLST_CMD"
    echo "Configura la variable WLS_HOME correctamente"
    exit 1
fi

# Create temporary WLST script
TEMP_SCRIPT=$(mktemp /tmp/test_connection_XXXXX.py)

cat > $TEMP_SCRIPT << 'EOF'
import sys

admin_url = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

print("=" * 60)
print("Testing WebLogic Domain Connection")
print("=" * 60)
print("Admin URL: " + admin_url)
print("Username:  " + username)
print("")

try:
    print("Connecting to AdminServer...")
    connect(username, password, admin_url)
    print("[OK] Connection successful!")
    print("")
    
    # Get domain info
    domainRuntime()
    print("Domain Name: " + cmo.getName())
    print("")
    
    # Get server runtimes
    print("Servers:")
    print("-" * 60)
    servers = cmo.getServerRuntimes()
    for server in servers:
        print("  - %s: %s (Health: %s)" % (
            server.getName(), 
            server.getState(), 
            server.getHealthState().getState()
        ))
    
    print("")
    print("[OK] All checks passed!")
    disconnect()
    sys.exit(0)
    
except Exception as e:
    print("[ERROR] Connection failed!")
    print("Error: " + str(e))
    sys.exit(1)
EOF

# Execute test
echo "Ejecutando prueba de conexión..."
echo ""

$WLST_CMD $TEMP_SCRIPT "$ADMIN_URL" "$USERNAME" "$PASSWORD"
EXIT_CODE=$?

# Cleanup
rm -f $TEMP_SCRIPT

exit $EXIT_CODE
