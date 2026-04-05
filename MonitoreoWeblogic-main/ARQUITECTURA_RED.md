# 🌐 Arquitectura de Red y Conectividad - WebLogic Monitor

## Diagrama de Red Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RED CORPORATIVA                              │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    ZONA DE USUARIOS                         │    │
│  │                                                             │    │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐               │    │
│  │    │ Usuario  │  │ Usuario  │  │ Usuario  │               │    │
│  │    │   PC 1   │  │   PC 2   │  │   PC N   │               │    │
│  │    └─────┬────┘  └─────┬────┘  └─────┬────┘               │    │
│  │          │             │             │                      │    │
│  │          └─────────────┼─────────────┘                      │    │
│  │                        │                                    │    │
│  └────────────────────────┼────────────────────────────────────┘    │
│                           │                                          │
│                           │ HTTP/HTTPS                               │
│                           │ Puerto 80/443                            │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              SERVIDOR DASHBOARD                              │   │
│  │              (Linux - RHEL/CentOS/Ubuntu)                    │   │
│  │              IP: 192.168.1.100 (ejemplo)                     │   │
│  │                                                              │   │
│  │  ┌────────────────────┐    ┌──────────────────────┐        │   │
│  │  │   Nginx            │    │   Backend FastAPI    │        │   │
│  │  │   :80 / :443       │◄───┤   :8000              │        │   │
│  │  │                    │    │                      │        │   │
│  │  │  /var/www/         │    │  /opt/weblogic-      │        │   │
│  │  │  weblogic-monitor/ │    │  monitor/            │        │   │
│  │  │                    │    │                      │        │   │
│  │  │  • index.html      │    │  • app.py            │        │   │
│  │  │  • React Dashboard │    │  • WLST Scripts      │        │   │
│  │  └────────────────────┘    │  • Cache (15s)       │        │   │
│  │                            └──────────┬───────────┘        │   │
│  │                                       │                     │   │
│  │                            ┌──────────▼───────────┐        │   │
│  │                            │  Password Files      │        │   │
│  │                            │  /secure/weblogic-   │        │   │
│  │                            │  monitor/            │        │   │
│  │                            │  • prod01_pass.txt   │        │   │
│  │                            │  • prod02_pass.txt   │        │   │
│  │                            │  • ...               │        │   │
│  │                            │  Permisos: 600       │        │   │
│  │                            └──────────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           │                                          │
│                           │ T3 Protocol                              │
│                           │ Puerto 7001                              │
│                           │ (Salida a 90 dominios)                   │
│                           │                                          │
│    ┌──────────────────────┼──────────────────────────────────┐     │
│    │                      │                                   │     │
│    ▼                      ▼                                   ▼     │
│  ┌─────────────────┐  ┌─────────────────┐    ...  ┌─────────────┐ │
│  │  DOMINIO 1      │  │  DOMINIO 2      │         │  DOMINIO 90 │ │
│  │  Producción     │  │  Producción     │         │  Desarrollo │ │
│  │                 │  │                 │         │             │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │         │ ┌─────────┐ │ │
│  │  │AdminServer│  │  │  │AdminServer│  │         │ │AdminSrv │ │ │
│  │  │  :7001    │  │  │  │  :7001    │  │         │ │ :7001   │ │ │
│  │  │  (T3)     │  │  │  │  (T3)     │  │         │ │ (T3)    │ │ │
│  │  └───────────┘  │  │  └───────────┘  │         │ └─────────┘ │ │
│  │       ▲         │  │       ▲         │         │      ▲      │ │
│  │       │         │  │       │         │         │      │      │ │
│  │  ┌────┴─────┐   │  │  ┌────┴─────┐   │         │ ┌────┴────┐ │ │
│  │  │Managed   │   │  │  │Managed   │   │         │ │Managed  │ │ │
│  │  │Server 1  │   │  │  │Server 1  │   │         │ │Server 1 │ │ │
│  │  └──────────┘   │  │  └──────────┘   │         │ └─────────┘ │ │
│  │  ┌──────────┐   │  │  ┌──────────┐   │         │             │ │
│  │  │Managed   │   │  │  │Managed   │   │         │             │ │
│  │  │Server 2  │   │  │  │Server 2  │   │         │             │ │
│  │  └──────────┘   │  │  └──────────┘   │         │             │ │
│  │                 │  │                 │         │             │ │
│  │  Host: wls-prod-│  │  Host: wls-prod-│         │ Host: wls-  │ │
│  │  admin01.ej.com │  │  admin02.ej.com │         │ dev01.ej.com│ │
│  │  IP: 10.1.1.10  │  │  IP: 10.1.1.11  │         │ IP:10.3.1.1 │ │
│  └─────────────────┘  └─────────────────┘         └─────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Tabla de Conectividad Detallada

### Conexiones de Usuarios → Dashboard

| Origen | Destino | Puerto | Protocolo | Dirección | Observaciones |
|--------|---------|--------|-----------|-----------|---------------|
| Navegador Usuario | Servidor Dashboard | 80 | HTTP | Entrada | Tráfico web no encriptado |
| Navegador Usuario | Servidor Dashboard | 443 | HTTPS | Entrada | Tráfico web encriptado (recomendado) |

**Configuración de Firewall (Dashboard Server):**
```bash
# Permitir entrada HTTP/HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# O con iptables:
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### Conexiones Dashboard → Dominios WebLogic

| Origen | Destino | Puerto | Protocolo | Dirección | Observaciones |
|--------|---------|--------|-----------|-----------|---------------|
| Backend (FastAPI) | AdminServer Dominio 1 | 7001 | T3 | Salida | Consulta de métricas |
| Backend (FastAPI) | AdminServer Dominio 2 | 7001 | T3 | Salida | Consulta de métricas |
| Backend (FastAPI) | AdminServer Dominio 3 | 7001 | T3 | Salida | Consulta de métricas |
| ... | ... | ... | ... | ... | ... |
| Backend (FastAPI) | AdminServer Dominio 90 | 7001 | T3 | Salida | Consulta de métricas |

**Notas:**
- El puerto puede ser diferente (7001, 7002, 8001, etc.)
- Si usas SSL: puerto 7002 con protocolo T3S
- Frecuencia: Cada 15 segundos (configurable)

**Configuración de Firewall (Dashboard Server - Salida):**
```bash
# Permitir salida a puerto 7001
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port protocol="tcp" port="7001" accept'
sudo firewall-cmd --reload

# O con iptables:
sudo iptables -A OUTPUT -p tcp --dport 7001 -j ACCEPT
```

**Configuración de Firewall (Servidores WebLogic - Entrada):**
```bash
# En cada servidor WebLogic, permitir desde IP del Dashboard
# Reemplazar 192.168.1.100 con la IP real del servidor Dashboard

sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.100" port protocol="tcp" port="7001" accept'
sudo firewall-cmd --reload

# O con iptables:
sudo iptables -A INPUT -s 192.168.1.100 -p tcp --dport 7001 -j ACCEPT
```

---

## 🔐 Seguridad de Red

### Zona de Seguridad Recomendada

```
┌───────────────────────────────────────────────┐
│  DMZ (Zona Desmilitarizada)                   │
│  ┌─────────────────────────────────────┐     │
│  │  Servidor Dashboard (Nginx)          │     │
│  │  - Solo puerto 80/443 expuesto       │     │
│  │  - Firewall estricto                 │     │
│  └─────────────────────────────────────┘     │
└───────────────────────────────────────────────┘
                    │
         ┌──────────┼──────────┐
         │                     │
┌────────▼──────────┐  ┌───────▼─────────┐
│  Zona Interna      │  │  Zona Interna   │
│  (Producción)      │  │  (Dev/QA)       │
│  - Dominios 1-60   │  │  - Dominios     │
│  - Solo acceso     │  │    61-90        │
│    desde Dashboard │  │                 │
└────────────────────┘  └─────────────────┘
```

### Mejores Prácticas de Seguridad

1. **Usar HTTPS** para acceso al dashboard
2. **Credenciales en archivos seguros** (permisos 600)
3. **Firewall restrictivo** (solo IPs necesarias)
4. **Monitoreo de logs** para detectar accesos no autorizados
5. **Rotación de contraseñas** periódica
6. **VPN** si el dashboard se accede remotamente

---

## 📊 Ancho de Banda y Performance

### Consumo de Red Esperado

**Por Dominio:**
- Request WLST: ~5-10 KB
- Response con métricas: ~20-50 KB
- Total por consulta: ~30-60 KB

**Para 90 Dominios:**
- Primera consulta (sin cache): ~2.7-5.4 MB
- Consultas subsecuentes (con cache): ~0 MB (no hay tráfico de red)
- Cada 15 segundos: Consulta a ~6 dominios (rotación de cache)

**Tráfico Total Estimado:**
- Por hora: ~60-120 MB
- Por día: ~1.5-3 GB

### Latencia Esperada

| Escenario | Tiempo |
|-----------|--------|
| Cache HIT | <50 ms |
| Cache MISS (1 dominio) | 1-3 segundos |
| Consulta completa (90 dominios, primera vez) | 30-45 segundos |
| Consulta completa (con cache parcial) | 5-10 segundos |

---

## 🌍 Escenarios de Despliegue

### Escenario 1: Todos en la Misma Red

```
Servidor Dashboard: 192.168.1.100
Dominios WebLogic:  192.168.1.10-192.168.1.99

Ventaja: Latencia mínima
Complejidad: Baja
```

**Configuración:**
```python
# En app.py
DOMAINS_CONFIG = [
    {"name": "Dom1", "admin_url": "t3://192.168.1.10:7001", ...},
    {"name": "Dom2", "admin_url": "t3://192.168.1.11:7001", ...},
]
```

### Escenario 2: Múltiples Redes/Datacenters

```
Servidor Dashboard: 192.168.1.100 (Datacenter 1)
Dominios DC1:       192.168.1.10-50
Dominios DC2:       10.20.30.10-50

Ventaja: Monitoreo centralizado
Complejidad: Media (requiere VPN/túneles)
```

**Configuración:**
```python
DOMAINS_CONFIG = [
    # Datacenter 1
    {"name": "DC1-Dom1", "admin_url": "t3://192.168.1.10:7001", ...},
    
    # Datacenter 2 (a través de VPN)
    {"name": "DC2-Dom1", "admin_url": "t3://10.20.30.10:7001", ...},
]
```

### Escenario 3: Segmentación por Ambiente

```
Dashboard en DMZ:    172.16.1.100
Producción:          10.1.x.x
QA:                  10.2.x.x  
Desarrollo:          10.3.x.x

Ventaja: Separación de ambientes
Complejidad: Alta (múltiples reglas de firewall)
```

---

## 🧪 Scripts de Verificación de Conectividad

### Script 1: Verificar Todos los Puertos

```bash
#!/bin/bash
# verify_connectivity.sh

DASHBOARD_IP="192.168.1.100"

echo "Verificando conectividad a 90 dominios..."

# Lista de AdminServers (personalizar)
DOMAINS=(
    "wls-prod-admin01.ejemplo.com:7001"
    "wls-prod-admin02.ejemplo.com:7001"
    # ... agregar los 90
)

for domain in "${DOMAINS[@]}"; do
    host="${domain%:*}"
    port="${domain#*:}"
    
    echo -n "Testing $domain... "
    
    if timeout 5 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
        echo "✓ OK"
    else
        echo "✗ FAILED"
    fi
done
```

### Script 2: Verificar WLST

```bash
#!/bin/bash
# verify_wlst.sh

WLST="/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"

echo "Verificando WLST..."

if [ ! -f "$WLST" ]; then
    echo "✗ WLST no encontrado en: $WLST"
    exit 1
fi

echo "✓ WLST encontrado"

# Test básico
echo "Testing WLST execution..."
$WLST -skipWLSModuleScanning <<EOF
print("✓ WLST funciona correctamente")
exit()
EOF
```

### Script 3: Test Masivo de Conexiones

```bash
#!/bin/bash
# mass_connection_test.sh

CONFIG_FILE="/opt/weblogic-monitor/backend/test_config.txt"

# Formato del archivo: admin_url,username,password_file
# Ejemplo:
# t3://wls-prod01.ejemplo.com:7001,weblogic,/secure/prod01_pass.txt

while IFS=',' read -r url username passfile; do
    echo "Testing: $url"
    
    /opt/weblogic-monitor/scripts/test_domain_connection.sh \
        "$url" "$username" "$passfile"
    
    if [ $? -eq 0 ]; then
        echo "✓ $url OK"
    else
        echo "✗ $url FAILED"
    fi
    echo "---"
done < "$CONFIG_FILE"
```

---

## 📋 Checklist de Conectividad Pre-Instalación

```
☐ 1. Servidor Dashboard tiene IP estática
☐ 2. DNS resuelve nombres de todos los AdminServers
☐ 3. Ping exitoso a todos los AdminServers
☐ 4. Telnet/nc exitoso al puerto 7001 de todos los AdminServers
☐ 5. WLST instalado y accesible
☐ 6. Conexión WLST manual funciona a al menos 1 dominio
☐ 7. Firewall del Dashboard permite salida a puerto 7001
☐ 8. Firewalls de WebLogic permiten entrada desde Dashboard
☐ 9. Usuario tiene permisos de administrador en WebLogic
☐ 10. No hay proxies/NAT bloqueando T3
```

---

## 🔧 Comandos de Diagnóstico de Red

```bash
# Verificar resolución DNS
nslookup wls-prod-admin01.ejemplo.com

# Verificar ruta de red
traceroute wls-prod-admin01.ejemplo.com

# Verificar puerto abierto
nc -zv wls-prod-admin01.ejemplo.com 7001
# O
telnet wls-prod-admin01.ejemplo.com 7001

# Ver conexiones activas
netstat -an | grep 7001

# Ver reglas de firewall
sudo iptables -L -n -v
# O
sudo firewall-cmd --list-all

# Capturar tráfico (debugging)
sudo tcpdump -i any -n port 7001

# Ver latencia
ping -c 10 wls-prod-admin01.ejemplo.com
```

---

## 🚨 Problemas Comunes de Conectividad

### Problema: "No route to host"

**Causa:** Firewall bloqueando  
**Solución:** Configurar firewall en servidor Dashboard y WebLogic

### Problema: "Connection timeout"

**Causa:** AdminServer no escuchando en puerto o firewall intermedio  
**Solución:** Verificar AdminServer corriendo y firewall de red

### Problema: "Connection refused"

**Causa:** Servicio no corriendo en el puerto  
**Solución:** Verificar que AdminServer esté UP

### Problema: "Name resolution failed"

**Causa:** DNS no configurado  
**Solución:** Agregar entradas a /etc/hosts o configurar DNS

---

## 📞 Información de Contacto para Firewall

Al solicitar apertura de puertos a tu equipo de redes, proporciona:

```
SOLICITUD DE APERTURA DE PUERTOS

Origen:    [IP Servidor Dashboard]
Destino:   [IPs de AdminServers - lista completa]
Puerto:    7001 (TCP)
Protocolo: T3 (WebLogic)
Propósito: Monitoreo de métricas WebLogic
Aplicación: WebLogic Monitor Dashboard
Horario:   24/7
Contacto:  [Tu nombre y email]
Ticket:    [Número de ticket]
```

---

¡Con esta guía tienes toda la información necesaria sobre conectividad! 🎉
