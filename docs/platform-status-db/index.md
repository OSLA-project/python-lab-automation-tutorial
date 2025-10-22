# Platform Status DB Documentation

Platform Status DB is a Django-based database system designed for tracking and managing the status of robotic laboratory automation platforms. It implements the interface required by the [laborchestrator](https://gitlab.com/OpenLabAutomation/lab-automation-packages/laborchestrator) package for process logging, container tracking, and device management.

## What is Platform Status DB?

Platform Status DB provides a centralized database for:

- **Device Management**: Track laboratory devices (robotic arms, plate readers, incubators, etc.) and their available positions
- **Container Tracking**: Monitor laboratory containers (plates, tubes, etc.) as they move through the platform
- **Process Logging**: Record process steps, experiments, and their execution details
- **Duration Estimation**: Predict process step durations based on historical data
- **Web Interface**: View and manage platform status through Django admin and custom views

## Key Features

- **Real-time Container Tracking**: Know the current location of every container on your platform
- **Movement History**: Full audit trail of all container movements
- **Process Step Recording**: Detailed logs of all operations with timing information
- **Barcode Support**: Track containers using barcode identifiers
- **Lid Management**: Track lidding/unlidding operations and lid locations
- **Historical Analysis**: Duration estimation for future operations based on past performance
- **REST-like Interface**: Programmatic access through Python API
- **Web Dashboard**: Visual interface for monitoring platform status

## Architecture Overview

The system consists of two main Django applications:

1. **larastatus**: Core implementation and configuration
   - Implements `StatusDBInterface` from laborchestrator
   - Provides duration estimation capabilities
   - Django project configuration

2. **job_logs**: Data models and web views
   - Database models for devices, containers, and processes
   - Web views for visualizing platform status
   - Django admin interface customization

## Use Cases

### Laboratory Automation
Track containers through complex multi-step laboratory workflows, ensuring traceability and monitoring system utilization.

### Process Optimization
Analyze historical data to identify bottlenecks and optimize workflow scheduling.

### Compliance and Auditing
Maintain detailed logs of all operations for regulatory compliance and troubleshooting.

### Integration with Orchestration Systems
Provide real-time status information to laboratory orchestration systems for intelligent decision-making.

## Documentation Structure

- **[Getting Started](getting-started.md)**: Installation, setup, and first steps
- **[Managing Devices](managing-devices.md)**: How to add and configure laboratory devices
- **[Managing Containers](managing-containers.md)**: Working with containers and tracking their movement
- **[API Reference](api-reference.md)**: Complete reference for StatusDBImplementation methods
- **[Advanced Usage](advanced-usage.md)**: Experiments, process tracking, and duration estimation

## Quick Example

```python
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
from laborchestrator import structures

# Initialize the database
db = StatusDBImplementation()

# Create lab from configuration file
db.create_lab_from_config("lab_config.yaml")

# Add a container
container_info = structures.ContainerInfo(
    name="Plate001",
    current_device="RoboticArm1",
    current_pos=0,
    barcode="BC12345",
    lidded=True,
    filled=True
)
db.add_container(container_info)

# Track a movement
db.moved_container(
    source_device="RoboticArm1",
    source_pos=0,
    target_device="PlateReader",
    target_pos=1,
    barcode="BC12345"
)

# Query container location
container = db.get_cont_info_by_barcode("BC12345")
print(f"Container is at {container.current_device}, position {container.current_pos}")
```

## System Requirements

- Python 3.9 or higher
- Django 4.1+
- laborchestrator package (<0.3)
- SQLite (default) or other Django-supported databases

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions:
- GitLab Issues: [Platform Status DB Issues](https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db/-/issues)
- Documentation: [Online Documentation](https://openlabautomation.gitlab.io/-/lab-automation-packages/platform_status_db/)
