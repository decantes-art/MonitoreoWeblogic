"""
WebLogic Monitoring Dashboard - Backend API
FastAPI server that collects metrics from WebLogic domains using WLST
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
import subprocess
import json
import time
from pathlib import Path

app = FastAPI(title="WebLogic Monitor API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache configuration
CACHE_TTL = 15  # seconds
metrics_cache = {}

# WebLogic domains configuration
DOMAINS_CONFIG = [
    # Example configuration - replace with your actual domains
    {
        "name": "ProductionDomain1",
        "admin_url": "t3://prod-admin1.example.com:7001",
        "username": "weblogic",
        "password_file": "/secure/prod1_pass.txt",
        "servers": ["AdminServer", "ManagedServer1", "ManagedServer2"]
    },
    # Add your 90 domains here
]

class ServerMetrics(BaseModel):
    name: str
    state: str
    health_state: str
    uptime: int
    thread_pool: Dict[str, int]
    jvm: Dict[str, Any]
    timestamp: datetime

class ApplicationMetrics(BaseModel):
    name: str
    state: str
    open_sessions: int
    avg_response_time: Optional[float]

class DatasourceMetrics(BaseModel):
    name: str
    active_connections: int
    available_connections: int
    waiters: int
    capacity: int
    failures: int

class JMSMetrics(BaseModel):
    destination: str
    current_messages: int
    pending_messages: int
    delayed_messages: int
    consumers: int

class DomainStatus(BaseModel):
    name: str
    admin_url: str
    last_update: datetime
    servers: List[ServerMetrics]
    applications: List[ApplicationMetrics]
    datasources: List[DatasourceMetrics]
    jms_destinations: List[JMSMetrics]
    overall_health: str


def create_wlst_script(domain_config: dict) -> str:
    """Generate WLST Jython script for metrics collection"""
    script = f"""
import sys
import json
from datetime import datetime

# Connection parameters
admin_url = '{domain_config["admin_url"]}'
username = '{domain_config["username"]}'
password_file = '{domain_config["password_file"]}'

# Read password
with open(password_file, 'r') as f:
    password = f.read().strip()

metrics = {{
    'domain': '{domain_config["name"]}',
    'timestamp': str(datetime.now()),
    'servers': [],
    'applications': [],
    'datasources': [],
    'jms_destinations': []
}}

try:
    # Connect to AdminServer
    connect(username, password, admin_url)
    
    # Get ServerRuntime for each server
    domainRuntime()
    
    servers = cmo.getServerRuntimes()
    for server in servers:
        server_metrics = {{
            'name': server.getName(),
            'state': server.getState(),
            'health_state': server.getHealthState().getState(),
            'uptime': server.getUptime() if server.getUptime() else 0,
            'thread_pool': {{}},
            'jvm': {{}}
        }}
        
        # Thread Pool metrics
        try:
            cd('/ServerRuntimes/' + server.getName() + '/ThreadPoolRuntime/ThreadPoolRuntime')
            server_metrics['thread_pool'] = {{
                'total_threads': get('ExecuteThreadTotalCount'),
                'idle_threads': get('ExecuteThreadIdleCount'),
                'stuck_threads': get('StuckThreadCount'),
                'hogging_threads': get('HoggingThreadCount'),
                'pending_requests': get('PendingUserRequestCount')
            }}
        except Exception as e:
            print('Error getting thread pool: ' + str(e))
        
        # JVM metrics
        try:
            cd('/ServerRuntimes/' + server.getName() + '/JVMRuntime/' + server.getName())
            server_metrics['jvm'] = {{
                'heap_used': get('HeapSizeCurrent'),
                'heap_max': get('HeapSizeMax'),
                'heap_free': get('HeapFreeCurrent'),
                'heap_percent': get('HeapFreePercent'),
                'total_threads': get('ThreadsCount') if hasattr(cmo, 'ThreadsCount') else 0
            }}
        except Exception as e:
            print('Error getting JVM metrics: ' + str(e))
        
        metrics['servers'].append(server_metrics)
    
    # Application metrics
    cd('/AppRuntimeStateRuntime/AppRuntimeStateRuntime')
    app_runtimes = cmo.getApplicationRuntimes()
    for app in app_runtimes:
        app_name = app.getName()
        app_metrics = {{
            'name': app_name,
            'state': app.getState(),
            'open_sessions': 0,
            'avg_response_time': None
        }}
        
        # Get web app component runtimes
        try:
            components = app.getComponentRuntimes()
            for comp in components:
                if comp.getType() == 'WebAppComponentRuntime':
                    app_metrics['open_sessions'] += comp.getOpenSessionsCurrentCount()
                    
                    # Try to get servlet stats
                    servlets = comp.getServlets()
                    if servlets and len(servlets) > 0:
                        total_time = 0
                        count = 0
                        for servlet in servlets:
                            exec_time = servlet.getExecutionTimeAverage()
                            if exec_time > 0:
                                total_time += exec_time
                                count += 1
                        if count > 0:
                            app_metrics['avg_response_time'] = total_time / count
        except Exception as e:
            print('Error getting app component metrics: ' + str(e))
        
        metrics['applications'].append(app_metrics)
    
    # JDBC Datasource metrics
    cd('/JDBCServiceRuntime/' + servers[0].getName())
    datasources = cmo.getJDBCDataSourceRuntimeMBeans()
    for ds in datasources:
        ds_metrics = {{
            'name': ds.getName(),
            'active_connections': ds.getActiveConnectionsCurrentCount(),
            'available_connections': ds.getActiveConnectionsCurrentCount(),
            'waiters': ds.getWaitingForConnectionCurrentCount(),
            'capacity': ds.getCurrCapacity(),
            'failures': ds.getFailuresToReconnectCount()
        }}
        metrics['datasources'].append(ds_metrics)
    
    # JMS Destination metrics
    try:
        cd('/JMSRuntime/' + servers[0].getName())
        jms_servers = cmo.getJMSServers()
        for jms_server in jms_servers:
            destinations = jms_server.getDestinations()
            for dest in destinations:
                dest_metrics = {{
                    'destination': dest.getName(),
                    'current_messages': dest.getMessagesCurrentCount(),
                    'pending_messages': dest.getMessagesPendingCount(),
                    'delayed_messages': dest.getMessagesDelayedCount() if hasattr(dest, 'getMessagesDelayedCount') else 0,
                    'consumers': dest.getConsumersCurrentCount()
                }}
                metrics['jms_destinations'].append(dest_metrics)
    except Exception as e:
        print('Error getting JMS metrics: ' + str(e))
    
    # Disconnect
    disconnect()
    
    # Output JSON
    print('METRICS_JSON_START')
    print(json.dumps(metrics))
    print('METRICS_JSON_END')
    
except Exception as e:
    print('ERROR: ' + str(e))
    sys.exit(1)
"""
    return script


async def collect_domain_metrics(domain_config: dict) -> Optional[DomainStatus]:
    """Execute WLST script and parse results"""
    cache_key = domain_config['name']
    
    # Check cache
    if cache_key in metrics_cache:
        cached_data, cached_time = metrics_cache[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            return cached_data
    
    # Generate WLST script
    script = create_wlst_script(domain_config)
    script_path = f"/tmp/wlst_collect_{domain_config['name']}.py"
    
    with open(script_path, 'w') as f:
        f.write(script)
    
    # Execute WLST
    try:
        # Adjust path to your WebLogic installation
        wlst_cmd = "/u01/oracle/middleware/oracle_common/common/bin/wlst.sh"
        
        process = await asyncio.create_subprocess_exec(
            wlst_cmd, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
        
        # Parse JSON output
        output = stdout.decode()
        if 'METRICS_JSON_START' in output:
            json_start = output.index('METRICS_JSON_START') + len('METRICS_JSON_START')
            json_end = output.index('METRICS_JSON_END')
            json_str = output[json_start:json_end].strip()
            
            data = json.loads(json_str)
            
            # Convert to DomainStatus
            domain_status = DomainStatus(
                name=data['domain'],
                admin_url=domain_config['admin_url'],
                last_update=datetime.fromisoformat(data['timestamp']),
                servers=[ServerMetrics(**s) for s in data['servers']],
                applications=[ApplicationMetrics(**a) for a in data['applications']],
                datasources=[DatasourceMetrics(**d) for d in data['datasources']],
                jms_destinations=[JMSMetrics(**j) for j in data['jms_destinations']],
                overall_health='HEALTHY'  # Calculate based on metrics
            )
            
            # Calculate overall health
            health_states = [s.health_state for s in domain_status.servers]
            if any('CRITICAL' in h for h in health_states):
                domain_status.overall_health = 'CRITICAL'
            elif any('WARNING' in h for h in health_states):
                domain_status.overall_health = 'WARNING'
            
            # Cache result
            metrics_cache[cache_key] = (domain_status, time.time())
            
            return domain_status
            
    except asyncio.TimeoutError:
        print(f"Timeout collecting metrics for {domain_config['name']}")
        return None
    except Exception as e:
        print(f"Error collecting metrics for {domain_config['name']}: {e}")
        return None


@app.get("/")
async def root():
    return {"message": "WebLogic Monitoring API", "version": "1.0.0"}


@app.get("/api/domains", response_model=List[Dict[str, Any]])
async def get_domains():
    """Get list of all domains with basic status"""
    domains = []
    for config in DOMAINS_CONFIG:
        domains.append({
            "name": config['name'],
            "admin_url": config['admin_url'],
            "server_count": len(config['servers'])
        })
    return domains


@app.get("/api/domain/{domain_name}/metrics", response_model=DomainStatus)
async def get_domain_metrics(domain_name: str):
    """Get detailed metrics for a specific domain"""
    domain_config = next((d for d in DOMAINS_CONFIG if d['name'] == domain_name), None)
    
    if not domain_config:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    metrics = await collect_domain_metrics(domain_config)
    
    if not metrics:
        raise HTTPException(status_code=500, detail="Failed to collect metrics")
    
    return metrics


@app.get("/api/metrics/all")
async def get_all_metrics():
    """Get metrics for all domains (parallel collection)"""
    tasks = [collect_domain_metrics(config) for config in DOMAINS_CONFIG]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, DomainStatus):
            valid_results.append(result)
        else:
            print(f"Failed to collect metrics for {DOMAINS_CONFIG[i]['name']}: {result}")
    
    return {
        "total_domains": len(DOMAINS_CONFIG),
        "successful": len(valid_results),
        "failed": len(DOMAINS_CONFIG) - len(valid_results),
        "domains": valid_results
    }


@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "cache_size": len(metrics_cache)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
