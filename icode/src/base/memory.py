import pickle
import os
from .system import BASE_PATH, SYS_SEP, make_dirs

icode_data_file = f'{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}data{SYS_SEP}memory{SYS_SEP}data.idt'
need_dirs = [os.path.join(BASE_PATH, 'smartcode', 'data'), os.path.join(BASE_PATH, 'smartcode', 'data', 'memory')]
make_dirs(need_dirs)

try:
    with open(icode_data_file, 'x') as fp:
        pass
except:pass

MEMORY = {
    "icode":{
        "editing":[],
        "paths":{
            "current-path":""
        }
    }
}

def write(key:object, value:object) -> None:
    MEMORY[key] = value

def write_append(key:object, value:object) -> None:
    if isinstance(MEMORY[key], list):
        MEMORY[key].append(value)

def write_insert(key:object, pos:int, value:object) -> None:
    if isinstance(MEMORY[key], list):
        MEMORY[key].insert(pos, value)

def write_add(key:object, new_key:object, value:object) -> None:
    if isinstance(MEMORY[key], dict):
        MEMORY[key][new_key]=value

def read(key:object) -> object:
    return MEMORY[key]

def save_memory():
    with open(icode_data_file, 'wb') as file:
        pickle.dump(MEMORY, file)

def restore_memory():
    global MEMORY
    try:
        with open(icode_data_file, 'rb') as file:
            MEMORY = pickle.load(file)
    except EOFError:
        pass

restore_memory()