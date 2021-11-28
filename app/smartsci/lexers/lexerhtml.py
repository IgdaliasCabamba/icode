from . import *
from system import SYS_NAME

class HTMLLexer(QsciLexerHTML):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        
        self.styles_num = 128

    def language(self):
        return "html"
    
    def set_style_api(self, api):
        style = api["lexer-styles"]
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))
    