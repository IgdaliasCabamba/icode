from . import *
from system import SYS_NAME

class CPPLexer(QsciLexerCPP):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        
        self.styles_num = 28
    
    def language(self):
        return "c++"
    
    def set_style_api(self, style):
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))

        self.setColor(QColor(style["Default"]["fg"]), QsciLexerCPP.Default)
        self.setColor(QColor(style["Comment"]["fg"]), QsciLexerCPP.Comment)
        self.setColor(QColor(style["CommentLine"]["fg"]), QsciLexerCPP.CommentLine)
        self.setColor(QColor(style["CommentDoc"]["fg"]), QsciLexerCPP.CommentDoc)
        self.setColor(QColor(style["Number"]["fg"]), QsciLexerCPP.Number)
        self.setColor(QColor(style["Keyword"]["fg"]), QsciLexerCPP.Keyword)
        self.setColor(QColor(style["DoubleQuotedString"]["fg"]), QsciLexerCPP.DoubleQuotedString)
        self.setColor(QColor(style["SingleQuotedString"]["fg"]), QsciLexerCPP.SingleQuotedString)
        self.setColor(QColor(style["UUID"]["fg"]), QsciLexerCPP.UUID)
        self.setColor(QColor(style["PreProcessor"]["fg"]), QsciLexerCPP.PreProcessor)
        self.setColor(QColor(style["Operator"]["fg"]), QsciLexerCPP.Operator)
        self.setColor(QColor(style["Identifier"]["fg"]), QsciLexerCPP.Identifier)
        self.setColor(QColor(style["UnclosedString"]["fg"]), QsciLexerCPP.UnclosedString)
        self.setColor(QColor(style["VerbatimString"]["fg"]), QsciLexerCPP.VerbatimString)
        self.setColor(QColor(style["Regex"]["fg"]), QsciLexerCPP.Regex)
        self.setColor(QColor(style["CommentLineDoc"]["fg"]), QsciLexerCPP.CommentLineDoc)
        self.setColor(QColor(style["KeywordSet2"]["fg"]), QsciLexerCPP.KeywordSet2)
        self.setColor(QColor(style["CommentDocKeyword"]["fg"]), QsciLexerCPP.CommentDocKeyword)
        self.setColor(QColor(style["GlobalClass"]["fg"]), QsciLexerCPP.GlobalClass)
        self.setColor(QColor(style["RawString"]["fg"]), QsciLexerCPP.RawString)
        self.setColor(QColor(style["TripleQuotedVerbatimString"]["fg"]), QsciLexerCPP.TripleQuotedVerbatimString)
        self.setColor(QColor(style["HashQuotedString"]["fg"]), QsciLexerCPP.HashQuotedString)
        self.setColor(QColor(style["PreProcessorComment"]["fg"]), QsciLexerCPP.PreProcessorComment)
        self.setColor(QColor(style["PreProcessorCommentLineDoc"]["fg"]), QsciLexerCPP.PreProcessorCommentLineDoc)
        self.setColor(QColor(style["UserLiteral"]["fg"]), QsciLexerCPP.UserLiteral)
        self.setColor(QColor(style["TaskMarker"]["fg"]), QsciLexerCPP.TaskMarker)
        self.setColor(QColor(style["EscapeSequence"]["fg"]), QsciLexerCPP.EscapeSequence)

        self.setPaper(QColor(style["Default"]["bg"]), QsciLexerCPP.Default)
        self.setPaper(QColor(style["Comment"]["bg"]), QsciLexerCPP.Comment)
        self.setPaper(QColor(style["CommentLine"]["bg"]), QsciLexerCPP.CommentLine)
        self.setPaper(QColor(style["CommentDoc"]["bg"]), QsciLexerCPP.CommentDoc)
        self.setPaper(QColor(style["Number"]["bg"]), QsciLexerCPP.Number)
        self.setPaper(QColor(style["Keyword"]["bg"]), QsciLexerCPP.Keyword)
        self.setPaper(QColor(style["DoubleQuotedString"]["bg"]), QsciLexerCPP.DoubleQuotedString)
        self.setPaper(QColor(style["SingleQuotedString"]["bg"]), QsciLexerCPP.SingleQuotedString)
        self.setPaper(QColor(style["UUID"]["bg"]), QsciLexerCPP.UUID)
        self.setPaper(QColor(style["PreProcessor"]["bg"]), QsciLexerCPP.PreProcessor)
        self.setPaper(QColor(style["Operator"]["bg"]), QsciLexerCPP.Operator)
        self.setPaper(QColor(style["Identifier"]["bg"]), QsciLexerCPP.Identifier)
        self.setPaper(QColor(style["UnclosedString"]["bg"]), QsciLexerCPP.UnclosedString)
        self.setPaper(QColor(style["VerbatimString"]["bg"]), QsciLexerCPP.VerbatimString)
        self.setPaper(QColor(style["Regex"]["bg"]), QsciLexerCPP.Regex)
        self.setPaper(QColor(style["CommentLineDoc"]["bg"]), QsciLexerCPP.CommentLineDoc)
        self.setPaper(QColor(style["KeywordSet2"]["bg"]), QsciLexerCPP.KeywordSet2)
        self.setPaper(QColor(style["CommentDocKeyword"]["bg"]), QsciLexerCPP.CommentDocKeyword)
        self.setPaper(QColor(style["GlobalClass"]["bg"]), QsciLexerCPP.GlobalClass)
        self.setPaper(QColor(style["RawString"]["bg"]), QsciLexerCPP.RawString)
        self.setPaper(QColor(style["TripleQuotedVerbatimString"]["bg"]), QsciLexerCPP.TripleQuotedVerbatimString)
        self.setPaper(QColor(style["HashQuotedString"]["bg"]), QsciLexerCPP.HashQuotedString)
        self.setPaper(QColor(style["PreProcessorComment"]["bg"]), QsciLexerCPP.PreProcessorComment)
        self.setPaper(QColor(style["PreProcessorCommentLineDoc"]["bg"]), QsciLexerCPP.PreProcessorCommentLineDoc)
        self.setPaper(QColor(style["UserLiteral"]["bg"]), QsciLexerCPP.UserLiteral)
        self.setPaper(QColor(style["TaskMarker"]["bg"]), QsciLexerCPP.TaskMarker)
        self.setPaper(QColor(style["EscapeSequence"]["bg"]), QsciLexerCPP.EscapeSequence)
    