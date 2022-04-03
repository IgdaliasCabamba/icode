from . import *
from .utils import *


class NoneLexer(QsciLexer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.style = None

    def language(self):
        return "none"

    def description(self, style):
        return ""

    def styleText(self, start, end):
        pass

    def set_style_api(self, style: dict):
        try:
            x = "@lexer-" + self.language()
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
