from . import *
from system import SYS_NAME

class JSONLexer(QsciLexerJSON):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent

        self.styles_num = 14
    
    def language(self):
        return "json"
    
    def set_style_api(self, style):
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))
        
        self.setColor(QColor(style["Default"]["fg"]), QsciLexerJSON.Default)
        self.setColor(QColor(style["Comment"]["fg"]), QsciLexerJSON.CommentLine)
        self.setColor(QColor(style["Number"]["fg"]), QsciLexerJSON.Number)
        self.setColor(QColor(style["String"]["fg"]), QsciLexerJSON.String)
        self.setColor(QColor(style["EscapeSequence"]["fg"]), QsciLexerJSON.EscapeSequence)
        self.setColor(QColor(style["Property"]["fg"]), QsciLexerJSON.Property)
        self.setColor(QColor(style["Keyword"]["fg"]), QsciLexerJSON.Keyword)
        self.setColor(QColor(style["KeywordLD"]["fg"]), QsciLexerJSON.KeywordLD)
        self.setColor(QColor(style["Operator"]["fg"]), QsciLexerJSON.Operator)
        self.setColor(QColor(style["CommentBlock"]["fg"]), QsciLexerJSON.CommentBlock)
        self.setColor(QColor(style["UnclosedString"]["fg"]), QsciLexerJSON.UnclosedString)
        self.setColor(QColor(style["Error"]["fg"]), QsciLexerJSON.Error)
        self.setColor(QColor(style["IRICompact"]["fg"]), QsciLexerJSON.IRICompact)
        self.setColor(QColor(style["IRI"]["fg"]), QsciLexerJSON.IRI)
        
        self.setPaper(QColor(style["Default"]["bg"]), QsciLexerJSON.Default)
        self.setPaper(QColor(style["Comment"]["bg"]), QsciLexerJSON.CommentLine)
        self.setPaper(QColor(style["Number"]["bg"]), QsciLexerJSON.Number)
        self.setPaper(QColor(style["String"]["bg"]), QsciLexerJSON.String)
        self.setPaper(QColor(style["EscapeSequence"]["bg"]), QsciLexerJSON.EscapeSequence)
        self.setPaper(QColor(style["Property"]["bg"]), QsciLexerJSON.Property)
        self.setPaper(QColor(style["Keyword"]["bg"]), QsciLexerJSON.Keyword)
        self.setPaper(QColor(style["KeywordLD"]["bg"]), QsciLexerJSON.KeywordLD)
        self.setPaper(QColor(style["Operator"]["bg"]), QsciLexerJSON.Operator)
        self.setPaper(QColor(style["CommentBlock"]["bg"]), QsciLexerJSON.CommentBlock)
        self.setPaper(QColor(style["UnclosedString"]["bg"]), QsciLexerJSON.UnclosedString)
        self.setPaper(QColor(style["Error"]["bg"]), QsciLexerJSON.Error)
        self.setPaper(QColor(style["IRICompact"]["bg"]), QsciLexerJSON.IRICompact)
        self.setPaper(QColor(style["IRI"]["bg"]), QsciLexerJSON.IRI)