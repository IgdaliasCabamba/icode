from extension_api import *  #pyright: ignore

from PyQt5.QtGui import QFontMetrics
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
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from core.code_api import icode_api


class SmartJupyterConsole(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("Frame")
        self.color_map = icode_api.get_editor_styles()
        self.icons = getfn.get_smartcode_icons("console")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(180)

        self.console = RichJupyterWidget()

        self.console.kernel_manager = QtInProcessKernelManager()
        self.console.kernel_manager.start_kernel(show_banner=False)
        self.console.kernel_manager.kernel.gui = 'qt'
        self.console.kernel_client = self.console._kernel_manager.client()
        self.console.kernel_client.start_channels()

        
        # TODO: put this styles on qss file
        self.console.setStyleSheet(f"background:{self.color_map['paper']}")

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


class JupyterConsole(QFrame):
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
        console = SmartJupyterConsole(self)
        self.vbox.addWidget(console)
