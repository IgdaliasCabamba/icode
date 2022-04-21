import re
import keyword
import textwrap
import sys
from pycodestyle import *

EXCEPTIONS_REGEX = str()
EXCEPTIONS_REGEX += "BaseException||FileNotFoundError||Exception||ArithmeticError||"
EXCEPTIONS_REGEX += (
    "BufferError||LookupError||AssertionError||AttributeError||EOFError||"
)
EXCEPTIONS_REGEX += "NameError"

BUILTIN_EXCEPTIONS = [
    "BaseException",
    "FileNotFoundError",
    "Exception",
    "ArithmeticError",
    "BufferError",
    "LookupError",
    "AssertionError",
    "AttributeError",
    "EOFError",
    "NameError",
]

DEBUG_STATUS_REGEX = re.compile("([_a-z-A-Z-0-9]*.py)\\(([0-9]*)\\)<([_a-z-A-Z-0-9]*)>")
DEBUG_RETURN_REGEX = re.compile("(->) (.*)")
DEBUG_CONTEXT_REGEX = re.compile("(Pdb)")
DEBUG_EXCEPTION_REGEX = re.compile(f"({EXCEPTIONS_REGEX})(:)(.*)")

builtin_functions = {
    "abs": "(x)",
    "all": "(iterable)",
    "any": "(iterable)",
    "ascii": "(object)",
    "bin": "(x)",
    "breakpoint": "(*args, **kws)",
    "callable": "(object)",
    "chr": "(i)",
    "compile": "(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)",
    "delattr": "(object, name)",
    "dir": "([object])",
    "divmod": "(a, b)",
    "enumerate": "(iterable, start=0)",
    "eval": "(expression[, globals[, locals]])",
    "exec": "(object[, globals[, locals]])",
    "filter": "(function, iterable)",
    "format": "(value[, format_spec])",
    "getattr": "(object, name[, default])",
    "hasattr": "(object, name)",
    "hash": "(object)",
    "help": "([object])",
    "hex": "(x)",
    "id": "(object)",
    "input": "([prompt])",
    "isinstance": "(object, classinfo)",
    "issubclass": "(class, classinfo)",
    "iter": "(object[, sentinel])",
    "len": "(s)",
    "map": "(function, iterable, ...)",
    "max": "(iterable, *[, key, default])||(arg1, arg2, *args[, key])",
    "min": "(iterable, *[, key, default])||(arg1, arg2, *args[, key])",
    "next": "(iterator[, default])",
    "oct": "(x)",
    "open": "(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)",
    "ord": "(c)",
    "pow": "(base, exp[, mod])",
    "print": r"(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)",
    "repr": "(object)",
    "reversed": "(seq)",
    "round": "(number[, ndigits])",
    "setattr": "(object, name, value)",
    "sorted": "(iterable, *, key=None, reverse=False)",
    "sum": "(iterable, /, start=0)",
    "super": "([type[, object-or-type]])",
    "vars": "([object])",
    "zip": "(*iterables)",
}
primitive_types = {
    "int": "int(x, base=10)",
    "str": "str(object=b'', encoding='utf-8', errors='strict')",
    "float": "float([x])",
    "bool": "bool([x])",
}
builtin_classes = {
    "tuple": "tuple([iterable])",
    "list": "list([iterable])",
    "set": "set([iterable])",
    "dict": "dict(mapping, **kwarg)",
}
python_key_list = [
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "super",
    "try",
    "while",
    "with",
    "yield",
]
python_extra_key_list = [
    "False",
    "True",
    "None",
    "self",
    "int",
    "str",
    "object",
    "list",
    "set",
    "dict",
    "tuple",
    "float",
    "bool",
    "byte",
]
