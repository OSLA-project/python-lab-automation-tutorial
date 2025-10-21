# PythonLab Documentation

Welcome to the PythonLab package documentation. PythonLab is a Python framework for defining, parsing, and managing laboratory automation workflows.

## Version

Current version: **0.2.3**

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
5. [Documentation Index](#documentation-index)

## Overview

PythonLab allows you to:
- **Define laboratory workflows** in Python syntax
- **Parse workflows** into directed acyclic graphs (DAGs)
- **Model laboratory resources** (devices, labware, substances, data)
- **Support runtime decision-making** based on experimental measurements
- **Enable workflow scheduling and optimization**

The framework converts laboratory process descriptions into executable workflow graphs that can be analyzed, scheduled, and executed by automation systems.

## Core Concepts

### 1. Processes (`PLProcess`)

A **process** is a Python class that describes a laboratory workflow. It defines:
- What resources are needed (devices, labware, substances)
- The sequence of operations to perform
- How data flows through the workflow
- Runtime decision points based on measurements

### 2. Resources

Resources represent the physical and logical components of laboratory automation:

- **ServiceResource**: Laboratory equipment and software services (incubators, centrifuges, plate readers, etc.)
- **LabwareResource**: Physical containers (plates, tubes, flasks)
- **SubstanceResource**: Chemical and biological materials
- **DataResource**: Data inputs and outputs

### 3. Workflow Graphs

The `PLProcessReader` parses process definitions into NetworkX directed graphs where:
- **Nodes** represent operations, labware, variables, or decisions
- **Edges** represent dependencies and data flow
- **Metadata** includes timing, costs, and constraints

### 4. Runtime vs Compile-Time

**Compile-time** (during parsing):
- Static variables and loops are evaluated
- Workflow structure is determined
- Graph is constructed

**Runtime** (during execution):
- Measurements produce values
- Conditional branches are selected
- Dynamic decisions are made

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PLProcess (Abstract)                      │
│  - Defines workflow in process() method                      │
│  - Declares resources in create_resources()                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ parse
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   PLProcessReader                            │
│  - Extracts source code                                      │
│  - Parses AST                                                │
│  - Builds workflow graph                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ creates
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 PLProcessSimulator                           │
│  - Inherits from PLProcess                                   │
│  - Contains workflow: nx.DiGraph()                           │
│  - Tracks labware state                                      │
│  - Manages graph construction                                │
└─────────────────────────────────────────────────────────────┘
```

## Getting Started

### Basic Example

```python
from pythonlab.resource import ServiceResource, LabwareResource
from pythonlab.process import PLProcess
from pythonlab.pythonlab_reader import PLProcessReader

# Define a custom service
class MyIncubator(ServiceResource):
    def incubate(self, labware, duration, temperature, **kwargs):
        kwargs.update(dict(
            fct='incubate',
            duration=duration,
            temperature=temperature
        ))
        self.proc.add_process_step(self, [labware], **kwargs)

# Define a process
class SimpleProcess(PLProcess):
    def create_resources(self):
        self.incubator = MyIncubator(proc=self, name="Incubator1")
        self.plate = LabwareResource(proc=self, name="Plate1")

    def init_service_resources(self):
        super().init_service_resources()

    def process(self):
        # Define the workflow
        self.incubator.incubate(self.plate, duration=3600, temperature=310)

# Parse the process
simulator = PLProcessReader.parse_process(SimpleProcess())

# Visualize the workflow
simulator.visualize_workflow_graph()

# Access the graph
print(f"Nodes: {simulator.workflow.number_of_nodes()}")
print(f"Edges: {simulator.workflow.number_of_edges()}")
```

## Documentation Index

### Guides

1. **[Writing PLProcessReader-Compliant Processes](pythonlab/writing_processes.md)** - Comprehensive guide to implementing processes
2. **[Resource Guide](./resources.md)** - Details on all resource types
3. **[Control Flow and Runtime Decisions](./control_flow.md)** - Handling conditionals and loops
4. **[Workflow Graph Structure](pythonlab/workflow_graph.md)** - Understanding the graph representation

### Reference

1. **[PLProcess API Reference](./api_plprocess.md)** - Complete PLProcess class documentation
2. **[PLProcessReader API Reference](./api_reader.md)** - Parser and simulator documentation
3. **[Built-in Services](pythonlab/builtin_services.md)** - Available ServiceResource implementations
4. **[Examples](pythonlab/examples.md)** - Complete example processes

## Project Structure

```
pythonlab/
├── __init__.py                 # Package initialization
├── process.py                  # PLProcess base class
├── resource.py                 # Resource base classes
├── pythonlab_reader.py         # PLProcessReader and PLProcessSimulator
├── processes/                  # Process-specific modules
│   ├── liquid_handling/
│   ├── incubation/
│   ├── separation/
│   └── ...
└── resources/                  # Resource implementations
    ├── services/               # ServiceResource implementations
    │   ├── incubation.py
    │   ├── moving.py
    │   ├── centrifugation.py
    │   ├── analysis.py
    │   └── ...
    ├── labware/
    ├── substances/
    └── data/
```

## Key Files

- **pythonlab/process.py** - Defines the `PLProcess` abstract base class
- **pythonlab/resource.py** - Defines all resource base classes
- **pythonlab/pythonlab_reader.py** - Contains `PLProcessReader` and `PLProcessSimulator`

## Next Steps

1. Read **[Writing PLProcessReader-Compliant Processes](pythonlab/writing_processes.md)** for a detailed tutorial
2. Explore the **[examples](pythonlab/examples.md)** to see complete implementations
3. Review **[Built-in Services](pythonlab/builtin_services.md)** to understand available devices

## Contributing

When creating new processes:
1. Subclass `PLProcess`
2. Implement all abstract methods
3. Define resources in `create_resources()`
4. Initialize services in `init_service_resources()`
5. Describe workflow in `process()`

## Support

For issues and questions, refer to the project repository or contact the development team.
