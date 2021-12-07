from system import SYS_NAME, end
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout,
    QListWidget, QPushButton,
    QScrollArea, QSplitter,
    QStackedLayout, QVBoxLayout,
    QGraphicsDropShadowEffect, QSizePolicy)
    
from smartlibs.iterm import TerminalWidget
from .igui import TerminalListWidgetItem
from functions import getfn
from smartlibs.pyqtconsole.console import PythonConsole
import smartlibs.pyqtconsole.highlighter as hl

from smartlibs.qtconsole.rich_ipython_widget import RichIPythonWidget
from smartlibs.qtconsole.inprocess import QtInProcessKernelManager

class TerminalBase(TerminalWidget):
    def __init__(self, parent, bin, color_map):
        
        super().__init__(
                parent=parent,
                command = bin,
                color_map = color_map,
                font_name="Monospace",
                font_size=16
                )
        self.setFocus()
        self.setObjectName("terminal")
        self.header_item = None
    
class Terminal(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("terminal-view")
        self.term_index = 0
        self.icons=getfn.get_application_icons("terminal")
        self.parent.notebook.cornerWidget().btn_new_terminal.clicked.connect(lambda: self.add_terminal())
        self.parent.notebook.cornerWidget().btn_remove_terminal.clicked.connect(lambda: self.remove_terminal())
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.div = QSplitter(self)
        self.div.setObjectName("terminal-view-div")
        self.div.setOrientation(Qt.Horizontal)
        self.div.setChildrenCollapsible(True)

        self.term_header = QListWidget(self)
        self.term_header.itemClicked.connect(self.change_to_terminal)
        self.term_header.currentRowChanged.connect(self.change_to_terminal_from_row)
        self.term_header.setMaximumWidth(360)
        
        self.terminals_frame = QFrame(self)
        self.terminals_layout = QStackedLayout(self.terminals_frame)
        self.terminals_frame.setLayout(self.terminals_layout)

        self.div.addWidget(self.terminals_frame)
        self.div.addWidget(self.term_header)
        self.div.setSizes([1000,200])
        self.div.setStretchFactor(1, 0)

        self.layout.addWidget(self.div)
        self.add_terminal()
    
    def change_to_terminal_from_row(self, row):
        item = self.term_header.item(row)
        self.change_to_terminal(item)
    
    def change_to_terminal(self, item):
        if self.term_header.count() > 0:
            widget = item.item_data["widget"]
            self.terminals_layout.setCurrentWidget(widget)

    def add_terminal(self, name = None, bin = None):
        if name is None:
            name = f"TERMINAL {self.term_index}"
        if bin is None:
            bin = "/bin/bash"
            if SYS_NAME == "windows":
                bin = "powershell.exe"
                
        self._create_terminal(name, bin)
        self.term_index += 1
        
    def _create_terminal(self, name, bin):
        new_term = TerminalBase(self, bin, getfn.get_terminal_color_map())
        new_term_header = TerminalListWidgetItem(
            self.icons.get_icon("bash"),
            name,
            None,
            {
                "widget":new_term,
                "index":self.term_index
            }
        )
        self.term_header.addItem(new_term_header)
        new_term.header_item = new_term_header
        self.terminals_layout.addWidget(new_term)
        self.terminals_layout.setCurrentWidget(new_term)
    
    def _delete_terminal(self, index, row, widget):
        self.terminals_layout.takeAt(index)
        self.term_header.takeItem(row)
        widget.stop()

    def remove_terminal(self):
        if self.term_header.count() > 1:
            widget = self.terminals_layout.currentWidget()
            index = self.terminals_layout.currentIndex()
            item = widget.header_item
            row = self.term_header.row(item)
            self._delete_terminal(index, row, widget)

class IPythonConsole(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("ipyconsole-view")
        self.color_map = getfn.get_pyconsole_color_map()
        self.icons=getfn.get_application_icons("pyconsole")
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(180)

        self.console = PythonConsole(formats={
            'keyword':    hl.format(self.color_map["keyword"][0]),
            'operator':   hl.format(self.color_map["operator"][0]),
            'brace':      hl.format(self.color_map["brace"][0]),
            'defclass':   hl.format(self.color_map["defclass"][0]),
            'string':     hl.format(self.color_map["string"][0]),
            'string2':    hl.format(self.color_map["string2"][0]),
            'comment':    hl.format(self.color_map["comment"][0]),
            'self':       hl.format(self.color_map["self"][0]),
            'numbers':    hl.format(self.color_map["numbers"][0]),
            'inprompt':   hl.format(self.color_map["inprompt"][0]),
            'outprompt':  hl.format(self.color_map["outprompt"][0]),
        })
        self.console.eval_in_thread()

        self.gde = QGraphicsDropShadowEffect(self)
        self.gde.setBlurRadius(15)
        self.gde.setOffset(0, 0)
        self.gde.setColor(
            getfn.get_qcolor(
                getfn.get_drop_shadow_color()
                )
            )
        self.setGraphicsEffect(self.gde)
        self.layout.addWidget(self.console)

        self.hbox = QHBoxLayout()

        self.btn_run_code = QPushButton(self)
        self.btn_run_code.clicked.connect(self.run_current_code)
        self.btn_run_code.setIcon(self.icons.get_icon("start"))
        self.btn_run_code.setObjectName("btn-run")
        self.btn_run_code.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_clear = QPushButton(self)
        self.btn_clear.setIcon(self.icons.get_icon("clear"))
        self.btn_clear.setObjectName("btn-clear")
        self.btn_clear.clicked.connect(self.clear_console)
        self.btn_clear.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.btn_delete = QPushButton(self)
        self.btn_delete.clicked.connect(self.remove_self)
        self.btn_delete.setIcon(self.icons.get_icon("remove"))
        self.btn_delete.setObjectName("btn-rem")
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
        self.setObjectName("pyconsole-view")
        self.parent.notebook.cornerWidget().btn_add_pycell.clicked.connect(lambda: self.add_cell())
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.widget = QFrame(self)
        self.widget.setObjectName("main-frame")
        
        self.vbox = QVBoxLayout(self.widget) 
        self.vbox.setSpacing(10)

        self.widget.setLayout(self.vbox)

        self.scroll_area=QScrollArea(self)
        self.scroll_area.setObjectName("scroll-area")

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)
        
        self.layout.addWidget(self.scroll_area)

        self.add_cell()
    
    def add_cell(self):
        console = IPythonConsole(self)
        self.vbox.addWidget(console)