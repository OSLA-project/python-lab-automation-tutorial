# Customization
To customize the simulated example to your own needs, you will need to take a couple of steps.

- [Find lab resource classes](#resource_classes)
- [Find or implement lab SiLA servers](#sila_servers)
- [Write your device wrappers](#device_wrappers)
- [Configure your lab definition](#lab_definition)
- [Write your process descriptions](#process_descriptions)
- [Customize the robot arm](#robot_arm)

## Find lab resource classes {#resource_classes}
The first step is to find the lab resource classes that you want to use in your lab. The 
[PythonLab](https://gitlab.com/OpenLabAutomation/lab-automation-packages/pythonLab) package provides a set
of predefined resource classes (see [PythonLab api reference](pythonlab/api_reference.md)) that you can use as a starting 
point.

## Find or implement lab SiLA servers {#sila_servers}
The default method for communicating with lab devices in the LARA lab automation suite is through SiLA servers. 
[SiLA](https://sila-standard.com/) is an open source standard for communication between lab devices and has an active
community of developers and users. SiLA server implementations for common lab devices can be found in various repositories,
some of which we link to below:

- [LARA Lab Automation device integration](https://gitlab.com/OpenLabAutomation/device-integration)
- [SiLA Awesome List of Servers](https://gitlab.com/SiLA2/sila_awesome#servers)


## Write your device wrappers {#device_wrappers}
The communication between the lab orchestrator and the sila servers is handled by device wrappers. These wrappers 
translate the high-level commands defined in the process descriptions to specific SiLA commands. The 
[quickstart](quickstart.md) example comes with a couple of example wrappers that you can use as a starting point. 
You can find more information about writing device wrappers in the [wrappers documentation](wrappers.md).

## Configure your lab definition {#lab_definition}
You lab config file describes the available resources in your lab and their capacities. In the quickstart template this
file is named `platform_config.yaml`. You will need to modify this file to match the resources available in your lab.
More information about the lab definition can be found at [lab configuration](lab_configuration.md).

## Write your process descriptions {#process_descriptions}
A Pythonlab process description describes the steps that should be executed in the lab. They are written in python and
parsed into a workflow graph by the orchestrator. The process descriptions are the main part of your lab automation and 
you will need to write them to match your specific use case. You can find more information about writing process 
descriptions in the [pythonLab introduction](pythonlab/processes.md).

## Customize the robot arm {#robot_arm}
Customizing the robot arm involves two parts. First of all, you will need to configure the 
[GenericRobotArm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm) SiLA server to match the 
brand and model of your robot arm. 
The [adaptation guide for the GenericRoboticArm](https://gitlab.com/OpenLabAutomation/device-integration/genericroboticarm/-/blob/main/docs/adaption.md)
provides some guidance on how to do this.

The second part is to configure locations of your labware and the devices with respect to the robot arm.
This is done with the RobotTeachingService endpoint on the GenericRobotArm SiLA server. 

More info on configuring the arm and the locations can be found in the [robot arm documentation](robot%20arm.md).