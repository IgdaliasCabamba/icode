from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox, QDesktopWidget,
                             QFileDialog, QFrame, QHBoxLayout, QLabel,
                             QMainWindow, QMenu, QMenuBar, QPushButton,
                             QScrollArea, QSizePolicy, QSplitter,
                             QStackedLayout, QStatusBar, QTabWidget, QToolBar,
                             QToolButton, QVBoxLayout, QWidget, qApp, QActionGroup)

from functions import getfn
from .assistant import AprilFace
from .explorer import FileExplorer
from .istore import ExtensionsUi
from .research_space import Labs
from .code_notebook import SideBottomNotebook
from .log_viewer import ProblemLogs
from .investigator import Searcher
from .source_control import IGit
from .terminals import Terminal
from .widgets import Notes, WorkSpace, Table

from .igui import HeaderPushButton
from data import note_file_path

from functools import partial

class IndentSizeMenu(QMenu):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.build()

    def build(self) -> None:
        self.setTitle("")
        self.group = QActionGroup(self)
        
        self.min = QAction("2", self)
        self.min.setCheckable(True)
        self.normal = QAction("4", self)
        self.normal.setCheckable(True)
        self.normal.setChecked(True)
        self.large = QAction("8", self)
        self.large.setCheckable(True)
        self.toolarge = QAction("16", self)
        self.toolarge.setCheckable(True)
        
        self.group.addAction(self.min)
        self.group.addAction(self.normal)
        self.group.addAction(self.large)
        self.group.addAction(self.toolarge)
        
        self.addAction(self.min)
        self.addAction(self.normal)
        self.addAction(self.large)
        self.addAction(self.toolarge)

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
        self.current_actions = []
        self.build()

    def build(self) -> None:
        self.setTitle("Open Recent")

        self.open_last_closed_tab = QAction(
            "Reopen Closed Editor\tCtrl+Shift+T")
        self.open_last_closed_tab.setShortcut("Ctrl+Shift+T")
        
        self.open_last_closed_tabs = QAction(
            "Reopen Closed Editors")
    
        self.update_menu()
    
    def set_recent_files(self, files:list, method:object):
        self.update_menu()
        
        if isinstance(files, list):
            files.reverse()
            added = []
            max = len(files)
            if max > 15:
                max = 15
            
            index_ref = 1
            
            for i in range(max):
                file = files[i]
                if file not in added:
                    action = QAction(file, self)
                    action.setShortcut("Ctrl+Shift+"+str(index_ref))
                    action.triggered.connect(partial(method, file))
                    self.addAction(action)
                    self.current_actions.append(action)
                    added.append(file)
                    index_ref+=1
    
    def update_menu(self):
        self.clear()
        self.addAction(self.open_last_closed_tab)
        self.addAction(self.open_last_closed_tabs)
        self.addSeparator()
            
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
        
        self.addSeparator()

        self.goto_file = QAction("Goto File\tCtrl+P", self)
        self.goto_file.setShortcut("Ctrl+P")
        self.addAction(self.goto_file)

        self.goto_line = QAction("Goto Line\tCtrl+G", self)
        self.goto_line.setShortcut("Ctrl+G")
        self.addAction(self.goto_line)
        
        self.goto_tab = QAction("Goto Tab\tCtrl+Tab", self)
        self.goto_tab.setShortcut("Ctrl+Tab")
        self.addAction(self.goto_tab)


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

        self.new_file = QAction("New File\tCtrl+N", self)
        self.new_file.setShortcut("Ctrl+N")
        self.addAction(self.new_file)
        
        self.new_menu = QMenu(self)
        self.new_menu.setTitle("New")
        self.new_notebook_vertical = QAction("New Notebook Vertical", self)
        self.new_notebook_horizontal = QAction("New Notebook Horizontal", self)
        self.new_menu.addAction(self.new_notebook_horizontal)
        self.new_menu.addAction(self.new_notebook_vertical)
        self.addMenu(self.new_menu)

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