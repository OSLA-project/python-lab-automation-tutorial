# Deployment

This guide covers deploying Lab Orchestrator in production environments.

## Deployment Options

Lab Orchestrator supports multiple deployment methods:

1. **Docker** (Recommended) - Containerized deployment
2. **Direct Python** - Running directly with Python


## Docker Deployment

### Using Docker Compose (Recommended)

The easiest production deployment method.

#### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    container_name: lab_orchestrator
    restart: unless-stopped
    ports:
      - "50052:50052"  # SiLA server
      - "8050:8050"    # Dash web UI
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./lab_config.yml:/app/lab_config.yml:ro
      - ./processes:/app/processes:ro
      - ./logs:/app/logs
      - ./certs:/app/certs:ro
    command: >
      python -m laborchestrator.sila_server
      -c /app/certs/server-cert.pem
      -k /app/certs/server-key.pem
      -a 0.0.0.0
      -p 50052
    networks:
      - lab_network

networks:
  lab_network:
    driver: bridge
```

#### 2. Start the Service

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### Manual Docker Build

#### Build Image

```bash
# Default Python 3.9
docker build -t laborchestrator:latest .

# Specific Python version
docker build --build-arg PYTHON_VERSION=3.10 -t laborchestrator:3.10 .
```

#### Run Container

```bash
# Basic run
docker run -d \
  --name lab_orchestrator \
  -p 50052:50052 \
  -p 8050:8050 \
  -v $(pwd)/lab_config.yml:/app/lab_config.yml:ro \
  -v $(pwd)/logs:/app/logs \
  laborchestrator:latest

# With SSL
docker run -d \
  --name lab_orchestrator \
  -p 50052:50052 \
  -p 8050:8050 \
  -v $(pwd)/lab_config.yml:/app/lab_config.yml:ro \
  -v $(pwd)/certs:/app/certs:ro \
  -v $(pwd)/logs:/app/logs \
  laborchestrator:latest \
  python -m laborchestrator.sila_server \
    -c /app/certs/server-cert.pem \
    -k /app/certs/server-key.pem \
    -a 0.0.0.0 \
    -p 50052
```

### Docker Invoke Tasks

Use the invoke tasks for Docker operations:

```bash
# Run tests in Docker
invoke docker-test

# Build Docker image
invoke docker-build

# Build with specific Python version
invoke docker-build --python-version=3.10
```

## Direct Python Deployment

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install laborchestrator --index-url https://gitlab.com/api/v4/projects/39006834/packages/pypi/simple

# Or for development
pip install -e .[dev]
```

### Running

```bash
# Start SiLA server
python -m laborchestrator.sila_server \
  -c /path/to/server-cert.pem \
  -k /path/to/server-key.pem \
  -a 0.0.0.0 \
  -p 50052

# Or with screen for background execution
screen -dmS orchestrator python -m laborchestrator.sila_server --insecure
```
## Environment Variables

### Supported Variables

```bash
# Python runtime
PYTHONUNBUFFERED=1

# SiLA server
SILA_SERVER_IP=0.0.0.0
SILA_SERVER_PORT=50052
SILA_SERVER_UUID=<uuid>

# Lab configuration
LAB_CONFIG_PATH=/app/lab_config.yml

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/orchestrator.log

# Database
DB_CONNECTION_STRING=<database-url>
```

### Using .env Files

Create `.env` file:

```bash
PYTHONUNBUFFERED=1
SILA_SERVER_IP=0.0.0.0
SILA_SERVER_PORT=50052
LAB_CONFIG_PATH=/app/lab_config.yml
LOG_LEVEL=DEBUG
```

Load in docker-compose.yml:

```yaml
services:
  orchestrator:
    env_file:
      - .env
```

## Security Considerations

### SSL/TLS Configuration

Always use SSL in production:

```bash
# Generate certificates (if not using CA)
openssl genrsa -out server-key.pem 2048
openssl req -new -key server-key.pem -out server.csr
openssl x509 -req -days 365 -in server.csr -signkey server-key.pem -out server-cert.pem
```

### Firewall Configuration

```bash
# Allow SiLA port
sudo ufw allow 50052/tcp

# Allow web UI (optional)
sudo ufw allow 8050/tcp

# Restrict to specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 50052
```

### User Permissions

Run with non-root user:

```dockerfile
# In Dockerfile
RUN useradd -m -u 1000 labuser
USER labuser
```

### Network Isolation

Use Docker networks or Kubernetes network policies:

```yaml
# docker-compose.yml
networks:
  lab_network:
    driver: bridge
    internal: true  # No external access
```
