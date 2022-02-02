icode_packages=[
"os",
"sys",
"tarfile",
"appdirs",
"attrs",
"automat",
"bs4",
"cachelib",
"certifi",
"characteristic",
"charset_normalizer",
"click",
"commonmark",
"constantly",
"cssselect",
"deprecated",
"github",
"hjson",
"hyperlink",
"idna",
"importlib_metadata",
"incremental",
"jwt",
"keep",
"klein",
"lxml",
"nacl",
"packaging",
"patchelf",
"pycparser",
"pygit2",
"pygments",
"pyparsing",
"pyperclip",
"PyQt5",
"PyQt5.Qsci",
"pyquery",
"qtpy",
"requests",
"shamanld",
"six",
"soupsieve",
"terminaltables",
"toml",
"tubes",
"typing_extensions",
"urllib3",
"validus",
"werkzeug",
"wikipedia",
"wrapt",
"zipp",
"zope.interface",
# Special libs
"cffi",
"filecmp"]

import twisted

from os import *
from sys import *
from tarfile import *
from appdirs import *
from attrs import *
from automat import *
from bs4 import *
from cachelib import *
from certifi import *
from characteristic import *
from charset_normalizer import *
from click import *
from commonmark import *
from constantly import *
from cssselect import *
from cx_Freeze import *
from deprecated import *
from github import *
from hjson import *
from hyperlink import *
from idna import *
from importlib_metadata import *
from incremental import *
from jwt import *
from keep import *
from klein import *
from lxml import *
from nacl import *
from packaging import *
from patchelf import *
from pycparser import *
from pygit2 import *
from pygments import *
from pyparsing import *
from pyperclip import *
from PyQt5 import *
from PyQt5.Qsci import *
from pyquery import *
from qtpy import *
from requests import *
from shamanld import *
from six import *
from soupsieve import *
from terminaltables import *
from toml import *
from tubes import *
from twisted import *
from typing_extensions import *
from urllib3 import *
from validus import *
from werkzeug import *
from wikipedia import *
from wrapt import *
from zipp import *
from zope.interface import *

build_exe_options = {"packages": icode_packages, "excludes": ["tkinter"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "icode",
    version = "0.1",
    description = "Smart Code Editor",
    options = {"build_exe": build_exe_options},
    executables = [Executable("app.py", base=base)]
)
