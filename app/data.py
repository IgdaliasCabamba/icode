from system import SYS_SEP, BASE_PATH, SYS_NAME, os, Path
import json
from smartlibs import jedit2 as ijson
from smartlibs.iterm import TerminalWidget
import jedi

cache_directorys = [
    os.path.join(BASE_PATH, '.cache', 'jedi'),
    os.path.join(BASE_PATH, '.cache', 'editors'),
    os.path.join(BASE_PATH, '.cache', 'labs'),
    os.path.join(BASE_PATH, '.cache', 'april'),
    os.path.join(BASE_PATH, 'data', 'user', 'envs')
]

for cache_directory in cache_directorys:
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

note_file_path = f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}labs{SYS_SEP}notes.txt"

note_file_path_obj = Path(note_file_path)

if not note_file_path_obj.exists() or not note_file_path_obj.is_file():
    with open(note_file_path, "x") as file:
        pass

python_envs = []

env = jedi.get_default_environment()
python_envs.append(env)

if 'PYTHONPATH' in os.environ:
    envs = os.environ['PYTHONPATH'].split(os.pathsep)
    if envs:
        for env in envs:
            python_envs.append(jedi.create_environment(str(env)))

if SYS_NAME == "linux":
    try:
        python_envs.append(jedi.create_environment("/usr/bin/python3"))
        python_envs.append(jedi.create_environment("/bin/python3"))
    except Exception as e:
        print(e)
        pass

app_icon_path = f"{BASE_PATH}{SYS_SEP}data{SYS_SEP}icons{SYS_SEP}"
smartcode_directory = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}"

ext_python              = {".py", ".pyw", ".pyi", ".scons"}
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

builtin_functions={
    "abs":"(x)",
    "all":"(iterable)",
    "any":"(iterable)",
    "ascii":"(object)",
    "bin":"(x)",
    "breakpoint":"(*args, **kws)",
    "callable":"(object)",
    "chr":"(i)",
    "compile":"(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)",
    "delattr":"(object, name)",
    "dir":"([object])",
    "divmod":"(a, b)",
    "enumerate":"(iterable, start=0)",
    "eval":"(expression[, globals[, locals]])",
    "exec":"(object[, globals[, locals]])",
    "filter":"(function, iterable)",
    "format":"(value[, format_spec])",
    "getattr":"(object, name[, default])",
    "hasattr":"(object, name)",
    "hash":"(object)",
    "help":"([object])",
    "hex":"(x)",
    "id":"(object)",
    "input":"([prompt])",
    "isinstance":"(object, classinfo)",
    "issubclass":"(class, classinfo)",
    "iter":"(object[, sentinel])",
    "len":"(s)",
    "map":"(function, iterable, ...)",
    "max":"(iterable, *[, key, default])||(arg1, arg2, *args[, key])",
    "min":"(iterable, *[, key, default])||(arg1, arg2, *args[, key])",
    "next":"(iterator[, default])",
    "oct":"(x)",
    "open":"(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)",
    "ord":"(c)",
    "pow":"(base, exp[, mod])",
    "print":r"(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)",
    "repr":"(object)",
    "reversed":"(seq)",
    "round":"(number[, ndigits])",
    "setattr":"(object, name, value)",
    "sorted":"(iterable, *, key=None, reverse=False)",
    "sum":"(iterable, /, start=0)",
    "super":"([type[, object-or-type]])",
    "vars":"([object])",
    "zip":"(*iterables)"
}
primitive_types = {
    "int":"int(x, base=10)",
    "str":"str(object=b'', encoding='utf-8', errors='strict')",
    "float":"float([x])",
    "bool":"bool([x])"
}
builtin_classes = {
    "tuple":"tuple([iterable])",
    "list":"list([iterable])",
    "set":"set([iterable])",
    "dict":"dict(mapping, **kwarg)",
}

python_key_list=['and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'super', 'try', 'while', 'with', 'yield']
python_extra_key_list=['False','True', 'None', 'self', 'int', 'str', 'object', 'list', 'set', 'dict', 'tuple', 'float', 'bool', 'byte']
