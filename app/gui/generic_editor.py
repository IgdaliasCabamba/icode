from PyQt5.Qsci import *
from PyQt5.QtGui import QColor
from functions import getfn

class Editor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUtf8(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabIndents(False)
        self.apply_styles(getfn.get_editor_styles())
        
    
    def set_text(self, text:str) -> None:
        self.setText(text)
    
    def set_lexer(self, lexer:object) -> None:
        self.setLexer(lexer)
        font=getfn.get_native_font()
        font.setPixelSize(1)
        font.setPointSizeF(10.5)
        font.setBold(False)
        lexer.setDefaultFont(font)
        
        end_styles = lexer.styles_num
        
        for i in range(0, end_styles):
            lexer.setFont(font, i)
        
        lexer.set_style_api(getfn.get_lexer_colors())
            
        
    def apply_styles(self, styles):
        self.setColor(QColor(styles["color"]))
        self.setPaper(QColor(styles["paper"]))
        self.setMarginsBackgroundColor(QColor(styles["margin-background"]))
        self.setMarginsForegroundColor(QColor(styles["margin-foreround"]))
        self.setSelectionForegroundColor(QColor(styles["selection-foreground"]))
        self.setWhitespaceBackgroundColor(QColor(styles["whitespace-background"]))
        self.setWhitespaceForegroundColor(QColor(styles["whitespace-foreground"]))