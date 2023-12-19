from core import *


class App(Server):
    def __init__(self, ui: object, qt_app: object) -> None:
        super().__init__(None)
        self.qt_app = qt_app
        self.ui = ui
        self.ui.set_controller(self)
        self.menu = self.ui.menu_bar
        self.tool_bar = self.ui.tool_bar
        self.status_bar = self.ui.status_bar
        self.side_left = self.ui.side_left
        self.side_right = self.ui.side_right
        self.editor_widgets = self.ui.editor_widgets
        self.april = self.ui.april
        self.styler = Styler(self, self.ui, self.qt_app)
        self.styler.beautify()
        self.init_controllers()
        self.run()  # running the server
        self.run_api()  # setting the api for external services as widgets
        self.run_ui()
        self.load_plugins()
        self.build_components()
        self.open_app()

    def run_ui(self) -> None:
        """Organize the main widgets in current notebook"""
        self.welcome_widget = self.ui.welcome
        index = self.ui.notebook.add_tab_and_get_index(
            self.welcome_widget, f"# Get Started"
        )
        self.configure_tab(index=index, tab_type="icode")
        self.on_new_tab.emit(self.welcome_widget)

        self.ui.config_ui.setVisible(False)
        self.ui.notebook.close_widget(self.ui.config_ui)

    def open_file_from_search(self, file: str, query: str) -> None:
        if file is not None:
            self.open_file(file)
            try:
                editor = self.ui.notebook.currentWidget().editor
                editor.findFirst(query, True, False, True, True)
            except Exception as e:
                print(e)

    def open_file_from_explorer(self, file_with_path: str) -> None:
        self.open_file(file_with_path)

    def open_file(self, file_with_path=False) -> None:
        home_dir = str(Path.home())
        if file_with_path:
            code_file = Path(file_with_path)
            duplicate = self.is_file_duplicated(file_with_path, self.ui.notebook)
            if code_file.is_file():
                if duplicate:
                    # if file already exist in this notebook just go to file tab
                    duplicate["notebook"].setCurrentWidget(duplicate["widget"])
                else:
                    self.create_editor_from_file(code_file)
                    editor_cache.save_to_list(str(file_with_path), "files")

        else:
            home_dir = settings.ipwd()
            files = QFileDialog.getOpenFileNames(None, "Open File", home_dir)
            if files[0]:
                for file in files[0]:
                    code_file = Path(file)
                    duplicate = self.is_file_duplicated(file, self.ui.notebook)
                    if code_file.is_file() and not duplicate:
                        self.create_editor_from_file(code_file)
                        editor_cache.save_to_list(str(file), "files")
                    else:
                        duplicate["notebook"].setCurrentWidget(duplicate["widget"])

        self.on_commit_app.emit(0)

    def open_dir(self, dir=None) -> None:
        if dir is not None:
            folder = self.file_explorer.open_folder(dir)
            if not self.ui.side_left.explorer.isVisible():
                self.tool_bar.explorer.trigger()
            self.status_bar.open_folder_mode()
            settings.icwd(folder)

    def explorer_path_changed(self, folder_with_path):
        editor_cache.save_to_list(str(folder_with_path), "folders")

    def open_folder(self):
        folder = self.file_explorer.open_folder()
        if folder is not None:
            if not self.ui.side_left.explorer.isVisible():
                self.tool_bar.explorer.trigger()
            self.status_bar.open_folder_mode()
        self.on_commit_app.emit(0)
        settings.icwd(folder)

    def open_repository(self, repository=None):
        if not isinstance(repository, str) or repository is None:
            repository = self.git.open_repository()
        self.enter_repository(repository)
        self.on_commit_app.emit(0)

    def close_folder(self):
        self.file_explorer.close_folder()
        self.status_bar.open_folder_mode(False)

    def restore_folder(self, path):
        if pathlib.Path(path).exists() and pathlib.Path(path).is_dir():
            folder = self.file_explorer.goto_folder(path)
            if folder is not None:
                self.status_bar.open_folder_mode()

    def restore_repository(self, path):
        if pathlib.Path(path).exists() and pathlib.Path(path).is_dir():
            repository = self.git.open_repository(path)
            self.enter_repository(repository)

    def reopen_editors(self):
        for notebook in self.ui.notebooks:
            notebook.open_last_closed_tab()

    def reopen_editor(self):
        self.ui.notebook.open_last_closed_tab()

    def save_file(self):
        if isinstance(self.ui.notebook.currentWidget(), EditorView):
            self.ui.notebook.currentWidget().save_file()
        self.on_commit_app.emit(1)

    def save_all(self):
        for notebook in self.ui.notebooks:
            for i in range(notebook.count()):
                editor = notebook.widget(i)
                if isinstance(editor, EditorView):
                    editor.save_file()
        self.on_commit_app.emit(1)

    def close_editor(self):
        self.ui.notebook.close_tab()
        self.on_commit_app.emit(1)

    def find_in_editor(self):
        self.editor_widgets.close_all()
        if not self.are_notebooks_empty():
            widget = self.ui.notebook.currentWidget()
            if widget.objectName() == "editor-frame":
                self.ui.notebook.find_replace.do_find()

    def replace_in_editor(self):
        self.editor_widgets.close_all()
        if not self.are_notebooks_empty():
            widget = self.ui.notebook.currentWidget()
            if widget.objectName() == "editor-frame":
                self.ui.notebook.find_replace.do_replace()

    def configure_tab(self, index: int, tab_text: str = "", tab_type: str = ""):
        widget = self.ui.notebook.widget(index)
        if tab_type == "icode":
            self.ui.notebook.setTabIcon(index, getfn.get_app_icon())

        else:
            self.ui.notebook.setTabIcon(
                index, getfn.get_qicon(getfn.get_icon_from_ext(tab_text))
            )

        if isfn.is_widget_code_editor(widget):
            widget.set_title(tab_text)
            self.ui.notebook.setTabToolTip(index, str(tab_text))

    def configure_icode(self):
        if self.ui.notebook.is_widget_in(self.ui.config_ui):
            self.ui.notebook.close_widget(self.ui.config_ui)
        else:
            index = self.ui.notebook.add_tab_and_get_index(
                self.ui.config_ui, "Settings"
            )
            self.configure_tab(index=index, tab_type="icode")

    def change_minimap_visiblity(self, visiblity: bool) -> None:
        for notebook in self.ui.notebooks:
            for i in range(notebook.count()):
                widget = notebook.widget(i)
                if isfn.is_widget_code_editor(widget):
                    for editor in widget.get_editors():
                        editor.set_minimap_visiblity(visiblity)


    def show_notifications(self):
        """Show/Hide Notifications Panel"""
        self.ui.notificator.show_hide()

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

    def toggle_eol_visiblity(self):
        editor = self.has_notebook_editor()
        if editor:
            if editor.editor.eolVisibility():
                editor.editor.set_eol_visible(False)
                self.ui.status_bar.toggle_eol_visiblity("show")
            else:
                editor.editor.set_eol_visible(True)
                self.ui.status_bar.toggle_eol_visiblity("hide")

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
                title = title[0 : iconsts.MAX_TITLE_LENGTH]
                title += "..."

            self.ui.notebook.setTabText(index, title + " " + str(data["widget"].title))
        else:
            self.ui.notebook.setTabText(index, data["data"]["name"])

        self.ui.notebook.setTabToolTip(index, data["data"]["tooltip"])
        self.ui.notebook.setTabIcon(index, data["data"]["icon"])
        self.ui.set_window_title(
            f"{self.ui.notebook.tabText(index)} - Intelligent Code"
        )

    def last_tab_closed(self):
        """Display home screen when no have more tabs to show in any notebook"""
        self.toggle_main_views()

    def notebook_tab_closed(self, widget):
        pass

    def set_current_editor(self, widget):
        """Set the current editor and change icode current working dir in memory"""
        file = widget.file
        self.editor_widgets.set_current_editor(widget)
        self.todos.set_data(widget, file)
        if file is not None:
            settings.icwd(pathlib.Path(file).parent)
        self.on_current_editor_changed.emit(widget)

    def notebook_tab_changed(self, index):
        """Update widgets to show new tab data"""
        self.editor_widgets.close_all()
        widget = isfn.is_widget_code_editor(self.ui.notebook.widget(index))

        if index == -1:
            tab_text = ""
        else:
            tab_text = self.ui.notebook.tabText(index) + " - "

            if widget:
                self.set_current_editor(widget)
                widget.editor.update_status_bar()
                self.status_bar.editor_view()

            else:
                self.ui.notebook.find_replace.hide_all()
                self.status_bar.main_view()

        self.ui.set_window_title(f"{tab_text}Intelligent Code")

    def toggle_main_views(self):
        """toggle beetwen initial screen and editor screen"""
        if self.are_notebooks_empty():
            self.ui.index.setVisible(True)
            self.ui.scroll_area.setVisible(False)
            self.status_bar.main_view()

        else:
            self.ui.scroll_area.setVisible(True)
            self.ui.index.setVisible(False)
            if self.has_notebook_editor():
                self.status_bar.editor_view()
            else:
                self.status_bar.main_view()

    def tab_droped(self, event, notebook, tab_data):
        """When tab is droped prepare notebook to recive the tab"""
        if event.source().count() <= 0:
            event.source().parent().hide()

        index = notebook.indexOf(tab_data.widget)

        notebook.setTabText(index, tab_data.title)
        notebook.setTabIcon(index, tab_data.icon)
        notebook.setTabToolTip(index, tab_data.tooltip)
        self.notebook_tab_changed(index)

    def editor_changed(self, editor):
        """Change to editor view code buttons is showing"""
        self.status_bar.editor_view()

    def tab_buffer_focused(self, buffer):
        """Change to main view code buttons is hidden"""
        self.status_bar.main_view()

    def tabbar_last_closed(self, tw):
        """When some tabbar close the last tab"""
        self.ui.isplitter.notebook_last_tab_closed()

    def open_research_space(self, area: str) -> None:
        """Turn visible the side right(labs) and change current workspace"""
        self.side_right.set_space(area)
        self.side_right.setVisible(True)
        sizes = self.ui.div_main.sizes()
        sizes[2] = iconsts.LAB_BASE_SIZE
        self.ui.div_main.setSizes(sizes)

    def close_lab(self):
        self.side_right.setVisible(False)

    def split_notebook_hor(self, widget: QWidget) -> None:
        """Create a new notebook and split horizontally, like a vscode"""
        self.create_new_notebook(Qt.Horizontal, widget)

    def split_notebook_ver(self, widget: QWidget) -> None:
        """Create a new notebook and split vertically, like a vscode"""
        self.create_new_notebook(Qt.Vertical, widget)

    def split_in_group_hor(self) -> None:
        """Split the editor in two horizontally, like a vscode"""
        widget = self.has_notebook_editor()
        if widget:
            widget.split_horizontally()

    def split_in_group_ver(self) -> None:
        """Split the editor in two vertically, like a vscode"""
        widget = self.has_notebook_editor()
        if widget:
            widget.split_vertically()

    def join_in_group(self) -> None:
        """Merge the splited editors in one, like a vscode"""
        widget = self.has_notebook_editor()
        if widget:
            widget.join_in_group()

    def enter_repository(self, repository, opened: bool = True) -> None:
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
                    f"{pathlib.Path(repo_path).name}{repo_branch}"
                )
                self.file_explorer.goto_folder(repo_path)
                if opened:
                    if not self.ui.side_left.git.isVisible():
                        self.tool_bar.igit.trigger()
                    editor_cache.save_to_list(str(repo_path), "repositorys")

    def open_app(self):
        print("Status: ", True)

    def quit_app(self, window):
        self.save_status()
        system.end(0)

    def save_status(self):
        settings.save_window(self.ui, self)

    def commit_app(self, command: int = 0):
        if command == 0:
            self.last_files = editor_cache.get_all_from_list("files")
            self.last_folders = editor_cache.get_all_from_list("folders")
            self.update_components()

        elif command == 1:
            self.save_status()

        elif command == 2:
            self.update_components()
            self.save_status()

# .......................................................................................................................

    def new_editor(self, notebook, file=None, content_type=None):
        editor = EditorView(self, self.ui, notebook, file, content_type)
        self.configure_editor(editor)
        return editor

    def new_editor_notebook(self, orientation: int) -> None:
        self.tabs_count += 1
        notebook = self.create_new_notebook(orientation, self.ui.notebook, False)
        self.new_file(notebook)

    def new_file(self, notebook=False) -> EditorView:
        if isinstance(notebook, bool):
            notebook = self.ui.notebook

        self.tabs_count += 1

        editor = EditorView(self, self.ui, notebook)
        editor.on_tab_content_changed.connect(self.update_tab)
        index = notebook.add_tab_and_get_index(editor, f"# Untituled-{self.tabs_count}")
        self.configure_tab(index, f"# Untituled-{self.tabs_count}", None)
        self.configure_editor(editor)
        self.on_commit_app.emit(1)
        return editor

    def configure_editor(self, editor):
        editor.on_tab_content_changed.connect(self.update_tab)
        self.on_new_editor.emit(editor)

    def copy_editor(self, notebook, tab_data) -> EditorView:
        editor = self.new_editor(
            notebook, tab_data.widget.file, tab_data.widget.content_type
        )
        editor.make_deep_copy(tab_data.widget)
        index = notebook.add_tab_and_get_index(editor, tab_data.title)
        notebook.setTabToolTip(index, tab_data.tooltip)
        notebook.setTabIcon(index, tab_data.icon)
        return editor

    def create_editor_from_file(self, code_file: str) -> EditorView:
        editor = EditorView(self, self.ui, self.ui.notebook, code_file)
        index = self.ui.notebook.add_tab_and_get_index(editor, code_file.name)
        self.configure_tab(index, code_file)
        self.configure_editor(editor)
        self.files_opened.append(code_file)
        self.on_commit_app.emit(1)
        return editor

    def create_new_notebook(
        self, orientation: int, widget=None, copy: bool = True
    ) -> NoteBookEditor:
        """Create a new notebook and split in mainwindow"""
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
            self.copy_editor(notebook, tab_data)

        DIRS = {Qt.Vertical: consts.DOWN, Qt.Horizontal: consts.RIGHT}

        self.ui.isplitter.add_notebook(notebook)
        self.ui.isplitter.splitAt(parent_notebook, DIRS[orientation], notebook)
        self.on_commit_app.emit(1)
        return notebook

    def current_notebook_editor(
        self, notebook: object = None, attr: str = None, value: object = None
    ) -> Union[object, bool]:
        if not self.are_notebooks_empty():
            if notebook is None:
                widget = self.ui.notebook.currentWidget()
            else:
                widget = notebook.currentWidget()
            if widget is not None:
                if isfn.is_widget_code_editor(widget, attr, value):
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

    def is_file_duplicated(self, file: str, notebook: object) -> bool:
        for i in range(notebook.count()):
            widget = notebook.widget(i)
            if isfn.is_widget_code_editor(widget):
                if str(widget.file) == file:
                    return {"index": i, "widget": widget, "notebook": notebook}
        return False



def run(args=None, call_out=None) -> None:
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    qapp = QApplication(sys.argv)
    qapp.setDesktopFileName("Icode")
    qapp.setApplicationVersion("0.0.1")
    qapp.setApplicationName("Intelligent Code")
    qapp.setDesktopSettingsAware(False)
    
    exe = MainWindow(None, styler.windows_style, qapp)
    app = App(exe, qapp)
    settings.restore_window(exe, app, getfn)
    if call_out is not None:
        qapp.lastWindowClosed.connect(call_out)
    exe.show_()
    sys.exit(qapp.exec_())


if __name__ == "__main__":
    run()
