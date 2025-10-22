# Getting Started

This guide will help you install and run Lab Orchestrator for the first time.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) Docker and docker-compose for containerized deployment

## Installation

### Install from PyPI

```bash
pip install laborchestrator --index-url https://gitlab.com/api/v4/projects/39006834/packages/pypi/simple
```

### Development Installation

For development or local modifications:

```bash
# Clone the repository
git clone <repository-url>
cd laborchestrator

# Install with development dependencies
pip install -e .[dev]
```

## Quick Start

### 1. Start the SiLA Server

The simplest way to get started is to run the SiLA server:

```bash
python -m laborchestrator.sila_server --insecure -a 127.0.0.1 -p 50052
```

This starts the orchestrator's SiLA interface on `localhost:50052` without SSL encryption.

### 2. Using the Orchestrator Programmatically

Create a Python script to use the orchestrator:

```python
from laborchestrator.orchestrator_implementation import Orchestrator

# Create orchestrator instance
orchestrator = Orchestrator()

# Load lab configuration
orchestrator.add_lab_resources_from_file("path/to/lab_config.yml")

# Add a process from a file
orchestrator.add_process(
    file_path="path/to/process.py",
    name="MyProcess"
)

# Start the process
orchestrator.start_processes(["MyProcess"])
```

### 3. Running with Docker

The easiest deployment method is using Docker:

```bash
# Build and start
docker-compose up --build
```

This will:
- Build the Lab Orchestrator container
- Start the orchestrator service
- Expose the SiLA server on port 50052
- Start the Dash web interface

## Command-Line Interface

### SiLA Server Options

```bash
python -m laborchestrator.sila_server [OPTIONS]
```

Available options:

- `-a, --ip-address TEXT` - Server IP address (default: 127.0.0.1)
- `-p, --port INTEGER` - Server port (default: 50052)
- `--server-uuid TEXT` - Custom server UUID
- `--disable-discovery` - Disable SiLA discovery service
- `--insecure` - Start without SSL encryption (for development)
- `-k, --private-key-file PATH` - Path to SSL private key
- `-c, --cert-file PATH` - Path to SSL certificate
- `--verbose` - Enable verbose logging
- `--debug` - Enable debug logging
- `--quiet` - Suppress non-error messages

### Example Commands

Start server with SSL:
```bash
python -m laborchestrator.sila_server \
    -c server-cert.pem \
    -k server-key.pem \
    -a 0.0.0.0 \
    -p 50052
```

Start server for local development:
```bash
python -m laborchestrator.sila_server --insecure --debug
```

### Process Reader CLI

Read and validate a PythonLab process file:

```bash
read_process path/to/process.py
```

This command parses a PythonLab process file and validates its structure.

## Development Commands

Lab Orchestrator uses `invoke` for development tasks:

### Testing

```bash
# Run all tests
invoke test

# Run tests with HTML coverage report
invoke test --coverage=html

# Run tests with JUnit XML output
invoke test --junit

# Run tests in Docker
invoke docker-test

# Run specific test file
pytest tests/test_laborchestrator.py
```

### Code Quality

```bash
# Format code (applies changes)
invoke format

# Check formatting without making changes
invoke format --check

# Run linting
invoke lint

# Run security checks
invoke security
```

### Documentation

```bash
# Build and open documentation
invoke docs

# Build without opening browser
invoke docs --no-launch
```

### Build & Release

```bash
# Clean all build artifacts
invoke clean

# Build Docker image (default Python 3.9)
invoke docker-build

# Build with specific Python version
invoke docker-build --python-version=3.10

# Version bump (patch/minor/major)
bumpversion patch
bumpversion minor
bumpversion major
```

## Next Steps

1. **Configure your lab**: Create a lab configuration YAML file. See [Configuration](configuration.md).
2. **Write your first process**: Learn the PythonLab syntax. See [Writing Processes](writing-processes.md).
3. **Integrate with SiLA**: Connect to your lab devices. See [SiLA Integration](sila-integration.md).
4. **Deploy**: Set up for production use. See [Deployment](deployment.md).

## Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'pythonlab'`

**Solution**: The pythonlab package is hosted on a custom GitLab index. Make sure your `pyproject.toml` includes:

```toml
[[tool.uv.index]]
name = "gitlab-pythonlab"
url = "https://gitlab.com/api/v4/projects/70367030/packages/pypi/simple"
```

**Problem**: SiLA server won't start

**Solution**: Check that the port (default 50052) is not already in use. Use a different port with `-p` option.

**Problem**: Cannot connect to scheduler service

**Solution**: Ensure the scheduler service is running and discoverable on your network. Check firewall settings.

## Verifying Installation

Run the test suite to verify your installation:

```bash
invoke test
```

All tests should pass. If you encounter failures, check that:
- All dependencies are installed
- Python version is 3.9 or higher
- You have network access for downloading test data
