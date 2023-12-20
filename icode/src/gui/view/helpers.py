from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QPushButton,
    QStatusBar,
    QToolBar,
    QWidget,
    qApp,
    QSizePolicy,
)
from functions import getfn
from smartlibs.qtmd import QGithubButton
from .menus import IndentSizeMenu


class ToolBar(QToolBar):

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setObjectName("tool-bar")
        self.parent = parent
        self.actions_list = []
        self.init_ui()

    def init_ui(self) -> None:
        self.setFloatable(False)
        self.setMovable(False)
        self.setOrientation(Qt.Vertical)
        self.icons = getfn.get_smartcode_icons("toolbar")

        self.spacing = QWidget(self)
        self.spacing.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)

        self.explorer = QAction(self.icons.get_icon("explorer"), "", self)
        self.explorer.setCheckable(True)
        self.explorer.setToolTip("Explorer(Ctrl+Shift+E)")
        self.explorer.setShortcut("Ctrl+Shift+E")

        self.search = QAction(self.icons.get_icon("search"), "", self)
        self.search.setCheckable(True)
        self.search.setToolTip("Search(Ctrl+Shift+F)")
        self.search.setShortcut("Ctrl+Shift+F")

        self.extensions = QAction(self.icons.get_icon("extension"), "", self)
        self.extensions.setCheckable(True)
        self.extensions.setToolTip("Icode marketplace, extends your editor")

        self.april = QAction(self.icons.get_icon("april"), "", self)
        self.april.setCheckable(True)
        self.april.setToolTip("April, your assitent")

        self.config = QAction(self.icons.get_icon("config"), "", self)
        self.config.setCheckable(False)
        self.config.setToolTip("Settings")

        self.ilab = QAction(self.icons.get_icon("ilab"), "", self)
        self.ilab.setCheckable(True)
        self.ilab.setToolTip("Icode Labs")

        self.igit = QAction(self.icons.get_icon("source_control"), "", self)
        self.igit.setCheckable(True)
        self.igit.setToolTip("Source Control")

        self.add_action(self.explorer)
        self.add_action(self.search)
        self.add_action(self.ilab)
        self.add_action(self.extensions)
        self.add_action(self.april)
        self.add_action(self.igit)
        self.addWidget(self.spacing)
        self.add_action(self.config)

        self.actionTriggered.connect(self.mark_action)

    def add_action(self, action: object) -> None:
        self.actions_list.append(action)
        self.addAction(action)

    def mark_action(self, action):
        for act in self.actions_list:
            if act != action:
                act.setChecked(False)


class StatusBar(QStatusBar):

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.editor_widgets = []
        self.app_widgets = []
        self.widgets = {}
        self.icons = getfn.get_smartcode_icons("statusbar")
        self.setObjectName("status-bar")
        self.setProperty("folder_open", False)
        self.indent_size_menu = IndentSizeMenu(self)
        self.init_ui()

    def init_ui(self) -> None:
        self.notify = QPushButton(self)
        self.notify.setIcon(self.icons.get_icon("notify"))
        self.lang = QPushButton(self)
        self.encode = QPushButton(self)

        self.eol_box = QGithubButton(self)
        self.end_line_seq = QPushButton(self.eol_box)
        self.eol_visiblity = QPushButton(self.eol_box)
        self.eol_visiblity.setIcon(self.icons.get_icon("show"))
        self.eol_box.set_widget_primary(self.end_line_seq)
        self.eol_box.set_widget_secondary(self.eol_visiblity)

        self.indentation_box = QGithubButton(self)
        self.indentation = QPushButton(self.indentation_box)
        self.indentation_size = QPushButton(self.indentation_box)
        self.indentation_size.setMenu(self.indent_size_menu)
        self.indentation_size.clicked.connect(
            lambda: self.indentation_size.showMenu())
        self.indentation_box.set_widget_primary(self.indentation)
        self.indentation_box.set_widget_secondary(self.indentation_size)

        self.line_col = QPushButton(self)

        self.warnings = QPushButton(self)
        self.warnings.setIcon(self.icons.get_icon("warnings"))
        self.errors = QPushButton(self)
        self.errors.setIcon(self.icons.get_icon("errors"))
        self.source_control = QPushButton(self)
        self.source_control.setIcon(self.icons.get_icon("source_control"))

        self.add_status_widget(self.source_control)
        self.add_status_widget(self.errors)
        self.add_status_widget(self.warnings)

        self.add_editor_widget(self.line_col)
        self.add_editor_widget(self.indentation_box)
        self.add_editor_widget(self.encode)
        self.add_editor_widget(self.eol_box)
        self.add_editor_widget(self.lang)
        self.add_widget(self.notify)

        self.widgets["editor"] = self.editor_widgets
        self.widgets["app"] = self.app_widgets

        self.main_view()

    def add_widget(self, widget: object, category="permanent") -> None:
        if category in self.widgets.keys():
            self.widgets[category].append(widget)
        else:
            self.widgets[category] = [widget]

        self.addPermanentWidget(widget)

    def add_editor_widget(self, widget: object) -> None:
        self.editor_widgets.append(widget)
        self.addPermanentWidget(widget)

    def add_status_widget(self, widget: object) -> None:
        self.app_widgets.append(widget)
        self.addWidget(widget)

    def main_view(self) -> None:
        self.update_visiblity("editor", False)

    def editor_view(self):
        self.update_visiblity("editor", True)

    def update_visiblity(self, category: str, value: bool) -> None:
        for widget in self.widgets[category]:
            widget.setVisible(value)

    def open_folder_mode(self, flag: bool = True):
        self.setProperty("folder_open", flag)
        self.style().polish(self)

    def toggle_eol_visiblity(self, mode: str):
        self.eol_visiblity.setIcon(self.icons.get_icon(mode))
