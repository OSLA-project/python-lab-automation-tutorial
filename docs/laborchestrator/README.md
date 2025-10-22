# Lab Orchestrator Documentation

Welcome to the Lab Orchestrator documentation. This directory contains comprehensive guides for configuring and using Lab Orchestrator in your laboratory automation environment.

## Documentation Structure

This documentation is organized into the following sections:

### 1. [Getting Started](getting-started.md)
- Installation instructions
- Quick start guide
- Command-line interface
- Development commands
- Troubleshooting common installation issues

**Start here if you're new to Lab Orchestrator.**

### 2. [Configuration](configuration.md)
- Lab configuration YAML format
- Device types and parameters
- PythonLab translation mappings
- Orchestrator parameters
- Environment variables
- Best practices for configuration management

**Use this guide to set up your laboratory devices and resources.**

### 3. [Writing Processes](writing-processes.md)
- PythonLab process structure
- Resource types (devices and containers)
- Device operations
- Complete workflow examples
- Best practices for process development
- Troubleshooting process errors

**Learn how to create laboratory workflows using PythonLab.**

### 4. [SiLA Integration](sila-integration.md)
- Starting the SiLA server
- SiLA features and commands
- Client integration examples
- SSL/TLS configuration
- Network discovery
- Security best practices

**Integrate Lab Orchestrator with your laboratory automation system.**

### 5. [API Reference](api-reference.md)
- Orchestrator class reference
- ScheduleManager API
- Data structures (ProcessStep, ContainerInfo, etc.)
- WorkerInterface and WorkerObserver
- Database integration
- Complete code examples

**Detailed reference for developers working with the Lab Orchestrator API.**

### 6. [Deployment](deployment.md)
- Docker deployment (recommended)
- Direct Python deployment
- Systemd service setup
- Kubernetes deployment
- Security considerations
- Monitoring and logging
- Backup and recovery

**Deploy Lab Orchestrator in production environments.**

## Quick Navigation

### Common Tasks

- **Install Lab Orchestrator**: [Getting Started → Installation](getting-started.md#installation)
- **Configure lab devices**: [Configuration → Lab Configuration YAML](configuration.md#lab-configuration-yaml)
- **Write your first process**: [Writing Processes → Examples](writing-processes.md#examples)
- **Start the SiLA server**: [SiLA Integration → Starting the SiLA Server](sila-integration.md#starting-the-sila-server)
- **Deploy with Docker**: [Deployment → Docker Deployment](deployment.md#docker-deployment)

### Reference Materials

- **Device types**: [Configuration → Device Types](configuration.md#device-types)
- **Process methods**: [Writing Processes → Device Operations](writing-processes.md#device-operations)
- **Orchestrator API**: [API Reference → Orchestrator](api-reference.md#orchestrator)
- **Data structures**: [API Reference → Data Structures](api-reference.md#data-structures)

## Documentation Format

All documentation is written in **Markdown** format, making it easy to:
- View directly on GitLab/GitHub
- Integrate with MkDocs
- Convert to other formats (HTML, PDF, etc.)
- Version control alongside code

## Integrating with MkDocs

To integrate this documentation with MkDocs, create a `mkdocs.yml` file in your project root:

```yaml
site_name: Lab Orchestrator Documentation
site_description: Documentation for Lab Orchestrator - Laboratory Workflow Automation
site_author: Your Organization

theme:
  name: material
  palette:
    primary: indigo
    accent: blue
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate

nav:
  - Home: new_docs/index.md
  - Getting Started: new_docs/getting-started.md
  - Configuration: new_docs/configuration.md
  - Writing Processes: new_docs/writing-processes.md
  - SiLA Integration: new_docs/sila-integration.md
  - API Reference: new_docs/api-reference.md
  - Deployment: new_docs/deployment.md

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed

plugins:
  - search
  - mkdocstrings
```

Then build and serve the documentation:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## Contributing to Documentation

When updating these docs:

1. **Use clear, concise language** - Write for users of all skill levels
2. **Include code examples** - Show don't tell
3. **Test examples** - Ensure all code examples work
4. **Update cross-references** - Keep links between docs accurate
5. **Follow the structure** - Maintain consistent formatting
6. **Add to index** - Update navigation when adding new sections

## Documentation Coverage

This documentation covers:

- ✅ Installation and setup
- ✅ Configuration management
- ✅ Process development with PythonLab
- ✅ SiLA 2 integration
- ✅ Complete API reference
- ✅ Production deployment
- ✅ Security best practices
- ✅ Monitoring and troubleshooting
- ✅ Code examples throughout

## Getting Help

If you can't find what you're looking for:

1. Check the [index](index.md) for an overview
2. Use the search feature (if using MkDocs)
3. Look at example processes in `tests/test_data/`
4. Run `invoke test` to see working configurations
5. Review the project's CLAUDE.md file for development guidance

## Version Information

This documentation is for Lab Orchestrator version **0.2.8**.

Last updated: 2025-10-22

## License

This documentation is part of the Lab Orchestrator project. Refer to the main project repository for license information.
