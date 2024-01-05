from core.system import SMARTCODE_PATH, ROOT_PATH, SYS_NAME
import os
from pathlib import Path
import smartlibs.mjson as ijson
from core.storer import CacheManager, DataManager

user_cache = CacheManager(str(Path(ROOT_PATH)
                          .joinpath(".cache")
                          .joinpath("user")
                          .joinpath("user.idt")))

editor_cache = CacheManager(str(Path(ROOT_PATH)
                            .joinpath(".cache")
                            .joinpath(".editors")
                            .joinpath("cache.idt").as_posix()))

april_cache = CacheManager(str(Path(ROOT_PATH).joinpath(".cache").joinpath("april").joinpath("cache.idt").as_posix()))

qt_cache = CacheManager(str(Path(ROOT_PATH).joinpath(".cache").joinpath("user").joinpath("cache.idt").as_posix()))

labels_cache = CacheManager(str(Path(ROOT_PATH).joinpath(".cache").joinpath("labs").joinpath("labels.idt").as_posix()))

DATA_FILE = Path(SMARTCODE_PATH).joinpath("code").joinpath("settings.json")
TERMINALS_FILE = Path(SMARTCODE_PATH).joinpath("code").joinpath("terminals.json")
EDITOR_FILE = Path(SMARTCODE_PATH).joinpath("code").joinpath("editor.json")

note_file_path = Path(ROOT_PATH).joinpath(".cache").joinpath("labs").joinpath("notes.txt")

cache_directorys = [
    os.path.join(ROOT_PATH, ".cache", "labs"),
    os.path.join(ROOT_PATH, ".cache", "april"),
    os.path.join(ROOT_PATH, ".cache", "editors"),
    os.path.join(ROOT_PATH, ".cache", "extensions"),
    os.path.join(ROOT_PATH, "smartcode", "code"),
    os.path.join(ROOT_PATH, "smartcode", "data"),
    os.path.join(ROOT_PATH, "smartcode", "data", "user"),
    os.path.join(ROOT_PATH, "smartcode", "data", "memory"),
    os.path.join(ROOT_PATH, "smartcode", "data", "extensions"),
]


def build_app_dirs():
    for cache_directory in cache_directorys:
        if not os.path.exists(cache_directory):
            os.makedirs(cache_directory)


def build_notes_file():
    if not note_file_path.exists() or not note_file_path.is_file():
        with open(note_file_path, "x") as file:
            pass


build_app_dirs()
build_notes_file()


def save_data():
    pass


ext_python = {".py", ".pyw", ".pyi", ".scons", ".w"}
ext_cython = {".pyx", ".pxd", ".pxi"}
ext_c = {".c", ".h"}
ext_cpp = {".c++", ".h++", ".cc", ".hh", ".cpp", ".hpp", ".cxx", ".hxx"}
ext_pascal = {".pas", ".pp", ".lpr", ".cyp"}
ext_oberon = {".mod", ".ob", ".ob2", ".cp"}
ext_ada = {".ads", ".adb"}
ext_json = {".json"}
ext_lua = {".lua"}
ext_d = {".d"}
ext_nim = {".nim", ".nims"}
ext_perl = {".pl", ".pm"}
ext_xml = {".xml", ".tpy"}
ext_batch = {".bat", ".batch"}
ext_bash = {".sh"}
ext_ini = {".ini"}
ext_text = {".txt", ".text"}
ext_coffeescript = {".coffee"}
ext_csharp = {".cs"}
ext_java = {".java"}
ext_javascript = {".js"}
ext_octave = {".m"}
ext_routeros = {".rsc"}
ext_sql = {".sql"}
ext_postscript = {
    ".ps",
}
ext_fortran = {".f90", ".f95", ".f03"}
ext_fortran77 = {".f", ".for"}
ext_idl = {".idl"}
ext_ruby = {".rb", ".rbw"}
ext_html = {".html", ".htm"}
ext_css = {".css"}
ext_awk = {".awk"}
ext_cicode = {".ci"}
ext_yaml = {".yaml", ".yml"}
ext_markdown = {".md", ".MARKDOWN", ".rst"}
