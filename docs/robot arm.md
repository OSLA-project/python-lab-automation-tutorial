# Generic Robotic Arm

The [genericroboticarm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git) package provides a SiLA2 server and teaching interface for robotic arms.
It ships with built-in support for several arm models (Dummy/simulation, JoyIt, Dorna2, UFactory XArm, Precise Flex 400, Precise Flex on a rail) and can be adapted to new hardware.

## Installation

```bash
pip install git+https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm.git
```

## Starting the server

```bash
genericroboticarm -r <ArmImplementation>
```

To try without real hardware, use the built-in `Dummy` implementation:

```bash
genericroboticarm -r Dummy
```

On startup you will see output like:

```
Dash is running on http://127.0.0.1:8055/
WARNING| sila_server.__start: Starting SiLA server without encryption.
```

This starts two services:

| Service | Address | Purpose |
|---------|---------|---------|
| Dash visualisation | `http://127.0.0.1:8055/` | Interactive position graph + keyboard control |
| SiLA2 server | `127.0.0.1:50051` | High-level command API used by the orchestrator |

## Teaching positions

Before the arm can be used in automated workflows, you need to teach it the positions it will navigate between (e.g. device slots, a home position, intermediate waypoints).

### Keyboard control

Open `http://127.0.0.1:8055/` in a browser and click the text box in the upper-left corner to give it focus.
Use the following keys to move the arm to the desired position:

| Key | Movement |
|-----|---------|
| Arrow keys | X/Y plane |
| `a` / `y` | Z axis |

### Saving positions via SiLA2

Once the arm is at the correct coordinates, save the position using the **RobotTeachingService** SiLA2 feature.
You can do this with the [SiLA Browser](https://gitlab.com/unitelabs/sila2/sila-browser) (auto-discovers the server) or via Python:

```python
# Example using the sila2 Python client
await teaching_client.AddPosition(identifier="device_A_slot_1")
```

Positions are stored as nodes in a position graph (a `.gml` file). Connections between nodes define the paths the arm can travel.
The 

Key teaching commands:

| SiLA command | Effect |
|-------------|--------|
| `AddPosition(identifier)` | Save current coordinates as a named node |
| `AddConnection(tail, head)` | Add an edge between two nodes |
| `ReteachPosition(identifier)` | Update coordinates of an existing node |
| `RemovePosition(identifier)` | Delete a node |
| `RemoveConnection(tail, head)` | Delete an edge |

### Where position graphs are stored

Position graphs are saved as `.gml` files named `position_graph_<ArmName>.gml` in the platform's user config directory:

| OS | Path |
|----|------|
| Linux | `~/.config/GenericRoboticArm/` |
| macOS | `~/Library/Preferences/GenericRoboticArm/` |
| Windows | `%LOCALAPPDATA%\GenericRoboticArm\GenericRoboticArm\` |

The exact path is printed at startup: `Using <path> to load/store position graph.`

A custom directory can be set by passing `graph_dir` in a custom arm implementation.

### Position naming convention

Positions are referenced by a string identifier. When addressing a specific device slot from the orchestrator, the default convention is `<device><slot_index>` (concatenation). The Dash visualisation shows the current position graph and the arm's current location.

## Controlling the arm via SiLA2

The server exposes three SiLA2 features for runtime control:

### RobotController

High-level movement and safety commands:

| Command | Description |
|---------|-------------|
| `MoveToPosition(position)` | Navigate to a named node along graph edges |
| `PickPlate(site)` | Pick labware from a device site |
| `PlacePlate(site)` | Place labware at a device site |
| `MovePlate(origin, target)` | Pick from one site and place at another |
| `SetSpeed(percentage)` | Adjust movement speed (0–100 %) |
| `SetAcceleration(percentage)` | Adjust acceleration (0–100 %) |
| `EmergencyStop()` | Immediately halt all movement |
| `Reinitialize()` | Re-establish connection to the arm hardware |

### LabwareTransferManipulatorController

Handles the full pick-and-place sequence with handover positions:

| Command | Description |
|---------|-------------|
| `PrepareForInput(handover, internal, labware_type, labware_id)` | Move arm to receive labware |
| `PrepareForOutput(handover, internal)` | Move arm to deliver labware |
| `PutLabware(handover, intermediate_actions)` | Execute the put motion |
| `GetLabware(handover, intermediate_actions)` | Execute the get motion |
| `GetAvailableHandoverPositions()` | List all taught handover positions |
| `GetNumberOfInternalPositions()` | Query internal storage capacity |

### GripController

| Command | Description |
|---------|-------------|
| `Grip()` | Close the gripper |
| `Release()` | Open the gripper |

## Using the arm in a PythonLab workflow

The arm's SiLA2 server is registered as a Service resource in the orchestrator. From a PythonLab process you interact with it through the orchestrator's labware transfer interface — you do not call the SiLA2 commands directly. See the [Wrappers](wrappers.md) page for how device wrappers translate PythonLab steps into SiLA2 calls.

## Adapting to a new arm

To support a new hardware model, implement the `RobotInterface` and start the server with your implementation:

```bash
genericroboticarm --arm-impl path/to/your_implementation.py
```

See the [adaption guide](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm/-/blob/main/docs/adaption.md) in the source repository for details.
