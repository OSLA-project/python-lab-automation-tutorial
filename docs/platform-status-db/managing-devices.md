# Managing Devices

Devices represent the physical equipment in your laboratory automation platform, such as robotic arms, plate readers, incubators, and liquid handlers. Each device has multiple positions (slots) where containers can be placed.

## Understanding Devices and Positions

### Device Model

A device in Platform Status DB represents a piece of laboratory equipment with the following properties:

- **lara_name** (string): Unique identifier for the device
- **num_slots** (integer): Number of available positions/slots
- **lara_uri** (URL): Network endpoint for the device (e.g., `http://192.168.1.100:50051`)
- **server_certificate** (text, optional): SSL/TLS certificate for secure communication

### Position Model

Each device has multiple positions (slots) where containers can be placed:

- **device**: Reference to the parent device
- **slot_number** (integer): Zero-indexed position number (0 to num_slots-1)
- **deep_well_suited** (boolean): Whether the position can accommodate deep-well plates

When you create a device, positions are typically created automatically based on the `num_slots` value.

## Adding Devices

### Method 1: Using a Configuration File (Recommended)

The recommended approach is to define your laboratory layout in a YAML configuration file:

```yaml
# lab_config.yaml
sila_servers:
  robotic_arms:
    Hamilton_STAR:
      capacity: 15
      type: "liquid_handler"
    UR5_Arm:
      capacity: 8
      type: "robot"

  readers:
    Tecan_Infinite:
      capacity: 1
      type: "plate_reader"
    Zebra_Barcode:
      capacity: 1
      type: "barcode_reader"

  incubators:
    Liconic_STX:
      capacity: 44
      type: "incubator"
    ThermoFisher_Shaker:
      capacity: 4
      type: "shaker_incubator"

  storage:
    ColdStorage:
      capacity: 100
      type: "refrigerator"
```

Load the configuration:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()
db.create_lab_from_config("lab_config.yaml")
```

**How it works**: The `create_lab_from_config` method parses the YAML file and creates a `Device` entry for each device listed. For each device, it automatically creates `Position` objects numbered from 0 to `capacity-1`.

**Note**: The configuration file structure follows the laborchestrator convention with a `sila_servers` top-level key, grouping devices by type (though the grouping is just for organization).

### Method 2: Using the Django Admin Interface

1. Navigate to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
2. Log in with your admin credentials
3. Under "JOB_LOGS", click on "Devices"
4. Click "Add Device" button

Fill in the form:
- **Lara name**: Enter a unique identifier (e.g., "Hamilton_STAR")
- **Num slots**: Enter the number of positions (e.g., 15)
- **Lara uri**: Enter the device endpoint (e.g., "http://192.168.1.50:50051")
- **Server certificate**: Leave blank unless using SSL/TLS

Click "Save" to create the device.

**Creating Positions**: After saving the device, you'll need to manually create positions:
1. In the admin interface, click on "Positions"
2. Click "Add Position" and select the device
3. Set the slot number (starting from 0)
4. Set "Deep well suited" if applicable
5. Repeat for all positions

### Method 3: Programmatic Creation

For integration into automated setup scripts:

```python
from platform_status_db.job_logs.models import Device, Position

# Create a device
device = Device.objects.create(
    lara_name="Hamilton_STAR",
    num_slots=15,
    lara_uri="http://192.168.1.50:50051"
)

# Create positions
for i in range(device.num_slots):
    Position.objects.create(
        device=device,
        slot_number=i,
        deep_well_suited=(i >= 10)  # Example: Last 5 positions support deep wells
    )

print(f"Created device {device.lara_name} with {device.num_slots} positions")
```

### Method 4: Using Django Shell

For interactive testing and debugging:

```bash
python src/platform_status_db/manage.py shell
```

```python
from platform_status_db.job_logs.models import Device, Position

# Create device
device = Device.objects.create(
    lara_name="Tecan_Infinite",
    num_slots=1,
    lara_uri="http://192.168.1.51:50051"
)

# Create position
Position.objects.create(device=device, slot_number=0, deep_well_suited=False)
```

## Querying Devices

### Get All Devices

```python
from platform_status_db.job_logs.models import Device

# Get all devices
all_devices = Device.objects.all()
for device in all_devices:
    print(f"{device.lara_name}: {device.num_slots} slots")
```

### Get a Specific Device

```python
# By name
device = Device.objects.get(lara_name="Hamilton_STAR")
print(f"URI: {device.lara_uri}")

# Handle device not found
try:
    device = Device.objects.get(lara_name="NonExistent")
except Device.DoesNotExist:
    print("Device not found")
```

### Get Device Positions

Using the StatusDBImplementation API:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()
positions = db.get_all_positions("Hamilton_STAR")
print(f"Available positions: {positions}")  # [0, 1, 2, 3, ...]
```

Using Django ORM:

```python
from platform_status_db.job_logs.models import Device, Position

device = Device.objects.get(lara_name="Hamilton_STAR")
positions = Position.objects.filter(device=device)

for pos in positions:
    print(f"Position {pos.slot_number}: deep_well={pos.deep_well_suited}")
```

### Check Position Availability

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Check if a position is empty
is_empty = db.position_empty(device="Hamilton_STAR", pos=5)
if is_empty:
    print("Position 5 is available")
else:
    print("Position 5 is occupied")
```

## Updating Devices

### Update Device Properties

```python
from platform_status_db.job_logs.models import Device

device = Device.objects.get(lara_name="Hamilton_STAR")
device.lara_uri = "http://192.168.1.60:50051"  # New IP address
device.save()
```

### Update via Admin Interface

1. Go to the admin interface at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
2. Click on "Devices" under JOB_LOGS
3. Click on the device name you want to edit
4. Modify the fields
5. Click "Save"

### Add More Positions to Existing Device

```python
from platform_status_db.job_logs.models import Device, Position

device = Device.objects.get(lara_name="Hamilton_STAR")

# Update capacity
old_capacity = device.num_slots
device.num_slots = 20  # Increase from 15 to 20
device.save()

# Add new positions
for i in range(old_capacity, device.num_slots):
    Position.objects.create(
        device=device,
        slot_number=i,
        deep_well_suited=False
    )
```

## Server Certificates

For secure communication with devices using SSL/TLS:

### Store a Certificate

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

with open("device_cert.pem", "r") as f:
    cert_content = f.read()

db.write_server_certificate("Hamilton_STAR", cert_content)
```

### Retrieve a Certificate

```python
cert = db.get_server_certificate("Hamilton_STAR")
if cert:
    with open("retrieved_cert.pem", "w") as f:
        f.write(cert)
```

## Removing Devices

### Soft Delete: Remove All Containers

If you want to clear all containers from a device without deleting it:

```python
from platform_status_db.job_logs.models import Container, Position

# Get all positions for the device
positions = Position.objects.filter(device__lara_name="Hamilton_STAR")

# Mark all containers at these positions as removed
for position in positions:
    containers = Container.objects.filter(current_pos=position, removed=False)
    for container in containers:
        container.removed = True
        container.save()
```

### Hard Delete: Remove Device Completely

**Warning**: This will delete all associated positions and container history!

```python
from platform_status_db.job_logs.models import Device

device = Device.objects.get(lara_name="Hamilton_STAR")
device.delete()  # Also deletes all associated positions (cascade)
```

### Wipe Entire Laboratory

To reset all devices and containers:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()
db.wipe_lab()  # Removes all devices and marks all containers as removed
```

## Best Practices

### Device Naming

- Use descriptive, unique names: `Hamilton_STAR_01`, not `Robot1`
- Include model information when you have multiple similar devices
- Use consistent naming conventions across your lab

### Capacity Planning

- Set `num_slots` to match the physical device capacity
- Don't overestimate capacity - it's better to be accurate
- Consider reserving positions for calibration or maintenance

### Position Numbering

- Positions are zero-indexed (0 to num_slots-1)
- Maintain consistency with device's native position numbering
- Document any position number mappings if device uses different indexing

### URI Configuration

- Use static IP addresses for devices, not DHCP
- Include the correct port number
- Test connectivity before adding to database
- Example formats:
  - HTTP: `http://192.168.1.50:50051`
  - HTTPS: `https://device.lab.local:443`
  - gRPC: `grpc://192.168.1.50:50052`

### Deep Well Support

- Mark positions as `deep_well_suited=True` only if they physically support it
- Consider height restrictions and compatibility
- Document which positions support special labware types

## Common Patterns

### Initialize Lab from Scratch

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

# Create clean database
db = StatusDBImplementation()
db.wipe_lab()

# Load from configuration
db.create_lab_from_config("production_lab_config.yaml")
```

### Audit Device Configuration

```python
from platform_status_db.job_logs.models import Device, Position

print("Laboratory Device Inventory")
print("=" * 50)

for device in Device.objects.all():
    positions = Position.objects.filter(device=device)
    deep_well_count = positions.filter(deep_well_suited=True).count()

    print(f"\n{device.lara_name}")
    print(f"  URI: {device.lara_uri}")
    print(f"  Total positions: {device.num_slots}")
    print(f"  Deep-well positions: {deep_well_count}")
    print(f"  Has certificate: {'Yes' if device.server_certificate else 'No'}")
```

### Check Device Occupancy

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()
device_name = "Hamilton_STAR"

positions = db.get_all_positions(device_name)
empty_positions = [pos for pos in positions if db.position_empty(device_name, pos)]
occupied_positions = [pos for pos in positions if not db.position_empty(device_name, pos)]

print(f"Device: {device_name}")
print(f"Empty positions: {empty_positions}")
print(f"Occupied positions: {occupied_positions}")
print(f"Utilization: {len(occupied_positions)}/{len(positions)} ({len(occupied_positions)/len(positions)*100:.1f}%)")
```

## Next Steps

- **[Managing Containers](managing-containers.md)**: Learn how to add and track containers
- **[API Reference](api-reference.md)**: Complete method reference
- **[Advanced Usage](advanced-usage.md)**: Experiments and process tracking
