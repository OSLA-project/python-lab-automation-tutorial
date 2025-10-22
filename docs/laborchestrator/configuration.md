# Configuration

This guide explains how to configure Lab Orchestrator and your laboratory resources.

## Overview

Lab Orchestrator uses YAML configuration files to define:
- Available laboratory devices
- Device capacities and constraints
- Device groupings by type
- Mapping to PythonLab resource types

## Lab Configuration YAML

### Structure

A lab configuration file has two main sections:

1. `description` - Human-readable description of the lab
2. `sila_servers` - Dictionary of device types and their instances
3. `pythonlab_translation` - Mapping from device types to PythonLab resource classes

### Example Configuration

```yaml
description: "Demo lab configuration"

sila_servers:
    incubators:
        Incubator1:
            capacity: 32
        Incubator2:
            capacity: 32
        Incubator3:
            capacity: 32
        Incubator4:
            capacity: 30

    plate_readers:
        Plate_Reader:
            capacity: 1
        Plate_Reader2:
            capacity: 1

    liquid_handlers:
        Liquid_Handler:
            capacity: 6
            process_capacity: 1
            allows_overlap: False

    movers:
        Mover:
            capacity: 1
            allows_overlap: False

    centrifuges:
        Centrifuge:
            min_capacity: 4
            capacity: 4
            allows_overlap: False

    storage:
        Carousel:
            capacity: 150
        Transfer:
            capacity: 4

pythonlab_translation:
    incubators: IncubatorServiceResource
    centrifuges: CentrifugeServiceResource
    movers: MoverServiceResource
    liquid_handlers: LiquidHandlerServiceResource
    plate_readers: PlateReaderServiceResource
    storage: LabwareStorageResource
```

## Device Types

### Incubators

Devices that maintain temperature and optionally other environmental conditions.

```yaml
incubators:
    IncubatorName:
        capacity: 32  # Number of containers it can hold
```

**Parameters**:
- `capacity` (required): Maximum number of containers

### Plate Readers

Devices for reading absorbance, fluorescence, or luminescence from microplates.

```yaml
plate_readers:
    PlateReaderName:
        capacity: 1  # Usually 1 plate at a time
```

**Parameters**:
- `capacity` (required): Number of simultaneous measurements

### Liquid Handlers

Automated liquid handling systems for pipetting operations.

```yaml
liquid_handlers:
    LiquidHandlerName:
        capacity: 6              # Deck positions
        process_capacity: 1      # Simultaneous processes
        allows_overlap: False    # Whether operations can overlap
```

**Parameters**:
- `capacity` (required): Number of container positions on deck
- `process_capacity` (optional): Number of simultaneous operations
- `allows_overlap` (optional): Whether multiple operations can overlap in time

### Movers

Robotic arms or transfer systems for moving containers between devices.

```yaml
movers:
    MoverName:
        capacity: 1              # Number of containers in gripper
        allows_overlap: False    # Whether moves can overlap
```

**Parameters**:
- `capacity` (required): Gripper capacity (usually 1)
- `allows_overlap` (optional): Concurrent operation support

### Centrifuges

Devices for separating samples by centrifugal force.

```yaml
centrifuges:
    CentrifugeName:
        min_capacity: 4          # Minimum containers for balance
        capacity: 4              # Maximum containers
        allows_overlap: False    # Whether runs can overlap
```

**Parameters**:
- `capacity` (required): Maximum number of containers
- `min_capacity` (optional): Minimum containers required (for balance)
- `allows_overlap` (optional): Concurrent operation support

### Storage

Storage locations like carousels, hotels, or transfer stations.

```yaml
storage:
    StorageName:
        capacity: 150  # Number of storage positions
```

**Parameters**:
- `capacity` (required): Number of storage positions

## PythonLab Translation

The `pythonlab_translation` section maps device type keys to PythonLab resource class names:

```yaml
pythonlab_translation:
    incubators: IncubatorServiceResource
    centrifuges: CentrifugeServiceResource
    movers: MoverServiceResource
    liquid_handlers: LiquidHandlerServiceResource
    plate_readers: PlateReaderServiceResource
    storage: LabwareStorageResource
```

This mapping allows PythonLab processes to reference the correct resource types.

## Loading Configuration

### Programmatically

```python
from laborchestrator.orchestrator_implementation import Orchestrator

orchestrator = Orchestrator()
orchestrator.add_lab_resources_from_file("path/to/lab_config.yml")
```

### Via ScheduleManager

```python
from laborchestrator.engine.schedule_manager import ScheduleManager

schedule_manager.configure_lab("path/to/lab_config.yml")
```

## Orchestrator Parameters

Beyond lab resources, you can configure orchestrator behavior:

### Initialization Parameters

```python
from laborchestrator.orchestrator_implementation import Orchestrator
from laborchestrator.engine.worker_interface import WorkerInterface

orchestrator = Orchestrator(
    reader: str = "PythonLab",  # Process reader type
    worker_type: Type[WorkerInterface] = WorkerInterface  # Worker implementation
)
```

### Runtime Parameters

```python
# Set scheduling time limits
orchestrator.set_parameter("time_limit_short", 2)  # Quick scheduling (seconds)
orchestrator.set_parameter("time_limit_long", 5)   # Full scheduling (seconds)

# Inject database interface
from laborchestrator.database_integration import StatusDBInterface
orchestrator.inject_db_interface(db_client)
```

## Schedule Manager Configuration

The ScheduleManager handles the core scheduling logic:

```python
from laborchestrator.engine.schedule_manager import ScheduleManager

# Create manager
schedule_manager = ScheduleManager(
    jssp=scheduling_instance,
    db_client=db_interface  # Optional
)

# Configure scheduling parameters
schedule_manager.time_limit_short = 2  # Quick rescheduling timeout
schedule_manager.time_limit_long = 5   # Full scheduling timeout
schedule_manager.max_iterations = 1000  # Max scheduling iterations

# Load lab configuration
schedule_manager.configure_lab("lab_config.yml")
```

## Environment Variables

Lab Orchestrator supports configuration via environment variables (defined in `.env` files):

```bash
# Example .env file
PYTHONUNBUFFERED=1
SILA_SERVER_IP=0.0.0.0
SILA_SERVER_PORT=50052
LAB_CONFIG_PATH=/path/to/lab_config.yml
```

## Docker Configuration

When running in Docker, configuration is managed via:

### docker-compose.yml

```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "50052:50052"
      - "8050:8050"  # Dash UI
    volumes:
      - ./lab_config.yml:/app/lab_config.yml
      - ./logs:/app/logs
```

### Dockerfile Environment

```dockerfile
ENV PYTHONUNBUFFERED=1
```

## Best Practices

### 1. Device Naming

Use descriptive, unique names:
- ✅ Good: `Incubator_Room1_A`, `Plate_Reader_EnVision`
- ❌ Bad: `Device1`, `Inc1`

### 2. Capacity Planning

Set realistic capacities based on physical constraints:
```yaml
liquid_handlers:
    Tecan_EVO:
        capacity: 6              # 6 deck positions
        process_capacity: 1      # One process at a time
        allows_overlap: False    # No concurrent operations
```

### 3. Storage Organization

Separate storage by function:
```yaml
storage:
    InputHotel:
        capacity: 50
    OutputHotel:
        capacity: 50
    TransferStation:
        capacity: 4
```

### 4. Versioning Configuration

Keep lab configurations in version control:
```bash
git add lab_configs/
git commit -m "feat: Add new plate reader to lab config"
```

### 5. Testing Configuration

Always test configuration changes:
```python
# Test configuration loading
orchestrator = Orchestrator()
success = orchestrator.add_lab_resources_from_file("new_config.yml")
assert success, "Configuration failed to load"

# Verify devices are registered
devices = orchestrator.get_available_devices()
assert "NewDevice" in devices
```

## Configuration Validation

Lab Orchestrator validates configurations when loading. Common errors:

### Missing Required Fields

```yaml
# ❌ Error: Missing capacity
incubators:
    Incubator1: {}

# ✅ Correct
incubators:
    Incubator1:
        capacity: 32
```

### Invalid Device Types

```yaml
# ❌ Error: Unknown device type
invalid_devices:
    SomeDevice:
        capacity: 10

# ✅ Correct: Use standard types
incubators:
    SomeDevice:
        capacity: 10
```

### Mismatched Translation

```yaml
# ❌ Error: Device type not in translation
sila_servers:
    new_device_type:
        Device1:
            capacity: 5

# pythonlab_translation doesn't include 'new_device_type'

# ✅ Correct: Add to translation
pythonlab_translation:
    new_device_type: NewDeviceServiceResource
```

## Advanced Configuration

### Custom Device Parameters

You can add custom parameters for specific devices:

```yaml
incubators:
    SpecialIncubator:
        capacity: 32
        max_temperature: 350  # Custom parameter
        has_shaking: true     # Custom parameter
```

Access custom parameters in your code:
```python
device_config = orchestrator.get_device_config("SpecialIncubator")
if device_config.get("has_shaking"):
    # Handle shaking incubator differently
    pass
```

### Multiple Configuration Files

For complex labs, split configuration:

```python
# Load base configuration
orchestrator.add_lab_resources_from_file("base_config.yml")

# Add additional devices
orchestrator.add_lab_resources_from_file("expansion_devices.yml")
```

## See Also

- [Writing Processes](writing-processes.md) - Use configured devices in processes
- [SiLA Integration](sila-integration.md) - Connect to physical devices
- [API Reference](api-reference.md) - Configuration method details
