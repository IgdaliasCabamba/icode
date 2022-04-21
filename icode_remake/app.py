import faulthandler
import sys

sys.dont_write_bytecode = True
faulthandler.enable()

import os
import importlib
from bin import utils

IS_RUNNING = True
IS_FINISHED = False

src_path = "src"
root_path = os.getcwd()

if getattr(sys, "frozen", False):
    root_path = os.path.dirname(os.path.realpath(sys.executable))
    os.chdir(root_path + os.sep + src_path)
else:
    root_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(root_path + os.sep + src_path)


def finish():
    global IS_FINISHED
    if not IS_FINISHED:
        IS_FINISHED = True
        print(
            utils.kernel_version,
            utils.bin_version,
            utils.frameworks_version,
            main.version,
        )


main_path = os.getcwd()

sys.path.append(main_path + f"{os.sep}smartcode{os.sep}extensions")
sys.path.append(main_path + f"{os.sep}smartcode{os.sep}IEK")
sys.path.append(root_path + f"{os.sep}frameworks")
sys.path.append(main_path + f"{os.sep}smartcode")
sys.path.append(root_path)
sys.path.append(main_path)

main = importlib.import_module("main", "src")

main.run(None, finish)
