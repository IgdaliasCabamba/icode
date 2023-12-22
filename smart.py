import sys

sys.dont_write_bytecode = True

import click
import rich
import subprocess
import tempfile
import requests
from rich.progress import Progress
import toml

@click.group()
def manage():
    pass

show_alert = lambda: rich.print("[blue bold]Be sure that you are in icode home dir!")

@manage.command('start')
def start():

    show_alert()

    url = "https://github.com/IgdaliasCabamba/Pyuxterm/releases/download/v1.0.0/pyuxterm"

    output_file = "./icode/bin/pyuxterm"
    
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('content-length', 0))

    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading pyuxterm...", total=file_size)

        with open(output_file, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                progress.update(task, advance=len(data))

    with tempfile.NamedTemporaryFile(mode='w+t') as tmp:
        tmp.write(f"chmod +x {output_file}")
        tmp.flush()

        process = subprocess.Popen(["bash", tmp.name], stdout=subprocess.PIPE)
        output, err = process.communicate()

        rich.print(output.decode())
        
        if err:
            rich.print("[red bold] an error occurred :(")
        
        else:
            rich.print("[green bold]Installed pyuxterm succefully :)")


@manage.command('go')
def go():
    # run python app.py to sse error and warning logs

    show_alert()

    with tempfile.NamedTemporaryFile(mode='w+t') as tmp:
        tmp.write("source ./venv/bin/activate \n")
        tmp.write("python icode/app.py")
        tmp.flush()
        process = subprocess.Popen(["bash", tmp.name], stdout=subprocess.PIPE)
        output, err = process.communicate()

        if err:
            rich.print("[red bold] an error occurred :(")

        rich.print(output.decode())


@manage.command('version')
def go():
    
    show_alert()

    with open("icode/bin/program.toml", "r") as f:
        data = toml.load(f)
        rich.print(f"[bold purple]\tBin version: [/]{data['bin_version']}")
        rich.print(f"[bold purple]\tKernel version: [/]{data['kernel_version']}")
        rich.print(f"[bold purple]\tFrameworks version: [/]{data['frameworks_version']}")


if __name__ == '__main__':
    manage()
