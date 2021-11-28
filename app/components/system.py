import os, sys
import platform
from pathlib import Path

PLATFORM = platform.system()
SYS_NAME=PLATFORM.lower()

SYS_SEP = os.sep

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
    os.chdir(BASE_PATH)

BASE_PATH = os.getcwd()

sys.path.append(BASE_PATH+f"{SYS_SEP}smartcode")
sys.path.append(BASE_PATH+f"{SYS_SEP}editor")
sys.path.append(BASE_PATH+f"{SYS_SEP}components")
sys.path.append(BASE_PATH+f"{SYS_SEP}gui")
sys.path.append(BASE_PATH+f"{SYS_SEP}smartcode{SYS_SEP}extensions")
sys.path.append(BASE_PATH+f"{SYS_SEP}ilibs")
sys.path.append(BASE_PATH)

def end(code = 0):
    os._exit(code)
