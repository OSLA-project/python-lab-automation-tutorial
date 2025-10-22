# Managing Containers

Containers represent physical labware (plates, tubes, racks, etc.) that move through your laboratory automation platform. Platform Status DB tracks each container's location, barcode, lid status, and movement history.

## Understanding Containers

### Container Model

A container in Platform Status DB has the following properties:

- **current_pos**: Current position on the platform (device + slot number)
- **starting_pos**: Original position where the container was first placed
- **barcode**: Unique barcode identifier (string)
- **lidded**: Whether the container currently has its lid on (boolean)
- **lid_pos**: Location of the lid if currently removed (can be null)
- **removed**: Whether the container has been removed from the platform (boolean)
- **labware_uuid**: UUID identifier for the labware type

### ContainerInfo Structure

When working with the API, you'll use the `ContainerInfo` structure from laborchestrator:

```python
from laborchestrator import structures

container_info = structures.ContainerInfo(
    name="MyPlate",                    # Friendly name
    current_device="Hamilton_STAR",     # Device name
    current_pos=5,                      # Slot number (0-indexed)
    barcode="PLATE12345",               # Barcode identifier
    start_device="Hamilton_STAR",       # Starting device (optional)
    lidded=True,                        # Whether lid is on
    filled=True,                        # Whether container has contents
    lid_site=None                       # [device, pos] if lid is off, else None
)
```

## Adding Containers to the Database

### Basic Container Addition

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures

db = StatusDBImplementation()

# Create container info
container_info = structures.ContainerInfo(
    name="Plate001",
    current_device="Hamilton_STAR",
    current_pos=0,
    barcode="BC001",
    lidded=True,
    filled=True
)

# Add to database
db.add_container(container_info)
```

**What happens**:
- A `Container` record is created in the database
- Both `current_pos` and `starting_pos` are set to the same position
- The container is marked as not removed (`removed=False`)

### Adding Multiple Containers

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures

db = StatusDBImplementation()

# Add containers to different positions
containers = [
    ("PLATE001", "Hamilton_STAR", 0),
    ("PLATE002", "Hamilton_STAR", 1),
    ("PLATE003", "Incubator", 0),
    ("PLATE004", "Incubator", 1),
]

for barcode, device, pos in containers:
    container_info = structures.ContainerInfo(
        name=f"Sample_{barcode}",
        current_device=device,
        current_pos=pos,
        barcode=barcode,
        lidded=True,
        filled=True
    )
    db.add_container(container_info)
    print(f"Added {barcode} at {device}[{pos}]")
```

### Adding Containers via Django ORM

For direct database manipulation:

```python
from platform_status_db.job_logs.models import Container, Position

# Find the position
position = Position.objects.get(
    device__lara_name="Hamilton_STAR",
    slot_number=5
)

# Create container
container = Container.objects.create(
    current_pos=position,
    starting_pos=position,
    barcode="DIRECT_BC001",
    lidded=True,
    labware_uuid="00000000-0000-0000-0000-000000000000",
    removed=False
)
```

## Querying Containers

### Get Container by Barcode

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Get container information
container = db.get_cont_info_by_barcode("BC001")

if container:
    print(f"Container {container.barcode}")
    print(f"  Location: {container.current_device}[{container.current_pos}]")
    print(f"  Lidded: {container.lidded}")
    print(f"  Lid location: {container.lid_site}")
else:
    print("Container not found")
```

### Get Container at Position

```python
db = StatusDBImplementation()

# Check what's at a specific position
container = db.get_container_at_position(
    device="Hamilton_STAR",
    pos=5
)

if container:
    print(f"Found container: {container.barcode}")
else:
    print("Position is empty")
```

### Check if Position is Empty

```python
db = StatusDBImplementation()

if db.position_empty(device="Hamilton_STAR", pos=5):
    print("Position is available")
else:
    print("Position is occupied")
```

### Query All Containers

```python
from platform_status_db.job_logs.models import Container

# Get all active containers (not removed)
active_containers = Container.objects.filter(removed=False)

for container in active_containers:
    print(f"{container.barcode} at {container.current_pos}")

# Get all containers (including removed)
all_containers = Container.objects.all()
print(f"Total containers ever tracked: {all_containers.count()}")
```

### Query Containers by Device

```python
from platform_status_db.job_logs.models import Container

# Get all containers on a specific device
device_name = "Hamilton_STAR"
containers = Container.objects.filter(
    current_pos__device__lara_name=device_name,
    removed=False
)

print(f"Containers on {device_name}:")
for container in containers:
    print(f"  {container.barcode} at position {container.current_pos.slot_number}")
```

## Moving Containers

### Basic Movement

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Move container from one position to another
db.moved_container(
    source_device="Hamilton_STAR",
    source_pos=0,
    target_device="PlateReader",
    target_pos=0,
    barcode="BC001"  # Optional but recommended if multiple containers at source
)
```

**What happens**:
- The container's `current_pos` is updated to the new position
- The `starting_pos` remains unchanged (preserves origin)
- Movement is logged (when integrated with process tracking)

### Movement Without Barcode

If you're certain there's only one container at the source position:

```python
db.moved_container(
    source_device="Hamilton_STAR",
    source_pos=0,
    target_device="PlateReader",
    target_pos=0
    # barcode parameter omitted
)
```

**Warning**: If multiple containers are at the source position, this will raise an error. Always use barcode when possible.

### Complex Movement Workflow

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# 1. Check if source has a container
source_container = db.get_container_at_position("Hamilton_STAR", 0)
if not source_container:
    print("No container at source position")
    exit(1)

# 2. Check if destination is empty
if not db.position_empty("PlateReader", 0):
    print("Destination position is occupied")
    exit(1)

# 3. Perform the move
db.moved_container(
    source_device="Hamilton_STAR",
    source_pos=0,
    target_device="PlateReader",
    target_pos=0,
    barcode=source_container.barcode
)

# 4. Verify the move
moved_container = db.get_container_at_position("PlateReader", 0)
print(f"Successfully moved {moved_container.barcode}")
```

### Tracking Movement History

Movement history is captured through `ProcessStep` and `MoveStep` records when you log process steps:

```python
from laborchestrator import structures
from datetime import datetime

# Create a move step structure
move_step = structures.MoveStep(
    name="Move to reader",
    main_device=structures.DeviceInfo(name="Hamilton_STAR"),
    origin_device=structures.DeviceInfo(name="Hamilton_STAR"),
    target_device=structures.DeviceInfo(name="PlateReader"),
    origin_pos=0,
    destination_pos=0,
    data={"fct": "move"}
)

# Set timing
move_step.start = datetime.now()
# ... perform actual movement ...
move_step.finish = datetime.now()
move_step.status = "completed"

# Log to database
db.safe_step_to_db(
    step=move_step,
    container_info=source_container,
    experiment_uuid=experiment_uuid
)
```

## Managing Lids

### Remove Lid (Unlidding)

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Get container info
container = db.get_cont_info_by_barcode("BC001")

# Unlid and place lid at a position
db.unlidded_container(
    cont_info=container,
    lid_device="Hamilton_STAR",
    lid_pos=10  # Lid storage position
)

# Verify
updated_container = db.get_cont_info_by_barcode("BC001")
print(f"Lidded: {updated_container.lidded}")  # False
print(f"Lid location: {updated_container.lid_site}")  # ["Hamilton_STAR", 10]
```

### Replace Lid (Lidding)

```python
db = StatusDBImplementation()

# Get container info
container = db.get_cont_info_by_barcode("BC001")

# Put lid back on (optionally verify lid location)
db.lidded_container(
    cont_info=container,
    lid_device="Hamilton_STAR",  # Optional verification
    lid_pos=10                    # Optional verification
)

# Verify
updated_container = db.get_cont_info_by_barcode("BC001")
print(f"Lidded: {updated_container.lidded}")  # True
print(f"Lid location: {updated_container.lid_site}")  # None
```

### Update Lid Position

If the lid is moved while removed:

```python
db = StatusDBImplementation()

container = db.get_cont_info_by_barcode("BC001")

# Update lid position
container.lid_site = ["LidStorage", 0]
container.lidded = False

db.update_lid_position(container)
```

## Updating Container Information

### Update Barcode

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Get container
container = db.get_container_at_position("Hamilton_STAR", 0)

# Update barcode
container.barcode = "NEW_BC001"
db.set_barcode(container)
```

### Update Container via Django ORM

```python
from platform_status_db.job_logs.models import Container

# Get container
container = Container.objects.get(barcode="BC001", removed=False)

# Update properties
container.barcode = "UPDATED_BC001"
container.lidded = False
container.save()
```

## Removing Containers

### Soft Delete (Recommended)

Mark a container as removed without deleting its history:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Get container info
container = db.get_cont_info_by_barcode("BC001")

# Remove from platform
db.remove_container(container)

# Container is marked as removed=True but stays in database
# History is preserved for auditing
```

### Check Removed Status

```python
from platform_status_db.job_logs.models import Container

container = Container.objects.get(barcode="BC001")
if container.removed:
    print("Container has been removed from platform")
else:
    print("Container is active on platform")
```

### Hard Delete (Not Recommended)

Completely delete a container record:

```python
from platform_status_db.job_logs.models import Container

container = Container.objects.get(barcode="BC001")
container.delete()  # WARNING: Permanently deletes all history
```

### Remove All Containers from a Device

```python
from platform_status_db.job_logs.models import Container, Position

device_name = "Hamilton_STAR"
positions = Position.objects.filter(device__lara_name=device_name)

for position in positions:
    containers = Container.objects.filter(
        current_pos=position,
        removed=False
    )
    for container in containers:
        container.removed = True
        container.save()
```

## Common Workflows

### Workflow 1: Load Containers onto Platform

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures

db = StatusDBImplementation()

# Define containers to load
containers_to_load = [
    ("SAMPLE_01", "Hamilton_STAR", 0),
    ("SAMPLE_02", "Hamilton_STAR", 1),
    ("SAMPLE_03", "Hamilton_STAR", 2),
    ("CONTROL_01", "Hamilton_STAR", 3),
]

for barcode, device, pos in containers_to_load:
    # Check position is empty
    if not db.position_empty(device, pos):
        print(f"ERROR: Position {device}[{pos}] is occupied")
        continue

    # Add container
    container_info = structures.ContainerInfo(
        name=barcode,
        current_device=device,
        current_pos=pos,
        barcode=barcode,
        lidded=True,
        filled=True
    )
    db.add_container(container_info)
    print(f"Loaded {barcode} at {device}[{pos}]")
```

### Workflow 2: Container Processing Pipeline

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

barcode = "SAMPLE_01"

# 1. Start at liquid handler
container = db.get_cont_info_by_barcode(barcode)
print(f"Container at: {container.current_device}[{container.current_pos}]")

# 2. Move to plate reader
db.moved_container(
    source_device=container.current_device,
    source_pos=container.current_pos,
    target_device="PlateReader",
    target_pos=0,
    barcode=barcode
)
print("Moved to plate reader")

# 3. Move to incubator
db.moved_container(
    source_device="PlateReader",
    source_pos=0,
    target_device="Incubator",
    target_pos=5,
    barcode=barcode
)
print("Moved to incubator")

# 4. Return to liquid handler
db.moved_container(
    source_device="Incubator",
    source_pos=5,
    target_device="Hamilton_STAR",
    target_pos=10,
    barcode=barcode
)
print("Returned to liquid handler")

# 5. Unload from platform
container = db.get_cont_info_by_barcode(barcode)
db.remove_container(container)
print("Container removed from platform")
```

### Workflow 3: Lid Management During Processing

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

barcode = "SAMPLE_01"
container = db.get_cont_info_by_barcode(barcode)

# 1. Remove lid before processing
print(f"Container lidded: {container.lidded}")
db.unlidded_container(
    cont_info=container,
    lid_device="Hamilton_STAR",
    lid_pos=15  # Lid storage position
)
print("Lid removed and stored")

# 2. Perform processing (container remains unlidded)
# ... processing steps ...

# 3. Replace lid after processing
container = db.get_cont_info_by_barcode(barcode)  # Refresh
db.lidded_container(
    cont_info=container,
    lid_device="Hamilton_STAR",
    lid_pos=15
)
print("Lid replaced")
```

### Workflow 4: Platform Status Report

```python
from platform_status_db.job_logs.models import Container, Device

print("=== PLATFORM STATUS REPORT ===\n")

# Get all devices
devices = Device.objects.all()

for device in devices:
    print(f"\n{device.lara_name} ({device.num_slots} positions)")
    print("-" * 50)

    # Get containers on this device
    containers = Container.objects.filter(
        current_pos__device=device,
        removed=False
    )

    if not containers:
        print("  No containers")
    else:
        for container in containers:
            pos = container.current_pos.slot_number
            lid_status = "lidded" if container.lidded else "unlidded"
            print(f"  [{pos:2d}] {container.barcode} ({lid_status})")

            if not container.lidded and container.lid_pos:
                lid_loc = f"{container.lid_pos.device.lara_name}[{container.lid_pos.slot_number}]"
                print(f"       Lid at: {lid_loc}")

# Summary statistics
total_containers = Container.objects.filter(removed=False).count()
total_removed = Container.objects.filter(removed=True).count()

print(f"\n=== SUMMARY ===")
print(f"Active containers: {total_containers}")
print(f"Removed containers: {total_removed}")
print(f"Total tracked: {total_containers + total_removed}")
```

## Best Practices

### Barcode Management

- Always use unique barcodes for each container
- Use barcode parameter in `moved_container()` when multiple containers could be at source
- Validate barcodes before adding containers
- Maintain a barcode naming convention (e.g., `PROJ_SAMPLE_001`)

### Container Lifecycle

1. **Add**: Use `add_container()` when placing on platform
2. **Track**: Use `moved_container()` for all movements
3. **Remove**: Use `remove_container()` when unloading
4. **Query**: Use `get_cont_info_by_barcode()` for current status

### Error Handling

Always check positions and containers before operations:

```python
# Before adding
if not db.position_empty(device, pos):
    raise ValueError("Position occupied")

# Before moving
source_container = db.get_container_at_position(source_device, source_pos)
if not source_container:
    raise ValueError("No container at source")

if not db.position_empty(target_device, target_pos):
    raise ValueError("Target position occupied")
```

### Data Integrity

- Keep `starting_pos` unchanged (preserves container origin)
- Use soft delete (`removed=True`) instead of hard delete
- Log all movements with process steps for full audit trail
- Verify container location after movements in critical workflows

## Troubleshooting

### Container Not Found

```python
container = db.get_cont_info_by_barcode("BC001")
if not container:
    # Check if it was removed
    from platform_status_db.job_logs.models import Container
    try:
        cont = Container.objects.get(barcode="BC001")
        if cont.removed:
            print("Container was removed from platform")
    except Container.DoesNotExist:
        print("Container never existed in database")
```

### Multiple Containers at Position

```python
from platform_status_db.job_logs.models import Container, Position

position = Position.objects.get(device__lara_name="Hamilton_STAR", slot_number=0)
containers = Container.objects.filter(current_pos=position, removed=False)

if containers.count() > 1:
    print(f"ERROR: {containers.count()} containers at same position!")
    for cont in containers:
        print(f"  - {cont.barcode}")
```

## Next Steps

- **[API Reference](api-reference.md)**: Complete method reference
- **[Advanced Usage](advanced-usage.md)**: Experiments and process tracking
- **[Managing Devices](managing-devices.md)**: Device configuration and management
