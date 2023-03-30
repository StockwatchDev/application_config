## Files for storing parameters

Currently, two formats are supported for persistent storage of parameters: 
[`toml`](https://toml.io/en/) and [`json`](https://www.json.org/).

The `toml` format is human-oriented, flexible, standardardized and not overly complex.
It supports comments, and hence parameters can be easily documented in a toml file.
However, when parameters are initialized by reading from a toml file, then changed
(because it concerns settings) and subsequently written to file again for persistance,
the comments will be lost. Therefore, it does not make much sense to add documenting
comments to a settings file. Because config parameters are read-only, comments in a
config file will not get lost and do make sense. Because of this, the default format for
storing config parameters is `toml`. The name of a config file equals `config.toml` by
default.

JSON is a standardized, lightweight data-interchange format that is easy for machines to
parse and generate. It is a bit less straightforward to document parameters in this
format, which makes it less human-oriented than `toml`, but it is used widely for data
interchange between automated systems. Because of this, the default format for storing
settings parameters is `json`. The name of a settings file equals `settings.json` by
default.

The examples introduced in the previous section can for example be initialized with the
following files.

=== "`config.toml` file for the configuration example"
    ```toml
    [section1]
    # Use this section to set the config that you prefer by editing the file
    # field1 has default value 'field1'
    field1 = "my own version of the first field"
    # field2 has default value 2
    field2 = 22
    ```

=== "`settings.json` file for the settings example"
    ```json
    {
        "basics": {
            "name": "the stored name",
            "totals": 3
        }
    }
    ```


The fieldnames of a Container class are found as:

- the section names in the `toml` file
- the member names of the root object in the `json` file

The fieldnames of a Section class are found as:

- the fieldnames inside the corresponding section in the `toml` file
- the member names of the object that is the value of the name that represents the
  section in the `json` file

The order of sections and/or fields in the file does not have to adhere to the order
in which fields have been specified in the Container - or Section classes.

Presence of sections and/or fields in the files that are not defined in the classes goes
by silently.

Fields or complete sections defined in the classes can be absent in the files as long as
default values have been specified for all fields that have been left out. For more info
on data validation [click here](./5-Handling_deviations.md)

## Location, name and type of the file

By default, the config and settings file are located in a subfolder of the home folder of
the user running the application. The default name of that subfolder is provided by the
`default_foldername()` method and consists of a dot, followed by a name derived from your
container class: the word `Config`/`Settings` is removed, underscores are put in front of
capitals (except for the first letter) and all letters are made lower case. For example,
the Container class `MyExampleConfig` by default will store its config in
`~/.my_example/config.toml`. And `MyExampleSettings` will default to a settings file 
`~/.my_example/settings.json`.

If you want the files to be stored in a different location and/or have a different name
and/or change the format, then you can use the method `set_filepath`:

```python
# the next statement sets the location, name and format of the settings file
# the argument can be eiter a string or a Path
MyExampleSettings.set_filepath(r"C:\ProgramData\testsettings.toml")
```

The extension of the file is used to select the format for parsing and hence has to be
either `json`, `JSON`, `toml` or `TOML`.
