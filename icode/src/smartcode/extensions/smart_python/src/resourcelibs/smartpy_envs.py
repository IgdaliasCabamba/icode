from PyQt5.QtCore import pyqtSignal, Qt, QSize

from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
)

from ui.igui import IListWidgetItem, InputHistory
from smartpy_api import python_api
from functions import getfn
from extension_api import settings


class Screen1(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("child")
        self.icons = getfn.get_smartcode_icons("*")

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(5, 5, 5, 5)
        self.setLayout(vbox)

        self.input_env = InputHistory(self)
        self.input_env.setObjectName("child")
        self.input_env.setMinimumHeight(24)

        hbox_child = QHBoxLayout()

        self.btn_add_env = QPushButton(self)
        self.btn_add_env.setObjectName("child")
        self.btn_add_env.setIcon(self.icons.get_icon("add"))
        self.btn_add_env.setMinimumHeight(24)

        self.btn_rem_env = QPushButton(self)
        self.btn_rem_env.setObjectName("child")
        self.btn_rem_env.setIcon(self.icons.get_icon("remove"))
        self.btn_rem_env.setMinimumHeight(24)

        hbox_child.addWidget(self.btn_add_env)
        hbox_child.addWidget(self.btn_rem_env)

        self.env_list = QListWidget(self)
        self.env_list.setObjectName("child")
        self.env_list.setMinimumHeight(24)
        self.env_list.setIconSize(QSize(16, 16))

        vbox.addWidget(self.input_env)
        vbox.addWidget(self.env_list)
        vbox.addLayout(hbox_child)


class Screen2(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("child")
        self.icons = getfn.get_smartcode_icons("*")

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(5, 5, 5, 5)
        self.setLayout(vbox)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.input_path = InputHistory(self)
        self.input_path.setObjectName("child")
        self.input_path.setPlaceholderText("Type env path here or pick")
        self.input_path.setMinimumHeight(24)

        self.btn_select_path = QPushButton(self)
        self.btn_select_path.setIcon(self.icons.get_icon("folder"))
        self.btn_select_path.setObjectName("child")
        self.btn_select_path.setMinimumHeight(24)

        self.btn_select_env = QPushButton(self)
        self.btn_select_env.setIcon(self.icons.get_icon("backward"))
        self.btn_select_env.setObjectName("child")
        self.btn_select_env.setMinimumHeight(24)

        hbox.addWidget(self.btn_select_env)
        hbox.addWidget(self.input_path)
        hbox.addWidget(self.btn_select_path)
        vbox.addLayout(hbox)


class PythonEnvs(QFrame):

    focus_out = pyqtSignal(object, object)
    on_env_added = pyqtSignal(object)
    on_current_env = pyqtSignal(object)

    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self.icons = getfn.get_smartcode_icons("*")
        self.mode = 0
        self._parent = parent
        self.setObjectName("editor-widget")
        self.setParent(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.screen1 = Screen1(self)
        self.env_list = self.screen1.env_list
        self.input_env = self.screen1.input_env
        self.btn_add_env = self.screen1.btn_add_env
        self.btn_rem_env = self.screen1.btn_rem_env

        self.screen2 = Screen2(self)
        self.input_path = self.screen2.input_path
        self.btn_select_env = self.screen2.btn_select_env
        self.btn_select_path = self.screen2.btn_select_path

        self.input_env.textChanged.connect(self.search_env)
        self.input_env.returnPressed.connect(self.change_to_selected_env)
        self.btn_add_env.clicked.connect(self.add_env_mode)
        self.btn_rem_env.clicked.connect(self.rem_selected_env)
        self.env_list.itemActivated.connect(self.change_env)
        self.input_path.returnPressed.connect(
            lambda: self.enter_env(self.input_path.text())
        )
        self.btn_select_path.clicked.connect(self.pick_env)
        self.btn_select_env.clicked.connect(self.select_env_mode)

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

            self.env_list.setFixedHeight(height + 10)
            self.setFixedHeight(
                self.input_env.size().height()
                + self.btn_add_env.size().height()
                + self.env_list.size().height()
                + 20
            )
        else:
            self.setFixedHeight(self.input_path.size().height() + 10)

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

    def set_envs(self, envs: list):
        if envs:
            self.env_list.clear()
            for item in envs:
                row = IListWidgetItem(
                    self.icons.get_icon("python"),
                    str(item.executable),
                    None,
                    {"env": item},
                )
                self.env_list.addItem(row)
            self.env_list.setCurrentRow(0)
        self.update_size()

    def change_env(self, item):
        self.on_current_env.emit(item.item_data["env"])
        self.hide()

    def pick_env(self):
        home_dir = settings.ipwd()
        env_path = QFileDialog.getOpenFileName(None, "Select Interpreter", home_dir)
        self.enter_env(env_path[0])

    def enter_env(self, env_path):
        env = python_api.get_env(env_path)
        if env is not None:
            self.on_env_added.emit(env)
            self.on_current_env.emit(env)

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

    def rem_selected_env(self):
        print("TODO")
