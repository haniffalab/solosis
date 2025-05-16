## Examples directory contains the content needed to add a new command to solosis. 

Click python tool is used to construct solosis 
[Documentation](https://click.palletsprojects.com/en/stable/)

Main files needed:
* Command submission bash script 
    e.g. `bin/command-group/command.sh`
* Command click python script
    e.g. `solosis/commands/command-group/command.py`    

Changes will need to be made to:
* `cli.py` including `add_command()` for new command 
    e.g. 
```
@cli.group()
def alignment():
    """Commands for running alignment tools."""
    pass

alignment.add_command(cellranger_count.cmd, name="cellranger-count")
```

Check files in Utils (`solosis/utils/`), they include features that can be integrated in `command.py`:
* Logging configuration (`solosis/utils/logging_utils.py`)
* Input file validation (`solosis/utils/input_utils.py`)
* LSF job configuration (`solosis/utils/lsf_utils.py`)
* Environment and iRODS validation (`solosis/utils/env_utils.py`)
* Further LSF job configuration (`solosis/utils/subprocess_utils.py`)


Add pytests to ensure the code is covered and specified errors will be caught and notified:
Use existing tests at `tests/test_cli.py` as templates.