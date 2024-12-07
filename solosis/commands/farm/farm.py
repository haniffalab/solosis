import os
from .. import helpers
import click


codebase ='/lustre/scratch126/cellgen/team298/vm11/PROJECTS/SOLOSIS/solosis/bin/farm/'
def bash_submit(command: str,
                **kwargs) -> None:
    """
    Submit a bash script to the farm.
    """
    #command = "echo"
    for k,v in kwargs.items():
        os.environ[str(k)] = str(v)
    result = subprocess.run(
            [command],
            capture_output=True,
            text=True,
            )
    click.echo(result.stdout)
    click.echo(result.stderr)

@click.command("command")
@helpers.farm
def cmd():
    command=os.path.join(codebase, "single_job.sh")
    single_job(command, jobname="testing", queue=queue, time=time, cores=cores, mem=mem, command = "echo 'Hello, World!'")


if __name__ == "__main__":
    cmd=os.path.join(codebase, "test.sh")
    bash_submit(cmd, x = 'Hello, World!')
