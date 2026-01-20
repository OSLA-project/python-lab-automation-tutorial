# Built-in Service Resources

This document describes the service resources available in PythonLab.

## Overview

PythonLab provides several built-in `ServiceResource` implementations representing common laboratory equipment. These can be used directly in your processes or serve as examples for creating custom services.

## Location

All built-in services are in: `/home/dsmits/projects/osla/pythonLab/pythonlab/resources/services/`

## Available Services

### 1. IncubatorServiceResource

**File:** `incubation.py`

Represents an incubator for temperature-controlled incubation.

#### Methods

```python
def incubate(self, labware: LabwareResource, duration: int,
            temperature: float, shaking_frequency: int = 0, **kwargs)
```

Incubate labware at specified temperature.

**Parameters:**
- `labware`: Container to incubate
- `duration`: Time in seconds
- `temperature`: Temperature in Kelvin
- `shaking_frequency`: Shaking speed in RPM (default: 0)

**Example:**
```python
# In process():
self.incubator.incubate(
    self.plate,
    duration=3600,        # 1 hour
    temperature=310,      # 37°C (310K)
    shaking_frequency=200 # 200 RPM
)
```

---

### 2. MoverServiceResource

**File:** `moving.py`

Represents a robotic arm or automated moving system.

#### Methods

```python
def move(self, labware: LabwareResource, target_loc: ServiceResource,
        lidded: bool = True, **kwargs)
```

Move labware to a target location.

**Parameters:**
- `labware`: Container to move
- `target_loc`: Target ServiceResource (device)
- `lidded`: Whether labware has lid during move (default: True)

**Example:**
```python
# Move plate to incubator (with lid)
self.mover.move(self.plate, target_loc=self.incubator, lidded=True)

# Move plate to reader (remove lid)
self.mover.move(self.plate, target_loc=self.reader, lidded=False)
```

```python
def read_barcode(self, labware: LabwareResource, **kwargs)
```

Scan barcode on labware during handling.

**Parameters:**
- `labware`: Container to scan

**Example:**
```python
# Scan barcode during handling
self.mover.read_barcode(self.plate)
```

---

### 3. CentrifugeServiceResource

**File:** `centrifugation.py`

Represents a centrifuge for separating samples.

#### Methods

```python
def centrifuge(self, labwares: list, duration: int, rpm: int, **kwargs)
```

Centrifuge one or more containers.

**Parameters:**
- `labwares`: List of LabwareResource objects
- `duration`: Centrifugation time in seconds
- `rpm`: Revolutions per minute

**Example:**
```python
# Centrifuge multiple plates
self.centrifuge.centrifuge(
    labwares=[self.plate1, self.plate2, self.plate3],
    duration=600,    # 10 minutes
    rpm=4000
)
```

---

### 4. PlateReaderServiceResource

**File:** `analysis.py`

Represents a microplate reader for absorbance/fluorescence measurements.

#### Methods

```python
def single_read(self, labware: LabwareResource, wavelengths=None,
               temperature=305, method='single_read', **kwargs)
```

Perform a single absorbance/fluorescence reading.

**Parameters:**
- `labware`: Plate to read
- `wavelengths`: List of wavelengths in nm (optional)
- `temperature`: Reading temperature in Kelvin (default: 305)
- `method`: Method identifier (default: 'single_read')

**Returns:** Runtime variable representing measurement data

**Example:**
```python
# Single wavelength
abs_600 = self.reader.single_read(
    self.plate,
    wavelengths=[600],
    temperature=305
)

# Multiple wavelengths
abs_multi = self.reader.single_read(
    self.plate,
    wavelengths=[600, 660],
    method='multi_wavelength'
)
```

```python
def run_kinetic(self, labware: LabwareResource, wavelength: int,
               interval: int, reads: int, temperature=305, **kwargs)
```

Perform kinetic (time-series) measurements.

**Parameters:**
- `labware`: Plate to read
- `wavelength`: Wavelength in nm
- `interval`: Time between reads in seconds
- `reads`: Number of reads to perform
- `temperature`: Reading temperature in Kelvin (default: 305)

**Returns:** Runtime variable representing time-series data

**Example:**
```python
# Read every 60 seconds for 10 reads
kinetic_data = self.reader.run_kinetic(
    self.plate,
    wavelength=600,
    interval=60,
    reads=10,
    temperature=310
)
```

```python
def run_series(self, labware: LabwareResource, protocols: List[str], **kwargs)
```

Run a series of predefined protocols.

**Parameters:**
- `labware`: Plate to read
- `protocols`: List of protocol identifiers

**Returns:** Runtime variable representing protocol results

**Example:**
```python
# Run multiple protocols
results = self.reader.run_series(
    self.plate,
    protocols=['protocol_A', 'protocol_B', 'protocol_C']
)
```

---

### 5. LabwareStorageResource

**File:** `labware_storage.py`

Represents a storage location for labware (hotel, stack, etc.).

#### Properties

```python
@property
def next_free_position(self) -> int
```

Auto-incrementing position counter for storing labware.

#### Methods

```python
def eject(self, labware: LabwareResource, **kwargs)
```

Remove labware from storage.

**Parameters:**
- `labware`: Container to eject

**Example:**
```python
# Eject plate from storage
self.storage.eject(self.plate)
```

```python
def store(self, labware: LabwareResource, position: Optional[int] = None, **kwargs)
```

Store labware at specified or next available position.

**Parameters:**
- `labware`: Container to store
- `position`: Storage position (optional, uses next_free_position if None)

**Example:**
```python
# Store at next free position
self.storage.store(self.plate)

# Store at specific position
self.storage.store(self.plate, position=5)
```

#### Setting Starting Positions

```python
# In init_service_resources():
for i, plate in enumerate(self.plates):
    plate.set_start_position(
        self.storage,
        self.storage.next_free_position
    )
```

---

### 6. BarcodeReaderServiceResource

**File:** `barcode.py`

Represents a standalone barcode scanner.

**Note:** For barcode reading during movement, use `MoverServiceResource.read_barcode()`.

---

### 7. LiquidHandlingServiceResource

**File:** `liquid_handling.py`

Represents liquid handlers (pipetting robots).

#### Methods

```python
def transfer(self, source: LabwareResource, dest: LabwareResource,
            volume: float, **kwargs)
```

Transfer liquid between containers.

**Parameters:**
- `source`: Source container
- `dest`: Destination container
- `volume`: Volume in microliters

**Example:**
```python
# Transfer 100 µL
self.liquid_handler.transfer(
    source=self.reagent_trough,
    dest=self.sample_plate,
    volume=100.0
)
```

---

### 8. WasherDispenserServiceResource

**File:** `washer_dispenser.py`

Represents a plate washer/dispenser.

#### Methods

```python
def wash(self, labware: LabwareResource, cycles: int = 3, **kwargs)
```

Wash a plate.

**Parameters:**
- `labware`: Plate to wash
- `cycles`: Number of wash cycles (default: 3)

**Example:**
```python
# Wash plate with 3 cycles
self.washer.wash(self.plate, cycles=3)
```

```python
def dispense(self, labware: LabwareResource, volume: float,
            reagent: str = None, **kwargs)
```

Dispense liquid into plate.

**Parameters:**
- `labware`: Target plate
- `volume`: Volume in microliters
- `reagent`: Reagent identifier (optional)

**Example:**
```python
# Dispense 200 µL of media
self.dispenser.dispense(
    self.plate,
    volume=200.0,
    reagent='growth_media'
)
```

---

### 9. ThermalCyclerServiceResource

**File:** `thermal_cycler.py`

Represents a PCR thermal cycler.

#### Methods

```python
def run_pcr(self, labware: LabwareResource, cycles: int,
           denaturation_temp: float, annealing_temp: float,
           extension_temp: float, **kwargs)
```

Run a PCR protocol.

**Parameters:**
- `labware`: PCR plate
- `cycles`: Number of PCR cycles
- `denaturation_temp`: Denaturation temperature in Kelvin
- `annealing_temp`: Annealing temperature in Kelvin
- `extension_temp`: Extension temperature in Kelvin

**Example:**
```python
# Standard PCR protocol
self.thermal_cycler.run_pcr(
    self.pcr_plate,
    cycles=35,
    denaturation_temp=368,  # 95°C
    annealing_temp=328,     # 55°C
    extension_temp=345      # 72°C
)
```

---

### 10. ShakerServiceResource

**File:** `shaker.py`

Represents a plate shaker.

#### Methods

```python
def shake(self, labware: LabwareResource, duration: int,
         frequency: int, **kwargs)
```

Shake a plate at specified frequency.

**Parameters:**
- `labware`: Plate to shake
- `duration`: Shaking time in seconds
- `frequency`: Shaking frequency in RPM

**Example:**
```python
# Shake for 5 minutes at 300 RPM
self.shaker.shake(
    self.plate,
    duration=300,
    frequency=300
)
```

---

### 11. SealerServiceResource

**File:** `sealer.py`

Represents a plate sealer.

#### Methods

```python
def seal(self, labware: LabwareResource, seal_type: str = 'foil', **kwargs)
```

Seal a plate.

**Parameters:**
- `labware`: Plate to seal
- `seal_type`: Type of seal (default: 'foil')

**Example:**
```python
# Seal with foil
self.sealer.seal(self.plate, seal_type='foil')

# Seal with film
self.sealer.seal(self.plate, seal_type='film')
```

```python
def deseal(self, labware: LabwareResource, **kwargs)
```

Remove seal from plate.

**Parameters:**
- `labware`: Plate to deseal

**Example:**
```python
# Remove seal
self.sealer.deseal(self.plate)
```

---

### 12. MicroscopeServiceResource

**File:** `microscope.py`

Represents an automated microscope.

#### Methods

```python
def capture_image(self, labware: LabwareResource, magnification: int,
                 channels: List[str], **kwargs)
```

Capture microscopy images.

**Parameters:**
- `labware`: Container to image
- `magnification`: Objective magnification (e.g., 10, 40, 100)
- `channels`: List of imaging channels (e.g., ['brightfield', 'DAPI', 'GFP'])

**Returns:** Runtime variable representing image data

**Example:**
```python
# Capture brightfield and fluorescence
images = self.microscope.capture_image(
    self.plate,
    magnification=40,
    channels=['brightfield', 'GFP', 'RFP']
)
```

---

### 13. HumanServiceResource

**File:** `human.py`

Represents manual human intervention steps.

#### Methods

```python
def manual_step(self, labware: LabwareResource, instruction: str,
               estimated_duration: int, **kwargs)
```

Request human intervention.

**Parameters:**
- `labware`: Container requiring manual handling
- `instruction`: Instructions for operator
- `estimated_duration`: Estimated time for step in seconds

**Example:**
```python
# Manual colony picking
self.human.manual_step(
    self.plate,
    instruction="Pick 24 colonies and transfer to new plate",
    estimated_duration=900  # 15 minutes
)
```

---

### 14. CameraServiceResource

**File:** `camera.py`

Represents a camera for documentation/imaging.

#### Methods

```python
def take_photo(self, labware: LabwareResource, **kwargs)
```

Take a photograph of labware.

**Parameters:**
- `labware`: Container to photograph

**Returns:** Runtime variable representing image

**Example:**
```python
# Document plate state
photo = self.camera.take_photo(self.plate)
```

---

### 15. HelloWorldServiceResource

**File:** `hello_world.py`

Example/template service for testing and demonstration.

#### Methods

```python
def say_hello(self, labware: LabwareResource, message: str = "Hello", **kwargs)
```

Simple test operation.

**Example:**
```python
# Test operation
self.hello.say_hello(self.plate, message="Hello World")
```

---

## Creating Custom Services

Use built-in services as templates for creating custom services:

```python
from pythonlab.resource import ServiceResource, LabwareResource

class MyCustomService(ServiceResource):
    """Custom laboratory equipment."""

    def my_operation(self, labware: LabwareResource,
                    param1: float, param2: int, **kwargs):
        """
        Custom operation on labware.

        Args:
            labware: Container to process
            param1: First parameter
            param2: Second parameter
            **kwargs: Additional metadata
        """
        # Update kwargs with required metadata
        kwargs.update(dict(
            fct='my_operation',           # REQUIRED: operation name
            duration=120,                  # REQUIRED: duration in seconds
            param1=param1,                 # Include all parameters
            param2=param2
        ))

        # Add process step
        self.proc.add_process_step(self, [labware], **kwargs)

        # Optional: return for runtime variable
        # If this operation produces data, return here
```

### Best Practices for Custom Services

1. **Always include `fct` and `duration` in kwargs**
   ```python
   kwargs.update(dict(fct='operation_name', duration=60))
   ```

2. **Document parameters clearly**
   - Use docstrings with Args, Returns sections
   - Specify units (seconds, Kelvin, microliters, etc.)

3. **Pass labware as list**
   ```python
   self.proc.add_process_step(self, [labware], **kwargs)
   ```

4. **Use meaningful operation names**
   ```python
   fct='incubate'  # Good
   fct='op1'       # Bad
   ```

5. **Include all operation parameters in kwargs**
   ```python
   kwargs.update(dict(
       fct='incubate',
       duration=duration,
       temperature=temperature,
       shaking_frequency=shaking_frequency  # Include even optional params
   ))
   ```

6. **Return for runtime variables**
   - If operation produces data used in decisions, add return statement
   - Parser will create variable node

7. **Mark movement operations**
   ```python
   self.proc.add_process_step(self, [labware], is_movement=True, **kwargs)
   ```

## Usage Example

Complete process using multiple services:

```python
from pythonlab.process import PLProcess
from pythonlab.resource import LabwareResource
from pythonlab.resources.services.incubation import IncubatorServiceResource
from pythonlab.resources.services.moving import MoverServiceResource
from pythonlab.resources.services.analysis import PlateReaderServiceResource
from pythonlab.resources.services.labware_storage import LabwareStorageResource

class CompleteProcess(PLProcess):
    def create_resources(self):
        # Create services
        self.storage = LabwareStorageResource(proc=self, name="Hotel_1")
        self.mover = MoverServiceResource(proc=self, name="RobotArm")
        self.incubator = IncubatorServiceResource(proc=self, name="Incubator_37C")
        self.reader = PlateReaderServiceResource(proc=self, name="Reader_1")

        # Create labware
        self.plates = [
            LabwareResource(proc=self, name=f"Plate_{i}", lidded=True)
            for i in range(3)
        ]

    def init_service_resources(self):
        super().init_service_resources()

        # Set starting positions
        for plate in self.plates:
            plate.set_start_position(
                self.storage,
                self.storage.next_free_position
            )

    def process(self):
        # Process each plate
        for plate in self.plates:
            # Move to incubator
            self.mover.move(plate, target_loc=self.incubator, lidded=True)

            # Incubate
            self.incubator.incubate(
                plate,
                duration=7200,      # 2 hours
                temperature=310     # 37°C
            )

            # Move to reader
            self.mover.move(plate, target_loc=self.reader, lidded=False)

            # Measure
            absorbance = self.reader.single_read(
                plate,
                wavelengths=[600],
                temperature=305
            )

            # Return to storage
            self.mover.move(plate, target_loc=self.storage, lidded=True)
            self.storage.store(plate)
```

## Summary

PythonLab provides a rich set of built-in services covering common laboratory automation needs:
- **Incubation** - Temperature control
- **Movement** - Robotic handling
- **Centrifugation** - Sample separation
- **Analysis** - Spectroscopy and imaging
- **Storage** - Labware management
- **Liquid Handling** - Pipetting and dispensing
- **Thermal Cycling** - PCR
- **Washing/Sealing** - Plate preparation
- **Imaging** - Microscopy and documentation
- **Manual Steps** - Human intervention

These services can be used directly or serve as templates for custom equipment implementations.
