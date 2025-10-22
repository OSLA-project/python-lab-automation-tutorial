# API Reference

This document provides a complete reference for the `StatusDBImplementation` class, which is the main API for interacting with Platform Status DB.

## StatusDBImplementation Class

The `StatusDBImplementation` class implements the `StatusDBInterface` from the laborchestrator package, providing database operations for laboratory automation platforms.

### Import

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
```

### Initialization

```python
db = StatusDBImplementation(db_path=None)
```

**Parameters**:
- `db_path` (str, optional): Path to the database directory. If not provided, uses the default Django database configuration.

**Returns**: Instance of `StatusDBImplementation`

**Example**:
```python
# Use default configuration
db = StatusDBImplementation()

# Use custom path
db = StatusDBImplementation(db_path="/path/to/custom/db")
```

---

## Laboratory Configuration Methods

### create_lab_from_config()

Creates laboratory devices and positions from a YAML configuration file.

```python
db.create_lab_from_config(lab_config_file_path: str)
```

**Parameters**:
- `lab_config_file_path` (str): Path to YAML configuration file

**Configuration File Format**:
```yaml
sila_servers:
  device_type_1:
    DeviceName1:
      capacity: 10
      type: "device_type"
  device_type_2:
    DeviceName2:
      capacity: 5
      type: "device_type"
```

**Example**:
```python
db.create_lab_from_config("lab_config.yaml")
```

**See also**: status_db_implementation.py:64

---

### wipe_lab()

Removes all devices and marks all containers as removed. Use with caution!

```python
db.wipe_lab()
```

**Returns**: None

**Example**:
```python
db.wipe_lab()  # Clears entire laboratory configuration
```

**See also**: status_db_implementation.py:57

---

### wipe_lara()

Alias for `wipe_lab()`. Deprecated, use `wipe_lab()` instead.

```python
db.wipe_lara()
```

---

## Device Methods

### get_all_positions()

Returns a list of all position indices for a given device.

```python
db.get_all_positions(device: str) -> List[int]
```

**Parameters**:
- `device` (str): Name of the device (lara_name)

**Returns**: List of integers representing position indices (0-indexed)

**Example**:
```python
positions = db.get_all_positions("Hamilton_STAR")
# Output: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

**See also**: status_db_implementation.py:78

---

### position_empty()

Checks if a specific position on a device is empty (no container or lid).

```python
db.position_empty(device: str, pos: int) -> bool
```

**Parameters**:
- `device` (str): Name of the device
- `pos` (int): Position index (0-indexed)

**Returns**: `True` if position is empty, `False` if occupied

**Example**:
```python
if db.position_empty("Hamilton_STAR", 5):
    print("Position is available")
else:
    print("Position is occupied")
```

**See also**: status_db_implementation.py:115

---

## Container Methods

### add_container()

Adds a new container to the database at its current position.

```python
db.add_container(cont: structures.ContainerInfo)
```

**Parameters**:
- `cont` (structures.ContainerInfo): Container information object from laborchestrator

**Returns**: None

**Example**:
```python
from laborchestrator import structures

container_info = structures.ContainerInfo(
    name="Plate001",
    current_device="Hamilton_STAR",
    current_pos=0,
    barcode="BC12345",
    lidded=True,
    filled=True
)
db.add_container(container_info)
```

**See also**: status_db_implementation.py:226

---

### get_container_at_position()

Retrieves container information at a specific position.

```python
db.get_container_at_position(device: str, pos: int) -> Optional[structures.ContainerInfo]
```

**Parameters**:
- `device` (str): Name of the device
- `pos` (int): Position index

**Returns**: `ContainerInfo` object if container exists, `None` if position is empty

**Example**:
```python
container = db.get_container_at_position("Hamilton_STAR", 5)
if container:
    print(f"Found: {container.barcode}")
else:
    print("Position is empty")
```

**See also**: status_db_implementation.py:128

---

### get_cont_info_by_barcode()

Retrieves container information by barcode.

```python
db.get_cont_info_by_barcode(barcode: str) -> structures.ContainerInfo
```

**Parameters**:
- `barcode` (str): Barcode identifier

**Returns**: `ContainerInfo` object

**Raises**: May raise exception if container not found

**Example**:
```python
container = db.get_cont_info_by_barcode("BC12345")
print(f"Container at: {container.current_device}[{container.current_pos}]")
```

**See also**: status_db_implementation.py:207

---

### moved_container()

Records a container movement from one position to another.

```python
db.moved_container(
    source_device: str,
    source_pos: int,
    target_device: str,
    target_pos: int,
    barcode: Optional[str] = None
)
```

**Parameters**:
- `source_device` (str): Source device name
- `source_pos` (int): Source position index
- `target_device` (str): Target device name
- `target_pos` (int): Target position index
- `barcode` (str, optional): Container barcode for verification (recommended if multiple containers at source)

**Returns**: None

**Example**:
```python
db.moved_container(
    source_device="Hamilton_STAR",
    source_pos=0,
    target_device="PlateReader",
    target_pos=0,
    barcode="BC12345"
)
```

**See also**: status_db_implementation.py:149

---

### remove_container()

Marks a container as removed from the platform (soft delete).

```python
db.remove_container(cont: structures.ContainerInfo)
```

**Parameters**:
- `cont` (structures.ContainerInfo): Container to remove

**Returns**: None

**Example**:
```python
container = db.get_cont_info_by_barcode("BC12345")
db.remove_container(container)
```

**See also**: status_db_implementation.py:244

---

### set_barcode()

Updates the barcode of a container.

```python
db.set_barcode(cont: structures.ContainerInfo)
```

**Parameters**:
- `cont` (structures.ContainerInfo): Container with updated barcode

**Returns**: None

**Example**:
```python
container = db.get_container_at_position("Hamilton_STAR", 0)
container.barcode = "NEW_BC001"
db.set_barcode(container)
```

**See also**: status_db_implementation.py:272

---

## Lid Management Methods

### unlidded_container()

Records that a container's lid has been removed and placed at a specific location.

```python
db.unlidded_container(
    cont_info: structures.ContainerInfo,
    lid_device: str,
    lid_pos: int
)
```

**Parameters**:
- `cont_info` (structures.ContainerInfo): Container being unlidded
- `lid_device` (str): Device where lid is placed
- `lid_pos` (int): Position where lid is placed

**Returns**: None

**Example**:
```python
container = db.get_cont_info_by_barcode("BC12345")
db.unlidded_container(
    cont_info=container,
    lid_device="Hamilton_STAR",
    lid_pos=10
)
```

**See also**: status_db_implementation.py:177

---

### lidded_container()

Records that a container's lid has been replaced.

```python
db.lidded_container(
    cont_info: structures.ContainerInfo,
    lid_device: Optional[str] = None,
    lid_pos: Optional[int] = None
)
```

**Parameters**:
- `cont_info` (structures.ContainerInfo): Container being lidded
- `lid_device` (str, optional): Device where lid was stored (for verification)
- `lid_pos` (int, optional): Position where lid was stored (for verification)

**Returns**: None

**Example**:
```python
container = db.get_cont_info_by_barcode("BC12345")
db.lidded_container(
    cont_info=container,
    lid_device="Hamilton_STAR",
    lid_pos=10
)
```

**See also**: status_db_implementation.py:189

---

### update_lid_position()

Updates the lid position information for a container.

```python
db.update_lid_position(cont: structures.ContainerInfo)
```

**Parameters**:
- `cont` (structures.ContainerInfo): Container with updated lid information

**Returns**: None

**Example**:
```python
container = db.get_cont_info_by_barcode("BC12345")
container.lid_site = ["LidStorage", 5]
container.lidded = False
db.update_lid_position(container)
```

**See also**: status_db_implementation.py:280

---

## Process and Experiment Methods

### add_process_to_db()

Adds a reusable process definition to the database.

```python
db.add_process_to_db(name: str, src: str) -> str
```

**Parameters**:
- `name` (str): Name of the process
- `src` (str): Source code or description of the process

**Returns**: UUID string for the process

**Example**:
```python
process_uuid = db.add_process_to_db(
    name="Standard Assay",
    src="def standard_assay():\n    ..."
)
print(f"Process UUID: {process_uuid}")
```

**See also**: status_db_implementation.py:83

---

### get_available_processes()

Returns a list of all available processes in the database.

```python
db.get_available_processes() -> List[Tuple[str, str]]
```

**Returns**: List of tuples containing (process_name, process_uuid)

**Example**:
```python
processes = db.get_available_processes()
for name, uuid in processes:
    print(f"{name}: {uuid}")
```

**See also**: status_db_implementation.py:92

---

### get_process()

Retrieves the source code/description of a process by UUID.

```python
db.get_process(process_id: str) -> str
```

**Parameters**:
- `process_id` (str): UUID of the process

**Returns**: Source code or description string

**Example**:
```python
process_code = db.get_process("123e4567-e89b-12d3-a456-426614174000")
print(process_code)
```

**See also**: status_db_implementation.py:102

---

### create_experiment()

Creates a new experiment instance based on a process.

```python
db.create_experiment(process_id: str) -> str
```

**Parameters**:
- `process_id` (str): UUID of the process to use

**Returns**: UUID string for the experiment

**Example**:
```python
experiment_uuid = db.create_experiment(process_uuid)
print(f"Experiment UUID: {experiment_uuid}")
```

**See also**: status_db_implementation.py:106

---

### safe_step_to_db()

Saves a completed process step to the database.

```python
db.safe_step_to_db(
    step: structures.ProcessStep,
    container_info: structures.ContainerInfo,
    experiment_uuid: str
)
```

**Parameters**:
- `step` (structures.ProcessStep): The completed process step (must have start and finish times)
- `container_info` (structures.ContainerInfo): Container involved in the step (can be None)
- `experiment_uuid` (str): UUID of the experiment

**Returns**: None

**Note**: For `MoveStep` instances, creates a `MoveStep` database record. For other steps, creates a `ProcessStep` record.

**Example**:
```python
from laborchestrator import structures
from datetime import datetime

step = structures.ProcessStep(
    name="Read Absorbance",
    main_device=structures.DeviceInfo(name="PlateReader"),
    data={"fct": "absorbance", "wavelength": 450}
)
step.start = datetime.now()
# ... perform operation ...
step.finish = datetime.now()
step.status = "completed"

db.safe_step_to_db(
    step=step,
    container_info=container,
    experiment_uuid=experiment_uuid
)
```

**See also**: status_db_implementation.py:368

---

## Duration Estimation Methods

### get_estimated_duration()

Estimates the duration of a process step based on historical data.

```python
db.get_estimated_duration(
    step: structures.ProcessStep,
    confidence: float = 0.95
) -> Optional[float]
```

**Parameters**:
- `step` (structures.ProcessStep): The step to estimate
- `confidence` (float): Confidence level (default 0.95)

**Returns**: Estimated duration in seconds, or `None` if no historical data available

**Example**:
```python
from laborchestrator import structures

step = structures.ProcessStep(
    name="Read Absorbance",
    main_device=structures.DeviceInfo(name="PlateReader"),
    data={"fct": "absorbance", "method": "450nm"}
)

duration = db.get_estimated_duration(step)
if duration:
    print(f"Estimated duration: {duration:.2f} seconds")
else:
    print("No historical data available")
```

**See also**: status_db_implementation.py:296

---

### get_estimated_durations()

Estimates durations for multiple process steps.

```python
db.get_estimated_durations(
    steps: List[structures.ProcessStep],
    confidence: float = 0.95
) -> List[Optional[float]]
```

**Parameters**:
- `steps` (List[structures.ProcessStep]): List of steps to estimate
- `confidence` (float): Confidence level (default 0.95)

**Returns**: List of estimated durations in seconds (None for steps without historical data)

**Example**:
```python
steps = [step1, step2, step3]
durations = db.get_estimated_durations(steps)

for i, duration in enumerate(durations):
    if duration:
        print(f"Step {i+1}: {duration:.2f}s")
    else:
        print(f"Step {i+1}: No estimate")
```

**See also**: status_db_implementation.py:322

---

## Certificate Management Methods

### write_server_certificate()

Stores an SSL/TLS certificate for a device.

```python
db.write_server_certificate(device_name: str, cert: str) -> None
```

**Parameters**:
- `device_name` (str): Name of the device
- `cert` (str): Certificate content (PEM format)

**Returns**: None

**Example**:
```python
with open("device_cert.pem", "r") as f:
    cert_content = f.read()

db.write_server_certificate("Hamilton_STAR", cert_content)
```

**See also**: status_db_implementation.py:405

---

### get_server_certificate()

Retrieves the SSL/TLS certificate for a device.

```python
db.get_server_certificate(device_name: str) -> str
```

**Parameters**:
- `device_name` (str): Name of the device

**Returns**: Certificate content string, or None if not set

**Example**:
```python
cert = db.get_server_certificate("Hamilton_STAR")
if cert:
    with open("retrieved_cert.pem", "w") as f:
        f.write(cert)
```

**See also**: status_db_implementation.py:414

---

## Data Models

### Device

Represents a laboratory device.

**Fields**:
- `lara_name` (CharField): Unique device identifier
- `num_slots` (IntegerField): Number of available positions
- `lara_uri` (URLField): Network endpoint
- `server_certificate` (TextField, nullable): SSL/TLS certificate

**See also**: job_logs/models.py:4

---

### Position

Represents a position/slot on a device.

**Fields**:
- `device` (ForeignKey): Parent device
- `slot_number` (IntegerField): Position index (0-indexed)
- `deep_well_suited` (BooleanField): Whether position supports deep-well plates

**See also**: job_logs/models.py:19

---

### Container

Represents a physical container (plate, tube, etc.).

**Fields**:
- `current_pos` (ForeignKey): Current position
- `starting_pos` (ForeignKey): Original position
- `barcode` (CharField): Barcode identifier
- `lidded` (BooleanField): Whether lid is on
- `lid_pos` (ForeignKey, nullable): Position of lid if removed
- `removed` (BooleanField): Whether removed from platform
- `labware_uuid` (UUIDField): Labware type identifier

**See also**: job_logs/models.py:29

---

### ProcessStep

Represents a process step execution.

**Fields**:
- `start` (DateTimeField): Start time
- `finish` (DateTimeField): Finish time
- `executing_device` (ForeignKey): Device that executed the step
- `container` (ForeignKey, nullable): Container involved
- `experiment` (ForeignKey, nullable): Parent experiment
- `process_name` (CharField): Name of the process
- `is_simulation` (BooleanField): Whether this was a simulation
- `parameters` (TextField): JSON string of parameters

**Methods**:
- `get_duration()`: Returns duration in seconds

**See also**: job_logs/models.py:58

---

### MoveStep

Specialized ProcessStep for container movements.

**Inherits from**: ProcessStep

**Additional Fields**:
- `origin` (ForeignKey): Source position
- `destination` (ForeignKey): Target position
- `lidded_before` (BooleanField): Lid status before move
- `lidded_after` (BooleanField): Lid status after move
- `barcode_read` (BooleanField): Whether barcode was read during move
- `uri_format` (CharField): URI format used

**See also**: job_logs/models.py:78

---

### Experiment

Represents an experiment execution.

**Fields**:
- `experiment_uuid` (UUIDField): Unique identifier
- `process` (ForeignKey): Process definition used

**See also**: job_logs/models.py:52

---

### Process

Represents a reusable process definition.

**Fields**:
- `name` (CharField): Process name
- `pythonlab_description` (TextField): Source code or description
- `process_uuid` (UUIDField): Unique identifier

**See also**: job_logs/models.py:45

---

## Error Handling

Most methods will log errors and warnings but may not raise exceptions. Check return values and logs for error details.

**Example error handling pattern**:
```python
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Perform operations
try:
    container = db.get_cont_info_by_barcode("BC12345")
    if container:
        db.moved_container("Device1", 0, "Device2", 0, "BC12345")
    else:
        logging.error("Container not found")
except Exception as e:
    logging.error(f"Operation failed: {e}")
```

---

## Next Steps

- **[Managing Devices](managing-devices.md)**: Device configuration guide
- **[Managing Containers](managing-containers.md)**: Container tracking guide
- **[Advanced Usage](advanced-usage.md)**: Experiments and duration estimation
