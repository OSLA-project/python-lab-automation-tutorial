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

The most important components are the following:

### PythonLab

The PythonLab package is a framework to define laboratory processes in python syntax. It converts the process
definitions into workflow graphs that can be used by the orchestrator and scheduler.

### Orchestrator

The orchestrator is the component that executes the workflow graphs created by PythonLab. It manages the execution of
the processes,
allocates resources, and communicates with the devices through the wrappers.

### Scheduler

The scheduler is responsible for optimizing the execution of the workflows. It takes into account the availability of
resources,
the dependencies between tasks, and the overall goals of the laboratory automation.

### Platform status database

The platform status database keeps track of the status of all devices, labware, and substances in the laboratory.
It provides real-time information to the orchestrator and scheduler. It also provides a UI to set the initial status of
the lab.

### SiLA servers

Our framework uses [SiLA2](https://sila-standard.com/) as the standard communication protocol between the orchestrator
and the devices.
SiLA2 is a widely used standard in laboratory automation that defines a common interface for laboratory devices.
However, the core framework is designed to be agnostic about the communication protocol. Other protocols can be used by
implementing appropriate wrappers.

