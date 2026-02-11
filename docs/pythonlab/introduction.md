# pythonLab

**pythonLab** is a universal, extendable and safe language for laboratory processes.

Reproducibility and reliability is in the core of science.
Describing lab operations in a precise, easy and standardized form will help to transfer knowledge to every lab around the world.
A *laboratory process description language* is a long desired goal in laboratory process standardization and lab automation.
It will enable automated execution of steps and better machine learning and AI predictions, since these process descriptions
can be packed as metadata to the data resulting form this process.   

Since this process language needs many characteristics of a programming language, like conditions (if ...), loops 
(for/while), variables, etc. we do not want to re-invent the wheel twice but rather use the **python syntax**, which is
very popular in science. 

## Key (desired) Features 

  * easy and simple to learn and write (close to simple English)
  * clear, human readable syntax
  * universal - applicable for most laboratory operations
  * transferable from one lab to another
  * easy mapping between abstract resource representation and actual lab resource
  * [*Turing-complete*](https://en.wikipedia.org/wiki/Turing_completeness), including conditions and loops
  * easy extendible - prepared for the constant development of science
  * close to real laboratory work
  * vendor independent
  * safe to execute
  * converter from other lab description languages to pythonLab easy to implement

## Applications of pythonLab

  * general lab processes, common in any natural sciences lab (very broad application)
  * description of lab automation workflows
  * workflows on the lab devices (e.g. HPLC processes - sometimes also called 'methods', plate reader processes etc.)
  * data evaluation workflows

## Architecture of pythonLab

pythonLab processes are denoted in a python like syntax, but they are **not** directly executed by a *python interpreter*. They are rather parsed into a *workflow graph*, which can be used by a *Scheduler* to calculate 
an optimal schedule (=order of execution). This order of execution might be different from the initial notation. An *Orchestrator* executes then the schedule and supervises the device communication, e.g. to SiLA servers/devices.

<figure markdown="span">
![pythonLab Architecture](assets/pythonLab_architecture.svg)
<figcaption>Architecture of pythonLab</figcaption>
</figure>


[PythonLab specification](https://opensourcelab.gitlab.io/pythonLab/specification/0_specification_core.html)

Very briefly, the generic lab description language should have many features a common programming language has and following the desired *Turning-completeness*, like:  

- variables  (x = value)
- conditions (if, else, ...)
- loops      (for ... while ....)
- functions / methods and subroutines 
- modules
- namespaces and versions for unique addressing of a process step
- (at a later stage of language development: object orientation)

**!! This is a proposal - we would like to discuss it with a wide range of scientist to find the best common ground** 

## [Documentation](https://opensourcelab.gitlab.io/pythonLab/)

The pythonLab Documentation can be found in [docs](https://pythonlabor.gitlab.io/pythonLab/)

## Language Core extensions

extensible Modules for e.g.
- liquid handling
- cultivation
- (bio-chemical) assays
- molecular biology
- chemical synthesis
- data evaluation

are in preparation


## Examples

A simple description of liquid transfer step

```python

# using settings: volume unit: uL, liquid class: water
# these are set in a settings module
# specifying resources
from pythonlab.resource import LabwareResource, DeviceResource
from pythonlab.liquid_handling import aspirate, dispense

cont1 = LabwareResource()
cont2 = LabwareResource()          
liquid_handler = DeviceResource()

# process steps
liquid_handler.aspirate(cont1, row=1, col=3, vol=4.0)
liquid_handler.dispense(cont2, row=2, col=3 , vol=7.2)
...

```

A bit more complex example

```python
# default units (SI) are specified in the standard unit module
# additional unit definitions can be added in the code  
# specifying resources

from pythonlab.resource.labware import LabwareResource
from pythonlab.resource.services import MoverServiceResource, IncubationServiceResource

cont1 = LabwareResource()
mover = MoverServiceResource()
incubator = IncubationServiceResource()
start_pos = cont1.set_start_position(pos=1)
incubation_duration = 6 # hours

# initialise the process 
incubator.init()
# process steps
mover.move(cont1,  start_pos, incubator.nest1)
incubator.incubate(cont1, incubation_duration, unit="h")
mover.move(cont1, incubator.nest1, start_pos)


...

```

And finally a higher level example

```python
# default units (SI) are specified in the standard unit module
# additional unit definitions can be added in the code  
# specifying resources

from pythonlab.resource.labware import LabwareResource
from pythonlab.resource.services import MoverServiceResource, DispensionServiceResource, IncubationServiceResource

from pythonlab.processes.base import incubate, centrifugate
from pythonlab.bioprocess import inoculate

Labware_set = [LabwareResource(name=f"growth_plate_{cont}")
                           for cont in range(8)]

dispenser = DispensionServiceResource()
incubator = IncubationServiceResource()

inoculate([dispenser, Labware_set], source="starting_culture")
incubate([incubator, Labware_set], temp=310.0, shaking=(700,2) )  # temp in K
centrifugate([incubator, Labware_set], duration=600, force=4500)

...

```
## Why python ?

Python is a programming language that is very common in modern scientific laboratories and covers all the desired characteristics we expect of a user-friendly lab process programming language.

The syntax is very simple, and intuitive to learn.
Syntax validation comes for free: the python interpreter already does it.

Standardisation of a minimal set of functionally will be achieved by standardised packages provided by this site (or any publicly available site).
Defined namespaces and versioning allow unique addressing of a process step. 


## [Implementation](./implementation)

As a proof-of-concept we are planning to provide a [pypy-sandbox](https://www.pypy.org) implementation in the future.
[pypy-sandbox](https://www.pypy.org) offerers a safe execution environment to execute insecure code. 
A new version is currently developed to by the pypy community.
Alternatively WASM will be a possible safe execution environment.

## Related projects

Here is an incomplete list of related OpenSource projects - please let us know, if we missed a relevant project. 

###  [Autoprotocoll](http://autoprotocol.org)

  * Syntax: JSON based 
  * (-) not *Turing complete*
  * (-) hard to write and read by humans

###  [LabOP](https://bioprotocols.github.io/labop/)

  * Syntax: RDF / python
  * (-) not *Turing complete* (?)
  * (-) hard to write and read by humans

### [RoboLiq](https://ellis.github.io/roboliq/protocol/index.html)

  * Syntax: yaml / Javascript
  * (-) not *Turing complete*
  * (-) hard to write and read by humans
  * (-) design not clearly specified

## Repository Maintainer:

* mark doerr (mark.doerr@uni-greifswald.de)

## Documentation

The Documentation can be found here: [opensourcelab.gitlab.io/pythonLab](opensourcelab.gitlab.io/pythonLab) or [pythonLab.gitlab.io](pythonlab.gitlab.io/)


## Credits

This package was created with Cookiecutter* and the `opensource/templates/cookiecutter-pypackage`* project template.

[Cookiecutter](https://github.com/audreyr/cookiecutter )
[opensource/templates/cookiecutter-pypackage](https://gitlab.com/opensourcelab/software-dev/cookiecutter-pypackage) 