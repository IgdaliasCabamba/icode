from . import *
from .utils import *

python_key_list=['and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'super', 'try', 'while', 'with', 'yield']
python_extra_key_list=['False','True', 'None', 'self', 'int', 'str', 'object', 'list', 'set', 'dict', 'tuple', 'float', 'bool', 'byte']

class PythonLexer(QsciLexerPython, ILexer):
    def __init__(self, parent=None):
        super().__init__()
        self.parent=parent
        self.python_extra_key_list=python_extra_key_list
        self.python_key_list=python_key_list
        self.style = None
    
    def styleText(self, start, end):
        super().styleText(start, end)
        self.setStyling(None, self.Bug)
        self.setStyling(None, self.Todo)
        self.setStyling(None, self.Warning)
        self.setStyling(None, self.Disabled)
        self.setStyling(None, self.Done)
        self.setStyling(None, self.Tip)
        self.setStyling(None, self.Label)
        self.setStyling(None, self.AnnotationBug)
        self.setStyling(None, self.AnnotationTodo)
        self.setStyling(None, self.AnnotationWarning)
        self.setStyling(None, self.AnnotationDisabled)
        self.setStyling(None, self.AnnotationDone)
        self.setStyling(None, self.AnnotationTip)
        self.setStyling(None, self.AnnotationLabel)
    
    def keywords(self, keyset):
        if keyset == 1:
            return ' '.join(self.python_key_list) + ' ' + QsciLexerPython().keywords(keyset)
        elif keyset == 2:
            return ' '.join(self.python_extra_key_list)
        return QsciLexerPython.keywords(self, keyset)
    
    @staticmethod
    def add_extra_keywords(keys:list):
        for key in keys:
            if not key in self.python_extra_key_list:
                self.python_extra_key_list.append(key)
            continue
    
    def language(self):
        return "python"
    
    def set_style_api(self, style:dict):    
        try:
            x = "@lexer-"+self.language()
            if x in style.keys():
                style = style[x]
                
            self.style = style
        
            self.setDefaultColor(QColor(style["DefaultColor"]))
            self.setDefaultPaper(QColor(style["DefaultPaper"]))
            self.setDefaultFont(made_font(style["DefaultFont"]))
            
            for key, value in style.items():        
                hint = getattr(self, key, None)
                if isinstance(hint, int):
                    self.setColor(QColor(style[key]["fg"]), hint)
                    self.setPaper(QColor(style[key]["bg"]), hint)
                    self.setFont(made_font(style[key]["font"]), hint) 
        except Exception as e:
            print(e)