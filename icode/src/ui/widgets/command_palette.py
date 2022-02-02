from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame, QGridLayout,
    QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel
)

from ..igui import EditorListWidgetItem, InputHistory
from PyQt5.QtGui import QColor

from functions import getfn

class ApplicationCommandPalette(QFrame):
    
    focus_out = pyqtSignal(object, object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.input_edit = InputHistory(self)
        self.input_edit.setText(">")
        self.input_edit.setObjectName("child")
        self.input_edit.textChanged.connect(self.search_command)
        self.input_edit.returnPressed.connect(self.execute_selected_command)
        self.input_edit.setMinimumHeight(24)

        self.command_list = QListWidget(self)
        self.command_list.setIconSize(QSize(16, 16))
        self.command_list.setObjectName("child")
        self.command_list.itemActivated.connect(self.execute_command)
        self.command_list.setMinimumHeight(30)

        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.command_list)
    
    def search_command(self, text):
        if text.startswith(">"):
            if len(text) > 1:
                command = text.split(">")[1]
            
                commands = self.command_list.findItems(command, Qt.MatchContains)
        
                for i in range(self.command_list.count()):
                    self.command_list.setRowHidden(i, True)

                for row_item in commands:    
                    i = self.command_list.row(row_item)
                    self.command_list.setRowHidden(i, False)
                
                if len(commands) > 0:
                    i = self.command_list.row(commands[0])
                    self.command_list.setCurrentRow(i)

            else:
                for i in range(self.command_list.count()):
                    self.command_list.setRowHidden(i, False)
            
            self.update_size()
        
        elif text.startswith((":","@","!")):
            self.api.run_by_id(self, text)
    
    def update_size(self):
        height = 0
        for i in range(self.command_list.count()):
            if not self.command_list.isRowHidden(i):
                height += self.command_list.sizeHintForRow(i)

        self.command_list.setFixedHeight(height+10 if height < 300 else 300)
        self.setFixedHeight(self.input_edit.size().height()+self.command_list.size().height()+20)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)

    def execute_selected_command(self):
        items = self.command_list.selectedItems()
        for item in items:
            self.execute_command(item)

    def execute_command(self, item):
        try:
            item.data["command"]()
        except Exception as e:
            print(e)
        self.hide()
    
    def run(self):
        self.input_edit.setFocus()
        self.input_edit.setText(">")
    
    def set_commands(self, data=False):
        if data:
            self.command_list.clear()
            for item in data:
                row = EditorListWidgetItem()
                row.setText(item["name"])
                row.setIcon(item["icon"])
                row.set_data({"command":item["command"]})
                self.command_list.addItem(row)
            self.command_list.setCurrentRow(0)
        self.update_size()