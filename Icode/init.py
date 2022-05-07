import faulthandler
import sys

sys.dont_write_bytecode = True
faulthandler.enable()

import os
import importlib

if getattr(sys, "frozen", False):
    ROOT_PATH = os.path.dirname(os.path.realpath(sys.executable))
    os.environ["SMARTCODE_ROOT_PATH"] = ROOT_PATH
else:
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
    os.environ["SMARTCODE_ROOT_PATH"] = ROOT_PATH

SRC_PATH = os.path.join(ROOT_PATH, "src")
BIN_PATH = os.path.join(ROOT_PATH, "bin")

os.environ["SMARTCODE_SRC_PATH"] = SRC_PATH
os.environ["SMARTCODE_BIN_PATH"] = BIN_PATH
os.chdir(SRC_PATH)

def killed() -> bool:
    global IS_FINISHED
    if not IS_FINISHED:
        IS_FINISHED = True
        return False

sys.path.append(os.path.join(ROOT_PATH))
sys.path.append(os.path.join(ROOT_PATH, "smartlibs"))
sys.path.append(os.path.join(SRC_PATH))
sys.path.append(os.path.join(SRC_PATH, "smartcode"))
sys.path.append(os.path.join(SRC_PATH, "smartcode", "extensions"))
sys.path.append(os.path.join(SRC_PATH, "smartcode", "extapi"))

def main() -> None:
    ICODE = importlib.import_module("main", "src")
    ICODE.run(None, killed)

main()