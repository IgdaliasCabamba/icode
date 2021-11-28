from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel
)

from ..igui import EditorListWidgetItem, InputHistory
from PyQt5.QtGui import QColor

from functions import getfn

class PythonEnvs(QFrame):
    
    focus_out = pyqtSignal(object, object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        self.setObjectName("editor-widget")
        self.setParent(parent)
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.input_env = InputHistory(self)
        self.input_env.setObjectName("child")
        self.input_env.textChanged.connect(self.search_env)
        self.input_env.returnPressed.connect(self.change_to_selected_env)
        self.input_env.setMinimumHeight(30)

        self.btn_add_env = QPushButton("+ Add Env", self)
        self.btn_add_env.setObjectName("child")
        self.btn_add_env.setMinimumHeight(24)
        
        self.env_list = QListWidget(self)
        self.env_list.setObjectName("child")
        self.env_list.itemActivated.connect(self.change_env)
        self.env_list.setMinimumHeight(30)

        self.layout.addWidget(self.input_env)
        self.layout.addWidget(self.env_list)
        self.layout.addWidget(self.btn_add_env)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)
    
    def update_size(self):
        height = 0
        for i in range(self.env_list.count()):
            if not self.env_list.isRowHidden(i):
                height += self.env_list.sizeHintForRow(i)

        self.env_list.setFixedHeight(height+10)
        self.setFixedHeight(self.input_env.size().height()+self.btn_add_env.size().height()+self.env_list.size().height()+20)
    
    def search_env(self, query):
        
        if len(query) > 1:
        
            envs = self.env_list.findItems(query, Qt.MatchContains)
    
            for i in range(self.env_list.count()):
                self.env_list.setRowHidden(i, True)

            for row_item in envs:
                i = self.env_list.row(row_item)
                self.env_list.setRowHidden(i, False)
            
            if len(envs) > 0:
                i = self.env_list.row(envs[0])
                self.env_list.setCurrentRow(i)

        else:
            for i in range(self.env_list.count()):
                self.env_list.setRowHidden(i, False)
        
        self.update_size()
    
    def change_to_selected_env(self):
        items = self.env_list.selectedItems()
        for item in items:
            self.change_env(item)
    
    def set_envs(self, envs:list):
        if envs:
            self.env_list.clear()
            for item in envs:
                row = EditorListWidgetItem()
                row.setText(str(item.executable))
                row.set_data({"env":item})
                self.env_list.addItem(row)
            self.env_list.setCurrentRow(0)
        self.update_size()
    
    def change_env(self, item):
        self.api.set_current_env(item.data["env"])
        self.hide()
    
    def run(self):
        self.input_env.setFocus()