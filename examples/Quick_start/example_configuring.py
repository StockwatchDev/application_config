"""Example for configuration."""
from pathlib import Path

from application_settings import ConfigBase, ConfigSectionBase, dataclass


@dataclass(frozen=True)
class MyExampleConfigSection(ConfigSectionBase):
    """Config section for an example"""

    field1: float = 0.5
    field2: int = 2


@dataclass(frozen=True)
class MyExampleConfig(ConfigBase):
    """Config for an example"""

    name: str = "nice example"
    section1: MyExampleConfigSection = MyExampleConfigSection()


def main1() -> None:
    """example how to use the module application_settings"""
    # One of the first things to do in an application is loading the parameters
    MyExampleConfig.load()
    # Now you can access parameters via get()
    # If you get() MyExampleConfig before load(), it will be loaded automatically
    a_variable = MyExampleConfig.get().section1.field1
    print(f"a_variable == {a_variable}")  # a_variable == -0.5
    # You can also directly get() a section; but remember that the config should
    # be loaded already then (get() on a section does not automatically load())
    another_variable = MyExampleConfigSection.get().field2
    print(f"another_variable == {another_variable}")  # another_variable == 22


def main2() -> None:
    """continued example how to use the module application_settings"""
    # The only way to modify a config parameter is by editing the config file
    # or by changing the default value in the definition
    # Suppose that we edited the config file, changed the value for name to "new name"
    # and removed field2

    # You can reload a config
    MyExampleConfig.load()
    new_variable = MyExampleConfig.get().name
    print(f"new_variable == '{new_variable}'")  # new_variable == 'new name'
    another_new_variable = MyExampleConfigSection.get().field2
    print(
        f"another_new_variable == {another_new_variable}"
    )  # another_new_variable == 2


if __name__ == "__main__":
    # Set the filepath to the default filename, but then in the local folder
    local_filepath = (
        Path(__file__).parent.absolute() / MyExampleConfig.default_filename()
    )
    MyExampleConfig.set_filepath(local_filepath)

    main1()

    # Edit the config file
    with local_filepath.open("r") as file:
        filedata = file.read()
    filedata = filedata.replace('"the real thing"', '"new name"')
    filedata = filedata.replace("field2 = 22", "# field2 = 22")
    with local_filepath.open("w") as file:
        file.write(filedata)

    main2()

    # Restore the original config file
    with local_filepath.open("r") as file:
        filedata = file.read()
    filedata = filedata.replace('"new name"', '"the real thing"')
    filedata = filedata.replace("# field2 = 22", "field2 = 22")
    with local_filepath.open("w") as file:
        file.write(filedata)
