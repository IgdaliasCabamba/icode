from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QToolButton,
    QVBoxLayout,
)

from functions import getfn

from smartlibs.qtmd import HeaderPushButton, QGithubButton
from .file_explorer_ui import FileExplorerUi
from .igui import IGenericNotebook
from .investigator_ui import SearcherUi
from .istore import ExtensionsUi
from .log_viewer import ProblemLogs
from .research_space import Labs
from .git_ui import IGit
from .terminals import Terminal
from .laboratory import Table, WorkSpace
from .corners import BottomTabCorner


class SideBottom(QFrame):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("side-bottom")
        self.icons = getfn.get_smartcode_icons("tab-corner")
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(100)

        self.notebook = IGenericNotebook(self)
        self.corner = BottomTabCorner(self.notebook)
        self.notebook.setCornerWidget(self.corner)

        # Terminal Widgets
        self.terminal_pick_area = QGithubButton(self)

        self.term_picker = QToolButton(self)
        self.term_picker.setIcon(self.icons.get_icon("pick"))
        self.term_picker.clicked.connect(lambda: self.term_picker.showMenu())
        self.term_picker.setMaximumSize(self.term_picker.minimumSizeHint())

        self.btn_new_terminal = QPushButton()
        self.btn_new_terminal.setIcon(self.icons.get_icon("add"))

        self.terminal_pick_area.set_widget_primary(self.btn_new_terminal)
        self.terminal_pick_area.set_widget_secondary(self.term_picker)

        self.btn_remove_terminal = QPushButton()
        self.btn_remove_terminal.setIcon(self.icons.get_icon("remove"))

        # Problems Buttons
        self.btn_clear_problems = QPushButton()
        self.btn_clear_problems.setIcon(self.icons.get_icon("clear"))

        # Widgets
        self.problem_logs = ProblemLogs(self)
        self.terminal = Terminal(self)

        self.add_widget(self.problem_logs, "PROBLEMS",
                        [self.btn_clear_problems])
        self.add_widget(
            self.terminal,
            "TERMINAL",
            [self.terminal_pick_area, self.btn_remove_terminal],
        )

        self.notebook.cornerWidget().btn_close.clicked.connect(
            self.close_panel)
        self.notebook.cornerWidget().btn_maximize.clicked.connect(
            self.maximize)
        self.notebook.cornerWidget().btn_minimize.clicked.connect(
            self.minimize)

        self.layout.addWidget(self.notebook)

    def insert_widget(
        self,
        pos: int,
        widget: object,
        name: str,
        components: list = [],
        goto: bool = False,
    ) -> None:
        current_widget = None
        if self.notebook.count() > 0:
            current_widget = self.notebook.currentWidget()
        self.notebook.cornerWidget().add_widget(widget, components, goto)
        self.notebook.insertTab(pos, widget, name)
        if not goto and current_widget is not None:
            self.notebook.setCurrentWidget(current_widget)

    def add_widget(self,
                   widget: object,
                   name: str,
                   components: list = [],
                   goto: bool = True):
        current_widget = None
        if self.notebook.count() > 0:
            current_widget = self.notebook.currentWidget()
        self.notebook.cornerWidget().add_widget(widget, components, goto)
        self.notebook.addTab(widget, name)
        if not goto and current_widget is not None:
            self.notebook.setCurrentWidget(current_widget)

    def close_panel(self):
        index = self.parent.div_child.indexOf(self)
        self.parent.div_child.moveSplitter(2147483647, index)

    def maximize(self):
        index = self.parent.div_child.indexOf(self)
        self.parent.div_child.moveSplitter(0, index)
        self.notebook.cornerWidget().btn_minimize.setVisible(True)
        self.notebook.cornerWidget().btn_maximize.setVisible(False)

    def minimize(self):
        index = self.parent.div_child.indexOf(self)
        h = self.parent.size().height() - 100
        self.parent.div_child.moveSplitter(h, index)
        self.notebook.cornerWidget().btn_minimize.setVisible(False)
        self.notebook.cornerWidget().btn_maximize.setVisible(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.size().height() > self.parent.size().height() - 100:
            self.notebook.cornerWidget().btn_minimize.setVisible(True)
            self.notebook.cornerWidget().btn_maximize.setVisible(False)
        else:
            self.notebook.cornerWidget().btn_minimize.setVisible(False)
            self.notebook.cornerWidget().btn_maximize.setVisible(True)


class SideLeft(QFrame):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("side-left")
        self.widget_list = []
        self.init_ui()

    def init_ui(self) -> None:
        self.setMinimumWidth(100)
        self.setMaximumWidth(1000)
        self.layout = QStackedLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.explorer = FileExplorerUi(self)
        self.searcher = SearcherUi(self)
        self.extender = ExtensionsUi(self)
        self.labs = Labs(self)
        self.git = IGit(self)

        self.layout.addWidget(self.explorer)
        self.layout.addWidget(self.searcher)
        self.layout.addWidget(self.extender)
        self.layout.addWidget(self.labs)
        self.layout.addWidget(self.git)
        self.setVisible(False)

    def add_widget(self, widget: object) -> bool:
        self.widget_list.append(widget)
        self.layout.addWidget(widget)


    def do_files(self) -> None:
        if self.isVisible() and self.layout.currentWidget() is self.explorer:
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.layout.setCurrentWidget(self.explorer)


    def do_searchs(self) -> None:
        if self.isVisible() and self.layout.currentWidget() is self.searcher:
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.layout.setCurrentWidget(self.searcher)


    def do_extensions(self) -> None:
        if self.isVisible() and self.layout.currentWidget() is self.extender:
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.layout.setCurrentWidget(self.extender)


    def do_icode_labs(self) -> None:
        if self.isVisible() and self.layout.currentWidget() is self.labs:
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.layout.setCurrentWidget(self.labs)


    def do_igit(self) -> None:
        if self.isVisible() and self.layout.currentWidget() is self.git:
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.layout.setCurrentWidget(self.git)


    def do_any_widget(self, widget: object) -> None:
        if widget in self.widget_list:
            if self.isVisible() and self.layout.currentWidget() is widget:
                self.setVisible(False)
            else:
                self.setVisible(True)
                self.layout.setCurrentWidget(widget)


class SideRight(QFrame):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("side-right")
        self.icons = getfn.get_smartcode_icons("ilab")
        self.parent = parent
        self.spaces = {}
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.top_info = QLabel("<small>ICODE LABS</small>")

        self.btn_close_lab = HeaderPushButton(self)
        self.btn_close_lab.setObjectName("explorer-header-button")
        self.btn_close_lab.setIcon(self.icons.get_icon("close"))

        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.header_layout.addWidget(self.btn_close_lab)

        self.spaces_manager = QStackedLayout()
        self.spaces_manager.setContentsMargins(0, 0, 0, 0)

        self.layout.addLayout(self.header_layout)
        self.layout.addLayout(self.spaces_manager)

        self.setVisible(False)

    def set_space(self, name: str) -> None:
        self.spaces_manager.setCurrentWidget(self.spaces[name])

    def add_space(self, name: str, widget: object) -> None:
        self.spaces[name] = widget
        self.spaces_manager.addWidget(widget)

    def new_table(self, title: str, widget):
        new_table = Table(self, title)
        new_table.add_widget(widget)
        return new_table

    def new_space(self, name_id: str) -> object:
        new_research_space = WorkSpace(name_id, self)
        self.add_space(name_id, new_research_space)
        return new_research_space
