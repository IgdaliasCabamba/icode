from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QFrame,
    QMenu,
    QPushButton,
    QToolButton,
    QHBoxLayout,
)
from functions import getfn


class SplitButton(QToolButton):
    on_split_horizontal = pyqtSignal(object)
    on_split_vertical = pyqtSignal(object)

    def __init__(self, parent, notebook):
        super().__init__(parent)
        self.parent = parent
        self.notebook = notebook
        self.icons = getfn.get_smartcode_icons("tab-corner")

        self.setIcon(self.icons.get_icon("split"))

        menu = QMenu()

        action1 = menu.addAction("Split &vertically")
        action1.triggered.connect(self.split_horizontal)

        action2 = menu.addAction("Split &horizontally")
        action2.triggered.connect(self.split_vertical)

        self.setMenu(menu)
        self.setPopupMode(self.InstantPopup)
        self.notebook.currentChanged.connect(self.tab_changed)

    def tab_changed(self, index):
        widget = self.notebook.widget(index)
        if widget is not None:
            if widget.objectName() == "editor-frame":
                self.setVisible(True)
            else:
                self.setVisible(False)

    def split_horizontal(self):
        widget = self.notebook.currentWidget()
        if widget is not None:
            if widget.objectName() == "editor-frame":
                self.on_split_horizontal.emit(self.notebook)

    def split_vertical(self):
        widget = self.notebook.currentWidget()
        if widget is not None:
            if widget.objectName() == "editor-frame":
                self.on_split_vertical.emit(self.notebook)


class EditorMenu(QMenu):

    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Icode Notebook")
        self.build()

    def build(self):
        self.tab = QMenu(self)
        self.tab.setTitle("Notebook Tab")

        self.split_in_group_ver = QAction(self)
        self.split_in_group_ver.setText("Split in group vertical")
        self.tab.addAction(self.split_in_group_ver)

        self.split_in_group_hor = QAction(self)
        self.split_in_group_hor.setText("Split in group horizontal")
        self.tab.addAction(self.split_in_group_hor)

        self.join_in_group = QAction(self)
        self.join_in_group.setText("Join in group")
        self.tab.addAction(self.join_in_group)

        self.addMenu(self.tab)


class MainTabCorner(QFrame):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("tab-corner-widget-editor")
        self.parent = parent
        self.icons = getfn.get_smartcode_icons("tab-corner")
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        self.menu = EditorMenu(self)

        self.btn_menu = QPushButton(self)
        self.btn_menu.setIcon(self.icons.get_icon("menu"))
        self.btn_menu.setMenu(self.menu)

        self.btn_split = SplitButton(self, self.parent)

        self.layout.addWidget(self.btn_split)
        self.layout.addWidget(self.btn_menu)


class GenericTabCorner(QFrame):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("tab-corner-widget")
        self.icons = getfn.get_smartcode_icons("tab-corner")
        self.parent.currentChanged.connect(self.change_view)
        self.widget_dict = {}
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        self.layout.addSpacing(20)

    def change_view(self, index) -> None:
        widget = self.parent.widget(index)
        if widget in self.widget_dict.keys():
            self.change_to(widget)

    def set_visiblity(self, items: list, flag: bool):
        for item in items:
            if item in self.widget_dict.keys():
                for widget in self.widget_dict[item]:
                    widget.setVisible(flag)
            continue

    def change_to(self, name: object) -> None:
        self.set_visiblity([widget for widget in self.widget_dict.keys()],
                           False)
        if name in self.widget_dict.keys():
            self.set_visiblity([name], True)

    def add_widget(self, name: object, components: list, goto: bool = False):
        components = list(reversed(components))
        self.widget_dict[name] = components
        for widget in components:
            self.layout.insertWidget(0, widget)
        if goto:
            self.change_to(name)


class BottomTabCorner(GenericTabCorner):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("tab-corner-widget-bottom")
        self.icons = getfn.get_smartcode_icons("tab-corner")
        self.init_ui()

    def init_ui(self) -> None:
        self.btn_close = QPushButton(self)
        self.btn_close.setIcon(self.icons.get_icon("close"))

        self.btn_maximize = QPushButton(self)
        self.btn_maximize.setIcon(self.icons.get_icon("maximize"))

        self.btn_minimize = QPushButton(self)
        self.btn_minimize.setIcon(self.icons.get_icon("minimize"))
        self.btn_minimize.setVisible(False)

        self.layout.addSpacing(20)
        self.layout.addWidget(self.btn_maximize)
        self.layout.addWidget(self.btn_minimize)
        self.layout.addWidget(self.btn_close)
