from . import *

class NoneLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        self.styles_num = 1
        
    def language(self):
        return "none"

    def description(self, style):
        return ""

    def styleText(self, start, end):
        pass

    def set_style_api(self, style):
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))
    