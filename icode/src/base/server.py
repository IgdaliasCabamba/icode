from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication

from .system import *
from functions import *
import settings
from settings import DATA_FILE
from ui import *
from data import editor_cache
from .extender import Plugin
from typing import Union

plugin = Plugin()

class Core(object):

    on_new_notebook = pyqtSignal(object)
    on_new_tab = pyqtSignal(object)
    on_new_editor = pyqtSignal(object)
    on_window_title_changed = pyqtSignal(str)
    on_env_changed = pyqtSignal(object)
    on_commit_app = pyqtSignal(int)
    on_change_ide_mode = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        self.menu.file.new_file.triggered.connect(self.new_file)
        self.menu.file.new_notebook_vertical.triggered.connect(lambda: self.new_editor_notebook(Qt.Vertical))
        self.menu.file.new_notebook_horizontal.triggered.connect(lambda: self.new_editor_notebook(Qt.Horizontal))
        self.menu.file.open_file.triggered.connect(self.open_file)
        self.menu.file.save_file.triggered.connect(self.save_file)
        self.menu.file.save_all.triggered.connect(self.save_all)
        self.menu.file.open_folder.triggered.connect(self.open_folder)
        self.menu.file.close_editor.triggered.connect(self.close_editor)
        self.menu.file.open_recent_menu.open_last_closed_tab.triggered.connect(self.reopen_editor)
        self.menu.file.open_recent_menu.open_last_closed_tabs.triggered.connect(self.reopen_editors)

        self.menu.edit.find.triggered.connect(self.find_in_editor)
        self.menu.edit.replace_.triggered.connect(self.replace_in_editor)

        self.menu.view.command_palette.triggered.connect(self.show_command_palette)
        self.menu.view.languages.triggered.connect(self.show_langs)

        self.menu.go.goto_line.triggered.connect(self.show_goto_line)
        self.menu.go.goto_tab.triggered.connect(self.show_goto_tab)

        self.tool_bar.explorer.triggered.connect(self.side_left.do_files)
        self.tool_bar.search.triggered.connect(self.side_left.do_searchs)
        self.tool_bar.extensions.triggered.connect(self.side_left.do_extensions)
        self.tool_bar.april.triggered.connect(self.side_left.do_april)
        self.tool_bar.ilab.triggered.connect(self.side_left.do_icode_labs)
        self.tool_bar.igit.triggered.connect(self.side_left.do_igit)

        self.status_bar.lang.clicked.connect(self.show_langs)
        self.status_bar.line_col.clicked.connect(self.show_goto_line)
        self.status_bar.indentation.clicked.connect(self.show_space_mode)
        self.status_bar.end_line_seq.clicked.connect(self.show_eol_mode)
        self.status_bar.april.clicked.connect(self.call_april)
        self.status_bar.notify.clicked.connect(self.show_notifications)
        self.status_bar.eol_visiblity.clicked.connect(self.toggle_eol_visiblity)

        self.ui.index.on_double_clicked.connect(self.new_file)
        self.ui.index.actions.on_new_clicked.connect(self.new_file)
        self.ui.index.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.index.actions.on_open_folder_clicked.connect(self.open_folder)
        self.ui.index.actions.on_show_commands_clicked.connect(self.show_command_palette)

        self.ui.welcome.actions.on_open_recent_folder.connect(self.open_dir)
        self.ui.welcome.actions.on_new_clicked.connect(self.new_file)
        self.ui.welcome.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.welcome.actions.on_open_folder_clicked.connect(self.open_folder)

        self.side_left.explorer.on_file_clicked.connect(self.open_file_from_explorer)
        self.side_left.explorer.on_open_folder_request.connect(self.open_folder)
        self.side_left.explorer.btn_close_folder.clicked.connect(self.close_folder)
        self.side_left.searcher.display.on_open_file_request.connect(self.open_file_from_search)
        self.side_left.git.btn_open_repository.clicked.connect(self.open_repository)
        self.side_left.git.repository_menu.open_repository.triggered.connect(self.open_repository)
        self.side_left.labs.on_open_workspace.connect(self.open_research_space)
        
        self.side_right.btn_close_lab.clicked.connect(self.close_lab)

        self.ui.isplitter.on_last_tab_closed.connect(self.last_tab_closed)
        self.ui.on_editor_changed.connect(self.editor_changed)
        self.ui.on_tab_buffer_focused.connect(self.tab_buffer_focused)
        self.ui.on_close.connect(self.quit_app)

        self.on_new_notebook.connect(self.configure_notebook)
        self.on_commit_app.connect(self.commit_app)

        self.side_left.explorer.on_path_changed.connect(
            self.explorer_path_changed)
        
        self.april.on_mode_changed.connect(self.change_ide_mode)

        self.configure_notebook(self.ui.notebook)

    def configure_notebook(self, notebook):
        notebook.last_tab_closed.connect(self.tabbar_last_closed)
        notebook.on_user_event.connect(self.ui.set_notebook)
        notebook.on_tab_changed.connect(self.notebook_tab_changed)
        notebook.tabBarDoubleClicked.connect(lambda: self.new_file(notebook))
        notebook.tab_closed.connect(self.notebook_tab_closed)
        notebook.on_tab_added.connect(self.toggle_main_views)
        notebook.on_tab_droped.connect(self.tab_droped)
        notebook.cornerWidget().menu.split_in_group_ver.triggered.connect(
            self.split_in_group_ver)
        notebook.cornerWidget().menu.split_in_group_hor.triggered.connect(
            self.split_in_group_hor)
        notebook.cornerWidget().menu.join_in_group.triggered.connect(
            self.join_in_group)
        notebook.cornerWidget().btn_split.on_split_vertical.connect(
            self.split_notebook_ver)
        notebook.cornerWidget().btn_split.on_split_horizontal.connect(
            self.split_notebook_hor)

    def build_components(self):
        if self.last_repository is not None:
            self.restore_repository(self.last_repository)

        if self.last_folder is not None:
            self.restore_folder(self.last_folder)
        
        self.update_components()
        
    def update_components(self):
        self.welcome_widget.set_last_folders(self.last_folders)
        self.menu.file.open_recent_menu.set_recent_files(self.last_files, self.open_file)
            
class Base(QObject, Core):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self.logo_icons = getfn.get_smartcode_icons("logo")
        self.command_icons = getfn.get_smartcode_icons("action")
        self.indentation_icons = getfn.get_smartcode_icons("indentation")
        self.__lexers = []
        self.__commands = []
        
    def run_api(self):
        self.editor_widgets.set_api(self)

    def add_lexer(self, lexer: object) -> None:
        self.__lexers.append(lexer)
    
    def add_command(self, command) -> None:
        self.__commands.append(command)

    def load_plugins(self):
        data = {"app": self, "qt_app": self.qt_app}
        plugin.run_ui_plugin(DATA_FILE, data)
        plugin.run_app_plugin(DATA_FILE, data)

    def is_widget_code_editor(self, widget, attr:str=None, value:str=None) -> bool:
        if hasattr(widget, "objectName"):
            if widget.objectName() == "editor-frame":
                if getattr(widget.editor, str(attr), None) == value:
                    return widget
        return False

    def current_notebook_editor(self, notebook:object = None, attr:str=None, value:str=None) -> Union[object, bool]:
        if not self.are_notebooks_empty():
            if notebook is None:
                widget = self.ui.notebook.currentWidget()
            else:
                widget = notebook.currentWidget()
            if widget is not None:
                if self.is_widget_code_editor(widget, attr, value):
                    return widget.editor
        return False

    def are_notebooks_empty(self) -> bool:
        return self.ui.isplitter.is_empty

    def has_notebook_editor(self, notebook=None) -> Union[object, bool]:
        if notebook is None:
            notebook = self.ui.notebook
        widget = notebook.currentWidget()
        if widget is not None:
            if widget.objectName() == "editor-frame":
                return widget
        return False

    def have_notebooks_editor(self) -> bool:
        for notebook in self.ui.notebooks:
            widget = self.notebook_have_editor(notebook)
            if widget:
                return True
        return False
    
    def is_file_duplicated(self, file:str, notebook:object) -> bool:
        for i in range(notebook.count()):
            widget = notebook.widget(i)
            if self.is_widget_code_editor(widget):
                if str(widget.file) == file:
                    return {"index":i, "widget":widget, "notebook":notebook}
        return False
    
    @property
    def commands(self) -> list:
        return [
            {
                "name": "New File\t\tCtrl+N",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.new_file
            },
            {
                "name": "Open File\t\tCtrl+O",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.open_file
            },
            {
                "name": "Save File\t\tCtrl+S",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.save_file
            },
            {
                "name": "Open Folder\tCtrl+K",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.open_folder
            },
            {
                "name": "Open Repository\t",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.open_repository
            },
            {
                "name": "Close File\t\tCtrl+W",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.close_editor
            },
            {
                "name": "Reopen Last Closed Editor\tCtrl+Shift+T",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.reopen_editor
            },
            {
                "name": "Reopen Last Closed Editors",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.reopen_editors
            },
            {
                "name": "Split In Group Horizontal",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.split_in_group_hor
            },
            {
                "name": "Split In Group Vertical",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.split_in_group_ver
            },
            {
                "name": "Join In Group",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.join_in_group
            },
        ]
        
    @property
    def eols(self):
        return [{
            "name": r"Windows (\r\n)",
            "mode": 0,
            "icon": self.logo_icons.get_icon("windows")
        }, {
            "name": r"Unix (\n)",
            "mode": 2,
            "icon": self.logo_icons.get_icon("linux")
        }, {
            "name": r"MacOs (\r)",
            "mode": 1,
            "icon": self.logo_icons.get_icon("macos")
        }]
    
    @property
    def tabs_navigation(self):
        return {
            "notebook":self.ui.notebook,
            "tabs":notebook.get_navigation()
        }
    
    @property
    def indentation(self):
        return [{
            "name": "Indent Using Spaces",
            "action": 0,
            "icon": self.indentation_icons.get_icon("spaces")
        }, {
            "name": "Indent Using Tabs",
            "action": 1,
            "icon": self.indentation_icons.get_icon("tabs")
        }, {
            "name": "Detect Indentation from Content",
            "action": 2,
            "icon": self.indentation_icons.get_icon("auto")
        }, {
            "name": "Convert Indentation To Tabs",
            "action": 3,
            "icon": self.indentation_icons.get_icon("tabs")
        }, {
            "name": "Convert Indentation to Spaces",
            "action": 4,
            "icon": self.indentation_icons.get_icon("spaces")
        }]
    
    @property
    def lexers(self) -> dict:
        return [{
            "name": "python",
            "lexer": PythonLexer,
            "icon": getfn.get_lexer_icon_by_name("python")
        }, {
            "name": "c",
            "lexer": CLexer,
            "icon": getfn.get_lexer_icon_by_name("c")
        }, {
            "name": "c++",
            "lexer": CPPLexer,
            "icon": getfn.get_lexer_icon_by_name("c++")
        }, {
            "name": "css",
            "lexer": CSSLexer,
            "icon": getfn.get_lexer_icon_by_name("css")
        }, {
            "name": "html",
            "lexer": HTMLLexer,
            "icon": getfn.get_lexer_icon_by_name("html")
        }, {
            "name": "javaScript",
            "lexer": JavaScriptLexer,
            "icon": getfn.get_lexer_icon_by_name("javascript")
        }, {
            "name": "json",
            "lexer": JSONLexer,
            "icon": getfn.get_lexer_icon_by_name("json")
        }, {
            "name": "text",
            "lexer": NoneLexer,
            "icon": getfn.get_lexer_icon_by_name("text")
        }, {
            "name": "yaml",
            "lexer": YAMLLexer,
            "icon": getfn.get_lexer_icon_by_name("yaml")
        }, {
            "name": "java",
            "lexer": JavaLexer,
            "icon": getfn.get_lexer_icon_by_name("java")
        }, {
            "name": "markdown",
            "lexer": MarkdownLexer,
            "icon": getfn.get_lexer_icon_by_name("markdown")
        }]