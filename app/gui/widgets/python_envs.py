from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel, QFileDialog
)

from ..igui import EditorListWidgetItem, InputHistory
from PyQt5.QtGui import QColor

from functions import getfn

class PythonEnvs(QFrame):
    
    focus_out = pyqtSignal(object, object)
    on_env_added = pyqtSignal(object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self.mode = 0
        self._parent = parent
        self.setObjectName("editor-widget")
        self.setParent(parent)
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        self.screen1 = QFrame(self)
        self.screen1.setObjectName("child")
        vbox1 = QVBoxLayout(self.screen1)
        vbox1.setContentsMargins(5, 5, 5, 5)
        self.screen1.setLayout(vbox1)

        self.input_env = InputHistory(self)
        self.input_env.setObjectName("child")
        self.input_env.textChanged.connect(self.search_env)
        self.input_env.returnPressed.connect(self.change_to_selected_env)
        self.input_env.setMinimumHeight(24)

        self.btn_add_env = QPushButton("+ Add Env", self)
        self.btn_add_env.setObjectName("child")
        self.btn_add_env.clicked.connect(self.add_env_mode)
        self.btn_add_env.setMinimumHeight(24)
        
        self.env_list = QListWidget(self)
        self.env_list.setObjectName("child")
        self.env_list.itemActivated.connect(self.change_env)
        self.env_list.setMinimumHeight(30)
        
        vbox1.addWidget(self.input_env)
        vbox1.addWidget(self.env_list)
        vbox1.addWidget(self.btn_add_env)
        
        self.screen2 = QFrame(self)
        self.screen2.setObjectName("child")
        vbox2 = QVBoxLayout(self.screen2)
        vbox2.setContentsMargins(5, 5, 5, 5)
        self.screen2.setLayout(vbox2)
        
        hbox2 = QHBoxLayout()
        hbox2.setContentsMargins(0, 0, 0, 0)
        
        self.input_path = InputHistory(self)
        self.input_path.setObjectName("child")
        self.input_path.setPlaceholderText("Type env path here or")
        self.input_path.returnPressed.connect(lambda: self.enter_env(self.input_path.text()))
        self.input_path.setMinimumHeight(24)
        
        self.btn_select_path = QPushButton("Pick")
        self.btn_select_path.setObjectName("child")
        self.btn_select_path.clicked.connect(self.pick_env)
        self.btn_select_path.setMinimumHeight(24)
        
        hbox2.addWidget(self.input_path)
        hbox2.addWidget(self.btn_select_path)
        vbox2.addLayout(hbox2)
        
        self.btn_select_env = QPushButton("- Select env")
        self.btn_select_env.setObjectName("child")
        self.btn_select_env.clicked.connect(self.select_env_mode)
        self.btn_select_env.setMinimumHeight(24)
        vbox2.addWidget(self.btn_select_env)
        
        self.layout.addWidget(self.screen1)
        self.layout.addWidget(self.screen2)
        self.select_env_mode()
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)
    
    def update_size(self):
        if self._mode == 0:
            height = 0
            for i in range(self.env_list.count()):
                if not self.env_list.isRowHidden(i):
                    height += self.env_list.sizeHintForRow(i)

            self.env_list.setFixedHeight(height+10)
            self.setFixedHeight(self.input_env.size().height()+self.btn_add_env.size().height()+self.env_list.size().height()+20)
        else:
            self.setFixedHeight(self.input_path.size().height()+self.btn_select_env.size().height()+20)
            
    
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
    
    def pick_env(self):
        env_path = QFileDialog.getOpenFileName(None, 'Select Interpreter', "")
        self.enter_env(env_path[0])
    
    def enter_env(self, env_path):
        env = getfn.get_env(env_path)
        if env is not None:
            self.on_env_added.emit(env)
            self.api.add_env(env)
            self.api.set_current_env(env)
    
    def run(self):
        self.select_env_mode()
    
    def add_env_mode(self):
        self._mode = 1
        self.screen2.setVisible(True)
        self.screen1.setVisible(False)
        self.update_size()
        self.show()
        self.input_path.setFocus()
    
    def select_env_mode(self):
        self._mode = 0
        self.screen1.setVisible(True)
        self.screen2.setVisible(False)
        self.update_size()
        self.show()
        self.input_env.setFocus()