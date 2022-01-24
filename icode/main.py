import faulthandler
import sys

sys.dont_write_bytecode = True
faulthandler.enable()

from base import *

class App(Base):
    def __init__(self, ui, qt_app) -> None:
        super().__init__(None)
        self.qt_app = qt_app
        self.ui = ui
        self.last_files = editor_cache.get_all_from_list("files")
        self.last_folders = editor_cache.get_all_from_list("folders")
        self.last_folder = editor_cache.restore_from_list("folders", -1)
        self.last_repository = editor_cache.restore_from_list("repositorys", -1)
        self.files_opened = []
        self.tabs_count = iconsts.INIT_TAB_COUNT
        self.menu = self.ui.menu_bar
        self.tool_bar = self.ui.tool_bar
        self.status_bar = self.ui.status_bar
        self.side_bottom = self.ui.side_bottom
        self.side_left = self.ui.side_left
        self.side_right = self.ui.side_right
        self.editor_widgets = self.ui.editor_widgets
        self.april = self.ui.april
        self.ui.set_controller(self)
        self.run()
        self.run_api()
        self.init_ui()
        self.load_plugins()
        self.build_components()
        self.open_app()

    def init_ui(self):
        self.welcome_widget = self.ui.welcome
        index = self.ui.notebook.add_tab_and_get_index(
            self.welcome_widget, f"# Get Started"
        )
        self.configure_tab(index, f"# Get Started", "init")
        self.on_new_tab.emit(self.welcome_widget)

    #TODO
    def create_editor_from_file(self, code_file) -> object:
        editor = EditorView(self, self.ui, self.ui.notebook, code_file)
        editor.on_tab_content_changed.connect(self.update_tab)
        index = self.ui.notebook.add_tab_and_get_index(editor, code_file.name)
        self.configure_tab(index, code_file)
        self.on_new_editor.emit(editor)
        self.files_opened.append(code_file)
        return editor

    def create_new_notebook(self, orientation, widget=None, copy:bool=True):
        if widget is None:
            widget = self.ui.notebook
        parent_notebook = parent_tab_widget(widget)

        tab_data = parent_notebook.get_tab_data()

        notebook = NoteBookEditor(self.ui.isplitter, self)
        notebook.last_tab_closed.connect(self.tabbar_last_closed)
        notebook.on_user_event.connect(self.ui.set_notebook)

        self.on_new_notebook.emit(notebook)
        self.ui.set_notebook(notebook)
        
        if copy:
            editor = self.get_new_editor(notebook)
            editor.make_deep_copy(tab_data.widget)
            index = notebook.add_tab_and_get_index(editor, tab_data.title)
            notebook.setTabToolTip(index, tab_data.tooltip)
            notebook.setTabIcon(index, tab_data.icon)

        DIRS = {Qt.Vertical: consts.DOWN, Qt.Horizontal: consts.RIGHT}

        self.ui.isplitter.add_notebook(notebook)
        self.ui.isplitter.splitAt(parent_notebook, DIRS[orientation], notebook)
        return notebook

    def new_file(self, notebook=False):
        if isinstance(notebook, bool):
            notebook = self.ui.notebook

        self.tabs_count += 1

        editor = EditorView(self, self.ui, notebook)
        editor.on_tab_content_changed.connect(self.update_tab)
        index = notebook.add_tab_and_get_index(
            editor, f"# Untituled-{self.tabs_count}")
        self.configure_tab(index, f"# Untituled-{self.tabs_count}", "new")
        self.on_new_editor.emit(editor)

    def open_file_from_search(self, file, query):
        if file != None:
            self.open_file(file)
            try:
                editor = self.ui.notebook.currentWidget().editor
                editor.findFirst(query, True, False, True, True)
            except Exception as e:
                print(e)

    def open_file_from_explorer(self, file_with_path):
        self.open_file(file_with_path)

    def open_file(self, file_with_path=False):
        home_dir = str(Path.home())
        if file_with_path:
            code_file = Path(file_with_path)
            duplicate = self.is_duplicated_file(file_with_path, self.ui.notebook)
            if code_file.is_file():
                if duplicate:
                    duplicate["notebook"].setCurrentWidget(duplicate["widget"])
                else:
                    self.create_editor_from_file(code_file)
                    editor_cache.save_to_list(str(file_with_path), "files")
                
        else:
            if self.files_opened:
                home_dir = ""
            files = QFileDialog.getOpenFileNames(None, 'Open File', home_dir)
            if files[0]:
                for file in files[0]:
                    code_file = Path(file)
                    duplicate = self.is_duplicated_file(file_with_path, self.ui.notebook)
                    if code_file.is_file() and not duplicate:
                        self.create_editor_from_file(code_file)
                        editor_cache.save_to_list(str(file_with_path), "files")
                    else:
                        duplicate["notebook"].setCurrentWidget(duplicate["widget"])
            else:
                return
    
    def open_dir(self, dir=None):
        if dir is not None:
            folder = self.ui.side_left.explorer.open_folder(dir)
            if not self.ui.side_left.explorer.isVisible():
                self.tool_bar.explorer.trigger()
            self.status_bar.open_folder_mode()
    
    def explorer_path_changed(self, folder_with_path):
        editor_cache.save_to_list(str(folder_with_path), "folders")

    def open_folder(self):
        folder = self.ui.side_left.explorer.open_folder()
        if folder is not None:
            if not self.ui.side_left.explorer.isVisible():
                self.tool_bar.explorer.trigger()
            self.status_bar.open_folder_mode()
    
    def open_repository(self, repository=None):
        if not isinstance(repository, str) or repository is None:
            repository = self.ui.side_left.git.open_repository()
        self.enter_repository(repository)

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
            self.enter_repository(repository)

    def reopen_editors(self):
        for notebook in self.ui.notebooks:
            notebook.open_last_closed_tab()
    
    def reopen_editor(self):
        self.ui.notebook.open_last_closed_tab()

    def save_file(self):
        if isinstance(self.ui.notebook.currentWidget(), EditorView):
            self.ui.notebook.currentWidget().save_file()
    
    def save_all(self):
        for notebook in self.ui.notebooks:
            for i in range(notebook.count()):
                editor = notebook.widget(i)
                if isinstance(editor, EditorView):
                    editor.save_file()

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
                    index, getfn.get_qicon(getfn.get_icon_from_ext(".?icode")))

            elif tab_type == "init":
                self.ui.notebook.setTabIcon(index, getfn.get_app_icon())

            else:
                self.ui.notebook.setTabIcon(
                    index, getfn.get_qicon(getfn.get_icon_from_ext(tab_text)))
    
    def change_ide_mode(self, mode:int) -> None:
        print(mode)
    
    def call_april(self):
        self.ui.april.appear()
    
    def show_notifications(self):
        self.ui.notificator.appear()
    
    def show_goto_tab(self):
        self.editor_widgets.do_goto_tab()
    
    def show_goto_line(self):
        self.editor_widgets.do_goto_line()

    def show_langs(self):
        self.editor_widgets.do_languages()

    def show_command_palette(self):
        self.editor_widgets.do_commands()
    
    def show_space_mode(self):
        self.editor_widgets.do_space_mode()
    
    def show_eol_mode(self):
        self.editor_widgets.do_eol_mode()

    def tab_focused(self, tab_widget, focus_event):
        self.editor_widgets.close_all()

    def update_tab(self, data):
        """When any change happen with tab data"""
        index = self.ui.notebook.indexOf(data["widget"])

        if index == -1:
            return

        if data["data"]["name"] is None:
            title = data["data"]["first_line"]

            if len(title) > iconsts.MAX_TITLE_LENGTH:
                title = title[0:iconsts.MAX_TITLE_LENGTH]
                title += "..."

            self.ui.notebook.setTabText(
                index, title + " " + str(data["widget"].title))
        else:
            self.ui.notebook.setTabText(index, data["data"]["name"])

        self.ui.notebook.setTabToolTip(index, data["data"]["tooltip"])
        self.ui.notebook.setTabIcon(index, data["data"]["icon"])
        self.ui.set_window_title(
            f"{self.ui.notebook.tabText(index)} - Intelligent Code")

    def last_tab_closed(self):
        self.toggle_main_views()

    def notebook_tab_closed(self, widget):
        pass    

    def notebook_tab_changed(self, index):
        """Update widgets to show new tab data"""
        self.editor_widgets.close_all()
        widget = self.ui.notebook.widget(index)

        if index == -1:
            tab_text = ""
        else:
            tab_text = self.ui.notebook.tabText(index) + " - "
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

    def toggle_main_views(self):
        """toggle beetwen initial screen and editor screen"""
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
        """When some tabbar close the last tab"""
        self.ui.isplitter.notebook_last_tab_closed()

    def open_research_space(self, area:str) -> None:
        """Turn visible the side right(labs) and change current workspace"""
        self.side_right.set_space(area)
        self.side_right.setVisible(True)
        sizes = self.ui.div_main.sizes()
        sizes[2] = iconsts.LAB_BASE_SIZE
        self.ui.div_main.setSizes(sizes)

    def close_lab(self):
        self.side_right.setVisible(False)
    
    def split_notebook_hor(self, widget:QWidget) -> None:
        """Create a new notebook and split horizontally, like a vscode"""
        self.create_new_notebook(Qt.Horizontal, widget)

    def split_notebook_ver(self, widget:QWidget) -> None:
        """Create a new notebook and split vertically, like a vscode"""
        self.create_new_notebook(Qt.Vertical, widget)

    def split_in_group_hor(self) -> None:
        """Split the editor in two horizontally, like a vscode"""
        widget = self.notebook_have_editor()
        if widget:
            widget.split_horizontally()

    def split_in_group_ver(self) -> None:
        """Split the editor in two vertically, like a vscode"""
        widget = self.notebook_have_editor()
        if widget:
            widget.split_vertically()

    def join_in_group(self) -> None:
        """Merge the splited editors in one, like a vscode"""
        widget = self.notebook_have_editor()
        if widget:
            widget.join_in_group()
    
    def enter_repository(self, repository, opened:bool=True) -> None:
        """
        Make the application create the enviroment for source control,
        change visual aspects and save the repository in cache
        """
        repo_path = getattr(repository, "workdir", None)
        if repo_path is not None:
            repo_branch = ""
            try:
                repo_branch = "/" + repository.head.shorthand
            except:
                pass

            if repo_path is not None:
                self.status_bar.open_folder_mode()
                self.status_bar.source_control.setText(
                    f"{pathlib.Path(repo_path).name}{repo_branch}")
                self.ui.side_left.explorer.goto_folder(repo_path)
                if opened:
                    if not self.ui.side_left.git.isVisible():
                        self.tool_bar.igit.trigger()
                    editor_cache.save_to_list(str(repo_path), "repositorys")
    
    def open_app(self):
        print("SUCESS:TRUE")
    
    def quit_app(self, window):
        settings.save_window(window, self)


def run(args=False) -> None:
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    qapp = QApplication(sys.argv)
    qapp.setDesktopFileName("Icode")
    qapp.setApplicationVersion("0.0.1")
    qapp.setApplicationName("Intelligent Code")
    qapp.setDesktopSettingsAware(False)

    styler.beautify(qapp)
    exe = MainWindow(None, styler.windows_style, qapp)
    app = App(exe, qapp)
    settings.restore_window(exe, app, getfn)
    exe.show_()
    sys.exit(qapp.exec_())

if __name__ == '__main__':
    run()