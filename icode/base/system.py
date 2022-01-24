import os
import platform
import sys

PLATFORM = platform.system()
SYS_NAME = PLATFORM.lower()

SYS_SEP = os.sep

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
    os.chdir(BASE_PATH)

BASE_PATH = os.getcwd()

sys.path.append(BASE_PATH + f"{SYS_SEP}smartcode")
sys.path.append(BASE_PATH + f"{SYS_SEP}smartcode{SYS_SEP}extensions")
sys.path.append(BASE_PATH + f"{SYS_SEP}smartcode{SYS_SEP}IEK")
#sys.path.append(BASE_PATH+f"{SYS_SEP}smartsci")
#sys.path.append(BASE_PATH+f"{SYS_SEP}base")
#sys.path.append(BASE_PATH+f"{SYS_SEP}ui")
#sys.path.append(BASE_PATH+f"{SYS_SEP}frameworks")
sys.path.append(BASE_PATH)


def add_path(type: str, path: str) -> list:
    if type.startswith("extension"):
        sys.path.append(BASE_PATH +
                        f"{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}" +
                        path)
        return sys.path

def make_dirs(dirs:list):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)    

def end(code=0):
    os._exit(code)
