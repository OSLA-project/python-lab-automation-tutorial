<figure markdown="span">
![LARA logo](assets/LARA_logo.svg)
</figure>

# What is the LARAsuite?
The LARAsuite is a freely and openly available collection of applications, libraries, databases and tools to plan, manage, 
create, monitor and evaluate (automated) processes in the laboratory. It has been developed by Mark Dörr and Stefan Maak
from the [LARA group](https://lara.uni-greifswald.de/team/) at the University of Greifswald.

The vision is to cover all steps of laboratory work in a uniform framework with standardized communication protocols and data formats (like SiLA2, AnIML). 

## Target Audience

People who have a robotic arm with several devices they can access via SiLA (or at least python) and look for a
framework do describe, orchestrate and schedule workflows on these devices. Some programming skills are necessary.

## The LARA workflow
LARA tries to cover all aspects of a common laboratory workflow, starting from the planning of the experiments until the final presentation of the results.

## The LARASuite architecture
The LARAsuite is modular and consists of different components that can be used independently or together to create a complete laboratory automation solution.

<figure markdown="span">
  ![LARASuite architecture](assets/architecture.png){ width="100%" }
  <figcaption>Architecture of LARASuite</figcaption>
</figure>

The most important components are the following:

### PythonLab
The PythonLab package is a framework to define laboratory processes in python syntax. It converts the process 
definitions into workflow graphs that can be used by the orchestrator and scheduler.

### Orchestrator
The orchestrator is the component that executes the workflow graphs created by PythonLab. It manages the execution of the processes,
allocates resources, and communicates with the devices through the wrappers.

### Scheduler
The scheduler is responsible for optimizing the execution of the workflows. It takes into account the availability of resources,
the dependencies between tasks, and the overall goals of the laboratory automation.

### Platform status database
The platform status database keeps track of the status of all devices, labware, and substances in the laboratory.
It provides real-time information to the orchestrator and scheduler. It also provides a UI to set the initial status of the lab.

## Disclaimer
This documentation has been written with the help of AI. 