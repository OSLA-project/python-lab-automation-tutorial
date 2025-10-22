# Advanced Usage

This guide covers advanced features of Platform Status DB including experiments, process tracking, duration estimation, and integration with laboratory orchestration systems.

## Experiments and Processes

### Understanding the Process-Experiment Model

Platform Status DB uses a hierarchical model for tracking laboratory workflows:

- **Process**: A reusable workflow definition (template)
- **Experiment**: A specific execution instance of a process
- **ProcessStep**: Individual operations within an experiment

```
Process (Definition)
  └── Experiment 1 (Instance)
       ├── ProcessStep 1
       ├── ProcessStep 2
       └── ProcessStep 3
  └── Experiment 2 (Instance)
       ├── ProcessStep 1
       └── ProcessStep 2
```

### Creating a Process

A process represents a reusable workflow that can be executed multiple times:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()

# Define process source code or description
process_code = """
def cell_culture_assay(plate):
    # Step 1: Add reagent
    liquid_handler.dispense(plate, reagent='MTT', volume=50)

    # Step 2: Incubate
    incubator.incubate(plate, temperature=37, duration=4*3600)

    # Step 3: Read absorbance
    reader.read_absorbance(plate, wavelength=570)
"""

# Store process in database
process_uuid = db.add_process_to_db(
    name="Cell Viability Assay",
    src=process_code
)

print(f"Process created with UUID: {process_uuid}")
```

### Listing Available Processes

```python
processes = db.get_available_processes()

print("Available Processes:")
for name, uuid in processes:
    print(f"  {name}: {uuid}")
```

### Retrieving a Process

```python
process_uuid = "123e4567-e89b-12d3-a456-426614174000"
process_code = db.get_process(process_uuid)
print(process_code)
```

### Creating an Experiment

An experiment is a specific execution instance of a process:

```python
# Create experiment based on a process
experiment_uuid = db.create_experiment(process_uuid)
print(f"Experiment created with UUID: {experiment_uuid}")

# Now you can execute process steps and associate them with this experiment
```

## Process Step Tracking

### Recording Basic Process Steps

Track individual operations within an experiment:

```python
from laborchestrator import structures
from datetime import datetime

db = StatusDBImplementation()

# Get container
container = db.get_cont_info_by_barcode("PLATE001")

# Create process step
step = structures.ProcessStep(
    name="Read Absorbance",
    main_device=structures.DeviceInfo(name="PlateReader"),
    data={
        "fct": "absorbance",
        "method": "endpoint",
        "wavelength": 450,
        "reads": 3
    }
)

# Record start time
step.start = datetime.now()

# ... perform actual operation on physical device ...

# Record finish time and status
step.finish = datetime.now()
step.status = "completed"

# Save to database
db.safe_step_to_db(
    step=step,
    container_info=container,
    experiment_uuid=experiment_uuid
)
```

### Recording Movement Steps

Movement steps are tracked with additional details:

```python
from laborchestrator import structures
from datetime import datetime

# Create move step
move_step = structures.MoveStep(
    name="Move to Reader",
    main_device=structures.DeviceInfo(name="RoboticArm"),
    origin_device=structures.DeviceInfo(name="Hamilton_STAR"),
    target_device=structures.DeviceInfo(name="PlateReader"),
    origin_pos=0,
    destination_pos=0,
    data={"fct": "move"}
)

# Record execution
move_step.start = datetime.now()

# Perform movement in database
db.moved_container(
    source_device="Hamilton_STAR",
    source_pos=0,
    target_device="PlateReader",
    target_pos=0,
    barcode=container.barcode
)

move_step.finish = datetime.now()
move_step.status = "completed"

# Save to database
db.safe_step_to_db(
    step=move_step,
    container_info=container,
    experiment_uuid=experiment_uuid
)
```

### Complete Experiment Example

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures
from datetime import datetime
import time

db = StatusDBImplementation()

# 1. Define and store process
process_code = """
Cell culture screening workflow:
1. Prepare plates with cells
2. Add compounds
3. Incubate
4. Read absorbance
"""

process_uuid = db.add_process_to_db(
    name="Cell Screening",
    src=process_code
)

# 2. Create experiment instance
experiment_uuid = db.create_experiment(process_uuid)
print(f"Running experiment: {experiment_uuid}")

# 3. Add container to platform
container_info = structures.ContainerInfo(
    name="ScreenPlate_01",
    current_device="Hamilton_STAR",
    current_pos=0,
    barcode="SCREEN_001",
    lidded=True,
    filled=True
)
db.add_container(container_info)

# 4. Execute and log process steps

# Step 1: Add compounds
step1 = structures.ProcessStep(
    name="Add Compounds",
    main_device=structures.DeviceInfo(name="Hamilton_STAR"),
    data={"fct": "dispense", "volume": 50, "reagent": "compound_library"}
)
step1.start = datetime.now()
time.sleep(2)  # Simulate operation
step1.finish = datetime.now()
step1.status = "completed"
db.safe_step_to_db(step1, container_info, experiment_uuid)

# Step 2: Move to incubator
move_step = structures.MoveStep(
    name="Move to Incubator",
    main_device=structures.DeviceInfo(name="RoboticArm"),
    origin_device=structures.DeviceInfo(name="Hamilton_STAR"),
    target_device=structures.DeviceInfo(name="Incubator"),
    origin_pos=0,
    destination_pos=5,
    data={"fct": "move"}
)
move_step.start = datetime.now()
db.moved_container("Hamilton_STAR", 0, "Incubator", 5, "SCREEN_001")
container_info = db.get_cont_info_by_barcode("SCREEN_001")
move_step.finish = datetime.now()
move_step.status = "completed"
db.safe_step_to_db(move_step, container_info, experiment_uuid)

# Step 3: Incubate
step3 = structures.ProcessStep(
    name="Incubate",
    main_device=structures.DeviceInfo(name="Incubator"),
    data={"fct": "incubate", "temperature": 37, "duration": 14400}
)
step3.start = datetime.now()
time.sleep(2)  # Simulate operation
step3.finish = datetime.now()
step3.status = "completed"
db.safe_step_to_db(step3, container_info, experiment_uuid)

# Step 4: Move to reader
move_step2 = structures.MoveStep(
    name="Move to Reader",
    main_device=structures.DeviceInfo(name="RoboticArm"),
    origin_device=structures.DeviceInfo(name="Incubator"),
    target_device=structures.DeviceInfo(name="PlateReader"),
    origin_pos=5,
    destination_pos=0,
    data={"fct": "move"}
)
move_step2.start = datetime.now()
db.moved_container("Incubator", 5, "PlateReader", 0, "SCREEN_001")
container_info = db.get_cont_info_by_barcode("SCREEN_001")
move_step2.finish = datetime.now()
move_step2.status = "completed"
db.safe_step_to_db(move_step2, container_info, experiment_uuid)

# Step 5: Read absorbance
step5 = structures.ProcessStep(
    name="Read Absorbance",
    main_device=structures.DeviceInfo(name="PlateReader"),
    data={"fct": "absorbance", "wavelength": 570}
)
step5.start = datetime.now()
time.sleep(2)  # Simulate operation
step5.finish = datetime.now()
step5.status = "completed"
db.safe_step_to_db(step5, container_info, experiment_uuid)

print(f"Experiment {experiment_uuid} completed")
```

## Duration Estimation

Platform Status DB can estimate the duration of future operations based on historical data.

### Estimating Single Step Duration

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures

db = StatusDBImplementation()

# Define a step to estimate
step = structures.ProcessStep(
    name="Read Absorbance",
    main_device=structures.DeviceInfo(name="PlateReader"),
    data={"fct": "absorbance", "method": "endpoint_570nm"}
)

# Get duration estimate
estimated_duration = db.get_estimated_duration(step, confidence=0.95)

if estimated_duration:
    print(f"Estimated duration: {estimated_duration:.2f} seconds")
    print(f"                   : {estimated_duration/60:.2f} minutes")
else:
    print("No historical data available for this step")
```

### Estimating Multiple Steps

```python
from laborchestrator import structures

db = StatusDBImplementation()

# Define workflow steps
steps = [
    structures.ProcessStep(
        name="Dispense",
        main_device=structures.DeviceInfo(name="Hamilton_STAR"),
        data={"fct": "dispense", "volume": 50}
    ),
    structures.MoveStep(
        name="Move to Reader",
        main_device=structures.DeviceInfo(name="RoboticArm"),
        origin_device=structures.DeviceInfo(name="Hamilton_STAR"),
        target_device=structures.DeviceInfo(name="PlateReader"),
        origin_pos=0,
        destination_pos=0,
        data={"fct": "move"}
    ),
    structures.ProcessStep(
        name="Read",
        main_device=structures.DeviceInfo(name="PlateReader"),
        data={"fct": "absorbance", "wavelength": 450}
    ),
]

# Get estimates for all steps
durations = db.get_estimated_durations(steps, confidence=0.95)

total_estimated = 0
for i, (step, duration) in enumerate(zip(steps, durations)):
    if duration:
        print(f"Step {i+1} ({step.name}): {duration:.2f}s")
        total_estimated += duration
    else:
        print(f"Step {i+1} ({step.name}): No estimate")

print(f"\nTotal estimated time: {total_estimated:.2f}s ({total_estimated/60:.2f} min)")
```

### How Duration Estimation Works

The duration estimator analyzes historical `ProcessStep` records and matches based on:

1. **Function name** (`data['fct']`)
2. **Device types** (for movement steps)
3. **Method parameters** (for protocol steps)
4. **Arbitrary parameters** (fallback matching)

The estimator uses specialized "historians" for different step types:
- **MoveHistorian**: Analyzes movement patterns between device pairs
- **ProtocolHistorian**: Analyzes protocol executions with similar parameters
- **GeneralHistorian**: Fallback for arbitrary step types

**Example**: A movement from Hamilton_STAR to PlateReader will match historical movements between the same device pair and use the maximum observed duration.

## Querying Historical Data

### Query Process Steps

```python
from platform_status_db.job_logs.models import ProcessStep, MoveStep
from django.db.models import Avg, Min, Max, Count

# Get all process steps
all_steps = ProcessStep.objects.all()
print(f"Total process steps logged: {all_steps.count()}")

# Get steps for a specific device
device_steps = ProcessStep.objects.filter(
    executing_device__lara_name="PlateReader"
)
print(f"PlateReader operations: {device_steps.count()}")

# Calculate statistics
stats = device_steps.aggregate(
    avg_duration=Avg('finish') - Avg('start'),
    min_duration=Min('finish') - Min('start'),
    max_duration=Max('finish') - Max('start'),
    total=Count('id')
)
print(f"Statistics: {stats}")

# Get movement steps only
move_steps = MoveStep.objects.all()
for move in move_steps[:10]:  # First 10 movements
    duration = move.get_duration()
    print(f"{move.origin} -> {move.destination}: {duration:.2f}s")
```

### Query Experiments

```python
from platform_status_db.job_logs.models import Experiment, ProcessStep

# Get all experiments
experiments = Experiment.objects.all()

for exp in experiments:
    steps = ProcessStep.objects.filter(experiment=exp)
    print(f"\nExperiment {exp.experiment_uuid}")
    print(f"  Process: {exp.process.name}")
    print(f"  Steps: {steps.count()}")

    # Calculate total duration
    if steps.exists():
        first_step = steps.order_by('start').first()
        last_step = steps.order_by('-finish').first()
        if first_step and last_step:
            total_duration = (last_step.finish - first_step.start).total_seconds()
            print(f"  Duration: {total_duration:.2f}s ({total_duration/60:.2f} min)")
```

### Analyze Container History

```python
from platform_status_db.job_logs.models import Container, ProcessStep

barcode = "SCREEN_001"

# Get container
container = Container.objects.get(barcode=barcode, removed=False)

# Get all steps involving this container
steps = ProcessStep.objects.filter(container=container).order_by('start')

print(f"History for container {barcode}:")
print(f"  Starting position: {container.starting_pos}")
print(f"  Current position: {container.current_pos}")
print(f"\nProcess steps:")

for step in steps:
    duration = step.get_duration()
    print(f"  [{step.start.strftime('%H:%M:%S')}] {step.process_name} "
          f"on {step.executing_device.lara_name} ({duration:.2f}s)")
```

## Integration Patterns

### Integration with Laborchestrator

Platform Status DB is designed to work seamlessly with laborchestrator:

```python
from laborchestrator.orchestrator import Orchestrator
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

# Create orchestrator with status DB
db = StatusDBImplementation()
orchestrator = Orchestrator(
    config_file="lab_config.yaml",
    status_db=db
)

# The orchestrator will automatically:
# - Track container movements
# - Log process steps
# - Update container states
# - Estimate durations
```

### Custom Workflow Integration

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures
from datetime import datetime

class WorkflowManager:
    def __init__(self, db: StatusDBImplementation):
        self.db = db

    def run_assay_workflow(self, plate_barcode: str, assay_config: dict):
        # Create experiment
        process_uuid = self.db.add_process_to_db(
            name=assay_config['name'],
            src=str(assay_config)
        )
        experiment_uuid = self.db.create_experiment(process_uuid)

        # Get container
        container = self.db.get_cont_info_by_barcode(plate_barcode)

        # Execute workflow steps
        for step_config in assay_config['steps']:
            step = self._create_step(step_config, container)

            # Estimate duration
            estimated = self.db.get_estimated_duration(step)
            if estimated:
                print(f"Estimated: {estimated:.2f}s")

            # Execute step
            step.start = datetime.now()
            self._execute_step(step, container)
            step.finish = datetime.now()
            step.status = "completed"

            # Log to database
            self.db.safe_step_to_db(step, container, experiment_uuid)

            # Update container info if needed
            if isinstance(step, structures.MoveStep):
                container = self.db.get_cont_info_by_barcode(plate_barcode)

        return experiment_uuid

    def _create_step(self, config: dict, container) -> structures.ProcessStep:
        # Create step based on configuration
        pass

    def _execute_step(self, step: structures.ProcessStep, container):
        # Execute on physical devices
        pass

# Usage
db = StatusDBImplementation()
workflow_mgr = WorkflowManager(db)

assay_config = {
    'name': 'Enzyme Assay',
    'steps': [
        {'type': 'dispense', 'device': 'Hamilton_STAR', 'volume': 50},
        {'type': 'move', 'from': 'Hamilton_STAR', 'to': 'Incubator'},
        {'type': 'incubate', 'device': 'Incubator', 'temp': 37, 'time': 3600},
        {'type': 'move', 'from': 'Incubator', 'to': 'PlateReader'},
        {'type': 'read', 'device': 'PlateReader', 'wavelength': 450},
    ]
}

experiment_uuid = workflow_mgr.run_assay_workflow("PLATE001", assay_config)
```

### REST API Wrapper Example

Create a REST API around Platform Status DB:

```python
from flask import Flask, jsonify, request
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures

app = Flask(__name__)
db = StatusDBImplementation()

@app.route('/api/containers/<barcode>', methods=['GET'])
def get_container(barcode):
    container = db.get_cont_info_by_barcode(barcode)
    if container:
        return jsonify({
            'barcode': container.barcode,
            'device': container.current_device,
            'position': container.current_pos,
            'lidded': container.lidded
        })
    return jsonify({'error': 'Container not found'}), 404

@app.route('/api/containers/<barcode>/move', methods=['POST'])
def move_container(barcode):
    data = request.json
    db.moved_container(
        source_device=data['source_device'],
        source_pos=data['source_pos'],
        target_device=data['target_device'],
        target_pos=data['target_pos'],
        barcode=barcode
    )
    return jsonify({'status': 'success'})

@app.route('/api/devices/<device>/positions', methods=['GET'])
def get_positions(device):
    positions = db.get_all_positions(device)
    status = []
    for pos in positions:
        is_empty = db.position_empty(device, pos)
        container = None if is_empty else db.get_container_at_position(device, pos)
        status.append({
            'position': pos,
            'empty': is_empty,
            'container': container.barcode if container else None
        })
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Performance Optimization

### Bulk Operations

When adding many containers, use batch operations:

```python
from django.db import transaction
from platform_status_db.job_logs.models import Container, Position

# Use transaction for atomic operations
with transaction.atomic():
    for i in range(100):
        position = Position.objects.get(device__lara_name="Storage", slot_number=i)
        Container.objects.create(
            current_pos=position,
            starting_pos=position,
            barcode=f"BATCH_{i:03d}",
            lidded=True,
            labware_uuid="00000000-0000-0000-0000-000000000000",
            removed=False
        )
```

### Caching Container Locations

For frequently accessed containers:

```python
from functools import lru_cache
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

class CachedStatusDB:
    def __init__(self):
        self.db = StatusDBImplementation()

    @lru_cache(maxsize=1000)
    def get_container_location(self, barcode: str):
        container = self.db.get_cont_info_by_barcode(barcode)
        return (container.current_device, container.current_pos) if container else None

    def moved_container(self, *args, **kwargs):
        # Clear cache on movement
        self.get_container_location.cache_clear()
        return self.db.moved_container(*args, **kwargs)
```

### Database Connection Pooling

For production deployments with high concurrency, configure connection pooling in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'platform_status',
        'CONN_MAX_AGE': 600,  # Persistent connections
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

## Best Practices

### Process Step Logging

1. Always set both `start` and `finish` times
2. Use meaningful step names
3. Include relevant parameters in `data` dict
4. Set appropriate `status` values
5. Log steps immediately after completion

### Experiment Organization

1. Create processes for reusable workflows
2. Create new experiment for each run
3. Associate all steps with experiment UUID
4. Use descriptive process names
5. Store process source/description for reproducibility

### Duration Estimation

1. Log sufficient historical data (at least 10 samples per operation type)
2. Use consistent parameter structures for better matching
3. Handle `None` estimates gracefully
4. Add buffer time to estimates for scheduling
5. Update estimates periodically as more data accumulates

### Error Handling

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    db.safe_step_to_db(step, container, experiment_uuid)
except Exception as e:
    logging.error(f"Failed to log step: {e}")
    # Continue workflow or retry
```

## Next Steps

- **[API Reference](api-reference.md)**: Complete method documentation
- **[Managing Devices](managing-devices.md)**: Device setup and configuration
- **[Managing Containers](managing-containers.md)**: Container tracking basics
