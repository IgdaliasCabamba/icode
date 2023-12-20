from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication

from .system import *
from functions import *
import settings
from settings import DATA_FILE
from gui.view import *
from data import editor_cache
from .extender import Plugger
from typing import Union
from gui.controller import *


class Core(object):
    on_style_changed = pyqtSignal(object)
    on_new_notebook = pyqtSignal(object)
    on_new_tab = pyqtSignal(object)
    on_new_editor = pyqtSignal(object)
    on_window_title_changed = pyqtSignal(str)
    on_commit_app = pyqtSignal(int)
    on_current_editor_changed = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        self.menu.file.new_file.triggered.connect(self.new_file)
        self.menu.file.new_notebook_vertical.triggered.connect(
            lambda: self.new_editor_notebook(Qt.Vertical))
        self.menu.file.new_notebook_horizontal.triggered.connect(
            lambda: self.new_editor_notebook(Qt.Horizontal))
        self.menu.file.open_file.triggered.connect(self.open_file)
        self.menu.file.save_file.triggered.connect(self.save_file)
        self.menu.file.save_all.triggered.connect(self.save_all)
        self.menu.file.open_folder.triggered.connect(self.open_folder)
        self.menu.file.close_editor.triggered.connect(self.close_editor)
        self.menu.file.open_recent_menu.open_last_closed_tab.triggered.connect(
            self.reopen_editor)
        self.menu.file.open_recent_menu.open_last_closed_tabs.triggered.connect(
            self.reopen_editors)

        self.menu.edit.find.triggered.connect(self.find_in_editor)
        self.menu.edit.replace_.triggered.connect(self.replace_in_editor)

        self.menu.view.command_palette.triggered.connect(
            self.show_command_palette)
        self.menu.view.languages.triggered.connect(self.show_langs)
        self.menu.view.minimap.triggered.connect(
            lambda: self.change_minimap_visiblity(self.menu.view.minimap.
                                                  isChecked()))

        self.menu.go.goto_line.triggered.connect(self.show_goto_line)
        self.menu.go.goto_tab.triggered.connect(self.show_goto_tab)

        self.tool_bar.explorer.triggered.connect(self.side_left.do_files)
        self.tool_bar.search.triggered.connect(self.side_left.do_searchs)
        self.tool_bar.extensions.triggered.connect(
            self.side_left.do_extensions)
        self.tool_bar.april.triggered.connect(self.side_left.do_april)
        self.tool_bar.ilab.triggered.connect(self.side_left.do_icode_labs)
        self.tool_bar.igit.triggered.connect(self.side_left.do_igit)
        self.tool_bar.config.triggered.connect(self.configure_icode)

        self.status_bar.lang.clicked.connect(self.show_langs)
        self.status_bar.line_col.clicked.connect(self.show_goto_line)
        self.status_bar.indentation.clicked.connect(self.show_space_mode)
        self.status_bar.end_line_seq.clicked.connect(self.show_eol_mode)
        self.status_bar.notify.clicked.connect(self.show_notifications)
        self.status_bar.eol_visiblity.clicked.connect(
            self.toggle_eol_visiblity)

        self.ui.index.on_double_clicked.connect(self.new_file)
        self.ui.index.actions.on_new_clicked.connect(self.new_file)
        self.ui.index.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.index.actions.on_open_folder_clicked.connect(self.open_folder)
        self.ui.index.actions.on_show_commands_clicked.connect(
            self.show_command_palette)

        self.ui.welcome.actions.on_open_recent_folder.connect(self.open_dir)
        self.ui.welcome.actions.on_new_clicked.connect(self.new_file)
        self.ui.welcome.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.welcome.actions.on_open_folder_clicked.connect(
            self.open_folder)

        self.file_explorer.on_file_clicked.connect(
            self.open_file_from_explorer)
        self.file_explorer.on_open_folder_request.connect(self.open_folder)
        self.ui.side_left.explorer.btn_close_folder.clicked.connect(
            self.close_folder)
        self.side_left.searcher.display.on_open_file_request.connect(
            self.open_file_from_search)
        self.side_left.searcher.display.on_open_folder_request.connect(
            self.open_folder)
        self.side_left.git.btn_open_repository.clicked.connect(
            self.open_repository)
        self.side_left.git.repository_menu.open_repository.triggered.connect(
            self.open_repository)
        self.side_left.labs.on_open_workspace.connect(self.open_research_space)

        self.side_right.btn_close_lab.clicked.connect(self.close_lab)

        self.ui.isplitter.on_last_tab_closed.connect(self.last_tab_closed)
        self.ui.on_editor_changed.connect(self.editor_changed)
        self.ui.on_tab_buffer_focused.connect(self.tab_buffer_focused)
        self.ui.on_close.connect(self.quit_app)

        self.on_new_notebook.connect(self.configure_notebook)
        self.on_commit_app.connect(self.commit_app)

        self.file_explorer.on_path_changed.connect(self.explorer_path_changed)

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
        self.menu.file.open_recent_menu.set_recent_files(
            self.last_files, self.open_file)


class Server(QObject, Core):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self.plugger = Plugger(self)
        self.logo_icons = getfn.get_smartcode_icons("logo")
        self.command_icons = getfn.get_smartcode_icons("action")
        self.indentation_icons = getfn.get_smartcode_icons("indentation")
        #self.style =
        self.__lexers = [
            {
                "name": "python",
                "lexer": PythonLexer,
                "icon": getfn.get_lexer_icon_by_name("python"),
            },
            {
                "name": "c",
                "lexer": CLexer,
                "icon": getfn.get_lexer_icon_by_name("c")
            },
            {
                "name": "c++",
                "lexer": CPPLexer,
                "icon": getfn.get_lexer_icon_by_name("c++"),
            },
            {
                "name": "css",
                "lexer": CSSLexer,
                "icon": getfn.get_lexer_icon_by_name("css"),
            },
            {
                "name": "html",
                "lexer": HTMLLexer,
                "icon": getfn.get_lexer_icon_by_name("html"),
            },
            {
                "name": "javaScript",
                "lexer": JavaScriptLexer,
                "icon": getfn.get_lexer_icon_by_name("javascript"),
            },
            {
                "name": "json",
                "lexer": JSONLexer,
                "icon": getfn.get_lexer_icon_by_name("json"),
            },
            {
                "name": "text",
                "lexer": NoneLexer,
                "icon": getfn.get_lexer_icon_by_name("text"),
            },
            {
                "name": "yaml",
                "lexer": YAMLLexer,
                "icon": getfn.get_lexer_icon_by_name("yaml"),
            },
            {
                "name": "java",
                "lexer": JavaLexer,
                "icon": getfn.get_lexer_icon_by_name("java"),
            },
            {
                "name": "markdown",
                "lexer": MarkdownLexer,
                "icon": getfn.get_lexer_icon_by_name("markdown"),
            },
        ]
        self.__commands = [
            {
                "name": "New File\t\tCtrl+N",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.new_file,
            },
            {
                "name": "Open File\t\tCtrl+O",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.open_file,
            },
            {
                "name": "Save File\t\tCtrl+S",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.save_file,
            },
            {
                "name": "Open Folder\tCtrl+K",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.open_folder,
            },
            {
                "name": "Open Repository\t",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.open_repository,
            },
            {
                "name": "Close File\t\tCtrl+W",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.close_editor,
            },
            {
                "name": "Reopen Last Closed Editor\tCtrl+Shift+T",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.reopen_editor,
            },
            {
                "name": "Reopen Last Closed Editors",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.reopen_editors,
            },
            {
                "name": "Split In Group Horizontal",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.split_in_group_hor,
            },
            {
                "name": "Split In Group Vertical",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.split_in_group_ver,
            },
            {
                "name": "Join In Group",
                "icon": self.command_icons.get_icon("run-command"),
                "command": self.join_in_group,
            },
        ]
        self.last_files = editor_cache.get_all_from_list("files")
        self.last_folders = editor_cache.get_all_from_list("folders")
        self.last_folder = editor_cache.restore_from_list("folders", -1)
        self.last_repository = editor_cache.restore_from_list(
            "repositorys", -1)
        self.files_opened = []
        self.tabs_count = iconsts.INIT_TAB_COUNT

    def init_controllers(self):
        self.ui.set_controller(self)
        self.assistant = AssistantController(self, self.ui.side_left.april)
        self.notes = NotesController(self, self.ui.side_right.notes)
        self.file_explorer = FileExplorerController(self,
                                                    self.ui.side_left.explorer)
        self.git = GitController(self, self.ui.side_left.git)
        self.searcher = SearcherController(self, self.ui.side_left.searcher)
        self.todos = TodosController(self, self.ui.side_right.todos)

    def notify(self, title, text, widgets):
        self.ui.notificator.new_notification(title, text, widgets)

    def run_api(self):
        self.editor_widgets.set_api(self)

    def load_plugins(self):
        data = {"app": self, "qt_app": self.qt_app}
        self.plugger.run_ui_plugin(DATA_FILE, data)
        self.plugger.run_app_plugin(DATA_FILE, data)

    def add_lexer(self, lexer_object: dict) -> None:
        if isinstance(lexer_object, dict):
            self.__lexers.append(lexer_object)

    def add_command(self, command) -> None:
        if isinstance(command, dict):
            self.__commands.append(command)

    @property
    def commands(self) -> list:
        return self.__commands

    @property
    def eols(self):
        return [
            {
                "name": r"Windows (\r\n)",
                "mode": 0,
                "icon": self.logo_icons.get_icon("windows"),
            },
            {
                "name": r"Unix (\n)",
                "mode": 2,
                "icon": self.logo_icons.get_icon("linux"),
            },
            {
                "name": r"MacOs (\r)",
                "mode": 1,
                "icon": self.logo_icons.get_icon("macos"),
            },
        ]

    @property
    def tabs_navigation(self):
        notebook = self.ui.notebook
        return {"notebook": notebook, "tabs": notebook.get_navigation()}

    @property
    def indentations(self):
        return [
            {
                "name": "Indent Using Spaces",
                "action": 0,
                "icon": self.indentation_icons.get_icon("spaces"),
            },
            {
                "name": "Indent Using Tabs",
                "action": 1,
                "icon": self.indentation_icons.get_icon("tabs"),
            },
            {
                "name": "Detect Indentation from Content",
                "action": 2,
                "icon": self.indentation_icons.get_icon("auto"),
            },
            {
                "name": "Convert Indentation To Tabs",
                "action": 3,
                "icon": self.indentation_icons.get_icon("tabs"),
            },
            {
                "name": "Convert Indentation to Spaces",
                "action": 4,
                "icon": self.indentation_icons.get_icon("spaces"),
            },
        ]

    @property
    def lexers(self) -> dict:
        return self.__lexers
