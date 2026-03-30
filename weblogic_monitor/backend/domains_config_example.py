# domains_config.py
# Configuración de dominios WebLogic
# Copiar este archivo a backend/domains_config.py y personalizar

DOMAINS_CONFIG = [
    # Dominios de Producción - Cluster 1
    {
        "name": "ProdDomain01",
        "admin_url": "t3://wls-prod-admin01.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod01_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2", "ManagedServer3"]
    },
    {
        "name": "ProdDomain02",
        "admin_url": "t3://wls-prod-admin02.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod02_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    
    # Dominios de Producción - Cluster 2
    {
        "name": "ProdDomain03",
        "admin_url": "t3://wls-prod-admin03.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod03_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2", "ManagedServer3", "ManagedServer4"]
    },
    {
        "name": "ProdDomain04",
        "admin_url": "t3://wls-prod-admin04.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/prod04_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    
    # Dominios de QA
    {
        "name": "QADomain01",
        "admin_url": "t3://wls-qa-admin01.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/qa01_pass.txt",
        "servers": ["AdminServer", "ManagedServer1"]
    },
    {
        "name": "QADomain02",
        "admin_url": "t3://wls-qa-admin02.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/qa02_pass.txt",
        "servers": ["AdminServer", "ManagedServer1"]
    },
    
    # Dominios de Desarrollo
    {
        "name": "DevDomain01",
        "admin_url": "t3://wls-dev-admin01.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/dev01_pass.txt",
        "servers": ["AdminServer", "ManagedServer1"]
    },
    {
        "name": "DevDomain02",
        "admin_url": "t3://wls-dev-admin02.ejemplo.com:7001",
        "username": "weblogic",
        "password_file": "/secure/weblogic-monitor/dev02_pass.txt",
        "servers": ["AdminServer", "ManagedServer1"]
    },
    
    # ... Agregar los 82 dominios restantes siguiendo el mismo patrón ...
    
    # Ejemplo de configuración para diferentes puertos
    {
        "name": "SpecialDomain",
        "admin_url": "t3://wls-special.ejemplo.com:8001",  # Puerto diferente
        "username": "admin",  # Usuario diferente
        "password_file": "/secure/weblogic-monitor/special_pass.txt",
        "servers": ["AdminServer", "Server1", "Server2", "Server3", "Server4", "Server5"]
    },
]

# Helper function para generar múltiples dominios
def generate_domain_configs(prefix, start_num, end_num, base_url_template, servers_per_domain=2):
    """
    Genera configuraciones de dominios de manera programática
    
    Ejemplo:
    configs = generate_domain_configs(
        prefix="Prod",
        start_num=10,
        end_num=20,
        base_url_template="t3://wls-prod-admin{:02d}.ejemplo.com:7001",
        servers_per_domain=3
    )
    """
    configs = []
    for i in range(start_num, end_num + 1):
        config = {
            "name": f"{prefix}Domain{i:02d}",
            "admin_url": base_url_template.format(i),
            "username": "weblogic",
            "password_file": f"/secure/weblogic-monitor/{prefix.lower()}{i:02d}_pass.txt",
            "servers": ["AdminServer"] + [f"ManagedServer{j}" for j in range(1, servers_per_domain + 1)]
        }
        configs.append(config)
    return configs

# Uso del helper para generar dominios automáticamente:
# DOMAINS_CONFIG.extend(generate_domain_configs("Prod", 10, 50, "t3://wls-prod-admin{:02d}.ejemplo.com:7001", 3))
# DOMAINS_CONFIG.extend(generate_domain_configs("QA", 1, 20, "t3://wls-qa-admin{:02d}.ejemplo.com:7001", 2))
# DOMAINS_CONFIG.extend(generate_domain_configs("Dev", 1, 20, "t3://wls-dev-admin{:02d}.ejemplo.com:7001", 1))
