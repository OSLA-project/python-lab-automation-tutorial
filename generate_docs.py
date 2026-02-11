from pythonlab.resources.services import *
from pythonlab.resources import LabwareResource
from pythonlab.resource import ServiceResource
import jinja2
from pathlib import Path


template_dir = Path("./templates")
output_dir = Path("./docs/pythonlab")


def get_all_subclasses(cls):
    """Recursively get all subclasses of a class."""
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


def main():
    # Get all subclasses
    service_subclasses = get_all_subclasses(ServiceResource)
    labware_subclasses = get_all_subclasses(LabwareResource)

    # Set up Jinja2 environment
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('api_reference.md.jinja2')

    # Render template
    output = template.render(
        service_subclasses=service_subclasses,
        labware_subclasses=labware_subclasses
    )

    # Write output file
    output_file = output_dir / "api_reference.md"
    output_file.write_text(output)
    print(f"Generated {output_file}")


if __name__ == "__main__":
    main()