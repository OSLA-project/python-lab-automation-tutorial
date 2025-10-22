# Quick Start Guide: Writing Processes

This is a condensed quick-start guide. For detailed information, see [writing_processes](writing_processes.md).

## The 3 Required Methods

Every PLProcess must implement:

```python
from pythonlab.process import PLProcess

class YourProcess(PLProcess):

    def create_resources(self):
        """Create all devices and labware"""
        # Create ServiceResources (devices)
        # Create LabwareResources (containers)
        # Resources auto-register with the process

    def init_service_resources(self):
        """Initialize devices and set starting positions"""
        super().init_service_resources()  # Always call this!
        # Set labware starting positions

    def process(self):
        """Define the workflow"""
        # Call methods on ServiceResources
        # This gets parsed into a workflow graph
```

## Minimal Complete Example

```python
from pythonlab.process import PLProcess
from pythonlab.resource import ServiceResource, LabwareResource
from pythonlab.pythonlab_reader import PLProcessReader


# 1. Define a custom service (device)
class MyIncubator(ServiceResource):
    def incubate(self, labware, duration, temperature, **kwargs):
        kwargs.update(dict(
            fct='incubate',           # REQUIRED: operation name
            duration=duration,         # REQUIRED: time in seconds
            temperature=temperature    # Include all parameters
        ))
        self.proc.add_process_step(self, [labware], **kwargs)


# 2. Define your process
class SimpleProcess(PLProcess):

    def create_resources(self):
        # Create device
        self.incubator = MyIncubator(proc=self, name="Incubator1")
        # Create labware
        self.plate = LabwareResource(proc=self, name="Plate1")

    def init_service_resources(self):
        super().init_service_resources()  # Don't forget this!

    def process(self):
        # Define workflow
        self.incubator.incubate(
            self.plate,
            duration=3600,    # 1 hour
            temperature=310   # 37°C in Kelvin
        )


# 3. Parse and use
simulator = PLProcessReader.parse_process(SimpleProcess())
simulator.visualize_workflow_graph()
print(f"Nodes: {simulator.workflow.number_of_nodes()}")
```

## ServiceResource Pattern

When creating device operations:

```python
class MyDevice(ServiceResource):
    def my_operation(self, labware: LabwareResource, param1, **kwargs):
        # 1. Update kwargs with metadata
        kwargs.update(dict(
            fct='my_operation',      # Operation name (REQUIRED)
            duration=60,             # Duration in seconds (REQUIRED)
            param1=param1            # Include all parameters
        ))

        # 2. Call add_process_step
        self.proc.add_process_step(
            self,                    # The device
            [labware],               # List of containers
            **kwargs
        )

        # 3. Optional: return for runtime variable
        # If this operation produces data that will be used in
        # decisions, add a return statement here
```

## Runtime Variables and Decisions

### Creating Runtime Variables

Variables from device operations are "runtime variables":

```python
def process(self):
    # This creates a runtime variable
    measurement = self.reader.measure(self.plate, wavelengths=[600])

    # Computations using runtime variables create computation nodes
    avg = self.calculate_average(measurement)

    # Decisions using runtime variables create if-nodes
    if avg > 0.6:
        # Both branches will be in the graph
        self.mover.move(self.plate, target_loc=self.storage)
    else:
        self.incubator.incubate(self.plate, duration=3600, temperature=310)
```

### Compile-Time vs Runtime

```python
# COMPILE-TIME (evaluated during parsing)
plate_count = 3
if plate_count > 2:
    # Only this branch will be in graph
    self.process_three_plates()

# RUNTIME (both branches in graph)
measurement = self.reader.measure(plate)
if measurement > 0.6:
    # Both branches will be in graph
    self.continue_growth()
else:
    self.harvest()
```

## Control Flow

### For Loops (Unrolled During Parsing)

```python
# Valid - known list
for plate in self.plates:
    self.incubator.incubate(plate, duration=3600, temperature=310)

# Valid - known range
for i in range(5):
    self.process_plate(self.plates[i])

# INVALID - runtime variable
count = self.counter.count_samples()
for i in range(count):  # ERROR: Can't iterate over runtime variable
    self.process_sample(i)
```

### If-Elif-Else

```python
# Compile-time
if self.plate_type == "96-well":
    volume = 200
elif self.plate_type == "384-well":
    volume = 50

# Runtime
measurement = self.reader.measure(plate)
if measurement < 0.3:
    self.incubate_long()
elif measurement < 0.7:
    self.incubate_short()
else:
    self.harvest()
```

## Common Patterns

### Movement Between Devices

```python
from pythonlab.resources.services.moving import MoverServiceResource

def create_resources(self):
    self.mover = MoverServiceResource(proc=self, name="RobotArm")
    self.incubator = IncubatorServiceResource(proc=self, name="Incubator")
    self.reader = PlateReaderServiceResource(proc=self, name="Reader")
    self.plate = LabwareResource(proc=self, name="Plate1", lidded=True)

def process(self):
    # Move to incubator (with lid)
    self.mover.move(self.plate, target_loc=self.incubator, lidded=True)

    # Incubate
    self.incubator.incubate(self.plate, duration=3600, temperature=310)

    # Move to reader (remove lid)
    self.mover.move(self.plate, target_loc=self.reader, lidded=False)

    # Measure
    self.reader.single_read(self.plate, wavelengths=[600])
```

### Setting Starting Positions

```python
def init_service_resources(self):
    super().init_service_resources()  # Always call first!

    # Set where labware starts
    self.plate.set_start_position(self.storage, position=1)

    # Or use auto-incrementing positions
    for plate in self.plates:
        plate.set_start_position(
            self.storage,
            self.storage.next_free_position
        )
```

### Multiple Labware Operations

```python
from pythonlab.resources.services.centrifugation import CentrifugeServiceResource

def create_resources(self):
    self.centrifuge = CentrifugeServiceResource(proc=self, name="Centrifuge")
    self.plates = [LabwareResource(proc=self, name=f"Plate_{i}")
                   for i in range(3)]

def process(self):
    # Centrifuge multiple plates together
    self.centrifuge.centrifuge(
        labwares=self.plates,      # List of labware
        duration=600,
        rpm=4000
    )
```

### Barcode Scanning

```python
def process(self):
    # Scan all plates
    for plate in self.plates:
        self.mover.read_barcode(plate)
```

## Built-in Services Quick Reference

```python
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.analysis import PlateReaderServiceResource
from pythonlab.resources.services.centrifugation import CentrifugeServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource

# Incubator
self.incubator.incubate(plate, duration=3600, temperature=310, shaking_frequency=200)

# Mover
self.mover.move(plate, target_loc=self.incubator, lidded=True)
self.mover.read_barcode(plate)

# Plate Reader
abs_data = self.reader.single_read(plate, wavelengths=[600, 660])
kinetic = self.reader.run_kinetic(plate, wavelength=600, interval=60, reads=10)

# Centrifuge
self.centrifuge.centrifuge(labwares=[plate1, plate2], duration=600, rpm=4000)

# Storage
self.storage.store(plate, position=5)
self.storage.eject(plate)
```

See [builtin_services.md](builtin_services.md) for complete reference.

## Common Mistakes to Avoid

### 1. Forgetting super() in init_service_resources()

```python
# WRONG
def init_service_resources(self):
    self.plate.set_start_position(self.storage, position=1)

# CORRECT
def init_service_resources(self):
    super().init_service_resources()  # Always call this!
    self.plate.set_start_position(self.storage, position=1)
```

### 2. Missing 'fct' or 'duration' in ServiceResource

```python
# WRONG
def my_operation(self, labware, **kwargs):
    self.proc.add_process_step(self, [labware], **kwargs)

# CORRECT
def my_operation(self, labware, **kwargs):
    kwargs.update(dict(
        fct='my_operation',
        duration=60
    ))
    self.proc.add_process_step(self, [labware], **kwargs)
```

### 3. Creating Resources in process()

```python
# WRONG
def process(self):
    new_plate = LabwareResource(proc=self, name="New")  # Don't do this!

# CORRECT
def create_resources(self):
    self.all_plates = [...]  # Create all resources here

def process(self):
    for plate in self.all_plates:  # Just use them
        ...
```

### 4. Forgetting to Pass Labware as List

```python
# WRONG
self.proc.add_process_step(self, labware, **kwargs)

# CORRECT
self.proc.add_process_step(self, [labware], **kwargs)
```

## Parsing and Using

```python
from pythonlab.pythonlab_reader import PLProcessReader

# Parse from instance
simulator = PLProcessReader.parse_process(MyProcess())

# Parse from file
simulator = PLProcessReader.parse_process_from_file_path("my_process.py")

# Parse from source code string
with open("my_process.py") as f:
    source = f.read()
simulator = PLProcessReader.parse_process_from_source_code(source)

# Visualize
simulator.visualize_workflow_graph()

# Access graph
graph = simulator.workflow  # NetworkX DiGraph

# Get nodes
for node_id, data in graph.nodes(data=True):
    print(f"{node_id}: {data['type']} - {data['name']}")

# Get edges
for source, target, data in graph.edges(data=True):
    print(f"{source} -> {target}")
```

## Next Steps

1. **Try the minimal example** above
2. **Read complete examples** in [examples.md](examples.md)
3. **Study the detailed guide** in [writing_processes.md](writing_processes.md)
4. **Explore built-in services** in [builtin_services.md](builtin_services.md)
5. **Understand workflow graphs** in [workflow_graph.md](workflow_graph.md)

## Complete Template

Copy and adapt this template:

```python
from pythonlab.process import PLProcess
from pythonlab.resource import ServiceResource, LabwareResource
from pythonlab.pythonlab_reader import PLProcessReader


class MyCustomService(ServiceResource):
    """Your custom device."""

    def my_operation(self, labware: LabwareResource, param1, **kwargs):
        kwargs.update(dict(
            fct='my_operation',
            duration=60,
            param1=param1
        ))
        self.proc.add_process_step(self, [labware], **kwargs)


class MyProcess(PLProcess):
    """Your process description."""

    def create_resources(self):
        # Create devices
        self.device = MyCustomService(proc=self, name="Device1")

        # Create labware
        self.labware = LabwareResource(proc=self, name="Container1")

    def init_service_resources(self):
        super().init_service_resources()

        # Set starting positions
        self.labware.set_start_position(self.device, position=0)

    def process(self):
        # Define workflow
        self.device.my_operation(self.labware, param1=100)


# Parse and use
if __name__ == "__main__":
    simulator = PLProcessReader.parse_process(MyProcess())
    simulator.visualize_workflow_graph()
    print(f"Workflow has {simulator.workflow.number_of_nodes()} nodes")
```

## Help and Documentation

- **[Full Documentation Index](./INDEX.md)**
- **[Detailed Guide](writing_processes.md)**
- **[Examples](examples.md)**
- **[Built-in Services](builtin_services.md)**
- **[Workflow Graph](workflow_graph.md)**
- **[Main README](../README.md)**
