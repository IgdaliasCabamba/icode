from . import *
from system import SYS_NAME

class CSSLexer(QsciLexerCSS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent

        self.styles_num = 24

    def language(self):
        return "css"
    
    def set_style_api(self, api):
        style = api["lexer-styles"]
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))
    