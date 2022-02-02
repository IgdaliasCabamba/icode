from PyQt5.Qsci import *
from PyQt5.QtGui import *

class ILexer:
    Todo = 200
    Warning = 201
    Bug = 202
    Disabled = 203
    Tip = 204
    Done = 205
    Label = 206
    AnnotationTodo = 207
    AnnotationWarning = 208
    AnnotationBug = 209
    AnnotationDisabled = 210
    AnnotationTip = 211
    AnnotationDone = 212
    AnnotationLabel = 213

from .lexerc import *
from .lexercpp import *
from .lexercss import *
from .lexerhtml import *
from .lexerjson import *
from .lexerjavascript import *
from .lexerpython import *
from .lexernone import *
from .lexerjava import *
from .lexeryaml import *
from .lexermarkdown import *