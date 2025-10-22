# API Reference

This document provides detailed reference for Lab Orchestrator's core classes and methods.

## Orchestrator

Main orchestrator class for managing laboratory workflows.

### Class: `Orchestrator`

Located in: `laborchestrator/orchestrator_implementation.py`

```python
from laborchestrator.orchestrator_implementation import Orchestrator
```

#### Constructor

```python
Orchestrator(
    reader: str = "PythonLab",
    worker_type: Type[WorkerInterface] = WorkerInterface
)
```

**Parameters**:
- `reader` (str): Process reader type (default: "PythonLab")
- `worker_type` (Type[WorkerInterface]): Worker implementation class

**Example**:
```python
orchestrator = Orchestrator()
```

#### Methods

##### `add_lab_resources_from_file`

Load lab configuration from a YAML file.

```python
add_lab_resources_from_file(lab_env_filename: str) -> bool
```

**Parameters**:
- `lab_env_filename` (str): Path to lab configuration YAML file

**Returns**: `bool` - True if successful

**Example**:
```python
success = orchestrator.add_lab_resources_from_file("lab_config.yml")
```

##### `add_process`

Add a process to the orchestrator.

```python
add_process(
    description: Optional[str] = None,
    file_path: Optional[str] = None,
    name: Optional[str] = None,
    process_object: Optional[PLProcess] = None,
    delay: int = 0
) -> str
```

**Parameters**:
- `description` (str, optional): Process source code as string
- `file_path` (str, optional): Path to Python process file
- `name` (str, optional): Process name
- `process_object` (PLProcess, optional): Process instance
- `delay` (int): Start delay in minutes (default: 0)

**Returns**: `str` - Process name

**Example**:
```python
# From file
name = orchestrator.add_process(
    file_path="process.py",
    name="MyProcess"
)

# From object
from my_processes import IncReadProcess
process = IncReadProcess(priority=5)
name = orchestrator.add_process(
    process_object=process,
    name="IncubationTest"
)

# From string
code = """
from pythonlab.process import PLProcess
# ...
"""
name = orchestrator.add_process(
    description=code,
    name="DynamicProcess"
)
```

##### `start_processes`

Start execution of processes.

```python
start_processes(process_names: List[str]) -> None
```

**Parameters**:
- `process_names` (List[str]): List of process names to start

**Example**:
```python
orchestrator.start_processes(["Process1", "Process2"])
```

##### `set_parameter`

Set orchestrator parameter.

```python
set_parameter(param_name: str, new_value: Any) -> None
```

**Parameters**:
- `param_name` (str): Parameter name
- `new_value` (Any): New parameter value

**Example**:
```python
orchestrator.set_parameter("time_limit_short", 2)
orchestrator.set_parameter("time_limit_long", 5)
```

##### `inject_db_interface`

Inject database interface for experiment tracking.

```python
inject_db_interface(db_client: StatusDBInterface) -> None
```

**Parameters**:
- `db_client` (StatusDBInterface): Database client instance

**Example**:
```python
from laborchestrator.database_integration import StatusDBInterface

db_interface = StatusDBInterface()
orchestrator.inject_db_interface(db_interface)
```

#### Properties

##### `processes`

Dictionary of all processes.

```python
processes: Dict[str, Process]
```

**Example**:
```python
for name, process in orchestrator.processes.items():
    print(f"{name}: {process.state}")
```

##### `schedule_manager`

The schedule manager instance.

```python
schedule_manager: ScheduleManager
```

**Example**:
```python
schedule_manager = orchestrator.schedule_manager
```

---

## ScheduleManager

Handles scheduling logic and device allocation.

### Class: `ScheduleManager`

Located in: `laborchestrator/engine/schedule_manager.py`

```python
from laborchestrator.engine.schedule_manager import ScheduleManager
```

#### Constructor

```python
ScheduleManager(
    jssp: SchedulingInstance,
    db_client: Optional[StatusDBInterface] = None
)
```

**Parameters**:
- `jssp` (SchedulingInstance): Scheduling instance
- `db_client` (StatusDBInterface, optional): Database client

#### Methods

##### `configure_lab`

Configure lab from YAML file.

```python
configure_lab(yaml_file: str) -> bool
```

**Parameters**:
- `yaml_file` (str): Path to lab configuration YAML

**Returns**: `bool` - True if successful

**Example**:
```python
success = schedule_manager.configure_lab("lab_config.yml")
```

##### `compute_schedule`

Compute optimal schedule for processes.

```python
compute_schedule(time_limit: Optional[float] = None) -> Dict
```

**Parameters**:
- `time_limit` (float, optional): Scheduling timeout in seconds

**Returns**: `Dict` - Schedule information

**Example**:
```python
schedule = schedule_manager.compute_schedule(time_limit=5.0)
```

#### Properties

##### `time_limit_short`

Quick scheduling timeout in seconds.

```python
time_limit_short: float
```

Default: 2 seconds

##### `time_limit_long`

Full scheduling timeout in seconds.

```python
time_limit_long: float
```

Default: 5 seconds

##### `lab_config_file`

Path to loaded lab configuration file.

```python
lab_config_file: str
```

---

## Data Structures

### ProcessStep

Represents a single operation in a workflow.

Located in: `laborchestrator/structures.py`

```python
from laborchestrator.structures import ProcessStep
from dataclasses import dataclass

@dataclass
class ProcessStep:
    name: str                           # Step identifier
    cont_names: List[str]              # Container names
    function: str                       # Operation type
    duration: float                     # Duration in seconds
    process_name: str                   # Parent process name
    used_devices: List[UsedDevice]     # Device requirements
    wait_to_start_costs: float         # Priority weighting
    data: Dict                          # Custom metadata
```

**Example**:
```python
step = ProcessStep(
    name="incubate_step_1",
    cont_names=["plate_1"],
    function="incubate",
    duration=120.0,
    process_name="MyProcess",
    used_devices=[device],
    wait_to_start_costs=0.0,
    data={"temperature": 310}
)
```

### MoveStep

Represents a container movement operation.

```python
@dataclass
class MoveStep:
    name: str                           # Step identifier
    cont_names: List[str]              # Container names
    function: str                       # Always "move"
    duration: float                     # Duration in seconds
    source_device: str                  # Source location
    target_device: str                  # Target location
    used_devices: List[UsedDevice]     # Mover device
    lidded: bool                        # Lid state
```

**Example**:
```python
move_step = MoveStep(
    name="move_to_incubator",
    cont_names=["plate_1"],
    function="move",
    duration=30.0,
    source_device="Carousel",
    target_device="Incubator1",
    used_devices=[mover],
    lidded=True
)
```

### ContainerInfo

Tracks labware container information.

```python
@dataclass
class ContainerInfo:
    name: str                           # Container identifier
    current_device: str                 # Current location
    current_pos: int                    # Position at location
    start_device: UsedDevice            # Starting location
    filled: bool                        # Filled/empty status
    content: str                        # Content description
    labware_type: str                   # Type (plate, tube, etc)
    barcode: Optional[str]              # Barcode number
    is_reagent: bool                    # Reagent flag
```

**Example**:
```python
container = ContainerInfo(
    name="culture_plate_1",
    current_device="Carousel",
    current_pos=10,
    start_device=storage_device,
    filled=True,
    content="E. coli culture",
    labware_type="96-well plate",
    barcode="BC123456",
    is_reagent=False
)
```

### UsedDevice

Represents device requirements/assignments.

```python
@dataclass
class UsedDevice:
    name: str                           # Device name
    device_type: str                    # Device type
    position: Optional[int]             # Position at device
    capacity: int                       # Device capacity
    allows_overlap: bool                # Concurrent operations
```

**Example**:
```python
device = UsedDevice(
    name="Incubator1",
    device_type="incubator",
    position=5,
    capacity=32,
    allows_overlap=False
)
```

### SchedulingInstance

Complete workflow container (JSSP - Job Shop Scheduling Problem).

```python
@dataclass
class SchedulingInstance:
    process_steps: List[ProcessStep]    # All process steps
    move_steps: List[MoveStep]          # All move steps
    containers: List[ContainerInfo]     # All containers
    devices: List[UsedDevice]           # All devices
    dependencies: Dict                   # Step dependencies
```

**Example**:
```python
instance = SchedulingInstance(
    process_steps=[step1, step2],
    move_steps=[move1, move2],
    containers=[container1, container2],
    devices=[device1, device2],
    dependencies={"step2": ["step1"]}
)
```

---

## WorkerInterface

Executes process steps by interfacing with lab devices.

### Class: `WorkerInterface`

Located in: `laborchestrator/engine/worker_interface.py`

```python
from laborchestrator.engine.worker_interface import WorkerInterface
```

#### Methods

##### `execute_step`

Execute a process step.

```python
execute_step(step: ProcessStep, containers: List[ContainerInfo]) -> bool
```

**Parameters**:
- `step` (ProcessStep): Step to execute
- `containers` (List[ContainerInfo]): Involved containers

**Returns**: `bool` - True if successful

##### `execute_move`

Execute a move step.

```python
execute_move(move: MoveStep, containers: List[ContainerInfo]) -> bool
```

**Parameters**:
- `move` (MoveStep): Move step to execute
- `containers` (List[ContainerInfo]): Containers to move

**Returns**: `bool` - True if successful

---

## WorkerObserver

Monitors execution and updates schedules.

### Class: `WorkerObserver`

Located in: `laborchestrator/engine/worker_observer.py`

```python
from laborchestrator.engine.worker_observer import WorkerObserver
```

#### Methods

##### `observe`

Monitor process execution.

```python
observe() -> None
```

Continuously monitors running steps and triggers rescheduling on delays or errors.

##### `update_schedule`

Trigger schedule update.

```python
update_schedule() -> None
```

Requests a new schedule computation based on current state.

---

## WFGManager

Manages workflow graphs for visualization.

### Class: `WFGManager`

Located in: `laborchestrator/engine/wfg_manager.py`

```python
from laborchestrator.engine.wfg_manager import WFGManager
```

#### Methods

##### `create_graph`

Create workflow graph from scheduling instance.

```python
create_graph(instance: SchedulingInstance) -> WorkFlowGraph
```

**Parameters**:
- `instance` (SchedulingInstance): Scheduling instance

**Returns**: `WorkFlowGraph` - NetworkX directed graph

##### `visualize`

Generate visualization of workflow graph.

```python
visualize(graph: WorkFlowGraph, output_file: str) -> None
```

**Parameters**:
- `graph` (WorkFlowGraph): Workflow graph
- `output_file` (str): Output file path

---

## PythonLabReader

Parses PythonLab process files.

### Class: `PythonLabReader`

Located in: `laborchestrator/pythonlab_reader.py`

```python
from laborchestrator.pythonlab_reader import PythonLabReader
```

#### Methods

##### `read_process`

Read and parse a PythonLab process file.

```python
read_process(file_path: str) -> PLProcess
```

**Parameters**:
- `file_path` (str): Path to process file

**Returns**: `PLProcess` - Parsed process object

**Example**:
```python
reader = PythonLabReader()
process = reader.read_process("process.py")
```

##### `try_to_read_process`

CLI command to read and validate a process.

```python
try_to_read_process(file_path: str) -> None
```

**Parameters**:
- `file_path` (str): Path to process file

**Example**:
```bash
read_process path/to/process.py
```

---

## Enums

### OrchestratorState

Orchestrator execution states.

Located in: `laborchestrator/orchestrator_interface.py`

```python
from laborchestrator.orchestrator_interface import OrchestratorState
from enum import Enum

class OrchestratorState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    FINISHED = "finished"
```

**Example**:
```python
if orchestrator.state == OrchestratorState.RUNNING:
    print("Orchestrator is running")
```

### ProcessState

Process execution states.

```python
from laborchestrator.orchestrator_interface import ProcessState
from enum import Enum

class ProcessState(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

**Example**:
```python
for name, process in orchestrator.processes.items():
    if process.state == ProcessState.FAILED:
        print(f"Process {name} failed")
```

### StepState

Process step execution states.

```python
from laborchestrator.orchestrator_interface import StepState
from enum import Enum

class StepState(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
```

---

## Database Integration

### StatusDBInterface

Abstract interface for database integration.

Located in: `laborchestrator/database_integration/status_db_interface.py`

```python
from laborchestrator.database_integration import StatusDBInterface
```

#### Methods

##### `update_process_status`

Update process status in database.

```python
update_process_status(
    process_name: str,
    state: ProcessState,
    progress: float
) -> None
```

**Parameters**:
- `process_name` (str): Process name
- `state` (ProcessState): Current state
- `progress` (float): Progress percentage (0-100)

##### `update_step_status`

Update step status in database.

```python
update_step_status(
    step_name: str,
    state: StepState,
    start_time: Optional[datetime],
    end_time: Optional[datetime]
) -> None
```

**Parameters**:
- `step_name` (str): Step name
- `state` (StepState): Current state
- `start_time` (datetime, optional): Start timestamp
- `end_time` (datetime, optional): End timestamp

##### `log_event`

Log an event to database.

```python
log_event(
    event_type: str,
    message: str,
    severity: str = "info"
) -> None
```

**Parameters**:
- `event_type` (str): Event type
- `message` (str): Event message
- `severity` (str): Severity level (info/warning/error)

---

## Type Hints

Common type aliases used in Lab Orchestrator:

```python
from typing import Dict, List, Optional, Tuple, Union
from laborchestrator.structures import ProcessStep, MoveStep, ContainerInfo, UsedDevice

# Workflow graph type (NetworkX directed graph)
WorkFlowGraph = nx.DiGraph

# Schedule type
Schedule = Dict[str, Any]

# Device configuration
DeviceConfig = Dict[str, Union[str, int, bool, float]]

# Lab configuration
LabConfig = Dict[str, Dict[str, DeviceConfig]]
```

---

## Complete Example

Here's a complete example using the API:

```python
from laborchestrator.orchestrator_implementation import Orchestrator
from laborchestrator.orchestrator_interface import ProcessState
from tests.test_data.inc_read_process import IncReadProcess

# Create orchestrator
orchestrator = Orchestrator()

# Configure lab
success = orchestrator.add_lab_resources_from_file("lab_config.yml")
if not success:
    print("Failed to load lab configuration")
    exit(1)

# Add processes
process1 = IncReadProcess(priority=5)
name1 = orchestrator.add_process(
    process_object=process1,
    name="IncubationTest"
)

name2 = orchestrator.add_process(
    file_path="another_process.py",
    name="SecondProcess",
    delay=30  # Start in 30 minutes
)

# Start processes
orchestrator.start_processes([name1, name2])

# Monitor execution
import time
while True:
    all_done = True
    for name, process in orchestrator.processes.items():
        print(f"{name}: {process.state}")
        if process.state not in [ProcessState.COMPLETED, ProcessState.FAILED]:
            all_done = False

    if all_done:
        break

    time.sleep(10)

print("All processes completed")
```

---

## See Also

- [Configuration](configuration.md) - Configure lab resources
- [Writing Processes](writing-processes.md) - Create workflows
- [SiLA Integration](sila-integration.md) - SiLA server API
- [Getting Started](getting-started.md) - Quick start guide
