# Wrappers
Wrappers are the interface between the lab orchestrator and the actual devices. They translate the high-level commands
defined in ?? to specific SILA commands.

## The wrapper structure

```python
class MyWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep,
        cont: ContainerInfo,
        sila_client: ShakerClient,
        **kwargs,
    ) -> Observable:
        ...
```

### ProcessStep
Describes the step that should be executed.

### ContainerInfo
Describes the container that is handled

### Sila client
