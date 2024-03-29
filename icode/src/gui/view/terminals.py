from core.system import SYS_NAME, end
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QSplitter,
    QStackedLayout,
    QVBoxLayout,
    QMenu,
    QAction,
    QActionGroup,
)

from smartlibs.iterm import TerminalWidget
from .igui import IListWidgetItem
from functions import getfn
from core.code_api import icode_api
from functools import partial

import random


class ItermBinsMenu(QMenu):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.build()

    def build(self):
        group_mode = QActionGroup(self)

        terminals_api = icode_api.get_terminals()
        id_current = terminals_api["current"]

        self.setTitle("Terminals")
        self.setToolTip("Pick a terminal")
        for terminal in icode_api.get_terminal_emulators():
            action = QAction(terminal["name"], self)
            action.setCheckable(True)

            if terminal["id"] == id_current:
                action.setChecked(True)

            action.triggered.connect(
                partial(self.parent.select_terminal, terminal))
            self.addAction(action)
            group_mode.addAction(action)


class Terminal(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("terminal-view")
        self.setStyleSheet("font-size:11pt")
        self.term_index = 0
        self.PORT = lambda: random.randint(7000, 65530)

        bin = "/bin/bash"
        name = "Bash"

        self.current_terminal = {"name": name, "bin": bin}

        self.icons = getfn.get_smartcode_icons("terminal")
        self.terminals_menu = ItermBinsMenu(self)
        self.parent.term_picker.setMenu(self.terminals_menu)
        self.start_timer = QTimer(self)
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
        self.term_header.currentRowChanged.connect(
            self.change_to_terminal_from_row)
        self.term_header.setMaximumWidth(360)

        self.terminals_frame = QFrame(self)
        self.terminals_layout = QStackedLayout(self.terminals_frame)
        self.terminals_frame.setLayout(self.terminals_layout)

        self.div.addWidget(self.terminals_frame)
        self.div.addWidget(self.term_header)
        self.div.setSizes([1000, 200])
        self.div.setStretchFactor(1, 0)

        self.layout.addWidget(self.div)

        self.start_timer.singleShot(3600, self.init_terminals)

    def change_to_terminal_from_row(self, row):
        item = self.term_header.item(row)
        self.change_to_terminal(item)

    def change_to_terminal(self, item):
        if self.term_header.count() > 0 and item is not None:
            widget = item.item_data["widget"]
            self.terminals_layout.setCurrentWidget(widget)

    def add_terminal(self, name=None, bin=None):
        if name is None:
            name = f"{self.current_terminal['name']} {self.term_index}"
        if bin is None:
            bin = self.current_terminal["bin"]

        self._create_terminal(name, bin)
        self.term_index += 1

    def _create_terminal(self, name, command):
        new_term = TerminalWidget(self, command, custom_theme=icode_api.get_terminal_theme())
        new_term.spawn(port = self.PORT())
        new_term_header = IListWidgetItem(
            self.icons.get_icon("bash"), name, None,
            {
                "widget": new_term,
                "index": self.term_index
            },
        )
        font = QFont()
        font.setPointSizeF(10.5)
        new_term_header.setFont(font)

        self.term_header.addItem(new_term_header)
        new_term.header_item = new_term_header
        self.terminals_layout.addWidget(new_term)
        self.terminals_layout.setCurrentWidget(new_term)

    def _delete_terminal(self, index, row, terminal:TerminalWidget):
        self.terminals_layout.takeAt(index)
        self.term_header.takeItem(row)
        terminal.terminate()

    def remove_terminal(self):
        if self.term_header.count() > 0:
            terminal:TerminalWidget = self.terminals_layout.currentWidget()
            index = self.terminals_layout.currentIndex()
            item = terminal.header_item
            row = self.term_header.row(item)
            self._delete_terminal(index, row, terminal)

    def set_current_terminal(self, data: dict) -> None:
        self.current_terminal = {"name": data["name"], "bin": data["bin"]}

    def select_terminal(self, data: dict) -> None:
        self.set_current_terminal(data)

    def listen_events(self):
        self.parent.btn_new_terminal.clicked.connect(
            lambda: self.add_terminal())
        self.parent.btn_remove_terminal.clicked.connect(
            lambda: self.remove_terminal())

    def init_terminals(self):
        terminals_api = icode_api.get_terminals()
        id_current = terminals_api["current"]
        self.listen_events()

        for terminal in icode_api.get_terminal_emulators():
            if "run_on_startup" in terminal.keys():
                if terminal["run_on_startup"]:
                    self.add_terminal(terminal["name"], terminal["bin"])

            if terminal["id"] == id_current:
                self.set_current_terminal(terminal)
