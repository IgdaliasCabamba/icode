from PyQt5.QtCore import QObject, pyqtSignal, QSettings

from components.system import *
from functions import *
import config
from config import DATA_FILE
from ui import *
from data import editor_cache
from components.extension_manager import Plugin
from components.python_api import PythonApi

python_api = PythonApi(
    f"{BASE_PATH}{SYS_SEP}.data{SYS_SEP}user{SYS_SEP}envs{SYS_SEP}envs")
plugin = Plugin()

class Core(object):

    on_new_notebook = pyqtSignal(object)
    on_new_tab = pyqtSignal(object)
    on_new_editor = pyqtSignal(object)
    on_window_title_changed = pyqtSignal(str)
    on_env_changed = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        self.menu.file.new_file.triggered.connect(self.new_file)
        self.menu.file.open_file.triggered.connect(self.open_file)
        self.menu.file.save_file.triggered.connect(self.save_file)
        self.menu.file.open_folder.triggered.connect(self.open_folder)
        self.menu.file.close_editor.triggered.connect(self.close_editor)
        self.menu.file.open_recent_menu.open_last_closed_tab.triggered.connect(self.reopen_editor)

        self.menu.edit.find.triggered.connect(self.find_in_editor)
        self.menu.edit.replace_.triggered.connect(self.replace_in_editor)
        self.menu.edit.straighten_code.triggered.connect(self.adjust_code)
        self.menu.edit.sort_imports.triggered.connect(self.adjust_imports)

        self.menu.view.command_palette.triggered.connect(self.show_command_palette)
        self.menu.view.python_env.triggered.connect(self.show_envs)
        self.menu.view.languages.triggered.connect(self.show_langs)

        self.menu.go.goto_symbol.triggered.connect(self.show_goto_symbol)
        self.menu.go.goto_line.triggered.connect(self.show_goto_line)

        self.tool_bar.explorer.triggered.connect(self.side_left.do_files)
        self.tool_bar.search.triggered.connect(self.side_left.do_searchs)
        self.tool_bar.extensions.triggered.connect(self.side_left.do_extensions)
        self.tool_bar.april.triggered.connect(self.side_left.do_april)
        self.tool_bar.ilab.triggered.connect(self.side_left.do_icode_labs)
        self.tool_bar.igit.triggered.connect(self.side_left.do_igit)

        self.status_bar.interpreter.clicked.connect(self.show_envs)
        self.status_bar.lang.clicked.connect(self.show_langs)
        self.status_bar.line_col.clicked.connect(self.show_goto_line)
        self.status_bar.april.clicked.connect(lambda: print("April"))

        self.ui.index.on_double_clicked.connect(self.new_file)
        self.ui.index.actions.on_new_clicked.connect(self.new_file)
        self.ui.index.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.index.actions.on_open_folder_clicked.connect(self.open_folder)
        self.ui.index.actions.on_show_commands_clicked.connect(self.show_command_palette)

        self.ui.welcome.actions.on_open_recent_file.connect(self.open_file)
        self.ui.welcome.actions.on_new_clicked.connect(self.new_file)
        self.ui.welcome.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.welcome.actions.on_open_folder_clicked.connect(self.open_folder)

        self.side_left.explorer.on_file_clicked.connect(self.open_file_from_explorer)
        self.side_left.explorer.btn_open_dir.clicked.connect(self.open_folder)
        self.side_left.explorer.btn_close_folder.clicked.connect(self.close_folder)
        self.side_left.labs.btn_notes.clicked.connect(self.run_user_notes)
        self.side_left.labs.btn_warnings.clicked.connect(self.run_code_warnings)
        self.side_left.labs.btn_analizys.clicked.connect(self.run_code_doctor)
        self.side_left.labs.btn_tree.clicked.connect(self.run_code_tree)

        self.side_left.searcher.display.on_open_file_request.connect(self.open_file_from_search)
        self.side_left.git.btn_open_repository.clicked.connect(self.open_repository)
        self.side_left.git.repository_menu.open_repository.triggered.connect(self.open_repository)
        
        self.side_right.code_doctor.btn_get_diagnosis.clicked.connect(self.run_code_doctor)
        self.side_right.code_warnings.btn_get_warnings.clicked.connect(self.run_code_warnings)
        self.side_right.code_warnings.on_fix_bugs_clicked.connect(self.fix_bugs)
        self.side_right.btn_close_lab.clicked.connect(self.close_lab)

        self.ui.isplitter.on_last_tab_closed.connect(self.last_tab_closed)
        self.ui.on_editor_changed.connect(self.editor_changed)
        self.ui.on_tab_buffer_focused.connect(self.tab_buffer_focused)

        self.on_new_notebook.connect(self.configure_notebook)
        self.on_env_changed.connect(self.update_statusbar_env)

        self.side_left.explorer.on_path_changed.connect(
            self.explorer_path_changed)

        self.configure_notebook(self.ui.notebook)

    def configure_notebook(self, notebook):
        notebook.last_tab_closed.connect(self.tabbar_last_closed)
        notebook.on_user_event.connect(self.ui.set_notebook)
        notebook.currentChanged.connect(self.notebook_tab_changed)
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
        
        self.welcome_widget.set_recent_files(self.last_files)
        self.menu.file.open_recent_menu.set_recent_files(self.last_files, self.open_file)
            
class Base(QObject, Core):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self.api_lexers_list: list = getfn.get_all_lexers_objects_api()
        self.api_envs_list = python_api.get_default_envs()
        self._current_env = None
        self.api_commands_list = self.get_api_commands_list(self)

    def run_api(self):
        self.editor_widgets.set_api(self)

    @property
    def commands_list(self) -> list:
        return self.api_commands_list

    @property
    def lexers_list(self) -> list:
        return self.api_lexers_list

    @property
    def envs_list(self) -> list:
        return self.api_envs_list

    @property
    def current_env(self):
        return self._current_env

    def add_lexer(self, lexer: object) -> None:
        self.lexer_list.append(lexer)

    def add_env(self, interpreter) -> None:
        self._env_list.append(interpreter)

    def add_command(self, command) -> None:
        self._env_list.append(command)

    def set_current_env(self, env: object) -> None:
        self._current_env = env
        self.on_env_changed.emit(env)

    def load_plugins(self):
        data = {"app": self, "qt_app": self.qt_app}
        plugin.run_ui_plugin(DATA_FILE, data)
        plugin.run_app_plugin(DATA_FILE, data)

    def get_new_editor(self, notebook):
        editor = EditorView(self, self.ui, notebook)
        editor.on_tab_content_changed.connect(self.update_tab)
        return editor

    def widget_is_code_editor(self, widget):
        if widget.objectName() == "editor-frame":
            return True
        return False

    def widget_is_code_editor_with_python_lexer(self, widget):
        if widget.objectName() == "editor-frame":
            if widget.editor.lexer_name == "python":
                return True
        return False

    def notebook_have_editor_with_python(self, notebook:object = None):
        if not self.notebooks_is_empty():
            if notebook is None:
                widget = self.ui.notebook.currentWidget()
                
            else:
                widget = notebook.currentWidget()
                if widget is not None:
                    if widget.objectName() == "editor-frame":
                        if widget.editor.lexer_name == "python":
                            return widget.editor

        return False

    def notebooks_is_empty(self) -> bool:
        return self.ui.isplitter.is_empty()

    def notebook_have_editor(self, notebook=None):
        if notebook is None:
            notebook = self.ui.notebook
        widget = notebook.currentWidget()
        if widget is not None:
            if widget.objectName() == "editor-frame":
                return widget
        return False

    def notebooks_have_editor(self):
        for notebook in self.ui.notebooks:
            widget = self.notebook_have_editor(notebook)
            if widget:
                return True
        return False
    
    def is_duplicated_file(self, file:str, notebook:object) -> bool:
        for i in range(notebook.count()):
            widget = notebook.widget(i)
            if self.widget_is_code_editor(widget):
                if str(widget.file) == file:
                    return {"index":i, "widget":widget, "notebook":notebook}
        return False

    def get_editor_class(self):
        return EditorView
    
    def get_api_commands_list(self, app) -> list:
        return [
            {
                "name": "New File\t\tCtrl+N",
                "command": app.new_file
            },
            {
                "name": "Open File\t\tCtrl+O",
                "command": app.open_file
            },
            {
                "name": "Save File\t\tCtrl+S",
                "command": app.save_file
            },
            {
                "name": "Open Folder\tCtrl+K",
                "command": app.open_folder
            },
            {
                "name": "Open Repository\t",
                "command": app.open_repository
            },
            {
                "name": "Close File\t\tCtrl+W",
                "command": app.close_editor
            },
            {
                "name": "Get Code Tree",
                "command": app.run_code_tree
            },
            {
                "name": "Get Code Warnings",
                "command": app.run_code_warnings
            },
            {
                "name": "Get Code Doctor Analyze",
                "command": app.run_code_doctor
            },
            {
                "name": "Show Notes",
                "command": app.run_user_notes
            },
            {
                "name": "Adjust this Code",
                "command": app.adjust_code
            },
            {
                "name": "Split in group Horizontal",
                "command": app.split_in_group_hor
            },
            {
                "name": "Split in group Vertical",
                "command": app.split_in_group_ver
            },
            {
                "name": "Split in group Horizontal",
                "command": app.split_in_group_hor
            },
        ]