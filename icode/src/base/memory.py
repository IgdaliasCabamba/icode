import pickle
import os
from .system import BASE_PATH, SYS_SEP, make_dirs
import pathlib

icode_data_file = f'{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}data{SYS_SEP}memory{SYS_SEP}data.idt'
need_dirs = [os.path.join(BASE_PATH, 'smartcode', 'data'), os.path.join(BASE_PATH, 'smartcode', 'data', 'memory')]
make_dirs(need_dirs)

# Making a sure that memory file exist before try to load it
try:
    with open(icode_data_file, 'x') as fp:
        pass
except:pass

# Default memory in case of memory file is empty
MEMORY = {
    "icode":{
        "editing":[],
        "paths":{
            "current-path":str(pathlib.Path.home())
        }
    },
    "April":{
        "settings":{}
    }
}

def write(key:object, value:object) -> None:
    """Write value in key of memory"""
    MEMORY[key] = value

def write_append(key:object, value:object) -> None:
    """Write value in last position of key of memory"""
    if isinstance(MEMORY[key], list):
        MEMORY[key].append(value)

def write_insert(key:object, pos:int, value:object) -> None:
    """Write value in given position of key of memory"""
    if isinstance(MEMORY[key], list):
        MEMORY[key].insert(pos, value)

def write_add(key:object, new_key:object, value:object) -> None:
    """Write value in new key of key of memory"""
    if isinstance(MEMORY[key], dict):
        MEMORY[key][new_key]=value

def read(key:object) -> object:
    """Read the memory in a given key"""
    return MEMORY[key]

def save_memory() -> None:
    """Dump the entire memory"""
    with open(icode_data_file, 'wb') as file:
        pickle.dump(MEMORY, file)

def restore_memory() -> None:
    """Load the entire memory"""
    global MEMORY
    try:
        with open(icode_data_file, 'rb') as file:
            MEMORY = pickle.load(file)
    except EOFError:
        pass

restore_memory() # calling this to load memory on startup