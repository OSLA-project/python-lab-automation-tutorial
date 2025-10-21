# Writing PLProcessReader-Compliant Processes

This guide provides comprehensive instructions for writing processes that comply with the `PLProcessReader` parsing system.
A [quickstart guide](processes_quickstart.md) is available as well.

## Table of Contents

1. [Introduction](#introduction)
2. [The PLProcess Interface](#the-plprocess-interface)
3. [Step-by-Step Tutorial](#step-by-step-tutorial)
4. [Service Resources](#service-resources)
5. [Runtime Variables and Decisions](#runtime-variables-and-decisions)
6. [Control Flow](#control-flow)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Advanced Topics](#advanced-topics)

## Introduction

A **PLProcessReader-compliant process** is a Python class that:
1. Inherits from `PLProcess`
2. Implements three required abstract methods
3. Describes a workflow that can be parsed into a graph
4. Follows specific patterns for control flow and variable management

The `PLProcessReader` analyzes your process code and converts it into a workflow graph (NetworkX DiGraph) that represents the sequence of operations, dependencies, and decision points.

## The PLProcess Interface

### Required Abstract Methods

Every PLProcess subclass must implement three methods:

```python
from pythonlab.process import PLProcess
from abc import abstractmethod

class YourProcess(PLProcess):

    @abstractmethod
    def create_resources(self):
        """
        Create and initialize all resources used in the process.

        This method is called during __init__. Resources automatically
        register themselves with the process when instantiated.

        You should create:
        - ServiceResource instances (devices)
        - LabwareResource instances (containers)
        - SubstanceResource instances (chemicals/materials)
        - DataResource instances (data inputs/outputs)
        """
        raise NotImplementedError

    @abstractmethod
    def init_service_resources(self):
        """
        Initialize service resources.

        Called after create_resources(). Typically:
        1. Call super().init_service_resources() to invoke init() on each service
        2. Set starting positions for labware
        3. Configure device-specific settings
        """
        raise NotImplementedError

    @abstractmethod
    def process(self):
        """
        Define the workflow.

        This method body is parsed (NOT executed during parsing) by PLProcessReader.
        Write it in imperative Python syntax describing the workflow steps.

        Key points:
        - Call methods on ServiceResource objects to add operations
        - Use variables to capture outputs from devices
        - Use control flow (if/for) to structure the workflow
        - The parser will convert this into a workflow graph
        """
        raise NotImplementedError
```

### Optional Overrides

You can optionally override:

```python
def add_process_step(self, service: ServiceResource,
                    labware: List[LabwareResource],
                    is_movement: bool = False, **kwargs):
    """
    Called whenever a ServiceResource method is invoked.

    During parsing, PLProcessSimulator.add_process_step() is called instead,
    which builds the workflow graph.

    In a non-parsed PLProcess, you could override this to track steps,
    log operations, etc.
    """
    pass

def set_starting_position(self, resource: LabwareResource,
                         device: ServiceResource, position: int):
    """
    Called when labware starting position is set.
    Override to customize behavior.
    """
    pass
```

## Step-by-Step Tutorial

Let's build a complete process from scratch.

### Step 1: Import Required Classes

```python
from pythonlab.process import PLProcess
from pythonlab.resource import (
    ServiceResource,
    LabwareResource,
    SubstanceResource,
    DataResource,
    DataDirection
)
```

### Step 2: Create Custom Service Resources

Services represent laboratory equipment. Each operation on a device is a method that calls `add_process_step()`.

```python
class IncubatorService(ServiceResource):
    """Represents an incubator device."""

    def incubate(self, labware: LabwareResource, duration: int,
                temperature: float, shaking_frequency: int = 0, **kwargs):
        """
        Incubate labware at specified conditions.

        Args:
            labware: The container to incubate
            duration: Time in seconds
            temperature: Temperature in Kelvin
            shaking_frequency: RPM for shaking (default 0)
            **kwargs: Additional metadata
        """
        # Update kwargs with operation metadata
        kwargs.update(dict(
            fct='incubate',              # Function name
            duration=duration,            # Time to execute
            temperature=temperature,      # Process parameter
            shaking_frequency=shaking_frequency
        ))
        # Add this operation to the workflow
        self.proc.add_process_step(self, [labware], **kwargs)


class PlateReaderService(ServiceResource):
    """Represents a microplate reader."""

    def measure_absorbance(self, labware: LabwareResource,
                          wavelengths: list, **kwargs):
        """
        Measure absorbance at specified wavelengths.

        Args:
            labware: Plate to read
            wavelengths: List of wavelengths in nm
            **kwargs: Additional metadata

        Returns:
            Variable representing measurement data (parsed as runtime variable)
        """
        kwargs.update(dict(
            fct='measure_absorbance',
            duration=30,                  # Assume 30 seconds to read
            wavelengths=wavelengths
        ))
        self.proc.add_process_step(self, [labware], **kwargs)


class MoverService(ServiceResource):
    """Represents a robotic arm or moving system."""

    def move(self, labware: LabwareResource, target_loc: ServiceResource,
            lidded: bool = True, **kwargs):
        """
        Move labware to a target location.

        Args:
            labware: Container to move
            target_loc: Target ServiceResource (device location)
            lidded: Whether labware should have lid during move
            **kwargs: Additional metadata
        """
        kwargs.update(dict(
            fct='move',
            duration=20,                  # Assume 20 seconds to move
            target=target_loc.name,
            lidded=lidded
        ))
        self.proc.add_process_step(self, [labware], is_movement=True, **kwargs)
```

**Key Pattern for ServiceResource Methods:**
1. Accept labware and operation parameters
2. Update `kwargs` with operation metadata (fct name, duration, parameters)
3. Call `self.proc.add_process_step(self, [labware], **kwargs)`

### Step 3: Define Your Process Class

```python
class MyBioProcess(PLProcess):
    """
    Example bioprocess: incubate samples, measure absorbance,
    make decisions based on results.
    """

    def __init__(self, priority=10):
        """
        Initialize the process.

        Args:
            priority: Process priority (0 = highest)
        """
        super().__init__(priority=priority)
```

### Step 4: Implement create_resources()

```python
    def create_resources(self):
        """Create all resources needed for this process."""

        # Create service resources (devices)
        self.incubator = IncubatorService(proc=self, name="Incubator_1")
        self.reader = PlateReaderService(proc=self, name="PlateReader_1")
        self.mover = MoverService(proc=self, name="RobotArm_1")

        # Create labware resources (containers)
        self.sample_plates = [
            LabwareResource(
                proc=self,
                name=f"SamplePlate_{i}",
                lidded=True,              # Has a lid
                plate_type="96-well"      # Additional metadata
            )
            for i in range(3)             # 3 plates
        ]

        # Create substance resources (optional)
        self.growth_media = SubstanceResource(
            proc=self,
            name="LB_Media",
            volume_ml=100
        )

        # Create data resources (optional)
        self.measurement_output = DataResource(
            proc=self,
            name="AbsorbanceData",
            direction=DataDirection.data_out
        )
```

**Important:** Resources auto-register with the process during `__init__`, so just creating them is sufficient.

### Step 5: Implement init_service_resources()

```python
    def init_service_resources(self):
        """Initialize services and set starting positions."""

        # Always call super to invoke init() on all services
        super().init_service_resources()

        # Set starting positions for labware
        for i, plate in enumerate(self.sample_plates):
            # Plates start at the mover location at positions 1, 2, 3
            plate.set_start_position(self.mover, position=i+1)
```

### Step 6: Implement process()

This is where you describe the workflow.

```python
    def process(self):
        """Define the workflow."""

        # Get references to plates for readability
        plate1, plate2, plate3 = self.sample_plates

        # Step 1: Move all plates to incubator
        for plate in self.sample_plates:
            self.mover.move(plate, target_loc=self.incubator, lidded=True)

        # Step 2: Incubate first batch
        self.incubator.incubate(plate1, duration=3600, temperature=310)
        self.incubator.incubate(plate2, duration=3600, temperature=310)

        # Step 3: Move first plate to reader
        self.mover.move(plate1, target_loc=self.reader, lidded=False)

        # Step 4: Measure absorbance (returns runtime variable)
        absorbance = self.reader.measure_absorbance(
            plate1,
            wavelengths=[600, 660]
        )

        # Step 5: Make runtime decision based on measurement
        avg_abs = self.compute_average(absorbance)

        if avg_abs < 0.5:
            # Low density - continue incubation
            self.mover.move(plate1, target_loc=self.incubator, lidded=True)
            self.incubator.incubate(plate1, duration=1800, temperature=310)
        else:
            # High density - proceed to next step
            self.mover.move(plate1, target_loc=self.reader, lidded=False)

        # Step 6: Process remaining plates
        for plate in [plate2, plate3]:
            self.mover.move(plate, target_loc=self.reader, lidded=False)
            self.reader.measure_absorbance(plate, wavelengths=[600, 660])

    def compute_average(self, data):
        """
        Helper function for computing average.

        Since this uses a runtime variable (data), it will be parsed
        as a computation node in the workflow graph.
        """
        # In real execution, this would process the data
        # During parsing, this creates a computation node
        pass
```

### Step 7: Parse and Visualize

```python
from pythonlab.pythonlab_reader import PLProcessReader

# Parse the process
simulator = PLProcessReader.parse_process(MyBioProcess())

# Visualize the workflow graph
simulator.visualize_workflow_graph()

# Access the graph
print(f"Number of nodes: {simulator.workflow.number_of_nodes()}")
print(f"Number of edges: {simulator.workflow.number_of_edges()}")

# Inspect nodes
for node_id, node_data in simulator.workflow.nodes(data=True):
    print(f"Node {node_id}: {node_data['type']} - {node_data['name']}")

# Inspect edges
for source, target, edge_data in simulator.workflow.edges(data=True):
    print(f"Edge {source} -> {target}: {edge_data}")
```

## Service Resources

### Anatomy of a Service Method

```python
def operation_name(self, labware: LabwareResource,
                  param1, param2, **kwargs):
    """
    Template for service method.

    Args:
        labware: Container(s) involved in operation
        param1, param2: Operation-specific parameters
        **kwargs: Additional metadata

    Returns:
        Optional: Variable representing output (for runtime variables)
    """
    # 1. Update kwargs with operation metadata
    kwargs.update(dict(
        fct='operation_name',      # REQUIRED: Function name
        duration=60,                # REQUIRED: Duration in seconds
        param1=param1,              # Include all parameters
        param2=param2
    ))

    # 2. Call add_process_step
    self.proc.add_process_step(
        self,                       # The service performing the operation
        [labware],                  # List of labware involved
        is_movement=False,          # True only for movement operations
        **kwargs                    # Operation metadata
    )

    # 3. Optionally return (creates runtime variable)
    # If this method returns, the parser treats it as a runtime variable
```

### Required Metadata in kwargs

- **fct** (str): Function/operation name
- **duration** (int): Time to execute in seconds

### Optional Metadata

- **executor** (list): List of specific devices that can execute this (if multiple available)
- **wait_to_start_costs** (float): Cost per second of waiting before starting
- **Any operation-specific parameters**: temperature, rpm, wavelengths, etc.

### Multiple Labware Example

Some operations involve multiple containers:

```python
class CentrifugeService(ServiceResource):
    def centrifuge(self, labwares: list, duration: int, rpm: int, **kwargs):
        """
        Centrifuge multiple containers simultaneously.

        Args:
            labwares: List of LabwareResource objects
            duration: Centrifugation time in seconds
            rpm: Revolutions per minute
        """
        kwargs.update(dict(
            fct='centrifuge',
            duration=duration,
            rpm=rpm
        ))
        # Pass list of all labware involved
        self.proc.add_process_step(self, labwares, **kwargs)

# Usage in process():
self.centrifuge.centrifuge(
    labwares=[plate1, plate2, plate3],
    duration=600,
    rpm=4000
)
```

## Runtime Variables and Decisions

### What are Runtime Variables?

**Runtime variables** are values that are only known during process execution (not during parsing). They come from:
1. Device measurements (e.g., absorbance readings)
2. Sensor outputs
3. User inputs during execution
4. Computations based on other runtime variables

### Creating Runtime Variables

A variable becomes "runtime" when it's assigned from a ServiceResource method call:

```python
# Runtime variable - value from device
measurement = self.reader.measure_absorbance(plate, wavelengths=[600])

# Runtime variable - value from sensor
temperature = self.sensor.read_temperature(device)

# Compile-time variable - value known during parsing
static_value = 100
loop_count = 5
```

### Computations on Runtime Variables

When you compute a value based on runtime variables, the parser creates a **computation node**:

```python
# measurement is runtime variable
measurement = self.reader.measure_absorbance(plate, wavelengths=[600])

# avg is derived from runtime variable -> becomes computation node
avg = self.calculate_average(measurement)

# ratio is derived from runtime variable -> becomes computation node
ratio = avg / 0.6

# decision uses runtime variable -> creates if_node with both branches
if avg > 0.5:
    # True branch
    self.mover.move(plate, target_loc=self.storage)
else:
    # False branch
    self.mover.move(plate, target_loc=self.incubator)
```

### Runtime Decisions (if-statements)

The parser distinguishes between **compile-time** and **runtime** conditionals:

#### Compile-Time Conditionals

Condition can be evaluated during parsing:

```python
plate_count = 3  # Known during parsing

if plate_count > 2:
    # Only this branch will be in the workflow graph
    self.incubator.incubate(plate3, duration=3600, temperature=310)
else:
    # This branch will NOT be in the graph
    pass
```

Result: Parser evaluates the condition, includes only the true branch.

#### Runtime Conditionals

Condition depends on runtime variables:

```python
# measurement is runtime variable
measurement = self.reader.measure_absorbance(plate, wavelengths=[600])
avg = self.calculate_average(measurement)

if avg > 0.6:
    # True branch - included in graph
    self.mover.move(plate, target_loc=self.storage)
else:
    # False branch - also included in graph
    self.mover.move(plate, target_loc=self.incubator)
```

Result: Parser creates an **if_node** with:
- A decision function (evaluating `avg > 0.6`)
- A true branch (dummy node → move to storage)
- A false branch (dummy node → move to incubator)

Both branches are present in the graph. The scheduler/executor will decide which branch to take during execution.

### Workflow Graph Structure for Runtime Decisions

```
        [measurement operation]
                 │
                 ▼
        [computation: avg]
                 │
                 ▼
          [if_node: avg > 0.6]
            ╱            ╲
           ╱              ╲
    [true_dummy]      [false_dummy]
          │                 │
          ▼                 ▼
    [move to storage]  [move to incubator]
          │                 │
          └────────┬────────┘
                   ▼
            [convergence point]
```

## Control Flow

### For Loops

For loops are **unrolled during parsing**. The iterable must be known at compile time.

#### Valid For Loops

```python
# Iterate over known list of labware
for plate in self.sample_plates:
    self.mover.move(plate, target_loc=self.incubator)
    self.incubator.incubate(plate, duration=3600, temperature=310)

# Iterate over range
for i in range(5):
    self.reader.measure_absorbance(self.plates[i], wavelengths=[600])

# Iterate over known values
for temperature in [300, 310, 320]:
    self.incubator.incubate(plate, duration=1800, temperature=temperature)
```

Result: Parser unrolls the loop, creating separate nodes for each iteration.

#### Invalid For Loops

```python
# INVALID - runtime_count is runtime variable
runtime_count = self.counter.count_samples(plate)
for i in range(runtime_count):  # ERROR: Can't iterate over runtime variable
    self.process_sample(i)
```

### Break Statements

You can use `break` to exit loops early:

```python
for plate in self.sample_plates:
    measurement = self.reader.measure_absorbance(plate, wavelengths=[600])
    avg = self.calculate_average(measurement)

    if avg > threshold:
        break  # Creates a break node

    self.incubator.incubate(plate, duration=3600, temperature=310)
```

The parser creates a **break node** that connects to the loop exit point.

### If-Elif-Else

```python
# Compile-time if-elif-else
if plate_type == "96-well":
    volume = 200
elif plate_type == "384-well":
    volume = 50
else:
    volume = 100

# Runtime if-elif-else
measurement = self.reader.measure_absorbance(plate, wavelengths=[600])
avg = self.calculate_average(measurement)

if avg < 0.3:
    # Low density
    self.incubator.incubate(plate, duration=7200, temperature=310)
elif avg < 0.7:
    # Medium density
    self.incubator.incubate(plate, duration=3600, temperature=310)
else:
    # High density - no additional incubation
    self.mover.move(plate, target_loc=self.storage)
```

## Best practices
### 1. Set Starting Positions

Always set starting positions for labware to provide context:

```python
def init_service_resources(self):
    super().init_service_resources()

    for i, plate in enumerate(self.sample_plates):
        plate.set_start_position(self.storage, position=i+1)
```

### 2. Use Labware Constraints

For time-sensitive operations:

```python
# Maximum 30 minutes between steps
plate.max_wait(duration=1800)

# Minimum 10 minutes before next step
plate.min_wait(duration=600)

# Cost per second of waiting (for scheduling optimization)
plate.wait_cost(cost=0.1)
```



## Advanced Topics

### Dynamic Labware Resources

For labware selected at runtime:

```python
from pythonlab.resource import DynamicLabwareResource

def create_resources(self):
    # Dynamic labware - usage order determined at runtime
    self.reagent_trough = DynamicLabwareResource(
        proc=self,
        name="ReagentTrough",
        outside_cost=5  # Cost when not actively used (e.g., cooling cost)
    )
```

### Priority Management

Control execution order:

```python
# High priority process (0 = highest)
critical_process = MyCriticalProcess(priority=0)

# Normal priority
normal_process = MyNormalProcess(priority=10)

# Low priority
background_process = MyBackgroundProcess(priority=20)
```

### Labware with Priority

```python
# High priority sample
priority_sample = LabwareResource(
    proc=self,
    name="UrgentSample",
    priority=0  # Process this first
)

# Normal priority
normal_sample = LabwareResource(
    proc=self,
    name="NormalSample",
    priority=None  # Default priority
)
```

### Process Order Preservation

If sample order must be maintained:

```python
def __init__(self):
    super().__init__()
    self.preserve_order = True  # Samples processed in order
```

### Data Resources

Track data inputs and outputs:

```python
from pythonlab.resource import DataResource, DataDirection, DataType

def create_resources(self):
    # Input data
    self.protocol_config = DataResource(
        proc=self,
        name="ProtocolConfig",
        direction=DataDirection.data_in,
        data_type=DataType.structured_data
    )

    # Output data
    self.measurement_results = DataResource(
        proc=self,
        name="Results",
        direction=DataDirection.data_out,
        data_type=DataType.data_stream
    )
```

### Complex Graph Structures

For advanced workflows with multiple decision points:

```python
def process(self):
    # Initial processing
    for plate in self.sample_plates:
        self.mover.move(plate, target_loc=self.incubator)
        self.incubator.incubate(plate, duration=3600, temperature=310)

    # Multiple runtime decision points
    for plate in self.sample_plates:
        measurement = self.reader.measure_absorbance(plate, wavelengths=[600])
        density = self.calculate_density(measurement)

        # Decision tree
        if density < 0.3:
            # Low density - long incubation
            self.incubator.incubate(plate, duration=7200, temperature=310)
        elif density < 0.7:
            # Medium density - short incubation
            self.incubator.incubate(plate, duration=3600, temperature=310)
        else:
            # High density - measure again
            second_measurement = self.reader.measure_absorbance(
                plate, wavelengths=[600, 660]
            )
            avg = self.calculate_average(second_measurement)

            if avg > 1.0:
                # Very high - store immediately
                self.mover.move(plate, target_loc=self.storage)
            else:
                # High - one more short incubation
                self.incubator.incubate(plate, duration=1800, temperature=310)
```

### Accessing Workflow Graph Details

After parsing:

```python
simulator = PLProcessReader.parse_process(MyProcess())

# Get all operation nodes
operation_nodes = [
    (node_id, data)
    for node_id, data in simulator.workflow.nodes(data=True)
    if data['type'] == 'operation'
]

# Get all if-decision nodes
if_nodes = [
    (node_id, data)
    for node_id, data in simulator.workflow.nodes(data=True)
    if data['type'] == 'if_node'
]

# Get critical path (longest path through graph)
import networkx as nx
longest_path = nx.dag_longest_path(simulator.workflow, weight='duration')

# Total process time (sum of longest path)
total_time = sum(
    simulator.workflow.nodes[node].get('duration', 0)
    for node in longest_path
)
print(f"Minimum process time: {total_time} seconds")
```

## Summary

To write a PLProcessReader-compliant process:

1. **Subclass PLProcess** and implement three abstract methods
2. **Create ServiceResources** with methods that call `add_process_step()`
3. **Create all resources** in `create_resources()`
4. **Initialize services** and set starting positions in `init_service_resources()`
5. **Define workflow** in `process()` using imperative syntax
6. **Use runtime variables** for device outputs and measurements
7. **Use control flow** (if/for) to structure the workflow
8. **Parse with PLProcessReader** to generate the workflow graph

The parser converts your Python code into a workflow graph that can be:
- Visualized
- Analyzed for timing and dependencies
- Optimized by schedulers
- Executed by automation systems

For complete examples, see the [Examples](examples.md) documentation.
