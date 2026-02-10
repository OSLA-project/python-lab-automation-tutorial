# Customization
To customize the simulated example to your own needs, you will need to take a couple of steps.

- Find lab resource classes
- Find or implement lab SiLA servers
- Write your device wrappers
- Configure your lab definition
- Write your process descriptions
- Customize the robot arm

## Find lab resource classes
The first step is to find the lab resource classes that you want to use in your lab. The 
[PythonLab](https://gitlab.com/OpenLabAutomation/lab-automation-packages/pythonLab) package provides a set
of predefined resource classes (see [PythonLab api reference](pythonlab/api_reference.md)) that you can use as a starting 
point.

## Find or implement lab SiLA servers
The default method for communicating with lab devices in the LARA lab automation suite is through SiLA servers. 
[SiLA](https://sila-standard.com/) is an open source standard for communication between lab devices and has an active
community of developers and users. SiLA server implementations for common lab devices can be found in various repositories,
some of which we link to below:

- [LARA Lab Automation device integration](https://gitlab.com/OpenLabAutomation/device-integration)
- [SiLA Awesome List of Servers](https://gitlab.com/SiLA2/sila_awesome#servers)


## Write your device wrappers
The communication between the lab orchestrator and the sila servers is handled by device wrappers. These wrappers 
translate the high-level commands defined in the process descriptions to specific SiLA commands. The 
[quickstart](quickstart.md) example comes with a couple of example wrappers that you can use as a starting point. 
You can find more information about writing device wrappers in the [wrappers documentation](wrappers.md).