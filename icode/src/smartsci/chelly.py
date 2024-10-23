from .chelly_core import *
from smartlibs.eqscintilla import PanelPosition, EQsciPanelManager


class EditorView(QFrame):

    on_tab_content_changed = pyqtSignal(dict)

    def __init__(
        self,
        api: object,
        parent: object,
        notebook: object,
        file=None,
        content_type=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("editor-frame")
        self.api = api
        self.parent = parent
        self.notebook = notebook
        self._title = None
        self.content_type = "text"
        if isinstance(content_type, str):
            self.content_type = content_type

        self.file = file
        self._editor = None
        self._editors = []
        self.icons = getfn.get_smartcode_icons("editor")
        self.file_watcher = IFile(self)
        self.view_thread = QThread(self)

        if self.file is not None:
            self.file_watcher.start_monitoring(str(self.file))

        self.init_ui()

    def run_schedule(self):
        self.breadcrumb_controller1.run()
        self.breadcrumb_controller2.run()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(iconsts.EDITOR_LAYOUT_SPACING)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.div = QSplitter(self)
        self.div.setOrientation(Qt.Vertical)

        self.div_main = Div(self.div)
        self.div_mirror = Div(self.div)

        self.init_text_editor()

        self.breadcrumb_controller1 = BreadcrumbController(
            self, self.editor_main)
        self.breadcrumb_controller1.on_update_header.connect(
            self.update_breadcrumb)
        self.breadcrumb_controller1.moveToThread(self.view_thread)

        self.breadcrumb_controller2 = BreadcrumbController(
            self, self.editor_mirror)
        self.breadcrumb_controller2.on_update_header.connect(
            self.update_breadcrumb)
        self.breadcrumb_controller2.moveToThread(self.view_thread)
        self.view_thread.started.connect(self.run_schedule)

        self._editors.append(self.editor_main)
        self._editors.append(self.editor_mirror)

        self.div.addWidget(self.div_main)
        self.div.addWidget(self.div_mirror)
        self.div.setSizes(iconsts.EDITOR_DIV_SIZES)
        self.setMinimumWidth(iconsts.EDITOR_MIN_WIDTH)

        self._editor = self.editor_main

        self.breadcrumbs_widget = Breadcrumbs(self)

        self.breadcrumbs = {
            "first": self.breadcrumbs_widget.breadcrumb0,
            "second": self.breadcrumbs_widget.breadcrumb1,
            "third": self.breadcrumbs_widget.breadcrumb2,
            "fourth": self.breadcrumbs_widget.breadcrumb3,
            "last": self.breadcrumbs_widget.breadcrumb4,
            "code-first": self.breadcrumbs_widget.breadcrumb00,
            "code-second": self.breadcrumbs_widget.breadcrumb01,
            "code-third": self.breadcrumbs_widget.breadcrumb02,
            "code-last": self.breadcrumbs_widget.breadcrumb03,
            "info-file": self.breadcrumbs_widget.file_info,
            "info-git": self.breadcrumbs_widget.src_ctrl_info,
            "info-warings": self.breadcrumbs_widget.warnings_info,
            "info-errors": self.breadcrumbs_widget.errors_info,
        }

        self.layout.addWidget(self.breadcrumbs_widget)
        self.layout.addWidget(self.div)

        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(
            iconsts.BREADCRUMB_SHADOW_BLURRADIUS_STATE0)
        self.drop_shadow.setOffset(
            iconsts.BREADCRUMB_SHADOW_Y_OFFSET_STATE0,
            iconsts.BREADCRUMB_SHADOW_X_OFFSET_STATE0,
        )
        self.drop_shadow.setColor(QColor(0, 0, 0))
        self.breadcrumbs_widget.setGraphicsEffect(self.drop_shadow)

        self.join_in_group()
        self.view_thread.start()

    def init_text_editor(self):
        """Editor Main"""
        self.editor_main = Editor(self, self.file)
        self.editor_main.connector.auto_save_file.connect(self.file_saved)
        self.editor_main.verticalScrollBar().valueChanged.connect(
            self.update_shadow)
        self.editor_main.cursorPositionChanged.connect(
            lambda: self.update_shadow(self.editor_main.verticalScrollBar().
                                       value()))
        self.editor_main.on_focused.connect(self.focused)
        self.editor_main.on_saved.connect(self.update_title)
        self.editor_main.idocument.on_changed.connect(self.update_code)
        self.minimap_main = MiniMapBox(self.editor_main)
        self.editor_main.set_minimap(self.minimap_main)
        self.panel_manager_main = EQsciPanelManager(self.editor_main)
        self.panel_manager_main.append(self.minimap_main, PanelPosition.RIGHT)

        self.idocument = self.editor_main.idocument

        self.div_main.addWidget(self.editor_main)
        """Editor Mirror"""

        self.editor_mirror = Editor(self, self.file)
        self.editor_mirror.setDocument(self.editor_main.document())
        self.editor_mirror.verticalScrollBar().valueChanged.connect(
            self.update_shadow)
        self.editor_mirror.cursorPositionChanged.connect(
            lambda: self.update_shadow(self.editor_mirror.verticalScrollBar().
                                       value()))
        self.editor_mirror.on_focused.connect(self.focused)
        self.editor_mirror.on_saved.connect(self.update_title)
        self.editor_mirror.idocument.on_changed.connect(self.update_code)
        self.minimap_mirror = MiniMapBox(self.editor_mirror)
        self.editor_mirror.set_minimap(self.minimap_mirror)
        self.panel_manager_mirror = EQsciPanelManager(self.editor_mirror)
        self.panel_manager_mirror.append(self.minimap_mirror, PanelPosition.RIGHT)

        self.idocument_mirror = self.editor_mirror.idocument

        self.div_mirror.addWidget(self.editor_mirror)
        self.editor_main.update_document()
        self.editor_mirror.update_document()


    def update_breadcrumb(self, data: dict) -> None:
        text = False
        widget = False
        type = False
        icon = False
        last = False
        keys = data.keys()
        if "text" in keys:
            text = data["text"]
        if "widget" in keys:
            if data["widget"] in self.breadcrumbs.keys():
                widget = self.breadcrumbs[data["widget"]]
        if "type" in keys:
            type = data["type"]
        if "icon" in keys:
            icon = data["icon"]
        if "last" in keys:
            last = data["last"]

        if widget:
            if text:
                if not last:
                    text += f" {get_unicon('fae', 'bigger')}"
                widget.setText(text)
            if icon:
                widget.setIcon(icon)

            if type:
                widget.setStyleSheet(f"color:{type}")

            widget.setVisible(True)

            if not text and not icon:
                widget.setVisible(False)

    def split_horizontally(self):
        self.div.setOrientation(Qt.Vertical)
        self.div_mirror.show()

    def split_vertically(self):
        self.div.setOrientation(Qt.Horizontal)
        self.div_mirror.show()

    def join_in_group(self):
        self.div_mirror.hide()

    def focused(self, event, widget):
        self._editor = widget
        self.api.tab_focused(self, event)
        self.update_shadow(self._editor.verticalScrollBar().value())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_shadow(self._editor.verticalScrollBar().value())

    def update_shadow(self, value):
        if value > 2:
            self.drop_shadow.setBlurRadius(
                iconsts.BREADCRUMB_SHADOW_BLURRADIUS_STATE1)
            self.drop_shadow.setOffset(
                iconsts.BREADCRUMB_SHADOW_Y_OFFSET_STATE1,
                iconsts.BREADCRUMB_SHADOW_X_OFFSET_STATE1,
            )
        else:
            w = self.editor.minimap.size().width()
            y_offset = self.size().width() - w - 200
            self.drop_shadow.setBlurRadius(
                iconsts.BREADCRUMB_SHADOW_BLURRADIUS_STATE0)
            self.drop_shadow.setOffset(
                y_offset, iconsts.BREADCRUMB_SHADOW_X_OFFSET_STATE0)

    @property
    def editor(self):
        return self._editor

    @property
    def editors(self):
        return self._editors

    def get_editors(self):
        return self.editor_main, self.editor_mirror

    @property
    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def update_title(self, new_title):
        self.set_title(new_title)

    def update_code(self, data):
        self.on_tab_content_changed.emit({"widget": self, "data": data})

    def save_file(self):
        if self.file is None:
            home_dir = settings.ipwd()
            file = QFileDialog.getSaveFileName(None, "Open file", home_dir)
            if file[0]:
                self.file = file[0]
                settings.icwd(Path(self.file).parent)

                filefn.write_to_file(self.editor_main.text(), file[0])
                self.editor_main.save_file(self.file)
                self.editor_mirror.save_file(self.file)

                self.editor_main.define_lexer()
                self.editor_mirror.define_lexer()
                self.file_watcher.start_monitoring(str(self.file))
        else:
            filefn.write_to_file(self.editor_main.text(), self.file)
            self.editor_main.save_file(self.file)
            self.editor_mirror.save_file(self.file)

    def file_saved(self):
        if self.file is None:
            self.save_file()

        else:
            self.editor_main.save_file(self.file)
            self.editor_mirror.save_file(self.file)

    def load_file(self):
        try:
            if self.file is not None:
                row1, col1 = self.editor_main.getCursorPosition()
                row2, col2 = self.editor_mirror.getCursorPosition()
                self.editor_main.set_text(filefn.read_file(self.file))
                self.editor_main.setCursorPosition(row1, col1)
                self.editor_mirror.setCursorPosition(row2, row2)
                self.save_file()
        except:
            pass

    def make_deep_copy(self, editor):
        self.file = editor.file
        self.editor_main.file_path = self.file
        self.editor_mirror.file_path = self.file
        self.editor_main.clone_this_editor(editor.editor_main)
        self.editor_mirror.clone_this_editor(editor.editor_mirror)


    def show_hide_breadcrumbs(self, state: bool = None):
        if state is None:
            self.breadcrumbs_widget.setVisible(
                not self.breadcrumbs_widget.isVisible())
        else:
            self.breadcrumbs_widget.setVisible(state)

    def show_breadcrumbs(self):
        self.breadcrumbs_widget.setVisible(True)

    def hide_breadcrumbs(self):
        self.breadcrumbs_widget.setVisible(False)

    def save_state(self):
        content_path = str(self.file)

        content = self.editor.text()
        selection = self.editor.getSelection()
        cursor_pos = self.editor.getCursorPosition()
        lexer = self.editor.lexer_name
        vbar = self.editor.verticalScrollBar().value()
        hbar = self.editor.horizontalScrollBar().value()
        if self.file is None:
            content_path = None

        return {
            "type": "text",
            "path": content_path,
            "text": content,
            "selection": selection,
            "cursor": cursor_pos,
            "lexer": lexer,
            "hbar": hbar,
            "vbar": vbar,
        }

    def restore_state(self, state):
        lexer_name = state["lexer"]
        file = state["path"]
        code = state["text"]
        cursor = state["cursor"]
        selection = state["selection"]
        scroll_v = state["hbar"]
        scroll_h = state["vbar"]

        if file is None:
            self.editor.set_text(code)

        for code_editor in self.editors:
            code_editor.set_lexer(getfn.get_lexer_from_name(lexer_name))
            code_editor.setCursorPosition(cursor[0], cursor[1])
            code_editor.verticalScrollBar().setValue(scroll_v)
            code_editor.horizontalScrollBar().setValue(scroll_h)
            code_editor.setSelection(selection[0], selection[1],
                                        selection[2], selection[3])