from . import *
from .utils import *

class CSSLexer(QsciLexerCSS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.style = None
        self.styles_num = 24

    def language(self):
        return "css"
    
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