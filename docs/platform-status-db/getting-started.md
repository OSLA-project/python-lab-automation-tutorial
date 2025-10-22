# Getting Started

This guide will help you install and set up Platform Status DB for your laboratory automation system.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (for cloning the repository)

### Install from GitLab

1. Clone the repository:

```bash
git clone https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git
cd platform_status_db
```

2. Install the package:

```bash
pip install -e .
```

3. Install the laborchestrator dependency:

```bash
pip install --index-url https://gitlab.com/api/v4/projects/70366855/packages/pypi/simple "laborchestrator<0.3"
```

### Verify Installation

Check that the installation was successful:

```bash
python -c "from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation; print('Installation successful!')"
```

## Initial Setup

### 1. Initialize the Database

Apply Django migrations to create the database schema:

```bash
python src/platform_status_db/manage.py makemigrations
python src/platform_status_db/manage.py migrate
```

This creates a SQLite database file at `src/platform_status_db/db.sqlite3`.

### 2. Create an Admin User

To access the Django admin interface, create a superuser:

```bash
python src/platform_status_db/manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email address
- Password (entered twice)

### 3. Start the Server

Start the development server:

```bash
run_db_server
```

Or alternatively:

```bash
python src/platform_status_db/manage.py runserver
```

The server will start on `http://127.0.0.1:8000/` by default.

## Accessing the Web Interface

### Admin Interface

Navigate to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in with the superuser credentials you created.

From the admin interface, you can:
- Add and manage devices
- View containers and their locations
- Browse process steps and experiments
- Manually edit database records

### Job Logs Interface

Navigate to [http://127.0.0.1:8000/job_logs/](http://127.0.0.1:8000/job_logs/) to view:
- Device list and status
- Container locations
- Process history
- Movement tracking

## Configuring Your Laboratory

### Option 1: Using a Configuration File (Recommended)

Create a YAML configuration file describing your laboratory setup:

```yaml
# lab_config.yaml
sila_servers:
  robotic_arms:
    RoboticArm1:
      capacity: 10
      type: "robot"
    RoboticArm2:
      capacity: 8
      type: "robot"

  readers:
    PlateReader1:
      capacity: 1
      type: "reader"
    BarcodeReader:
      capacity: 1
      type: "reader"

  incubators:
    Incubator1:
      capacity: 20
      type: "incubator"
```

Then load it programmatically:

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

db = StatusDBImplementation()
db.create_lab_from_config("lab_config.yaml")
```

### Option 2: Manual Configuration via Admin Interface

1. Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
2. Click on "Devices" under JOB_LOGS
3. Click "Add Device" in the top right
4. Fill in the device details:
   - **Lara name**: Unique identifier for the device
   - **Num slots**: Number of positions/slots available
   - **Lara uri**: URL endpoint for the device (e.g., `http://192.168.1.100:50051`)
5. Click "Save"

Positions are automatically created based on the number of slots.

### Option 3: Programmatic Configuration

```python
from platform_status_db.job_logs.models import Device, Position

# Create a device
device = Device.objects.create(
    lara_name="RoboticArm1",
    num_slots=10,
    lara_uri="http://192.168.1.100:50051"
)

# Create positions (if not auto-created)
for i in range(device.num_slots):
    Position.objects.create(
        device=device,
        slot_number=i,
        deep_well_suited=False
    )
```

## First Steps with the API

### Initialize the Status DB

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation

# Create instance
db = StatusDBImplementation()
```

### Add a Container

```python
from laborchestrator import structures

container_info = structures.ContainerInfo(
    name="TestPlate1",
    current_device="RoboticArm1",
    current_pos=0,
    barcode="PLATE001",
    lidded=True,
    filled=True
)

db.add_container(container_info)
```

### Check if a Position is Empty

```python
is_empty = db.position_empty(device="RoboticArm1", pos=0)
print(f"Position is empty: {is_empty}")  # False, we just added a container
```

### Get Container Information

```python
container = db.get_container_at_position(device="RoboticArm1", pos=0)
print(f"Container barcode: {container.barcode}")
print(f"Container is lidded: {container.lidded}")
```

### Move a Container

```python
db.moved_container(
    source_device="RoboticArm1",
    source_pos=0,
    target_device="PlateReader1",
    target_pos=0,
    barcode="PLATE001"
)
```

## Configuration Options

### Database Settings

By default, the system uses SQLite. To use a different database, edit `src/platform_status_db/larastatus/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "platform_status",
        "USER": "dbuser",
        "PASSWORD": "dbpassword",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### Timezone Configuration

The default timezone is `Europe/Berlin`. To change it, edit `settings.py`:

```python
TIME_ZONE = "UTC"  # or any other timezone
```

### Production Deployment

**Important**: The default settings are for development only. For production:

1. Change `DEBUG = False` in `settings.py`
2. Set a secure `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use a production database (PostgreSQL, MySQL, etc.)
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up static file serving

See Django's [deployment checklist](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/) for details.

## Testing Your Setup

Run the included tests to verify everything is working:

```bash
pytest
```

## Next Steps

- **[Managing Devices](managing-devices.md)**: Learn how to add and configure devices
- **[Managing Containers](managing-containers.md)**: Understand container tracking and movement
- **[API Reference](api-reference.md)**: Explore all available methods
- **[Advanced Usage](advanced-usage.md)**: Work with experiments and process tracking

## Troubleshooting

### ImportError: No module named 'django'

Make sure Django is installed:
```bash
pip install django
```

### ImportError: No module named 'laborchestrator'

Install the laborchestrator package:
```bash
pip install --index-url https://gitlab.com/api/v4/projects/70366855/packages/pypi/simple "laborchestrator<0.3"
```

### Database Migration Errors

If you encounter migration errors, try:
```bash
# Reset migrations (WARNING: This will delete all data)
rm src/platform_status_db/db.sqlite3
python src/platform_status_db/manage.py migrate
```

### Server Won't Start

Check if another process is using port 8000:
```bash
# Use a different port
python src/platform_status_db/manage.py runserver 8001
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [laborchestrator Documentation](https://gitlab.com/OpenLabAutomation/lab-automation-packages/laborchestrator)
- [Project Repository](https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db)
