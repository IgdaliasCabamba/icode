from . import *
from system import SYS_NAME

class JavaScriptLexer(QsciLexerJavaScript):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent

        self.styles_num = 28

    def language(self):
        return "javascript"
    
    def set_style_api(self, style):
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))

        self.setColor(QColor(style["Default"]["fg"]), QsciLexerJavaScript.Default)
        self.setColor(QColor(style["Comment"]["fg"]), QsciLexerJavaScript.Comment)
        self.setColor(QColor(style["CommentLine"]["fg"]), QsciLexerJavaScript.CommentLine)
        self.setColor(QColor(style["CommentDoc"]["fg"]), QsciLexerJavaScript.CommentDoc)
        self.setColor(QColor(style["Number"]["fg"]), QsciLexerJavaScript.Number)
        self.setColor(QColor(style["Keyword"]["fg"]), QsciLexerJavaScript.Keyword)
        self.setColor(QColor(style["DoubleQuotedString"]["fg"]), QsciLexerJavaScript.DoubleQuotedString)
        self.setColor(QColor(style["SingleQuotedString"]["fg"]), QsciLexerJavaScript.SingleQuotedString)
        self.setColor(QColor(style["UUID"]["fg"]), QsciLexerJavaScript.UUID)
        self.setColor(QColor(style["PreProcessor"]["fg"]), QsciLexerJavaScript.PreProcessor)
        self.setColor(QColor(style["Operator"]["fg"]), QsciLexerJavaScript.Operator)
        self.setColor(QColor(style["Identifier"]["fg"]), QsciLexerJavaScript.Identifier)
        self.setColor(QColor(style["UnclosedString"]["fg"]), QsciLexerJavaScript.UnclosedString)
        self.setColor(QColor(style["VerbatimString"]["fg"]), QsciLexerJavaScript.VerbatimString)
        self.setColor(QColor(style["Regex"]["fg"]), QsciLexerJavaScript.Regex)
        self.setColor(QColor(style["CommentLineDoc"]["fg"]), QsciLexerJavaScript.CommentLineDoc)
        self.setColor(QColor(style["KeywordSet2"]["fg"]), QsciLexerJavaScript.KeywordSet2)
        self.setColor(QColor(style["CommentDocKeyword"]["fg"]), QsciLexerJavaScript.CommentDocKeyword)
        self.setColor(QColor(style["GlobalClass"]["fg"]), QsciLexerJavaScript.GlobalClass)
        self.setColor(QColor(style["RawString"]["fg"]), QsciLexerJavaScript.RawString)
        self.setColor(QColor(style["TripleQuotedVerbatimString"]["fg"]), QsciLexerJavaScript.TripleQuotedVerbatimString)
        self.setColor(QColor(style["HashQuotedString"]["fg"]), QsciLexerJavaScript.HashQuotedString)
        self.setColor(QColor(style["PreProcessorComment"]["fg"]), QsciLexerJavaScript.PreProcessorComment)
        self.setColor(QColor(style["PreProcessorCommentLineDoc"]["fg"]), QsciLexerJavaScript.PreProcessorCommentLineDoc)
        self.setColor(QColor(style["UserLiteral"]["fg"]), QsciLexerJavaScript.UserLiteral)
        self.setColor(QColor(style["TaskMarker"]["fg"]), QsciLexerJavaScript.TaskMarker)
        self.setColor(QColor(style["EscapeSequence"]["fg"]), QsciLexerJavaScript.EscapeSequence)

        self.setPaper(QColor(style["Default"]["bg"]), QsciLexerJavaScript.Default)
        self.setPaper(QColor(style["Comment"]["bg"]), QsciLexerJavaScript.Comment)
        self.setPaper(QColor(style["CommentLine"]["bg"]), QsciLexerJavaScript.CommentLine)
        self.setPaper(QColor(style["CommentDoc"]["bg"]), QsciLexerJavaScript.CommentDoc)
        self.setPaper(QColor(style["Number"]["bg"]), QsciLexerJavaScript.Number)
        self.setPaper(QColor(style["Keyword"]["bg"]), QsciLexerJavaScript.Keyword)
        self.setPaper(QColor(style["DoubleQuotedString"]["bg"]), QsciLexerJavaScript.DoubleQuotedString)
        self.setPaper(QColor(style["SingleQuotedString"]["bg"]), QsciLexerJavaScript.SingleQuotedString)
        self.setPaper(QColor(style["UUID"]["bg"]), QsciLexerJavaScript.UUID)
        self.setPaper(QColor(style["PreProcessor"]["bg"]), QsciLexerJavaScript.PreProcessor)
        self.setPaper(QColor(style["Operator"]["bg"]), QsciLexerJavaScript.Operator)
        self.setPaper(QColor(style["Identifier"]["bg"]), QsciLexerJavaScript.Identifier)
        self.setPaper(QColor(style["UnclosedString"]["bg"]), QsciLexerJavaScript.UnclosedString)
        self.setPaper(QColor(style["VerbatimString"]["bg"]), QsciLexerJavaScript.VerbatimString)
        self.setPaper(QColor(style["Regex"]["bg"]), QsciLexerJavaScript.Regex)
        self.setPaper(QColor(style["CommentLineDoc"]["bg"]), QsciLexerJavaScript.CommentLineDoc)
        self.setPaper(QColor(style["KeywordSet2"]["bg"]), QsciLexerJavaScript.KeywordSet2)
        self.setPaper(QColor(style["CommentDocKeyword"]["bg"]), QsciLexerJavaScript.CommentDocKeyword)
        self.setPaper(QColor(style["GlobalClass"]["bg"]), QsciLexerJavaScript.GlobalClass)
        self.setPaper(QColor(style["RawString"]["bg"]), QsciLexerJavaScript.RawString)
        self.setPaper(QColor(style["TripleQuotedVerbatimString"]["bg"]), QsciLexerJavaScript.TripleQuotedVerbatimString)
        self.setPaper(QColor(style["HashQuotedString"]["bg"]), QsciLexerJavaScript.HashQuotedString)
        self.setPaper(QColor(style["PreProcessorComment"]["bg"]), QsciLexerJavaScript.PreProcessorComment)
        self.setPaper(QColor(style["PreProcessorCommentLineDoc"]["bg"]), QsciLexerJavaScript.PreProcessorCommentLineDoc)
        self.setPaper(QColor(style["UserLiteral"]["bg"]), QsciLexerJavaScript.UserLiteral)
        self.setPaper(QColor(style["TaskMarker"]["bg"]), QsciLexerJavaScript.TaskMarker)
        self.setPaper(QColor(style["EscapeSequence"]["bg"]), QsciLexerJavaScript.EscapeSequence)
