import sys

sys.dont_write_bytecode = True

import click
import rich
import subprocess
import tempfile

from rich.prompt import Prompt


@click.group()
def manage():
    pass


@manage.command('start')
def start():

    rich.print("[blue bold] Be sure that you are in icode home dir!")

    rich.print("[yellow bold]Downloading pyuxterm owo")

    with tempfile.NamedTemporaryFile(mode='w+t') as tmp:
        tmp.write(
            "curl -o ./icode/bin/pyuxterm https://github.com/IgdaliasCabamba/Pyuxterm/releases/download/v0.1.1/pyuxterm"
        )
        tmp.flush()
        process = subprocess.Popen(["bash", tmp.name], stdout=subprocess.PIPE)
        output, err = process.communicate()

        if err:
            rich.print("[red bold] an error occurred :(")

        rich.print(output.decode())

    rich.print("[green bold]Installed pyuxterm succefully :)")


@manage.command('go')
def go():

    rich.print("[blue bold] Be sure that you are in icode home dir!")

    with tempfile.NamedTemporaryFile(mode='w+t') as tmp:
        tmp.write("source ./venv/bin/activate \n")
        tmp.write("python icode/app.py")
        tmp.flush()
        process = subprocess.Popen(["bash", tmp.name], stdout=subprocess.PIPE)
        output, err = process.communicate()

        if err:
            rich.print("[red bold] an error occurred :(")

        rich.print(output.decode())


if __name__ == '__main__':
    manage()
