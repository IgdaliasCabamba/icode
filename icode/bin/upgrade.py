import tarfile
import hjson
import os
import shutil
import pathlib

cwd = os.getcwd()

def get_header():
    with open("headers.json", "r") as f:
        header = hjson.load(f)
        
    #dirs_to_remove = header["path"]["rem-dirs"]
    #files_to_remove = header["path"]["rem-files"]
    return header

def get_path(dir:str):
    dir = dir.replace(">", os.sep)
    dir = os.path.join(cwd, dir)
    return dir

def remove_dirs():
    for dir in dirs_to_remove:
        x = get_path(dir)
        if os.path.exists(x):
            try:
                shutil.rmtree(x)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

def remove_files():
    for file in files_to_remove:
        file = get_path(file)
        if os.path.exists(file):
            os.remove(file)

print("YEE")