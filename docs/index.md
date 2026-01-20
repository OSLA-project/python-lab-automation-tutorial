<figure markdown="span">
![LARA logo](assets/LARA_logo.svg)
</figure>

## What is LARA Lab Automation?

The LARA Lab automation framework is an open source set of tools and libraries to facilitate laboratory automation. It
covers all steps of laboratory automation such as process definition, orchestration, scheduling, device communication
and status tracking.
The framework is modular and consists of different components that can be used independently or together to create a
complete laboratory automation solution.

It has been developed by Mark Dörr and Stefan Maak
from the [LARA group](https://lara.uni-greifswald.de/team/) at the University of Greifswald.

## Quickstart

To get started with LARA Lab Automation, please refer to the [Quickstart guide](quickstart.md) which provides
step-by-step instructions on setting up the framework and running your first laboratory automation process in a
simulated environment.

## Target Audience

People who have a robotic arm with several devices they can access via SiLA (or at least python) and look for a
framework do describe, orchestrate and schedule workflows on these devices. Some programming skills are necessary.

## Architecture Overview

<div class="grid cards" markdown>

-    __Pythonlab__

    ---

    The PythonLab package is a framework to define laboratory processes in python syntax. It converts the process
    definitions into workflow graphs that can be used by the orchestrator and scheduler.
    
    :simple-gitlab: [PythonLab git repository](https://gitlab.com/OpenLabAutomation/lab-automation-packages/pythonLab)

-    __Lab orchestrator__

    ---

    The orchestrator is the component that executes the workflow graphs created by PythonLab. It manages the execution of
    the processes, allocates resources, and communicates with the devices through the wrappers.
    
    :simple-gitlab: [Lab orchestrator git repository](https://gitlab.com/OpenLabAutomation/lab-automation-packages/laborchestrator)

-    __Scheduler__

    ---

    The scheduler is responsible for optimizing the execution of the workflows. It takes into account the availability of
    resources, the dependencies between tasks, and the overall goals of the laboratory automation.
    
    :simple-gitlab: [Scheduler git repository](https://gitlab.com/OpenLabAutomation/lab-automation-packages/lab-scheduler)

-    __Platform status database__

    ---

    The platform status database keeps track of the status of all devices, labware, and substances in the laboratory.
    It provides real-time information to the orchestrator and scheduler. It also provides a UI to set the initial status of
    the lab.
    
    :simple-gitlab: [Platform status database git repository](https://gitlab.com/OpenLabAutomation/lab-automation-packages/platform_status_db)

-    __SiLA servers__

    ---

    Our framework uses [SiLA2](https://sila-standard.com/) as the standard communication protocol between the orchestrator
    and the devices. SiLA2 is a widely used standard in laboratory automation that defines a common interface for laboratory devices.
    However, the core framework is designed to be agnostic about the communication protocol. Other protocols can be used by
    implementing appropriate wrappers.
    
    :simple-gitlab: [SiLA2 standard website](https://sila-standard.com/)

</div>