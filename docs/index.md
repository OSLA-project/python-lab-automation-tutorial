# What is the LARAsuite ?
The LARAsuite is a freely and openly available collection of applications, libraries, databases and tools to plan, manage, create, monitor and evaluate (automated) processes in the laboratory.

The vision is to cover all steps of laboratory work in a uniform framework with standardized communication protocols and data formats (like SiLA2, AnIML).

One very strong aspect in science is reproducibility, transparency and accountability.

One needs to be able to trust what someone else did, and it is important to exactly understand all the steps leading to a certain result. This is in the core of science.

The LARA workflow
LARA tries cover all aspects of a common laboratory workflow, starting from the planning of the experiments until the final presentation of the results.

lara-workflow
The LARA structure
The LARAsuite is very modular, enabling a flexible extension of the concept.

lara-structure
The LARAsuite architecture
The current architecture looks like:


Things to explain:

- What is the LARA suite
- adaptation template
- what are processes
- what are workers
- Things to reuse, things to implement

## Pythonlab
PythonLab is a Python framework for defining, parsing, and managing laboratory automation workflows. It allows you to write laboratory processes in Python syntax and converts them into executable workflow graphs.


## Workers
Worker_adaptation also needs to be custom.
Worker calls steps through the wrappers, and returns the Observable object to orchestrator.


## Wrappers
Wrappers implement calls to actual sila servers. In worker the devices are still just conceptual. 

## Sila servers
Sila servers have 2 types of commands, one type is observable, other isn’t. If sila command isn’t observable, you have to fake the observable in the wrapper 

## Config file
Describes the capacity of the devices in your lab. This information is read by both the orchestrator and scheduler. 

## Disclaimer
This documentation has been written with the help of AI. 