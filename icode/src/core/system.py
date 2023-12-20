import os
import platform
import sys

PLATFORM = platform.system()
SYS_NAME = PLATFORM.lower()
SYS_SEP = os.sep

BASE_PATH = os.getcwd()


def add_path(type: str, path: str) -> list:
    if type.startswith("extension"):
        sys.path.append(BASE_PATH +
                        f"{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}" +
                        path)
        return sys.path


def make_dirs(dirs: list):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def end(code=0):
    os._exit(code)
