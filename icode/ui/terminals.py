from base.system import SYS_NAME, end
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QFrame, QListWidget, QSplitter,
    QStackedLayout, QVBoxLayout,)
    
from frameworks.iterm import TerminalWidget
from .igui import TerminalListWidgetItem
from functions import getfn

class TerminalBase(TerminalWidget):
    def __init__(self, parent, bin, color_map):
        
        super().__init__(
                parent=parent,
                command = bin,
                color_map = color_map,
                font_name="Monospace",
                font_size=16
                )
        #self.setFocus()
        self.setObjectName("terminal")
        self.header_item = None

    
class Terminal(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("terminal-view")
        self.setStyleSheet("font-size:11pt")
        self.term_index = 0
        self.icons=getfn.get_smartcode_icons("terminal")
        self.parent.btn_new_terminal.clicked.connect(lambda: self.add_terminal())
        self.parent.btn_remove_terminal.clicked.connect(lambda: self.remove_terminal())
        self.parent.term_picker.addItems(["py","sh","cmd","ps"])
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
        
        self.start_timer.singleShot(3600, self.add_terminal)
    
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