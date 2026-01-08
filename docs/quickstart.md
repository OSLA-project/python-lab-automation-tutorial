# Quickstart
## Simulated example
The fastest way to try out the LARA suite is by running the simulated example provided by the 
[adaptation template](https://gitlab.com/OpenLabAutomation/adaption-template).

There are two ways to run the example: using Docker or running it directly with Python.

## Cloning the repository
Whether you choose to run the example with Docker or Python, you first need to clone the repository:

```bash
git clone https://gitlab.com/OpenLabAutomation/adaption-template.git
cd adaption-template
```

## Running with Docker
Running the example with docker is straightforward, but it does require that you have the 
[Docker Desktop](https://docs.docker.com/get-started/get-docker/) or
[Docker Engine](https://docs.docker.com/engine/install/) installed on your machine.

To run the example with Docker, go to the root directory of the cloned repository and run the following command:

```bash
docker-compose up
```

## Running with Python
First, use your favourite tool to create and activate a new python environment with python 3.11 or higher. 
For example with pyvenv on linux:
```bash
   python -m venv labautomation
   source labautomation/bin/activate
```
3. Install all necessary packages:
   - to install all mandatory dependencies run:
```bash
    pip install -r requirements.txt -e .
```
   - to also install the example sila servers (necessary for the demo examples to run) add:
```bash
    pip install -r requirements_servers.txt
```
   - to also install requirements for stronger scheduling algorithms add:
```bash
    pip install -r requirements_mip_cp.txt
```
4. Install and set up the database

Installation: Run
```bash
    git clone https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db.git
    pip install -e platform_status_db/.
```
Setup: Run and follow the instructions to create an admin login to django. On windows you will have execute the steps manually.

```bash
    bash scripts/init_db.sh
```

Fill the database: Run
```bash
    python scripts/add_lab_setup_to_db.py
```
This adds the lab setup as described in platform_config.yml to the database.
Rerun this script after you customized the config file.

## Startup
Call from different console tabs

**Option 1:** In gnome terminal you could start all four of the following services in different tabs by running

```bash
bash scripts/run_services.sh
```

**Option 2:** Otherwise use individual commands (remember activating the virtual environment):

To start the scheduler:
```bash
labscheduler
```
To start the django database view (optional). If you changed directory, adapt the path:
```bash
run_db_server
```
To start the orchestrator:

```bash
laborchestrator
```

To start demo servers:
```bash
start_sila_servers
```

## Usage
You can access the GUI for different components:
- database of present labware at [http://127.0.0.1:8000/job_logs/present_labware/](http://127.0.0.1:8000/job_logs/present_labware/)
- orchestrator at [http://127.0.0.1:8050/](http://127.0.0.1:8050/)
- the human interaction sila server: [http://127.0.0.1:8054/](http://127.0.0.1:8054/)
- view and manual control of the robotic arm: [http://127.0.0.1:8055/](http://127.0.0.1:8055/)

To see how the example servers are controlled from the orchestrator, go to the the orchestrator GUI and load and start one of the
example processes.
- GreeterTest: Sends a Hello-World to the sila2-example-server
- MoverTest: You can view the robots movements in the robot GUI
- HumanTest: you will have to finish the tasks in the human interaction GUI
- InterestingExample: A more complex workflow with runtime decisions based on human interaction

<figure markdown="span">
![Orchestrator UI](assets/orchestrator_ui.png)
  <figcaption>Orchestrator UI</figcaption>
</figure>



### Loading and running a process

1. Go to the left dropdown menu and choose a process to load.
2. Click on "Load Process"
3. The corresponding workflow graph should appear below. You can zoom in/out and move it. Clicking on nodes dumps its 
   data structure as string into the textfield above (you might have to move the graph a bit down, so it gets visible).
4. Your loaded process should appear in the second dropdown menu. Choose it.
5. Click on "Add Containers to DB". This creates entries for all labware in that process in the positions described in
   the process in case there isn't already labware. Existing labware is considered to belong to that process. You can 
   see all present labware in the database view which updates automatically.
6. (Optional) Click on "Schedule Process" to get a predicted schedule. It will appear at gantt chart.
7. Click on "Start Process". This will update the schedule and will execute steps accordingly.
   You can monitor the progress in the orchestrator GUI and the labware movements in the database view.

### Things to observe during the process
While the process runs you can observe different features of our framework.

1. Live updates of the process in the orchestrator:
   1. The gantt chart has a moving bar of where in time you currently are
   2. Process step nodes in the graph turn to yellow while they are being executed and to green when they are finished. Pink means there was an error.
   3. Labware is shown by barcode in the gantt chart as soon as a barcode is read/assigned
2. Live updates of the database
   1. In the database view which auto-reloads all labware is listed with barcode ans current position
   2. You can check and manipulate in the [admin view](http://127.0.0.1:8000/admin/) of the database what the results, duration, and starting times of which steps were and which labware was involved. The credentials are the ones you chose during the installation process for superuser.


