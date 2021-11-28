import faulthandler
import sys

sys.dont_write_bytecode = True
faulthandler.enable()

from PyQt5.QtCore import QObject, pyqtSignal, QSettings

from components.system import *
from functions import *
import config
from config import DATA_FILE
from ui import *
from components.cache_manager import CacheManager
from components.extension_manager import Plugin
from components.python_api import PythonApi

python_api=PythonApi(f"{BASE_PATH}{SYS_SEP}.data{SYS_SEP}user{SYS_SEP}envs{SYS_SEP}envs.idt")
plugin=Plugin()
cache_manager = CacheManager(f"{BASE_PATH}{SYS_SEP}.cache{SYS_SEP}editors{SYS_SEP}cache.idt")

class API(QObject):
    
    on_env_changed = pyqtSignal(object)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self.api_lexers_list:list = getfn.get_all_lexers_objects_api()
        self.api_envs_list = python_api.get_default_envs()
        self._current_env = None
        self.api_commands_list = getfn.get_api_commands_list(self) 
        
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
    
    def add_lexer(self, lexer:object) -> None:
        self.lexer_list.append(lexer)
    
    def add_env(self, interpreter) -> None:
        self._env_list.append(interpreter)
    
    def add_command(self, command) -> None:
        self._env_list.append(command)

    def set_current_env(self, env:object) -> None:
        self._current_env = env
        self.on_env_changed.emit(env)
    
    def load_plugins(self):
        data={
            "app":self,
            "qt_app":self.qt_app
        }
        plugin.run_ui_plugin(DATA_FILE, data)
        plugin.run_app_plugin(DATA_FILE, data)
    
    #TODO
    def get_new_editor(self, notebook):
        editor = EditorView(self, self.ui, notebook)
        editor.on_tab_content_changed.connect(self.update_tab)
        return editor

class ComponentsInterface(API):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
    
    def build_components(self):        
        if self.last_repository is not None:
            self.restore_repository(self.last_repository)
        
        if self.last_folder is not None:
            self.restore_folder(self.last_folder)

    def widget_is_code_editor(self, widget):
        if widget.objectName() == "editor-frame":    
            return True
        return False
    
    def widget_is_code_editor_with_python_lexer(self, widget):
        if widget.objectName() == "editor-frame":
            if widget.editor.lexer_name == "python":
                return True
        return False
    
    def notebook_have_editor_with_python(self):
        if not self.notebooks_is_empty():
            widget = self.ui.notebook.currentWidget()
            if widget is not None:
                if widget.objectName() == "editor-frame":
                    if widget.editor.lexer_name=="python":
                        return widget.editor
        
        return False
    
    def notebooks_is_empty(self) -> bool:
        return self.ui.isplitter.is_empty()

    def notebook_have_editor(self, notebook = None):
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
    
    def prepare_lab(self, area:int) -> None:
        self.side_right.set_notebook_index(area)
        self.side_right.setVisible(True)
        sizes = self.ui.div_main.sizes()
        sizes[2] = 300
        self.ui.div_main.setSizes(sizes)

    def run_user_notes(self):
        self.prepare_lab(self.side_right.notes)

    def run_code_warnings(self):
        self.prepare_lab(self.side_right.code_warnings)
        editor=self.notebook_have_editor_with_python()
        if editor:
            self.side_right.code_warnings.get_warnings(editor)
    
    def run_code_tree(self):
        self.prepare_lab(self.side_right.code_tree)
        editor=self.notebook_have_editor_with_python()
        if editor:
                self.side_right.code_tree.build_tree(editor)
    
    def run_code_doctor(self):
        self.prepare_lab(self.side_right.code_doctor)
        editor=self.notebook_have_editor_with_python()
        if editor:
            self.side_right.code_doctor.do_analyze(editor.text(), editor)
    
    def adjust_code(self, editor = None):
        if editor is None or isinstance(editor, bool):
         if not self.notebooks_is_empty():
            widget=self.ui.notebook.currentWidget()
            if widget.objectName() == "editor-frame":
                editor = widget.editor
        
        if editor is None or isinstance(editor, bool):
            return

        if editor.lexer_name == "python":
            code_smell=editor.text()
            nice_code=getfn.get_straighten_code(code_smell)
            editor.set_text(nice_code)

    def adjust_imports(self):
        if not self.notebooks_is_empty():
            editor=self.ui.notebook.currentWidget().editor
            if editor.lexer_name == "python":
                code_smell=editor.text()
                nice_code=getfn.get_sorted_imports(code_smell)
                editor.set_text(nice_code)
    
    def fix_bugs(self, editor):
        self.adjust_code(editor)
        self.run_code_warnings()
    
    def close_lab(self):
        self.side_right.setVisible(False)
    
    def split_in_group_hor(self):
        widget = self.notebook_have_editor()
        if widget:
            widget.split_horizontally()

    def split_in_group_ver(self):
        widget = self.notebook_have_editor()
        if widget:
            widget.split_vertically()
    
    def join_in_group(self):
        widget = self.notebook_have_editor()
        if widget:
            widget.join_in_group()
    
    def get_editor_class(self):
        return EditorView

class Base(ComponentsInterface):
    
    on_new_notebook = pyqtSignal(object)
    on_new_tab = pyqtSignal(object)
    on_new_editor=pyqtSignal(object)
    on_window_title_changed = pyqtSignal(str)

    def __init__(self, parent) -> None:
        super().__init__(parent)
    
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

        self.ui.index.on_double_clicked.connect(self.new_file)
        self.ui.index.actions.on_new_clicked.connect(self.new_file)
        self.ui.index.actions.on_open_file_clicked.connect(self.open_file)
        self.ui.index.actions.on_open_folder_clicked.connect(self.open_folder)
        self.ui.index.actions.on_show_commands_clicked.connect(self.show_command_palette)
        
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
        
        self.side_left.explorer.on_path_changed.connect(self.explorer_path_changed)

        self.configure_notebook(self.ui.notebook)
        self.run_api()
        self.init_ui()
        self.load_plugins()
        self.build_components()
    
    def configure_notebook(self, notebook):
        notebook.last_tab_closed.connect(self.tabbar_last_closed)
        notebook.on_user_event.connect(self.ui.set_notebook)
        notebook.currentChanged.connect(self.notebook_tab_changed)
        notebook.tabBarDoubleClicked.connect(lambda: self.new_file(notebook))
        notebook.tab_closed.connect(self.notebook_tab_closed)
        notebook.on_tab_added.connect(self.toggle_main_views)
        notebook.on_tab_droped.connect(self.tab_droped)
        notebook.cornerWidget().menu.split_in_group_ver.triggered.connect(self.split_in_group_ver)
        notebook.cornerWidget().menu.split_in_group_hor.triggered.connect(self.split_in_group_hor)
        notebook.cornerWidget().menu.join_in_group.triggered.connect(self.join_in_group)
        notebook.cornerWidget().btn_split.on_split_vertical.connect(self.split_notebook_ver)
        notebook.cornerWidget().btn_split.on_split_horizontal.connect(self.split_notebook_hor)

class App(Base):
    def __init__(self, ui, qt_app) -> None:
        super().__init__(None)
        self.qt_app=qt_app
        self.ui=ui
        self.last_folder = cache_manager.restore_from_list("folders", -1)
        self.last_repository = cache_manager.restore_from_list("repositorys", -1)
        self.files_opened=[]
        self.tabs_count=0
        self.menu=self.ui.menu_bar
        self.tool_bar=self.ui.tool_bar
        self.status_bar=self.ui.status_bar
        self.side_bottom=self.ui.side_bottom
        self.side_left=self.ui.side_left
        self.side_right=self.ui.side_right
        self.editor_widgets = self.ui.editor_widgets
        self.ui.set_controller(self)
        self.run()
    
    def split_notebook_hor(self, widget):
        self.create_new_notebook(Qt.Horizontal, widget)        
    
    def split_notebook_ver(self, widget):
        self.create_new_notebook(Qt.Vertical, widget)
    
    def init_ui(self):
        self.welcome_widget=self.ui.welcome
        index = self.ui.notebook.add_tab_and_get_index(
            self.welcome_widget,
            f"# Get Started"
        )
        self.configure_tab(
            index,
            f"# Get Started", "init"
        )
        self.on_new_tab.emit(self.welcome_widget)
    
    #TODO
    def create_editor_from_file(self, code_file) -> object:
        editor=EditorView(self, self.ui, self.ui.notebook, code_file)
        editor.on_tab_content_changed.connect(self.update_tab)
        index = self.ui.notebook.add_tab_and_get_index(editor, code_file.name)
        self.configure_tab(index, code_file)
        self.on_new_editor.emit(editor)
        self.files_opened.append(code_file)
        return editor
    
    def create_new_notebook(self, orientation, widget=None):
        if widget is None:
            widget = self.ui.notebook
        parent_notebook = parent_tab_widget(widget)
        
        tab_data = parent_notebook.get_tab_data()

        notebook = NoteBookEditor(self.ui.isplitter, self)
        notebook.last_tab_closed.connect(self.tabbar_last_closed)
        notebook.on_user_event.connect(self.ui.set_notebook)
        
        self.on_new_notebook.emit(notebook)
        self.ui.set_notebook(notebook)
        
        editor = self.get_new_editor(notebook)
        editor.make_deep_copy(tab_data.widget)
        index = notebook.add_tab_and_get_index(editor, tab_data.title)
        notebook.setTabToolTip(index, tab_data.tooltip)
        notebook.setTabIcon(index, tab_data.icon)

        DIRS = {
            Qt.Vertical: consts.DOWN,
            Qt.Horizontal: consts.RIGHT
        }
        
        self.ui.isplitter.add_notebook(notebook)
        self.ui.isplitter.splitAt(parent_notebook, DIRS[orientation], notebook)
    
    def new_file(self, notebook=False):
        if isinstance(notebook, bool):
            notebook = self.ui.notebook

        self.tabs_count+=1

        editor=EditorView(self, self.ui,  notebook)
        editor.on_tab_content_changed.connect(self.update_tab)
        index = notebook.add_tab_and_get_index(
            editor,
            f"# Untituled-{self.tabs_count}"
        )
        self.configure_tab(
            index,
            f"# Untituled-{self.tabs_count}", "new"
        )
        self.on_new_editor.emit(editor)
    
    def open_file_from_search(self, file, query):
        if file != None:
            self.open_file(file)
            try:
                editor = self.ui.notebook.currentWidget().editor
                editor.findFirst(
                    query,
                    True,
                    False,
                    True,
                    True
                )
            except Exception as e:
                print(e)            

    def open_file_from_explorer(self, file_with_path):
        if Path(file_with_path).is_file():
            self.open_file(file_with_path)
    
    def open_file(self, file_with_path=False):
        home_dir = str(Path.home())
        if file_with_path:
            code_file = Path(file_with_path)

            if code_file.is_file():
                self.create_editor_from_file(code_file)

        else:
            if self.files_opened:
                home_dir=""
            files = QFileDialog.getOpenFileNames(None, 'Open File', home_dir)
            if files[0]:
                for file in files[0]:
                    code_file = Path(file)
                    if code_file.is_file():
                       self.create_editor_from_file(code_file)
            else:
                return
    def explorer_path_changed(self, folder_with_path):
        cache_manager.save_to_list(str(folder_with_path), "folders")
    
    def open_folder(self):
        folder = self.ui.side_left.explorer.open_folder()
        if folder is not None:
            if not self.ui.side_left.explorer.isVisible():
                self.tool_bar.explorer.trigger()
            self.status_bar.open_folder_mode()
    
    def open_repository(self):
        repository = self.ui.side_left.git.open_repository()
        repo_path = repository.workdir
        repo_branch = ""
        try:
            repo_branch = "/"+repository.head.shorthand
        except:
            pass
                
        if repo_path is not None:
            if not self.ui.side_left.git.isVisible():
                self.tool_bar.igit.trigger()
            self.ui.side_left.explorer.goto_folder(repo_path)
            self.status_bar.open_folder_mode()
            self.status_bar.source_control.setText(f"{pathlib.Path(repo_path).name}{repo_branch}")
            cache_manager.save_to_list(str(repo_path), "repositorys")
    
    def close_folder(self):
        self.ui.side_left.explorer.close_folder()
        self.status_bar.open_folder_mode(False) 
        
    def restore_folder(self, path):
        if pathlib.Path(path).exists() and pathlib.Path(path).is_dir():
            
            folder = self.ui.side_left.explorer.goto_folder(path)
            if folder is not None:
                self.status_bar.open_folder_mode()
        
    def restore_repository(self, path):
        if pathlib.Path(path).exists() and pathlib.Path(path).is_dir():
            
            repository = self.ui.side_left.git.open_repository(path)
            repo_path = repository.workdir
            repo_branch = ""
            try:
                repo_branch = "/"+repository.head.shorthand
            except:
                pass
            
            if repo_path is not None:
                self.status_bar.open_folder_mode()
                self.status_bar.source_control.setText(f"{pathlib.Path(repo_path).name}{repo_branch}")
                self.ui.side_left.explorer.goto_folder(repo_path)

    def reopen_editor(self):
        for notebook in self.ui.notebooks:
            notebook.open_last_closed_tab()
    
    def save_file(self):
        if isinstance(self.ui.notebook.currentWidget(), EditorView):
            self.ui.notebook.currentWidget().save_file()
    
    def close_editor(self):
        self.ui.notebook.close_tab()
    
    def find_in_editor(self):
        self.editor_widgets.close_all()
        if not self.notebooks_is_empty():
            widget = self.ui.notebook.currentWidget()
            if widget.objectName() == "editor-frame":
                self.ui.notebook.find_replace.do_find()
        
    def replace_in_editor(self):
        self.editor_widgets.close_all()
        if not self.notebooks_is_empty():
            widget = self.ui.notebook.currentWidget()
            if widget.objectName() == "editor-frame":
                self.ui.notebook.find_replace.do_replace()

    def configure_tab(self, index, tab_text, tab_type=False):
        widget = self.ui.notebook.widget(index)
        if widget is not None:

            if widget.objectName() == "editor-frame":
                widget.set_title(tab_text)
                
            self.ui.notebook.setTabToolTip(index, str(tab_text))

            if tab_type == "new":
                self.ui.notebook.setTabIcon(
                    index,
                    getfn.get_qicon(
                        getfn.get_icon_from_ext(".?icode")
                    )
                )
                
            elif tab_type == "init":
                self.ui.notebook.setTabIcon(
                    index,
                    getfn.get_app_icon()
                )

            else: 
                self.ui.notebook.setTabIcon(
                    index,
                    getfn.get_qicon(
                        getfn.get_icon_from_ext(
                            tab_text
                        )
                    )
                )
    
    def show_goto_line(self):
        self.editor_widgets.do_goto_line()
    
    def show_goto_symbol(self):
        self.editor_widgets.do_goto_symbol()

    def show_langs(self):
        self.editor_widgets.do_languages()

    def show_envs(self):
        self.editor_widgets.do_pyenvs()
    
    def show_command_palette(self):
        self.editor_widgets.do_commands()
    
    def tab_focused(self, tab_widget, focus_event):
        self.editor_widgets.close_all()
    
    def update_tab(self, data):
        index = self.ui.notebook.indexOf(data["widget"])

        if index == -1:
            return
        
        if data["data"]["name"] is None:
            title = data["data"]["first_line"]
            
            if len(title) > 20:
                title = title[0:20]
                title+="..."
            
            self.ui.notebook.setTabText(index, title+" "+str(data["widget"].title))
        else:
            self.ui.notebook.setTabText(index, data["data"]["name"])
        
        self.ui.notebook.setTabToolTip(index, data["data"]["tooltip"])
        self.ui.notebook.setTabIcon(index, data["data"]["icon"])
        self.ui.set_window_title(f"{self.ui.notebook.tabText(index)} - Intelligent Code")
        
    def last_tab_closed(self):
        self.toggle_main_views()

    def notebook_tab_closed(self, widget):
        if self.widget_is_code_editor(widget):
            file = widget.editor.file_path
            cache_manager.save_to_list(str(file), "files")

    def notebook_tab_changed(self, index):
        
        self.editor_widgets.close_all()
        widget = self.ui.notebook.widget(index)

        if index == -1:
            tab_text = ""
        else:
            tab_text = self.ui.notebook.tabText(index)+" - "
            if widget is not None:
                if widget.objectName() == "editor-frame":
                    self.editor_widgets.set_current_editor(widget)
                    if self.ui.notebook.currentWidget().objectName() == "editor-frame":
                        self.ui.notebook.currentWidget().editor.update_status_bar()
                        self.status_bar.editor_view()
                else:
                    self.ui.notebook.find_replace.hide_all()
                    self.status_bar.main_view()
                    
        self.ui.set_window_title(f"{tab_text}Intelligent Code")
            
    def update_statusbar_env(self, env):
        self.status_bar.interpreter.setText(f"Python {env.version_info.major}.{env.version_info.minor}.{env.version_info.micro}")
    
    def toggle_main_views(self):
        if self.notebooks_is_empty():
            self.ui.index.setVisible(True)
            self.ui.scroll_area.setVisible(False)
            self.status_bar.main_view()

        else:
            self.ui.scroll_area.setVisible(True)
            self.ui.index.setVisible(False)
            if self.notebooks_have_editor():
                self.status_bar.editor_view()
            else:
                self.status_bar.main_view()
    
    def tab_droped(self, event, notebook, tab_data):
        if event.source().count() <= 0:
            event.source().parent().hide()
        
        index = notebook.indexOf(tab_data.widget)
        
        notebook.setTabText(index, tab_data.title)
        notebook.setTabIcon(index, tab_data.icon)
        notebook.setTabToolTip(index, tab_data.tooltip)
        self.notebook_tab_changed(index)
    
    def editor_changed(self, editor):
        self.status_bar.editor_view()
    
    def tab_buffer_focused(self, buffer):
        self.status_bar.main_view()
    
    def tabbar_last_closed(self, tw):
        self.ui.isplitter.notebook_last_tab_closed()


def run(args=False) -> None:
    qapp = QApplication(sys.argv)
    qapp.setDesktopFileName("Icode")
    qapp.setApplicationVersion("0.0.1")
    qapp.setApplicationName("Intelligent Code")
    qapp.setDesktopSettingsAware(False)
    
    styler.beautify(qapp)
    exe=MainWindow(None, styler.windows_style, qapp)
    app=App(exe, qapp)
    config.restore_window(exe)
    exe.show_()
    sys.exit(qapp.exec_())

if __name__ == '__main__':
    run()
