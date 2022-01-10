from . import *

python_key_list=['and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'super', 'try', 'while', 'with', 'yield']
python_extra_key_list=['False','True', 'None', 'self', 'int', 'str', 'object', 'list', 'set', 'dict', 'tuple', 'float', 'bool', 'byte']

class PythonLexer(QsciLexerPython):
    def __init__(self, parent=None):
        super().__init__()
        self.parent=parent
        self.python_extra_key_list=python_extra_key_list
        self.python_key_list=python_key_list

        self.styles_num = 20
    
    def keywords(self, keyset):
        if keyset == 1:
            return ' '.join(self.python_key_list) + ' ' + QsciLexerPython().keywords(keyset)
        elif keyset == 2:
            return ' '.join(self.python_extra_key_list)
        return QsciLexerPython.keywords(self, keyset)

    def add_extra_keywords(self, keys:list):
        for key in keys:
            if not key in self.python_extra_key_list:
                self.python_extra_key_list.append(key)
            continue
    
    def language(self):
        return "python"
    
    def set_style_api(self, style):
        self.setDefaultColor(QColor(style["DefaultColor"]))
        self.setDefaultPaper(QColor(style["DefaultPaper"]))

        self.setColor(QColor(style["Default"]["fg"]), QsciLexerPython.Default)
        self.setColor(QColor(style["Comment"]["fg"]), QsciLexerPython.Comment)
        self.setColor(QColor(style["Number"]["fg"]), QsciLexerPython.Number)
        self.setColor(QColor(style["DoubleQuotedString"]["fg"]), QsciLexerPython.DoubleQuotedString)
        self.setColor(QColor(style["SingleQuotedString"]["fg"]), QsciLexerPython.SingleQuotedString)
        self.setColor(QColor(style["Keyword"]["fg"]), QsciLexerPython.Keyword)
        self.setColor(QColor(style["TripleSingleQuotedString"]["fg"]), QsciLexerPython.TripleSingleQuotedString)
        self.setColor(QColor(style["TripleDoubleQuotedString"]["fg"]), QsciLexerPython.TripleDoubleQuotedString)
        self.setColor(QColor(style["ClassName"]["fg"]), QsciLexerPython.ClassName)
        self.setColor(QColor(style["FunctionMethodName"]["fg"]), QsciLexerPython.FunctionMethodName)
        self.setColor(QColor(style["Operator"]["fg"]), QsciLexerPython.Operator)
        self.setColor(QColor(style["Identifier"]["fg"]), QsciLexerPython.Identifier)
        self.setColor(QColor(style["CommentBlock"]["fg"]), QsciLexerPython.CommentBlock)
        self.setColor(QColor(style["UnclosedString"]["fg"]), QsciLexerPython.UnclosedString)
        self.setColor(QColor(style["HighlightedIdentifier"]["fg"]), QsciLexerPython.HighlightedIdentifier)
        self.setColor(QColor(style["Decorator"]["fg"]), QsciLexerPython.Decorator)
        self.setColor(QColor(style["DoubleQuotedFString"]["fg"]), QsciLexerPython.DoubleQuotedFString)
        self.setColor(QColor(style["SingleQuotedFString"]["fg"]), QsciLexerPython.SingleQuotedFString)
        self.setColor(QColor(style["TripleSingleQuotedFString"]["fg"]), QsciLexerPython.TripleSingleQuotedFString)
        self.setColor(QColor(style["TripleDoubleQuotedFString"]["fg"]), QsciLexerPython.TripleDoubleQuotedFString)

        self.setPaper(QColor(style["Default"]["bg"]), QsciLexerPython.Default)
        self.setPaper(QColor(style["Comment"]["bg"]), QsciLexerPython.Comment)
        self.setPaper(QColor(style["Number"]["bg"]), QsciLexerPython.Number)
        self.setPaper(QColor(style["DoubleQuotedString"]["bg"]), QsciLexerPython.DoubleQuotedString)
        self.setPaper(QColor(style["SingleQuotedString"]["bg"]), QsciLexerPython.SingleQuotedString)
        self.setPaper(QColor(style["Keyword"]["bg"]), QsciLexerPython.Keyword)
        self.setPaper(QColor(style["TripleSingleQuotedString"]["bg"]), QsciLexerPython.TripleSingleQuotedString)
        self.setPaper(QColor(style["TripleDoubleQuotedString"]["bg"]), QsciLexerPython.TripleDoubleQuotedString)
        self.setPaper(QColor(style["ClassName"]["bg"]), QsciLexerPython.ClassName)
        self.setPaper(QColor(style["FunctionMethodName"]["bg"]), QsciLexerPython.FunctionMethodName)
        self.setPaper(QColor(style["Operator"]["bg"]), QsciLexerPython.Operator)
        self.setPaper(QColor(style["Identifier"]["bg"]), QsciLexerPython.Identifier)
        self.setPaper(QColor(style["CommentBlock"]["bg"]), QsciLexerPython.CommentBlock)
        self.setPaper(QColor(style["UnclosedString"]["bg"]), QsciLexerPython.UnclosedString)
        self.setPaper(QColor(style["HighlightedIdentifier"]["bg"]), QsciLexerPython.HighlightedIdentifier)
        self.setPaper(QColor(style["Decorator"]["bg"]), QsciLexerPython.Decorator)
        self.setPaper(QColor(style["DoubleQuotedFString"]["bg"]), QsciLexerPython.DoubleQuotedFString)
        self.setPaper(QColor(style["SingleQuotedFString"]["bg"]), QsciLexerPython.SingleQuotedFString)
        self.setPaper(QColor(style["TripleSingleQuotedFString"]["bg"]), QsciLexerPython.TripleSingleQuotedFString)
        self.setPaper(QColor(style["TripleDoubleQuotedFString"]["bg"]), QsciLexerPython.TripleDoubleQuotedFString)