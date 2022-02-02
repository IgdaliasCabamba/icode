import faulthandler
import sys
import os
import importlib

sys.dont_write_bytecode = True
faulthandler.enable()
src_path = "src"
root_path = os.getcwd()

if getattr(sys, 'frozen', False):
    root_path = os.path.dirname(sys.executable)
    os.chdir(root_path+os.sep+src_path)
else:
    root_path = os.getcwd()
    os.chdir(root_path+os.sep+src_path)
    
main_path = os.getcwd()

sys.path.append(main_path + f"{os.sep}smartcode{os.sep}extensions")
sys.path.append(main_path + f"{os.sep}smartcode{os.sep}IEK")
sys.path.append(root_path + f"{os.sep}frameworks")
sys.path.append(main_path + f"{os.sep}smartcode")
sys.path.append(root_path)
sys.path.append(main_path)

main = importlib.import_module("main", "src")
main.run()