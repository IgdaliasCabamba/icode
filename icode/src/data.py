from base.system import SYS_SEP, BASE_PATH, SYS_NAME
import os
from pathlib import Path
from frameworks import jedit2 as ijson
from base.icache import CacheManager
from base.isetting import DataManager

user_cache = CacheManager(
    f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}user{SYS_SEP}user.idt")

editor_cache = CacheManager(
    f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}editors{SYS_SEP}cache.idt")

april_cache = CacheManager(
    f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}april{SYS_SEP}cache.idt")

assistant_cache = CacheManager(
    f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}april{SYS_SEP}bot.idt")

DATA_FILE = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}data{SYS_SEP}settings.json"
TERMINALS_FILE = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}data{SYS_SEP}terminals.json"
EDITOR_FILE = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}data{SYS_SEP}editor.json"
app_settings = DataManager(f"{BASE_PATH}{SYS_SEP}data{SYS_SEP}data.idt")
qt_cache = CacheManager(BASE_PATH+SYS_SEP+".cache"+SYS_SEP+"user"+SYS_SEP+"cache.idt")
labels_cache = CacheManager(BASE_PATH+SYS_SEP+".cache"+SYS_SEP+"labs"+SYS_SEP+"labels.idt")

note_file_path = f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}labs{SYS_SEP}notes.txt"
note_file_path_obj = Path(note_file_path)

cache_directorys = [
    os.path.join(BASE_PATH, '.cache', 'editors'),
    os.path.join(BASE_PATH, '.cache', 'labs'),
    os.path.join(BASE_PATH, '.cache', 'april'),
]


def build_app_dirs():
    for cache_directory in cache_directorys:
        if not os.path.exists(cache_directory):
            os.makedirs(cache_directory)    

def build_notes_file():
    if not note_file_path_obj.exists() or not note_file_path_obj.is_file():
        with open(note_file_path, "x") as file:
            pass
    
build_app_dirs()
build_notes_file()

smartcode_directory = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}"

def save_data():
    pass
    

ext_python              = {".py", ".pyw", ".pyi", ".scons", ".w"}
ext_cython              = {".pyx", ".pxd", ".pxi"}
ext_c                   = {".c", ".h"}
ext_cpp                 = {".c++", ".h++", ".cc", ".hh", ".cpp", ".hpp", ".cxx", ".hxx"}
ext_pascal              = {".pas", ".pp", ".lpr", ".cyp"}
ext_oberon              = {".mod", ".ob", ".ob2", ".cp"}
ext_ada                 = {".ads", ".adb"}
ext_json                = {".json"}
ext_lua                 = {".lua"}
ext_d                   = {".d"}
ext_nim                 = {".nim", ".nims"}
ext_perl                = {".pl", ".pm"}
ext_xml                 = {".xml", ".tpy"}
ext_batch               = {".bat",  ".batch"}
ext_bash                = {".sh"}
ext_ini                 = {".ini"}
ext_text                = {".txt", ".text"}
ext_coffeescript        = {".coffee"}
ext_csharp              = {".cs"}
ext_java                = {".java"}
ext_javascript          = {".js"}
ext_octave              = {".m"}
ext_routeros            = {".rsc"}
ext_sql                 = {".sql"}
ext_postscript          = {".ps",}
ext_fortran             = {".f90", ".f95", ".f03"}
ext_fortran77           = {".f", ".for"}
ext_idl                 = {".idl"}
ext_ruby                = {".rb", ".rbw"}
ext_html                = {".html", ".htm"}
ext_css                 = {".css"}
ext_awk                 = {".awk"}
ext_cicode              = {".ci"}
ext_yaml                = {".yaml", ".yml"}
ext_markdown            = {".md", ".MARKDOWN", ".rst"} 