import os
import platform
import sys
import pathlib

PLATFORM = platform.system()
SYS_NAME = PLATFORM.lower()

ROOT_PATH = os.getcwd()

SMARTCODE_PATH = pathlib.Path(ROOT_PATH).joinpath("smartcode")

def add_path(type: str, path: str) -> list:
    if type.startswith("extension"):
        sys.path.append(str(pathlib.Path(SMARTCODE_PATH).joinpath("extensions").joinpath(path)))
        return sys.path


def make_dirs(dirs: list):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def end(code=0):
    os._exit(code)
