# Writing Processes

This guide explains how to write laboratory workflows using the PythonLab process description language.

## Overview

Lab Orchestrator uses **PythonLab** as its process description language. PythonLab allows you to write laboratory workflows in Python, with resources representing lab devices and containers.

## Process Structure

A PythonLab process is a Python class that inherits from `PLProcess`:

```python
from pythonlab.process import PLProcess

class MyProcess(PLProcess):
    def __init__(self, priority=10):
        # Initialize process-specific variables
        super().__init__(priority=priority)

    def create_resources(self):
        # Define devices and containers
        pass

    def init_service_resources(self):
        # Initialize container positions
        super().init_service_resources()

    def process(self):
        # Define the workflow steps
        pass
```

### Key Methods

1. **`__init__`** - Initialize the process with parameters
   - Set the `priority` (lower number = higher priority)
   - Define process-specific variables

2. **`create_resources`** - Define lab resources
   - Create device resource objects
   - Create container (labware) objects
   - Set container properties

3. **`init_service_resources`** - Initialize resources
   - Set starting positions of containers
   - Call `super().init_service_resources()` first

4. **`process`** - Define the workflow
   - Write the sequence of operations
   - Use device methods to perform actions

## Resource Types

### Service Resources (Devices)

Import from `pythonlab.resources.services`:

```python
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.analysis import PlateReaderServiceResource
from pythonlab.resources.services.centrifugation import CentrifugeServiceResource
from pythonlab.resources.services.liquid_handling import LiquidHandlerServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
```

Create device resources in `create_resources()`:

```python
def create_resources(self):
    self.incubator = IncubatorServiceResource(proc=self, name="Incubator1")
    self.robot_arm = MoverServiceResource(proc=self, name="Mover")
    self.reader = PlateReaderServiceResource(proc=self, name="Plate_Reader")
    self.centrifuge = CentrifugeServiceResource(proc=self, name="Centrifuge")
    self.liquid_handler = LiquidHandlerServiceResource(proc=self, name="Liquid_Handler")
    self.storage = LabwareStorageResource(proc=self, name="Carousel", capacity=200)
```

**Parameters**:
- `proc` (required): Reference to the process (`self`)
- `name` (required): Name matching the lab configuration
- `capacity` (for storage): Number of positions

### Labware Resources (Containers)

Import from `pythonlab.resource`:

```python
from pythonlab.resource import LabwareResource as ContainerResource
```

Create containers in `create_resources()`:

```python
def create_resources(self):
    # Single container
    self.plate1 = ContainerResource(
        proc=self,
        name="plate_1",
        lidded=True,
        filled=True
    )

    # Multiple containers
    self.plates = [
        ContainerResource(
            proc=self,
            name=f"plate_{i}",
            lidded=True,
            filled=True
        )
        for i in range(4)
    ]
```

**Parameters**:
- `proc` (required): Reference to the process (`self`)
- `name` (required): Unique container name
- `lidded` (optional): Whether container has a lid (default: False)
- `filled` (optional): Whether container is filled (default: True)

**Container Properties**:
```python
# Set priority (lower = higher priority)
self.plate1.priority = 1

# Set starting position
self.plate1.set_start_position(self.storage, position=10)
```

## Device Operations

### Mover Operations

```python
# Move container to device
self.robot_arm.move(container, target_loc=self.incubator)

# Move with specific position
self.robot_arm.move(container, target_loc=self.storage, position=15)

# Move with lid control
self.robot_arm.move(container, target_loc=self.reader, lidded=False)

# Read barcode
self.robot_arm.read_barcode(container)
```

### Incubator Operations

```python
# Incubate
self.incubator.incubate(
    container,
    duration=120,      # seconds
    temperature=310    # Kelvin (37°C = 310K)
)

# Incubate with shaking
self.incubator.incubate(
    container,
    duration=3600,
    temperature=310,
    shaking_speed=200  # RPM
)
```

### Plate Reader Operations

```python
# Single read
self.reader.single_read(
    container,
    method='abs_600nm',  # Method name from device
    duration=60          # seconds
)

# Get absorbance value
absorbance = self.reader.get_absorbance(container)
```

### Centrifuge Operations

```python
# Centrifuge
self.centrifuge.centrifuge(
    container,
    duration=300,      # seconds
    speed=4000         # RPM
)

# Centrifuge multiple containers
for container in self.plates:
    self.centrifuge.centrifuge(container, duration=300, speed=4000)
```

### Liquid Handler Operations

```python
# Pipette operation
self.liquid_handler.pipette(
    container,
    method='transfer_protocol',  # Protocol name
    duration=600                  # seconds
)

# Custom liquid handling
self.liquid_handler.execute(
    containers=[self.source, self.dest],
    method='custom_protocol',
    duration=300
)
```

## Examples

### Example 1: Simple Incubation and Reading

```python
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.analysis import PlateReaderServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resource import LabwareResource as ContainerResource
from pythonlab.process import PLProcess


class IncReadProcess(PLProcess):
    def __init__(self, priority=10):
        self.num_plates = 2
        super().__init__(priority=priority)

    def create_resources(self):
        # Create devices
        self.storage = LabwareStorageResource(proc=self, name="Carousel", capacity=200)
        self.incubator = IncubatorServiceResource(proc=self, name="Incubator1")
        self.robot_arm = MoverServiceResource(proc=self, name="Mover")
        self.reader = PlateReaderServiceResource(proc=self, name="Plate_Reader")

        # Create containers
        self.plates = [
            ContainerResource(proc=self, name=f"plate_{i}", lidded=True, filled=True)
            for i in range(self.num_plates)
        ]
        self.plates[0].priority = 2  # Higher priority for first plate

    def init_service_resources(self):
        super().init_service_resources()
        # Set starting positions
        for i, plate in enumerate(self.plates):
            plate.set_start_position(self.storage, self.storage.next_free_position + i)

    def process(self):
        incubation_duration = 120  # 2 minutes
        temperature = 310  # 37°C in Kelvin

        # Incubate all plates
        for plate in self.plates:
            self.robot_arm.read_barcode(plate)
            self.robot_arm.move(plate, target_loc=self.incubator)
            self.incubator.incubate(plate, duration=incubation_duration, temperature=temperature)

        # Read first plate
        plate = self.plates[0]
        self.robot_arm.move(plate, target_loc=self.reader, lidded=False)
        self.reader.single_read(plate, method='abs_600nm', duration=60)

        # Return all plates to storage
        for i, plate in enumerate(self.plates):
            position = 30 + i if i > 0 else None
            self.robot_arm.move(plate, target_loc=self.storage, position=position, lidded=True)
```

### Example 2: Centrifugation Workflow

```python
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.centrifugation import CentrifugeServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resource import LabwareResource as ContainerResource
from pythonlab.process import PLProcess


class CentrifugeProcess(PLProcess):
    def __init__(self, priority=5):
        self.num_plates = 4
        super().__init__(priority=priority)

    def create_resources(self):
        self.storage = LabwareStorageResource(proc=self, name="Carousel", capacity=200)
        self.centrifuge = CentrifugeServiceResource(proc=self, name="Centrifuge")
        self.robot_arm = MoverServiceResource(proc=self, name="Mover")

        self.plates = [
            ContainerResource(proc=self, name=f"sample_{i}", lidded=True, filled=True)
            for i in range(self.num_plates)
        ]

    def init_service_resources(self):
        super().init_service_resources()
        for i, plate in enumerate(self.plates):
            plate.set_start_position(self.storage, i)

    def process(self):
        # Move all plates to centrifuge (must meet min_capacity)
        for plate in self.plates:
            self.robot_arm.move(plate, target_loc=self.centrifuge)
            self.centrifuge.centrifuge(plate, duration=300, speed=4000)

        # Return to storage
        for plate in self.plates:
            self.robot_arm.move(plate, target_loc=self.storage, lidded=True)
```

### Example 3: Conditional Workflow

```python
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.analysis import PlateReaderServiceResource
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resource import LabwareResource as ContainerResource
from pythonlab.process import PLProcess


class ConditionalProcess(PLProcess):
    def __init__(self, priority=10):
        super().__init__(priority=priority)

    def create_resources(self):
        self.storage = LabwareStorageResource(proc=self, name="Carousel", capacity=200)
        self.incubator = IncubatorServiceResource(proc=self, name="Incubator1")
        self.reader = PlateReaderServiceResource(proc=self, name="Plate_Reader")
        self.robot_arm = MoverServiceResource(proc=self, name="Mover")

        self.plate = ContainerResource(proc=self, name="sample", lidded=True, filled=True)

    def init_service_resources(self):
        super().init_service_resources()
        self.plate.set_start_position(self.storage, 0)

    def process(self):
        # Initial incubation
        self.robot_arm.move(self.plate, target_loc=self.incubator)
        self.incubator.incubate(self.plate, duration=120, temperature=310)

        # Check absorbance
        self.robot_arm.move(self.plate, target_loc=self.reader, lidded=False)
        self.reader.single_read(self.plate, method='abs_600nm', duration=60)

        absorbance = self.reader.get_absorbance(self.plate)

        # Conditional: if absorbance is low, incubate more
        if absorbance < 0.5:
            self.robot_arm.move(self.plate, target_loc=self.incubator, lidded=True)
            self.incubator.incubate(self.plate, duration=180, temperature=310)

            # Read again
            self.robot_arm.move(self.plate, target_loc=self.reader, lidded=False)
            self.reader.single_read(self.plate, method='abs_600nm', duration=60)

        # Return to storage
        self.robot_arm.move(self.plate, target_loc=self.storage, lidded=True)
```

### Example 4: Multi-Device Workflow

```python
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.analysis import PlateReaderServiceResource
from pythonlab.resources.services.liquid_handling import LiquidHandlerServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource
from pythonlab.resource import LabwareResource as ContainerResource
from pythonlab.process import PLProcess


class ComplexWorkflow(PLProcess):
    def __init__(self, priority=10):
        super().__init__(priority=priority)

    def create_resources(self):
        # Devices
        self.storage = LabwareStorageResource(proc=self, name="Carousel", capacity=200)
        self.incubator = IncubatorServiceResource(proc=self, name="Incubator1")
        self.reader = PlateReaderServiceResource(proc=self, name="Plate_Reader")
        self.liquid_handler = LiquidHandlerServiceResource(proc=self, name="Liquid_Handler")
        self.robot_arm = MoverServiceResource(proc=self, name="Mover")

        # Containers
        self.culture_plate = ContainerResource(proc=self, name="culture", lidded=True, filled=True)
        self.assay_plate = ContainerResource(proc=self, name="assay", lidded=True, filled=False)

    def init_service_resources(self):
        super().init_service_resources()
        self.culture_plate.set_start_position(self.storage, 0)
        self.assay_plate.set_start_position(self.storage, 1)

    def process(self):
        # Step 1: Grow culture
        self.robot_arm.move(self.culture_plate, target_loc=self.incubator)
        self.incubator.incubate(self.culture_plate, duration=7200, temperature=310)

        # Step 2: Transfer samples to assay plate
        self.robot_arm.move(self.culture_plate, target_loc=self.liquid_handler, lidded=False)
        self.robot_arm.move(self.assay_plate, target_loc=self.liquid_handler, lidded=False)
        self.liquid_handler.pipette(
            self.culture_plate,
            method='transfer_protocol',
            duration=300
        )

        # Step 3: Read assay plate
        self.robot_arm.move(self.assay_plate, target_loc=self.reader, lidded=False)
        self.reader.single_read(self.assay_plate, method='fluorescence', duration=120)

        # Step 4: Return plates
        self.robot_arm.move(self.culture_plate, target_loc=self.storage, lidded=True)
        self.robot_arm.move(self.assay_plate, target_loc=self.storage, lidded=True)
```

## Best Practices

### 1. Use Descriptive Names

```python
# ✅ Good
self.culture_plate = ContainerResource(proc=self, name="culture_plate_1")
self.growth_incubator = IncubatorServiceResource(proc=self, name="Incubator1")

# ❌ Bad
self.c1 = ContainerResource(proc=self, name="c1")
self.inc = IncubatorServiceResource(proc=self, name="Incubator1")
```

### 2. Set Container Priorities

For time-sensitive containers, set higher priority (lower number):

```python
self.urgent_sample.priority = 1
self.normal_sample.priority = 10
```

### 3. Initialize Positions Carefully

Always call `super().init_service_resources()` first:

```python
def init_service_resources(self):
    super().init_service_resources()  # Call this first
    self.plate.set_start_position(self.storage, 0)
```

### 4. Handle Lids Correctly

Remove lids before reading or liquid handling:

```python
# Before reading
self.robot_arm.move(plate, target_loc=self.reader, lidded=False)

# After reading, return with lid
self.robot_arm.move(plate, target_loc=self.storage, lidded=True)
```

### 5. Use Meaningful Durations

Use seconds for all durations:

```python
# ✅ Good
incubation_duration = 7200  # 2 hours in seconds

# ❌ Bad
incubation_duration = 120  # Unclear if minutes or seconds
```

### 6. Comment Complex Logic

```python
def process(self):
    # Phase 1: Initial growth (overnight)
    self.incubator.incubate(self.culture, duration=28800, temperature=310)

    # Phase 2: Check growth via OD600
    self.reader.single_read(self.culture, method='abs_600nm', duration=60)
    od = self.reader.get_absorbance(self.culture)

    # Phase 3: Conditional processing based on growth
    if od > 0.6:
        # Sufficient growth, proceed with assay
        self.liquid_handler.pipette(self.culture, method='dilution', duration=300)
```

## Adding Processes to Orchestrator

### From Python File

```python
orchestrator.add_process(
    file_path="path/to/process.py",
    name="MyProcess"
)
```

### From Process Object

```python
from my_processes import IncReadProcess

process = IncReadProcess(priority=5)
orchestrator.add_process(
    process_object=process,
    name="IncubationWorkflow"
)
```

### From String Description

```python
process_code = '''
from pythonlab.process import PLProcess
# ... process definition
'''

orchestrator.add_process(
    description=process_code,
    name="DynamicProcess"
)
```

### With Delay

Start process after a delay:

```python
orchestrator.add_process(
    file_path="process.py",
    name="DelayedProcess",
    delay=60  # Start in 60 minutes
)
```

## Running Processes

```python
# Add processes
orchestrator.add_process(file_path="process1.py", name="Process1")
orchestrator.add_process(file_path="process2.py", name="Process2")

# Start specific processes
orchestrator.start_processes(["Process1", "Process2"])

# Start all processes
orchestrator.start_processes(list(orchestrator.processes.keys()))

# Check status
for name, process in orchestrator.processes.items():
    print(f"{name}: {process.state}")
```

## Troubleshooting

### Common Errors

**Error**: `Device not found: Incubator1`

**Solution**: Ensure device name matches lab configuration YAML

**Error**: `Container position out of bounds`

**Solution**: Check storage capacity in lab configuration

**Error**: `Minimum capacity not met for centrifuge`

**Solution**: Ensure enough containers are loaded (check `min_capacity`)

## See Also

- [Configuration](configuration.md) - Set up lab devices
- [API Reference](api-reference.md) - Detailed method documentation
- [SiLA Integration](sila-integration.md) - Connect to physical devices
