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
    ButtonPrimary = 207
    ButtonSecondary = 208
    ButtonDisabled = 209
    AnnotationTodo = 210
    AnnotationWarning = 211
    AnnotationBug = 212
    AnnotationDisabled = 213
    AnnotationTip = 214
    AnnotationDone = 215
    AnnotationLabel = 216
    AnnotationButtonPrimary = 217
    AnnotationButtonSecondary = 218
    AnnotationButtonDisabled = 219

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