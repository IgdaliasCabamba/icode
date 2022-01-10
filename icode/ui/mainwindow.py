from weakref import ref

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow,
                             QScrollArea, QSplitter,
                             qApp)

import base.consts as iconsts
from functions import BASE_PATH, SYS_SEP, getfn
from .root import consts, parent_tab_widget
from .menus import MenuBar, NMenuBar
from .mainwidgets import SideBottom, SideLeft, SideRight
from .helpers import StatusBar, ToolBar
from .code_gadgets import EditorWidgets
from .code_notebook import NoteBookEditor
from .splitter import ISplitter
from .index import Index, Welcome
from .April import April
from frameworks.icodeframe import iwindow
from smartsci.editor import *

class MainWindow(QMainWindow):

    resized = pyqtSignal()
    on_focused_buffer = pyqtSignal(object)
    on_editor_changed = pyqtSignal(object)
    on_new_notebook = pyqtSignal(object)
    on_tab_buffer_focused = pyqtSignal(object)
    on_close = pyqtSignal(object)

    def __init__(self, parent, style, qapp) -> None:
        super().__init__(parent=parent)
        self.setObjectName("main-window")
        self.__style = style
        self._controller = None
        self._current_notebook = None
        self.icons = getfn.get_application_icons("window")
        self.frame = False
        self.parent = parent
        self.last_focus = None
        self.editor_widgets = None
        self.april = None

        self.qapp = qapp
        self.qapp.focusChanged.connect(self._app_focus_changed)

        self._build_base_elements()
        self._init_ui()
        self._add_extra_widgets()
        self._build_window()

    def _build_base_elements(self):
        if self.__style in {"icode", "modern", "custom"}:
            self.menu_bar = MenuBar(self)
        else:
            self.menu_bar = NMenuBar(self)
            self.setMenuBar(self.menu_bar)

        self.tool_bar = ToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.tool_bar)
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        self.side_bottom = SideBottom(self)
        self.side_right = SideRight(self)
        self.side_left = SideLeft(self)

        self.isplitter = ISplitter(self)

        self.index = Index(self)
        self.index.setVisible(False)

        self._notebook = NoteBookEditor(self.isplitter, self)
        self._notebook.setVisible(True)

        self.welcome = Welcome(self._notebook)

        self._current_notebook = self._notebook
        self._current_notebook.last_tab_closed.connect(
            self.on_tabbar_last_closed)
        self._current_notebook.on_user_event.connect(self.set_notebook)

        self.isplitter.add_notebook(self._current_notebook)
        self.isplitter.splitAt(None, consts.RIGHT, self._current_notebook)

        self.scroll_area = QScrollArea(self)

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.isplitter)

    def _init_ui(self) -> None:
        self.div_child = QSplitter(self)
        self.div_child.setObjectName("div-child")
        self.div_child.setOrientation(Qt.Vertical)
        self.div_child.addWidget(self.index)
        self.div_child.addWidget(self.scroll_area)
        self.div_child.addWidget(self.side_bottom)
        self.div_child.setSizes(iconsts.DIV_CHILD_SIZES)
        self.div_child.setChildrenCollapsible(True)

        self.div_main = QSplitter(self)
        self.div_main.setObjectName("div-main")
        self.div_main.setOrientation(Qt.Horizontal)
        self.div_main.addWidget(self.side_left)
        self.div_main.addWidget(self.div_child)
        self.div_main.addWidget(self.side_right)
        self.div_main.setSizes(iconsts.DIV_CHILD_SIZES)
        self.div_main.setChildrenCollapsible(True)
        self.div_main.setMinimumSize(iconsts.DIV_MAIN_MIN_SIZE)

        self.setCentralWidget(self.div_main)

    def closeEvent(self, event): 
        self.on_close.emit(self)

    def _build_window(self):
        if self.__style in {"icode", "modern"}:
            self._make_window("icode")
        elif self.__style == "custom":
            self._make_window(self.style)
        else:
            self._native_window()

    @property
    def style(self):
        return self.__style

    def show_(self):
        if self.frame:
            self.frame.show()
        else:
            self.show()

    def _add_extra_widgets(self) -> None:
        self.editor_widgets = EditorWidgets(self)
        self.april = April(self)

    def center(self) -> None:
        app_geo = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        app_geo.moveCenter(screen_center)
        self.move(app_geo.topLeft())

    def _make_window(self, style: str) -> None:
        self.frame = iwindow.ModernWindow(self, style)
        self.frame.setWindowMenu(self.menu_bar)
        self.frame.setMenuIcon(self.icons.get_icon("menubar-menu"))
        self.frame.setWindowTitle("Icode")

    def _native_window(self) -> None:
        self.setWindowTitle("Icode")

    def set_notebook(self, notebook: object) -> None:
        self._current_notebook = notebook

    def set_controller(self, controller: object) -> None:
        self._controller = controller

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.resized.emit()

    def current_buffer(self):
        if self.last_focus is not None:
            return self.last_focus()

        return None

    @property
    def controller(self):
        return self._controller

    @property
    def notebooks(self):
        return self.isplitter.notebooks_list

    @property
    def notebook(self):
        return self._current_notebook

    def _app_focus_changed(self, _, new):
        if self.centralWidget().isAncestorOf(new):
            self.last_focus = ref(new)
            self.on_focused_buffer.emit(new)

            if isinstance(new.parent, NoteBookEditor):
                self._current_notebook = new.parent
                self.on_tab_buffer_focused.emit(new)

            if hasattr(new, "editor_view_parent"):
                if hasattr(new.editor_view_parent, "notebook"):
                    self.on_editor_changed.emit(new.editor_view_parent)
                    self._current_notebook = new.editor_view_parent.notebook

    def current_widget(self):
        return self.last_focus()

    def _create_new_notebook(self, orientation, widget=None):
        if widget is None:
            widget = self.notebook
        parent_notebook = parent_tab_widget(widget)

        tab_data = parent_notebook.get_tab_data()

        notebook = NoteBookEditor(self.isplitter, self)
        notebook.last_tab_closed.connect(self.on_tabbar_last_closed)
        notebook.on_user_event.connect(self.set_notebook)

        self.on_new_notebook.emit(notebook)
        self._current_notebook = notebook

        editor = self._controller.get_new_editor(notebook)
        editor.make_deep_copy(tab_data.widget)
        index = notebook.add_tab_and_get_index(editor, tab_data.title)
        notebook.setTabToolTip(index, tab_data.tooltip)
        notebook.setTabIcon(index, tab_data.icon)

        DIRS = {Qt.Vertical: consts.DOWN, Qt.Horizontal: consts.RIGHT}

        self.isplitter.add_notebook(notebook)
        self.isplitter.splitAt(parent_notebook, DIRS[orientation], notebook)

    def new_split_horizontal(self, widget=None):
        self._create_new_notebook(Qt.Horizontal, widget)

    def new_split_vertical(self, widget=None):
        self._create_new_notebook(Qt.Vertical, widget)

    def on_tabbar_last_closed(self, tw):
        self.isplitter.notebook_last_tab_closed()

    def set_window_title(self, title: str) -> None:
        if self.frame:
            self.frame.set_window_title(title)

        else:
            self.setWindowTitle(title)
