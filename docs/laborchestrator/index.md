# Lab Orchestrator Documentation

Lab Orchestrator is a general-purpose orchestrator for scientific laboratories that integrates with SiLA servers and uses pythonLab as a process description language. It manages and schedules complex laboratory workflows, coordinating devices, labware containers, and process steps.

## Documentation Contents

1. [Getting Started](getting-started.md) - Installation and quick start guide
2. [Configuration](configuration.md) - How to configure Lab Orchestrator and lab resources
3. [Writing Processes](writing-processes.md) - Guide to creating PythonLab workflows
4. [SiLA Integration](sila-integration.md) - Using the SiLA server interface
5. [API Reference](api-reference.md) - Core classes and methods
6. [Deployment](deployment.md) - Running in production with Docker

## Quick Links

- [Lab Configuration YAML Format](configuration.md#lab-configuration-yaml)
- [Process Examples](writing-processes.md#examples)
- [CLI Commands](getting-started.md#command-line-interface)
- [Docker Setup](deployment.md#docker-deployment)

## Key Features

- **Job Shop Scheduling**: Optimal scheduling of laboratory processes with device allocation
- **SiLA 2 Integration**: Standard protocol for laboratory automation
- **PythonLab Processes**: Intuitive Python-based process description language
- **Workflow Visualization**: NetworkX-based workflow graphs
- **Real-time Monitoring**: Dash web interface for process tracking
- **Database Integration**: Experiment tracking and status reporting
- **Container Management**: Track labware containers through complex workflows

## Architecture Overview

Lab Orchestrator is built around five main components:

1. **SchedulingInstance (JSSP)** - Central data structure holding processes, steps, containers, and devices
2. **ScheduleManager** - Handles scheduling logic and device allocation
3. **WFGManager** - Manages workflow graphs for visualization
4. **WorkerInterface** - Executes process steps by interfacing with lab devices
5. **WorkerObserver** - Monitors execution and triggers rescheduling

## Getting Help

- Check the documentation sections listed above
- Run tests to see example configurations: `invoke test`
- View example processes in `tests/test_data/`
- Report issues at the project repository
