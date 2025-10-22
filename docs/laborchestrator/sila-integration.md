# SiLA Integration

This guide explains how to use Lab Orchestrator's SiLA 2 server interface to integrate with laboratory automation systems.

## Overview

Lab Orchestrator implements the [SiLA 2](https://sila-standard.com/) (Standardization in Lab Automation) protocol, providing a standardized interface for controlling laboratory workflows. The SiLA server allows external systems to:

- Add and manage processes
- Start and stop workflow execution
- Monitor process status
- Pause and resume operations
- Run simulations

## Starting the SiLA Server

### Basic Usage

Start the server in insecure mode (no SSL) for development:

```bash
python -m laborchestrator.sila_server --insecure
```

This starts the server on `127.0.0.1:50052`.

### Production Usage

Start with SSL encryption for production:

```bash
python -m laborchestrator.sila_server \
    -c /path/to/server-cert.pem \
    -k /path/to/server-key.pem \
    -a 0.0.0.0 \
    -p 50052
```

### Command-Line Options

```bash
python -m laborchestrator.sila_server [OPTIONS]
```

**Available options**:

- `-a, --ip-address TEXT` - Server IP address (default: 127.0.0.1)
- `-p, --port INTEGER` - Server port (default: 50052)
- `--server-uuid TEXT` - Custom server UUID
- `--disable-discovery` - Disable SiLA discovery service
- `--insecure` - Start without SSL encryption (development only)
- `-k, --private-key-file PATH` - Path to SSL private key file
- `-c, --cert-file PATH` - Path to SSL certificate file
- `--verbose` - Enable verbose logging
- `--debug` - Enable debug logging
- `--quiet` - Suppress non-error messages

### Docker Deployment

Using docker-compose:

```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    ports:
      - "50052:50052"  # SiLA server
      - "8050:8050"    # Dash UI
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./lab_config.yml:/app/lab_config.yml
      - ./certs:/app/certs
    command: >
      python -m laborchestrator.sila_server
      -c /app/certs/server-cert.pem
      -k /app/certs/server-key.pem
      -a 0.0.0.0
      -p 50052
```

Start with:
```bash
docker-compose up --build
```

## SiLA Server Features

Lab Orchestrator implements four main SiLA features:

### 1. LabOrchestratorService

Main service for orchestrator control.

**Commands**:
- `AddProcess` - Add a new process to the orchestrator
- `StartProcesses` - Start execution of processes
- `GetProcessStatus` - Get status of running processes
- `ConfigureLab` - Load lab configuration
- `SetParameter` - Set orchestrator parameters

**Properties**:
- `AvailableDevices` - List of configured devices
- `RunningProcesses` - Currently executing processes
- `ServerStatus` - Orchestrator state

### 2. PauseController

Pause and resume workflow execution.

**Commands**:
- `Pause` - Pause all running processes
- `Resume` - Resume paused processes
- `PauseProcess` - Pause a specific process
- `ResumeProcess` - Resume a specific process

**Properties**:
- `IsPaused` - Current pause state

### 3. CancelController

Cancel running processes.

**Commands**:
- `Cancel` - Cancel all processes
- `CancelProcess` - Cancel a specific process

**Properties**:
- `CancellableProcesses` - List of processes that can be cancelled

### 4. SimulationController

Run workflow simulations without physical execution.

**Commands**:
- `StartSimulation` - Start simulation mode
- `StopSimulation` - Stop simulation mode
- `SimulateProcess` - Simulate a specific process

**Properties**:
- `IsSimulating` - Current simulation state
- `SimulationSpeed` - Simulation time multiplier

## Using the SiLA Client

### Python SiLA Client Example

```python
from sila2.client import SilaClient

# Connect to server
client = SilaClient(
    server_ip="127.0.0.1",
    server_port=50052,
    insecure=True  # For development only
)

# Add a process
process_code = """
from pythonlab.process import PLProcess
# ... process definition
"""

client.LabOrchestratorService.AddProcess(
    ProcessDescription=process_code,
    ProcessName="MyProcess"
)

# Configure lab
with open("lab_config.yml", "r") as f:
    lab_config = f.read()

client.LabOrchestratorService.ConfigureLab(
    ConfigurationYAML=lab_config
)

# Start processes
client.LabOrchestratorService.StartProcesses(
    ProcessNames=["MyProcess"]
)

# Monitor status
status = client.LabOrchestratorService.GetProcessStatus(
    ProcessName="MyProcess"
)
print(f"Status: {status.State}")

# Pause execution
client.PauseController.Pause()

# Resume execution
client.PauseController.Resume()

# Cancel process
client.CancelController.CancelProcess(
    ProcessName="MyProcess"
)
```

### With SSL

```python
from sila2.client import SilaClient

client = SilaClient(
    server_ip="orchestrator.lab.example.com",
    server_port=50052,
    insecure=False,
    server_cert="/path/to/server-cert.pem"
)
```

## Server Configuration

### Server Metadata

The server is configured with the following metadata:

```python
server_name = "Orchestrator"
server_type = "PythonLabOrchestratorServer"
server_version = "0.1"
server_description = "Use this to control a running pythonlaborchestrator"
server_vendor_url = "https://gitlab.com/SiLA2/sila_python"
```

### Custom Server UUID

Provide a custom UUID for the server:

```bash
python -m laborchestrator.sila_server --server-uuid "123e4567-e89b-12d3-a456-426614174000"
```

Or in Python:

```python
from uuid import UUID
from laborchestrator.sila_server.server import Server
from laborchestrator.orchestrator_implementation import Orchestrator

orchestrator = Orchestrator()
server = Server(
    orchestrator=orchestrator,
    server_uuid=UUID("123e4567-e89b-12d3-a456-426614174000")
)
```

### Discovery Service

By default, the SiLA server announces itself via mDNS for automatic discovery. To disable:

```bash
python -m laborchestrator.sila_server --disable-discovery --insecure
```

## Integration Examples

### Example 1: Remote Process Submission

```python
from sila2.client import SilaClient

def submit_process(process_file_path, process_name):
    """Submit a process to the orchestrator"""
    # Connect to orchestrator
    client = SilaClient("127.0.0.1", 50052, insecure=True)

    # Read process file
    with open(process_file_path, "r") as f:
        process_code = f.read()

    # Add process
    client.LabOrchestratorService.AddProcess(
        ProcessDescription=process_code,
        ProcessName=process_name
    )

    # Start process
    client.LabOrchestratorService.StartProcesses(
        ProcessNames=[process_name]
    )

    print(f"Process '{process_name}' submitted and started")

# Usage
submit_process("my_workflow.py", "ExperimentA")
```

### Example 2: Process Monitoring

```python
from sila2.client import SilaClient
import time

def monitor_process(process_name, poll_interval=5):
    """Monitor a process until completion"""
    client = SilaClient("127.0.0.1", 50052, insecure=True)

    while True:
        status = client.LabOrchestratorService.GetProcessStatus(
            ProcessName=process_name
        )

        print(f"Process: {process_name}")
        print(f"State: {status.State}")
        print(f"Progress: {status.Progress}%")
        print(f"Current Step: {status.CurrentStep}")
        print("---")

        if status.State in ["COMPLETED", "FAILED", "CANCELLED"]:
            break

        time.sleep(poll_interval)

    print(f"Process finished with state: {status.State}")

# Usage
monitor_process("ExperimentA", poll_interval=10)
```

### Example 3: Batch Process Submission

```python
from sila2.client import SilaClient

def submit_batch(process_files, lab_config_path):
    """Submit multiple processes as a batch"""
    client = SilaClient("127.0.0.1", 50052, insecure=True)

    # Configure lab
    with open(lab_config_path, "r") as f:
        lab_config = f.read()
    client.LabOrchestratorService.ConfigureLab(
        ConfigurationYAML=lab_config
    )

    # Add all processes
    process_names = []
    for i, process_file in enumerate(process_files):
        process_name = f"BatchProcess_{i}"
        with open(process_file, "r") as f:
            process_code = f.read()

        client.LabOrchestratorService.AddProcess(
            ProcessDescription=process_code,
            ProcessName=process_name
        )
        process_names.append(process_name)

    # Start all processes
    client.LabOrchestratorService.StartProcesses(
        ProcessNames=process_names
    )

    print(f"Started {len(process_names)} processes")

# Usage
submit_batch(
    ["workflow1.py", "workflow2.py", "workflow3.py"],
    "lab_config.yml"
)
```

### Example 4: Emergency Stop

```python
from sila2.client import SilaClient

def emergency_stop():
    """Stop all running processes immediately"""
    client = SilaClient("127.0.0.1", 50052, insecure=True)

    # Pause first (stops scheduling new steps)
    client.PauseController.Pause()
    print("Paused all processes")

    # Cancel all processes
    client.CancelController.Cancel()
    print("Cancelled all processes")

# Usage
emergency_stop()
```

### Example 5: Simulation Mode

```python
from sila2.client import SilaClient

def run_simulation(process_file, lab_config):
    """Run a process in simulation mode"""
    client = SilaClient("127.0.0.1", 50052, insecure=True)

    # Configure lab
    with open(lab_config, "r") as f:
        config = f.read()
    client.LabOrchestratorService.ConfigureLab(
        ConfigurationYAML=config
    )

    # Start simulation mode
    client.SimulationController.StartSimulation(
        SimulationSpeed=10.0  # 10x real-time speed
    )

    # Add and start process
    with open(process_file, "r") as f:
        process_code = f.read()
    client.LabOrchestratorService.AddProcess(
        ProcessDescription=process_code,
        ProcessName="SimProcess"
    )
    client.LabOrchestratorService.StartProcesses(
        ProcessNames=["SimProcess"]
    )

    # Monitor simulation
    # ... (same as Example 2)

    # Stop simulation
    client.SimulationController.StopSimulation()

# Usage
run_simulation("workflow.py", "lab_config.yml")
```

## SSL Certificate Generation

For production deployments, generate SSL certificates:

### Using OpenSSL

```bash
# Generate private key
openssl genrsa -out server-key.pem 2048

# Generate certificate signing request
openssl req -new -key server-key.pem -out server.csr

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in server.csr -signkey server-key.pem -out server-cert.pem

# Clean up CSR
rm server.csr
```

### Using Let's Encrypt

For publicly accessible servers:

```bash
certbot certonly --standalone -d orchestrator.lab.example.com
```

Then use the generated certificates:
```bash
python -m laborchestrator.sila_server \
    -c /etc/letsencrypt/live/orchestrator.lab.example.com/fullchain.pem \
    -k /etc/letsencrypt/live/orchestrator.lab.example.com/privkey.pem \
    -a 0.0.0.0 \
    -p 50052
```

## Logging

### Enable Verbose Logging

```bash
python -m laborchestrator.sila_server --verbose --insecure
```

### Enable Debug Logging

```bash
python -m laborchestrator.sila_server --debug --insecure
```

### Log to File

```bash
python -m laborchestrator.sila_server --insecure 2>&1 | tee orchestrator.log
```

## Firewall Configuration

Open port 50052 for SiLA communication:

### Linux (UFW)
```bash
sudo ufw allow 50052/tcp
```

### Linux (iptables)
```bash
sudo iptables -A INPUT -p tcp --dport 50052 -j ACCEPT
```

### Docker
Ensure port mapping in docker-compose.yml:
```yaml
ports:
  - "50052:50052"
```

## Network Discovery

The SiLA server supports automatic discovery via mDNS (multicast DNS). Clients can discover the server without knowing its IP address.

### Client Discovery Example

```python
from sila2.discovery import discover_servers

# Discover all SiLA servers on the network
servers = discover_servers(timeout=5)

for server in servers:
    if server.server_type == "PythonLabOrchestratorServer":
        print(f"Found orchestrator at {server.ip}:{server.port}")
        client = SilaClient(server.ip, server.port, insecure=True)
        break
```

## Troubleshooting

### Common Issues

**Problem**: `Connection refused` when connecting to server

**Solution**: Check that:
- Server is running
- Correct IP and port
- Firewall allows connections
- Using `--insecure` flag for development

**Problem**: SSL certificate errors

**Solution**:
- Verify certificate paths are correct
- Check certificate validity: `openssl x509 -in server-cert.pem -text`
- Ensure client has access to certificate

**Problem**: Server UUID conflicts

**Solution**: Use `--server-uuid` to set a unique identifier

**Problem**: Discovery not working

**Solution**:
- Check that discovery is not disabled (`--disable-discovery`)
- Verify mDNS is working on your network
- Try specifying IP address directly instead of discovery

## Best Practices

1. **Use SSL in Production**: Always use SSL encryption for production deployments
2. **Firewall Configuration**: Restrict access to known client IPs
3. **Logging**: Enable appropriate logging levels for debugging
4. **Monitoring**: Implement health checks and monitoring
5. **Error Handling**: Handle connection errors and timeouts gracefully
6. **Version Management**: Keep SiLA client and server versions synchronized

## See Also

- [Configuration](configuration.md) - Configure lab resources
- [Writing Processes](writing-processes.md) - Create workflows
- [API Reference](api-reference.md) - Detailed API documentation
- [Deployment](deployment.md) - Production deployment guide
- [SiLA 2 Standard](https://sila-standard.com/) - Official SiLA documentation
