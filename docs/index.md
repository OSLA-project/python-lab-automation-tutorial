# Welcome to MkDocs

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