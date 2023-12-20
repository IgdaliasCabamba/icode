from extension_api import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from functions import getfn
from pyqtconsole.console import PythonConsole  #pyright: ignore
import pyqtconsole.highlighter as hl  #pyright: ignore
from core.code_api import icode_api


class SmartPythonConsole(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("Frame")
        self.color_map = icode_api.get_generic_lexer_styles()
        self.icons = getfn.get_smartcode_icons("console")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(180)

        self.console = PythonConsole(
            formats={
                "keyword": hl.format(self.color_map["keyword"][0]),
                "operator": hl.format(self.color_map["operator"][0]),
                "brace": hl.format(self.color_map["brace"][0]),
                "defclass": hl.format(self.color_map["class-function"][0]),
                "string": hl.format(self.color_map["string"][0]),
                "string2": hl.format(self.color_map["string2"][0]),
                "comment": hl.format(self.color_map["comment"][0]),
                "self": hl.format(self.color_map["self"][0]),
                "numbers": hl.format(self.color_map["numbers"][0]),
                "inprompt": hl.format(self.color_map["inprompt"][0]),
                "outprompt": hl.format(self.color_map["outprompt"][0]),
            })
        self.console.eval_in_thread()
        self.console.setObjectName("Frame")
        self.console.setProperty("style-border-radius", "mid")
        self.console.setProperty("style-bg", "mid")
        self.console.setProperty("style-pad", "small")

        self.console.edit.setObjectName("TextArea")
        self.console.edit.setProperty("style-bg", "mid")
        self.console.edit.setProperty("style-pad", "small")

        self.gde = QGraphicsDropShadowEffect(self)
        self.gde.setBlurRadius(15)
        self.gde.setOffset(0, 0)
        self.gde.setColor(getfn.get_qcolor(icode_api.get_drop_shadow_color()))
        self.setGraphicsEffect(self.gde)
        self.layout.addWidget(self.console)

        self.hbox = QHBoxLayout()

        self.btn_run_code = QPushButton(self)
        self.btn_run_code.setObjectName("Button")
        self.btn_run_code.setProperty("style-bg", "transparent")
        self.btn_run_code.clicked.connect(self.run_current_code)
        self.btn_run_code.setIcon(self.icons.get_icon("start"))
        self.btn_run_code.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_clear = QPushButton(self)
        self.btn_clear.setObjectName("Button")
        self.btn_clear.setProperty("style-bg", "transparent")
        self.btn_clear.setIcon(self.icons.get_icon("clear"))
        self.btn_clear.clicked.connect(self.clear_console)
        self.btn_clear.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_delete = QPushButton(self)
        self.btn_delete.setObjectName("Button")
        self.btn_delete.setProperty("style-bg", "transparent")
        self.btn_delete.clicked.connect(self.remove_self)
        self.btn_delete.setIcon(self.icons.get_icon("remove"))
        self.btn_delete.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.hbox.addWidget(self.btn_run_code)
        self.hbox.addWidget(self.btn_clear)
        self.hbox.addWidget(self.btn_delete)
        self.hbox.setAlignment(Qt.AlignCenter)

        self.layout.addLayout(self.hbox)

    def remove_self(self):
        self.hide()
        self.close()
        self.deleteLater()

    def clear_console(self):
        self.console.clear_input_buffer()

    def run_current_code(self):
        notebook = self.parent.parent.parent.notebook
        if notebook.count() > 0:
            widget = notebook.currentWidget()
            if widget.objectName() == "editor-frame":
                self.console.insert_input_text(widget.editor.text())


class PyConsole(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("Frame")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QFrame(self)
        self.widget.setObjectName("Frame")
        self.widget.setProperty("style-bg", "transparent")

        self.vbox = QVBoxLayout(self.widget)
        self.vbox.setSpacing(10)

        self.widget.setLayout(self.vbox)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("Area")
        self.scroll_area.setProperty("style-bg", "transparent")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)

        self.layout.addWidget(self.scroll_area)

        self.add_cell()

    def add_cell(self):
        console = SmartPythonConsole(self)
        self.vbox.addWidget(console)
