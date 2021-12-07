from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox, QDesktopWidget,
                             QFileDialog, QFrame, QHBoxLayout, QLabel,
                             QMainWindow, QMenu, QMenuBar, QPushButton,
                             QScrollArea, QSizePolicy, QSplitter,
                             QStackedLayout, QStatusBar, QTabWidget, QToolBar,
                             QToolButton, QVBoxLayout, QWidget, qApp)

from functions import getfn
from gui.assistant import AprilFace
from gui.explorer import FileExplorer
from gui.extensions import ExtensionsUi
from gui.idebug import Debug
from gui.ilabs import Labs
from gui.widgets import (CodeDoctor, CodeTree, CodeWarnings, DeepAnalyze,
                       Notes, Refactor)
from gui.inotebook import SideBottomNotebook
from gui.iproblems import ProblemLogs
from gui.isearch import Searcher
from gui.isource_control import IGit
from gui.iterminals import PyConsole, Terminal

from .igui import HeaderPushButton
from data import note_file_path

from functools import partial


class ToolsMenu(QMenu):
    """
    ToolsMenu: a menu for external tools menus, such as extensions menus
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Tools")


class OpenRecentSubMenu(QMenu):
    """
    OpenRecentSubMenu: a menu for recent files opened in editor
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Open Recent")

        self.open_last_closed_tab = QAction(
            "Reopen Closed Editor\tCtrl+Shift+T")
        self.open_last_closed_tab.setShortcut("Ctrl+Shift+T")
        self.addAction(self.open_last_closed_tab)

        self.addSeparator()
    
    def set_recent_files(self, files, method):
        added = []
        max = len(files)
        if max > 100:
            max =  100

        for i in range(max):
            file = files[i]
            if file not in added:
                act = QAction(file, self)
                act.triggered.connect(partial(method, file))
                self.addAction(act)
                added.append(file)
            
class HelpMenu(QMenu):
    """
    HelpMenu: a menu for help actions such as useful links
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Help")
        self.welcome = QAction("Welcome", self)
        self.addAction(self.welcome)
        self.doc = QAction("Documentation", self)
        self.addAction(self.doc)
        self.release_notes = QAction("Release Notes", self)
        self.addAction(self.release_notes)
        self.addSeparator()
        self.tutorial_videos = QAction("Tutorial Videos", self)
        self.addAction(self.tutorial_videos)
        self.addSeparator()
        self.join_twitter = QAction("Join Us on Twitter", self)
        self.addAction(self.join_twitter)
        self.report_issue = QAction("Report Issue", self)
        self.addAction(self.report_issue)
        self.addSeparator()
        self.check_updates = QAction("Check for Updates", self)
        self.addAction(self.check_updates)
        self.addSeparator()
        self.about = QAction("About", self)
        self.addAction(self.about)


class RunMenu(QMenu):
    """
    RunMenu: a menu for run actions such as debug and run python code or file
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Run")
        self.run_file = QAction("Run File", self)
        self.addAction(self.run_file)
        self.run_selection = QAction("Run Selection", self)
        self.addAction(self.run_selection)
        self.addSeparator()
        self.analyze_file = QAction("Analyze File", self)
        self.addAction(self.analyze_file)


class GoMenu(QMenu):
    """
    GoMenu: a menu for go actions such as go to line, go to symbol and more
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Go")

        self.goto_symbol = QAction("Goto Symbol in Editor\tCtrl+Shift+O", self)
        self.goto_symbol.setShortcut("Ctrl+Shift+O")
        self.addAction(self.goto_symbol)

        self.addSeparator()

        self.goto_file = QAction("Goto File\tCtrl+P", self)
        self.goto_file.setShortcut("Ctrl+P")
        self.addAction(self.goto_file)

        self.goto_line = QAction("Goto Line\tCtrl+G", self)
        self.goto_line.setShortcut("Ctrl+G")
        self.addAction(self.goto_line)


class ViewMenu(QMenu):
    """
    ViewMenu: a menu for change visibility of some (main) widgets
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("View")

        self.command_palette = QAction("Command Palette\tCtrl+Shift+P", self)
        self.command_palette.setShortcut("Ctrl+Shift+P")
        self.addAction(self.command_palette)

        self.python_env = QAction("Python Interpreter\tCtrl+Alt+E", self)
        self.python_env.setShortcut("Ctrl+Alt+E")
        self.addAction(self.python_env)

        self.languages = QAction("Select Langauge Mode\tCtrl+Alt+L", self)
        self.languages.setShortcut("Ctrl+Alt+L")
        self.addAction(self.languages)

        self.addSeparator()

        self.explorer = QAction("Explorer", self)
        self.addAction(self.explorer)
        self.search = QAction("Search", self)
        self.addAction(self.search)
        self.extensions = QAction("Extensions", self)
        self.addAction(self.extensions)
        self.april = QAction("April", self)
        self.addAction(self.april)
        self.addSeparator()
        self.bottom = QAction("Side Bottom", self)
        self.addAction(self.bottom)
        self.left = QAction("Side Left", self)
        self.addAction(self.left)
        self.right = QAction("Side Right", self)
        self.addAction(self.right)


class SelectionMenu(QMenu):
    """
    SelectionMenu: a menu for selecting actions on editor
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Selection")


class EditMenu(QMenu):
    """
    SelectionMenu: a menu for editing actions on editor, it also has actions for formatting code
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("Edit")
        self.undo = QAction("Undo", self)
        self.addAction(self.undo)
        self.redo = QAction("Redo", self)
        self.addAction(self.redo)
        self.addSeparator()
        self.cut = QAction("Cut", self)
        self.addAction(self.cut)
        self.copy = QAction("Copy", self)
        self.addAction(self.copy)
        self.past = QAction("Past", self)
        self.addAction(self.past)
        self.addSeparator()
        self.find = QAction("Find", self)
        self.find.setShortcut("Ctrl+F")
        self.addAction(self.find)
        self.replace_ = QAction("Replace", self)
        self.replace_.setShortcut("Ctrl+H")
        self.addAction(self.replace_)
        self.addSeparator()
        self.straighten_code = QAction("Straighten Code", self)
        self.addAction(self.straighten_code)
        self.sort_imports = QAction("Sort Imports", self)
        self.addAction(self.sort_imports)


class FileMenu(QMenu):
    """
    SelectionMenu: a menu for file actions such as open, close, save, and create
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("File")

        self.new_file = QAction("New\tCtrl+N", self)
        self.new_file.setShortcut("Ctrl+N")
        self.addAction(self.new_file)

        self.new_window = QAction("New Window\tCtrl+Shift+N", self)
        self.new_window.setShortcut("Ctrl+Shift+N")
        self.addAction(self.new_window)

        self.addSeparator()

        self.open_file = QAction("Open File\tCtrl+O", self)
        self.open_file.setShortcut("Ctrl+O")
        self.addAction(self.open_file)

        self.open_folder = QAction("Open Folder\tCtrl+K", self)
        self.open_folder.setShortcut("Ctrl+K")
        self.addAction(self.open_folder)

        self.open_recent_menu = OpenRecentSubMenu(self)
        self.addMenu(self.open_recent_menu)

        self.addSeparator()

        self.save_file = QAction("Save File\tCtrl+S", self)
        self.save_file.setShortcut("Ctrl+S")
        self.addAction(self.save_file)

        self.save_all = QAction("Save All", self)
        self.addAction(self.save_all)

        self.auto_save = QAction("Auto Save", self)
        self.auto_save.setCheckable(True)
        self.auto_save.setChecked(False)
        self.addAction(self.auto_save)

        self.close_editor = QAction("Close Editor\tCtrl+W", self)
        self.close_editor.setShortcut("Ctrl+W")
        self.addAction(self.close_editor)

        self.close_window = QAction("Close Window", self)
        self.addAction(self.close_window)


class MenuBar(QMenu):
    """
    Custom Menu Bar for Icode, when user choose the custom or icode window style
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self) -> None:
        self.file = FileMenu(self)
        self.edit = EditMenu(self)
        self.selection = SelectionMenu(self)
        self.view = ViewMenu(self)
        self.go = GoMenu(self)
        self.run = RunMenu(self)
        self.help = HelpMenu(self)
        self.tools = ToolsMenu(self)
        self.menu_file = self.addMenu(self.file)
        self.menu_edit = self.addMenu(self.edit)
        self.menu_select = self.addMenu(self.selection)
        self.menu_view = self.addMenu(self.view)
        self.menu_go = self.addMenu(self.go)
        self.menu_run = self.addMenu(self.run)
        self.menu_help = self.addMenu(self.help)
        self.menu_tools = self.addMenu(self.tools)


class NMenuBar(QMenuBar):
    """
    Native Menu Bar for Icode, when user choose the native window style
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self) -> None:
        self.file = FileMenu(self)
        self.edit = EditMenu(self)
        self.selection = SelectionMenu(self)
        self.view = ViewMenu(self)
        self.go = GoMenu(self)
        self.run = RunMenu(self)
        self.help = HelpMenu(self)
        self.tools = ToolsMenu(self)
        self.menu_file = self.addMenu(self.file)
        self.menu_edit = self.addMenu(self.edit)
        self.menu_select = self.addMenu(self.selection)
        self.menu_view = self.addMenu(self.view)
        self.menu_go = self.addMenu(self.go)
        self.menu_run = self.addMenu(self.run)
        self.menu_help = self.addMenu(self.help)
        self.menu_tools = self.addMenu(self.tools)


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
        self.icons = getfn.get_application_icons("toolbar")

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

        self.april = QAction(self.icons.get_icon("april"), "", self)
        self.april.setCheckable(True)
        self.april.setToolTip("April, your assitent")

        self.config = QAction(self.icons.get_icon("config"), "", self)
        self.config.setCheckable(True)
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
    
    def add_action(self, action:object) -> None:
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
        self.icons = getfn.get_application_icons("statusbar")
        self.setObjectName("status-bar")
        self.setProperty("folder_open", False)
        self.init_ui()

    def init_ui(self) -> None:
        self.notify = QPushButton(self)
        self.notify.setIcon(self.icons.get_icon("notify"))
        self.lang = QPushButton(self)
        self.end_line_seq = QPushButton(self)
        self.encode = QPushButton(self)
        self.indentation = QPushButton(self)
        self.line_col = QPushButton(self)

        self.warnings = QPushButton(self)
        self.warnings.setIcon(self.icons.get_icon("warnings"))
        self.errors = QPushButton(self)
        self.errors.setIcon(self.icons.get_icon("errors"))
        self.interpreter = QPushButton(self)
        self.interpreter.setText('"SmartEnv"')
        self.source_control = QPushButton(self)
        self.source_control.setIcon(self.icons.get_icon("source_control"))
        self.source_control.setText("-")
        
        self.april = QPushButton(self)
        self.april.setIcon(self.icons.get_icon("april"))

        self.add_status_widget(self.errors)
        self.add_status_widget(self.warnings)
        self.add_status_widget(self.interpreter)
        self.add_status_widget(self.source_control)
        
        self.add_widget(self.april)

        self.add_editor_widget(self.line_col)
        self.add_editor_widget(self.indentation)
        self.add_editor_widget(self.encode)
        self.add_editor_widget(self.end_line_seq)
        self.add_editor_widget(self.lang)
        self.add_widget(self.notify)
        
        self.widgets["editor"] = self.editor_widgets
        self.widgets["app"] = self.app_widgets      

        self.main_view()
    
    def add_widget(self, widget:object, category="permanent") -> None:
        if category in self.widgets.keys():
            self.widgets[category].append(widget)
        else:
            self.widgets[category]=[widget]
            
        self.addPermanentWidget(widget)
    
    def add_editor_widget(self, widget:object) -> None:
        self.editor_widgets.append(widget)
        self.addPermanentWidget(widget)
    
    def add_status_widget(self, widget:object) -> None:
        self.app_widgets.append(widget)
        self.addWidget(widget)

    def main_view(self) -> None:
        self.update_visiblity("editor", False)

    def editor_view(self):
        self.update_visiblity("editor", True)

    def update_visiblity(self, category:str, value:bool) -> None:
        for widget in self.widgets[category]:
            widget.setVisible(value)        

    def open_folder_mode(self, flag:bool = True):
        self.setProperty("folder_open", flag)
        self.style().polish(self)


class SideBottom(QFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("side-bottom")
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(100)

        self.notebook = SideBottomNotebook(self)

        self.py_console = PyConsole(self)
        self.problem_logs = ProblemLogs(self)
        self.debug = Debug(self)
        self.terminal = Terminal(self)

        self.notebook.addTab(self.problem_logs, "PROBLEMS")
        self.notebook.addTab(self.py_console, "PYCONSOLE")
        self.notebook.addTab(self.debug, "DEBUG")
        self.notebook.addTab(self.terminal, "TERMINAL")

        self.notebook.cornerWidget().btn_close.clicked.connect(
            self.close_panel)
        self.notebook.cornerWidget().btn_maximize.clicked.connect(
            self.maximize)
        self.notebook.cornerWidget().btn_minimize.clicked.connect(
            self.minimize)

        self.layout.addWidget(self.notebook)

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
        self.layout = QStackedLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.explorer = FileExplorer(self)
        self.searcher = Searcher(self)
        self.extender = ExtensionsUi(self)
        self.april = AprilFace(self)
        self.labs = Labs(self)
        self.git = IGit(self)

        self.layout.addWidget(self.explorer)
        self.layout.addWidget(self.searcher)
        self.layout.addWidget(self.extender)
        self.layout.addWidget(self.april)
        self.layout.addWidget(self.labs)
        self.layout.addWidget(self.git)
        self.setVisible(False)

    def add_widget(self, widget: object) -> bool:
        self.widget_list.append(widget)
        self.layout.addWidget(widget)

    def do_april(self) -> None:
        if self.isVisible() and self.layout.currentWidget() is self.april:
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.layout.setCurrentWidget(self.april)

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
        self.thread_lab = QThread(self)
        self.icons = getfn.get_application_icons("ilab")
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.top_info = QLabel("<small>ICODE LABS</small>")
        
        self.btn_close_lab = HeaderPushButton(self)
        self.btn_close_lab.setObjectName("explorer-header-button")
        self.btn_close_lab.setIcon(self.icons.get_icon("close"))
        
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.header_layout.addWidget(self.btn_close_lab)

        self.div = QSplitter(self)

        self.notes = Notes(self, note_file_path)
        self.code_tree = CodeTree(self)
        self.code_doctor = CodeDoctor(self)
        self.code_warnings = CodeWarnings(self)
        self.refactor = Refactor(self)
        self.deep_analyze = DeepAnalyze(self)

        self.notebook_top = QTabWidget(self)
        self.notebook_top.addTab(self.notes, "Notes")
        self.notebook_top.addTab(self.code_tree, "Tree")
        self.notebook_top.addTab(self.refactor, "Refactor")

        self.notebook_bottom = QTabWidget(self)
        self.notebook_bottom.addTab(self.code_doctor, "Code Doctor")
        self.notebook_bottom.addTab(self.code_warnings, "Warnings")
        self.notebook_bottom.addTab(self.deep_analyze, "Deep Analyze")

        self.div.addWidget(self.notebook_top)
        self.div.addWidget(self.notebook_bottom)
        self.div.setOrientation(Qt.Vertical)
        self.div.setSizes([1000, 1000])

        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.div)

        self.setVisible(False)
        self.thread_lab.start()

    def set_notebook_index(self, widget):
        for i in range(self.notebook_top.count()):
            if widget == self.notebook_top.widget(i):
                self.notebook_top.setCurrentWidget(widget)
                return

        for i in range(self.notebook_bottom.count()):
            if widget == self.notebook_bottom.widget(i):
                self.notebook_bottom.setCurrentWidget(widget)
                return
