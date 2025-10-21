# Workflow Graph Structure

This document explains the structure of the workflow graph created by `PLProcessReader`.

## Overview

The workflow graph is a **NetworkX DiGraph** (directed graph) that represents the laboratory process as a directed acyclic graph (DAG). Each node represents an operation, labware, variable, or decision point, and edges represent dependencies and data flow.

## Graph Structure

```python
simulator = PLProcessReader.parse_process(MyProcess())
workflow_graph = simulator.workflow  # nx.DiGraph instance
```

## Node Types

The workflow graph contains several types of nodes:

### 1. Labware Nodes

Represent starting points for containers in the workflow.

```python
{
    'type': 'labware',
    'name': 'SamplePlate_1',
    'origin_pos': 5,                    # Starting position
    'origin': 'LabwareStorage_1',       # Starting location name
    'origin_type': <class>,              # ServiceResource class
    'lidded': True,                     # Whether container has lid
    'plate_type': '96-well',            # Custom metadata
    # ... additional kwargs from LabwareResource
}
```

**Properties:**
- Created for each `LabwareResource` with a starting position
- Serve as entry points in the graph
- No incoming edges
- Outgoing edges to first operations involving this labware

### 2. Operation Nodes

Represent laboratory operations (incubation, measurement, movement, etc.).

```python
{
    'type': 'operation',
    'name': 'incubate SamplePlate_1',
    'cont_names': ['SamplePlate_1'],    # Labware involved
    'device_type': <class>,              # ServiceResource class
    'fct': 'incubate',                  # Function/operation name
    'duration': 3600,                    # Time to execute (seconds)
    'temperature': 310,                  # Operation-specific parameters
    'shaking_frequency': 0,
    'executor': [<service_instance>],   # Device(s) that can execute
    'wait_to_start_costs': 0,           # Cost per second of waiting
    # ... additional kwargs from add_process_step()
}
```

**Properties:**
- Created when ServiceResource methods are called
- Always include `fct` and `duration`
- `cont_names` lists all labware participating
- Incoming edges from previous operations on same labware
- Outgoing edges to next operations on same labware

**Special Case: Movement Operations**
```python
{
    'type': 'operation',
    'name': 'move SamplePlate_1',
    'fct': 'move',
    'is_movement': True,                 # Flag for movement operations
    'target': 'Incubator_1',            # Target location
    'lidded': True,                     # Lid state during move
    # ...
}
```

### 3. Variable Nodes

Represent runtime outputs from operations.

```python
{
    'type': 'variable',
    'name': 'measurement_result',
    'var_name': 'measurement_result'
}
```

**Properties:**
- Created when a ServiceResource method returns a value
- Represent data that is only known at execution time
- Incoming edges from the operation that produces them
- Outgoing edges to computations or decisions that use them

**Example:**
```python
# In process():
absorbance = self.reader.measure_absorbance(plate, wavelengths=[600])
# Creates a variable node with name 'absorbance'
```

### 4. Computation Nodes

Represent derived values computed from runtime variables.

```python
{
    'type': 'computation',
    'name': 'average_calculation',
    'var_name': 'avg_abs',
    'function': <callable>               # Python function to execute
}
```

**Properties:**
- Created when computations use runtime variables
- `function` is a Python callable that performs the computation
- Incoming edges from variable/computation nodes used in calculation
- Outgoing edges to operations or decisions that use the result

**Example:**
```python
# In process():
absorbance = self.reader.measure_absorbance(plate, wavelengths=[600])
avg = self.calculate_average(absorbance)
# Creates computation node with function=calculate_average
```

### 5. If-Decision Nodes

Represent runtime conditional branches.

```python
{
    'type': 'if_node',
    'name': 'if avg_abs > 0.6',
    'function': <callable>,              # Decision function (returns bool)
    'true_dummy': 15,                    # Node ID of true branch entry
    'false_dummy': 16,                   # Node ID of false branch entry
}
```

**Properties:**
- Created when if-statements depend on runtime variables
- `function` evaluates the condition at runtime
- `true_dummy` and `false_dummy` point to dummy nodes (later contracted)
- Both branches are included in the graph
- Scheduler/executor decides which branch to take

**Example:**
```python
# In process():
measurement = self.reader.measure_absorbance(plate, wavelengths=[600])
avg = self.calculate_average(measurement)

if avg > 0.6:
    # True branch
    self.mover.move(plate, target_loc=self.storage)
else:
    # False branch
    self.incubator.incubate(plate, duration=3600, temperature=310)

# Creates if_node with both branches
```

### 6. Dummy Nodes

Temporary nodes used during parsing for control flow. **These are removed from the final graph.**

```python
{
    'type': 'dummy',
    'name': 'true_dummy',               # or 'false_dummy' or 'break_dummy'
    'cur_state': {...},                 # State snapshot (for break nodes)
    'if_nodes': []                      # List of if_nodes (for break tracking)
}
```

**Properties:**
- Used internally during graph construction
- Mark branch entry points and convergence points
- Contracted away by `contract_dummys()` before graph is returned
- Final graph should contain no dummy nodes

## Edge Structure

Edges connect nodes and represent dependencies and data flow.

### Edge Attributes

```python
{
    'cont_name': 'SamplePlate_1',       # Labware connecting the operations
    'label': '',                         # Optional step label
    'wait_cost': 0,                     # Cost per second for waiting
    'max_wait': float('inf'),           # Maximum time before next step
    'min_wait': None,                   # Minimum time before next step
    'sub_tree': True,                   # True/False for if-node branches
}
```

### Types of Edges

1. **Sequential Operation Edges**
   - Connect operations that share labware
   - Represent temporal dependencies
   ```python
   # operation_A -> operation_B
   # (same labware, must execute in order)
   ```

2. **Variable Dependency Edges**
   - Connect operations to variable nodes they produce
   - Connect variables to computations that use them
   ```python
   # operation -> variable
   # variable -> computation
   # computation -> if_node
   ```

3. **Control Flow Edges**
   - Connect if_nodes to branch dummies
   - Marked with `sub_tree=True` or `sub_tree=False`
   ```python
   # if_node -> true_dummy (sub_tree=True)
   # if_node -> false_dummy (sub_tree=False)
   ```

4. **Labware Initialization Edges**
   - Connect labware nodes to first operations
   ```python
   # labware_node -> first_operation
   ```

## Graph Properties

### Directed Acyclic Graph (DAG)

The workflow graph is a DAG:
- **Directed:** Edges have direction (A → B means A must happen before B)
- **Acyclic:** No cycles (no infinite loops)

This property allows:
- Topological sorting (valid execution order)
- Critical path analysis (longest path = minimum time)
- Parallel execution identification (independent branches)

### Multiple Roots

The graph may have multiple root nodes:
- Labware nodes (one per starting container)
- Variable nodes for data inputs

### Multiple Leaves

The graph may have multiple leaf nodes:
- Final operations
- Variable nodes for data outputs

## Accessing Graph Data

### Iterating Over Nodes

```python
# All nodes
for node_id, node_data in simulator.workflow.nodes(data=True):
    print(f"Node {node_id}: {node_data['type']} - {node_data['name']}")

# Filter by type
operation_nodes = [
    (nid, data) for nid, data in simulator.workflow.nodes(data=True)
    if data['type'] == 'operation'
]

# Get specific node
node_data = simulator.workflow.nodes[node_id]
print(f"Duration: {node_data.get('duration', 'N/A')}")
```

### Iterating Over Edges

```python
# All edges
for source, target, edge_data in simulator.workflow.edges(data=True):
    print(f"{source} -> {target}: {edge_data['cont_name']}")

# Filter by labware
plate1_edges = [
    (s, t, data) for s, t, data in simulator.workflow.edges(data=True)
    if data['cont_name'] == 'SamplePlate_1'
]

# Get specific edge
edge_data = simulator.workflow.edges[source_id, target_id]
print(f"Max wait: {edge_data['max_wait']}")
```

### Graph Analysis

```python
import networkx as nx

# Check if graph is DAG
assert nx.is_directed_acyclic_graph(simulator.workflow)

# Topological sort (valid execution order)
execution_order = list(nx.topological_sort(simulator.workflow))

# Critical path (longest path by duration)
# First, create weight attribute for operations
for node_id, node_data in simulator.workflow.nodes(data=True):
    simulator.workflow.nodes[node_id]['weight'] = node_data.get('duration', 0)

critical_path = nx.dag_longest_path(simulator.workflow, weight='weight')
total_time = sum(
    simulator.workflow.nodes[n].get('duration', 0)
    for n in critical_path
)
print(f"Minimum process time: {total_time} seconds ({total_time/60:.1f} minutes)")

# Find all paths between two nodes
all_paths = list(nx.all_simple_paths(
    simulator.workflow,
    source=start_node,
    target=end_node
))

# Identify parallel branches (nodes with no path between them)
for node1 in operation_nodes:
    for node2 in operation_nodes:
        if node1 != node2:
            has_path = nx.has_path(simulator.workflow, node1, node2)
            if not has_path and not nx.has_path(simulator.workflow, node2, node1):
                print(f"{node1} and {node2} can execute in parallel")
```

## Visualization

### Built-in Visualization

```python
# Generate and display graphviz visualization
simulator.visualize_workflow_graph(show=True)

# Save to file
simulator.visualize_workflow_graph(show=False)
# Saves to 'workflow_graph.png' or similar
```

### Custom Visualization with NetworkX

```python
import matplotlib.pyplot as plt
import networkx as nx

# Basic plot
pos = nx.spring_layout(simulator.workflow)
nx.draw(simulator.workflow, pos, with_labels=True, node_color='lightblue')
plt.show()

# Color-coded by node type
node_colors = {
    'labware': 'lightgreen',
    'operation': 'lightblue',
    'variable': 'yellow',
    'computation': 'orange',
    'if_node': 'red'
}

colors = [
    node_colors.get(data['type'], 'gray')
    for _, data in simulator.workflow.nodes(data=True)
]

pos = nx.spring_layout(simulator.workflow)
nx.draw(simulator.workflow, pos, node_color=colors, with_labels=True)
plt.show()
```

### Graphviz Visualization

```python
import pygraphviz as pgv

# Create graphviz graph
G = pgv.AGraph(directed=True)

for node_id, node_data in simulator.workflow.nodes(data=True):
    label = f"{node_data['name']}\n{node_data['type']}"
    G.add_node(node_id, label=label, shape='box')

for source, target, edge_data in simulator.workflow.edges(data=True):
    label = edge_data.get('cont_name', '')
    G.add_edge(source, target, label=label)

G.layout(prog='dot')
G.draw('workflow.png')
```

## Example Graph Walkthrough

Consider this simple process:

```python
class SimpleProcess(PLProcess):
    def create_resources(self):
        self.incubator = IncubatorService(proc=self, name="Inc1")
        self.reader = ReaderService(proc=self, name="Reader1")
        self.mover = MoverService(proc=self, name="Mover1")
        self.plate = LabwareResource(proc=self, name="Plate1", lidded=True)

    def init_service_resources(self):
        super().init_service_resources()
        self.plate.set_start_position(self.incubator, position=1)

    def process(self):
        self.incubator.incubate(self.plate, duration=3600, temperature=310)
        self.mover.move(self.plate, target_loc=self.reader, lidded=False)
        abs_value = self.reader.measure(self.plate, wavelengths=[600])
        avg = self.average(abs_value)

        if avg > 0.6:
            self.mover.move(self.plate, target_loc=self.storage)
        else:
            self.incubator.incubate(self.plate, duration=1800, temperature=310)
```

**Resulting Graph:**

```
Nodes:
[0] type=labware, name="Plate1", origin="Inc1", origin_pos=1
[1] type=operation, name="incubate Plate1", fct="incubate", duration=3600, temperature=310
[2] type=operation, name="move Plate1", fct="move", duration=20, target="Reader1"
[3] type=operation, name="measure Plate1", fct="measure", duration=30, wavelengths=[600]
[4] type=variable, name="abs_value"
[5] type=computation, name="average", var_name="avg", function=<average>
[6] type=if_node, name="if avg > 0.6", function=<lambda>
[7] type=operation, name="move Plate1" (to storage), fct="move", duration=20
[8] type=operation, name="incubate Plate1", fct="incubate", duration=1800, temperature=310

Edges:
[0] -> [1]: cont_name="Plate1" (labware to first operation)
[1] -> [2]: cont_name="Plate1" (incubate to move)
[2] -> [3]: cont_name="Plate1" (move to measure)
[3] -> [4]: (operation produces variable)
[4] -> [5]: (variable used in computation)
[5] -> [6]: (computation used in decision)
[6] -> [7]: sub_tree=True (if true, move to storage)
[6] -> [8]: sub_tree=False (if false, continue incubation)
```

**Visualization:**

```
      [Plate1]
         │
         ▼
    [incubate 3600s]
         │
         ▼
    [move to reader]
         │
         ▼
     [measure]
         │
         ▼
    [abs_value var]
         │
         ▼
    [compute avg]
         │
         ▼
   [if avg > 0.6]
      ╱       ╲
   True      False
    ╱           ╲
[move to      [incubate
 storage]      1800s]
```

## Graph Metadata Usage

The workflow graph metadata is used by:

1. **Schedulers:** Determine optimal execution order considering:
   - Duration of each operation
   - Wait costs and constraints (max_wait, min_wait)
   - Device availability
   - Parallel execution opportunities

2. **Executors:** Execute the workflow by:
   - Following topological order
   - Evaluating if-node decisions at runtime
   - Invoking device operations with parameters

3. **Analyzers:** Analyze the workflow for:
   - Total execution time (critical path)
   - Resource utilization
   - Bottlenecks
   - Optimization opportunities

4. **Visualizers:** Display the workflow for:
   - Process understanding
   - Validation
   - Documentation
   - Debugging

## Summary

The workflow graph is a rich data structure that:
- Represents laboratory processes as DAGs
- Contains multiple node types (labware, operations, variables, decisions)
- Encodes dependencies, timing, and constraints in edges
- Supports analysis, scheduling, execution, and visualization
- Is generated automatically by parsing PLProcess definitions

Understanding the graph structure enables advanced usage of PythonLab for process optimization, scheduling, and automation.
