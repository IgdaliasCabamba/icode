from .codesmart_core import *


class Editor(EditorBase):

    on_mouse_stoped = pyqtSignal(int, int, int)
    on_mouse_moved = pyqtSignal(object)
    on_mouse_pressed = pyqtSignal(object)
    on_mouse_released = pyqtSignal(object)
    on_cursor_pos_chnaged = pyqtSignal(int, int)
    on_lines_changed = pyqtSignal(int)
    on_selected = pyqtSignal(int, int, int, int)
    on_highlight_sel_request = pyqtSignal(int, int, int, int, bool, str, int,
                                          str)
    on_highlight_match_request = pyqtSignal(int, int, bool, str, int, str)
    on_focused = pyqtSignal(object, object)
    on_resized = pyqtSignal(object)
    on_style_changed = pyqtSignal(object)
    on_lexer_changed = pyqtSignal(object)
    on_word_added = pyqtSignal()
    on_modify_key = pyqtSignal()
    on_text_changed = pyqtSignal()
    on_document_changed = pyqtSignal(object)
    on_saved = pyqtSignal(str)
    on_abcd_added = pyqtSignal()
    on_complete = pyqtSignal(dict)
    on_close_char = pyqtSignal(str)
    on_intellisense = pyqtSignal(object, str)
    on_clear_annotation = pyqtSignal(list, int, str)

    def __init__(self, parent: object, file=Union[str, None]) -> None:
        super().__init__(parent)
        self.setObjectName("codesmart")
        self.parent = parent
        self.editor_view_parent = parent
        self.menu = self.parent.parent.menu_bar
        self.status_bar = self.parent.parent.status_bar
        self.file_path = file
        self._lexer = None
        self.lexer_name = "none"
        self.lexer_api = None
        self.minimap = False
        self._ide_mode = False
        self.edited = False
        self.saved = None
        self.saved_text = None
        self.folded_lines = []
        self.all_cursors_pos = []
        self._notes = []
        self.annotations_data = {
            "on_fold": [],
            "on_text_changed": [],
            "on_lines_changed": [],
            "on_cursor_pos_changed": [],
            "on_selection_changed": [],
            "permanent": [],
        }
        self.fold_indicators = {
            "lines": [],
            "image_id": [],
        }

        self.development_environment_thread = QThread(self)
        self.coeditor = CoEditor(self)
        self.connector = Connector(self)
        self.connector.update_all()
        self.connector.moveToThread(self.development_environment_thread)
        self.coeditor.moveToThread(self.development_environment_thread)
        self.development_environment_thread.started.connect(self.run_schedule)

        self.start()

    def start(self) -> None:
        if self.file_path is not None:
            self.set_text_from_file()
            self.saved = True

        else:
            self.define_lexer()
            self.saved = False

        self.update_document()
        self.listen_events()
        self.development_environment_thread.start()
        self.development_environment_thread.setPriority(QThread.LowestPriority)

    def listen_events(self):
        self._listen_sci_events()
        self.coeditor.on_change_lexer.connect(self.set_lexer)
        self.coeditor.on_highlight_selection.connect(self.add_indicator_range)
        self.coeditor.on_highlight_text.connect(self.add_indicator_range)
        self.coeditor.on_clear_indicator_range.connect(
            self.clear_indicator_range)
        self.coeditor.on_remove_annotations.connect(self.remove_annotations)
        self.on_key_pressed.connect(self.key_press_event)

    @property
    def ide_mode(self) -> bool:
        return self._ide_mode

    def set_ide_mode(self, ide_mode: bool) -> None:
        if ide_mode:
            self._ide_mode = True
            self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        else:
            self._ide_mode = False
            self.setAutoCompletionSource(QsciScintilla.AcsDocument)

    def add_development_environment_component(self, component: object,
                                              run: callable) -> None:
        self.development_environment_components.append(component)
        component.moveToThread(self.development_environment_thread)
        if self.development_environment_thread.isRunning():
            run()

    def run_schedule(self) -> None:
        self.connector.run()
        self.coeditor.run()

    def set_text_from_file(self, file_path: Union[str, None] = None) -> None:
        try:
            if file_path is None:
                code = filefn.read_file(self.file_path)
            else:
                code = filefn.read_file(file_path)
            self.setText(code)
            self.update_lines()
            self.define_lexer()
        except FileNotFoundError as e:
            self.info_image = self.add_image(self.icons.get_path("no-data"),
                                             (20, 5), (500, 500))
            self.set_mode(0)
            message = "File does not exist try to recreate pressing Ctrl+S"
            self.insertAt(message, 0, 0)

    def save_file(self, file_path: str):
        self.file_path = file_path
        self.saved = True
        self.on_saved.emit(str(self.file_path))
        self.saved_text = self.text()
        self.update_status_bar()
        self.update_document()

    def _margin_left_clicked(self, margin_nr: int, line_nr: int,
                             state: object) -> None:
        if self.markersAtLine(line_nr) == 0:
            self.debugger.add_break_point(line_nr)
        else:
            self.debugger.remove_break_point(line_nr)

    def _margin_right_clicked(self, margin_nr: int, line_nr: int,
                              state: object) -> None:
        pass

    def mouse_stoped(self, pos: int, x: int, y: int) -> None:
        self.on_mouse_stoped.emit(pos, x, y)

    def text_event(self) -> None:
        self.clear_annotations_by_type("on_text_changed")
        self.on_text_changed.emit()
        self.saved = False
        self.update_title()

    def lines_event(self) -> None:
        self.update_lines()
        self.clear_annotations_by_type("on_lines_changed")
        self.on_lines_changed.emit(self.lines())

    def cursor_event(self, index: int, line: int) -> None:
        self.update_status_bar_cursor_pos()
        self.clear_annotations_by_type("on_cursor_pos_changed")
        self.on_cursor_pos_chnaged.emit(index, line)
        self.on_highlight_match_request.emit(
            index,
            line,
            self.hasSelectedText(),
            self.wordAtLineIndex(index, line),
            self.lines(),
            self.text(),
        )

    def add_cursors(self, point: object, last_row: int, last_col: int) -> None:

        pos = self.SendScintilla(QsciScintillaBase.SCI_POSITIONFROMPOINTCLOSE,
                                 point.x(), point.y())

        if len(self.all_cursors_pos) > 1:
            for cur_pos in self.all_cursors_pos:
                offset = self.positionFromLineIndex(cur_pos[0], cur_pos[1])
                self.SendScintilla(QsciScintilla.SCI_ADDSELECTION, offset,
                                   offset)

        else:
            offset = self.positionFromLineIndex(last_row, last_col)

            self.SendScintilla(QsciScintilla.SCI_SETSELECTION, offset, offset)

            self.SendScintilla(QsciScintilla.SCI_ADDSELECTION, pos, pos)

    def remove_cursors(self) -> None:
        self.all_cursors_pos.clear()

    def remove_annotations(self, type, annotations):
        try:
            for annotation in annotations:  # BUG: ValueError: list.remove(x): x not in list
                if annotation["note"] in self.annotations_data[type]:
                    self.annotations_data[type].remove(annotation["note"])
                    self.clearAnnotations(annotation["line"])
        except Exception as e:
            print(e)

    def clear_annotations_by_type(self, type: str) -> None:
        if type in self.annotations_data.keys():
            self.on_clear_annotation.emit(self.annotations_data[type],
                                          self.lines(), type)

    def clear_annotations_by_line(self, type: str, line: object) -> None:
        try:
            if type in self.annotations_data.keys():
                for note in self.annotations_data[type]:
                    if line == note.row:
                        self.annotations_data[type].remove(note)
                        self.clearAnnotations(note.row)
        except Exception as e:
            print(e)

    def selection_event(self) -> None:
        row_from, col_from, row_to, col_to = self.getSelection()
        self.clear_annotations_by_type("on_selection_changed")
        self.on_selected.emit(row_from, col_from, row_to, col_to)
        self.on_highlight_sel_request.emit(
            row_from,
            col_from,
            row_to,
            col_to,
            self.hasSelectedText(),
            self.selectedText(),
            self.lines(),
            self.text(),
        )
        self.clear_indicator_range(0, 0, -1, -1, 2, False)
        if row_from + col_from + row_to + col_to > 0:
            self.show_white_spaces()
        else:
            self.hide_white_spaces()

    def display_tooltip(self, data: dict) -> None:
        QToolTip.showText(self.mapToGlobal(data["pos"]), data["text"],
                          self.viewport())

    def display_annotation(
        self,
        row: int,
        note: Union[str, list],
        type: int,
        event_to_remove: str,
        priority: int = 0,
    ) -> None:
        if priority > 0 and len(self.annotation(row)) > 0:
            return None

        annotation = SmartAnnotation(self._notes, note, row)

        if isinstance(annotation.annotation, list) or isinstance(
                annotation.annotation, QsciStyledText):
            self.annotate(row, annotation.annotation)
        else:
            self.annotate(row, annotation.annotation, type)

        if not event_to_remove in self.annotations_data.keys():
            self.annotations_data[event_to_remove] = []

        if not annotation in self.annotations_data[event_to_remove]:
            self.annotations_data[event_to_remove].append(annotation)
            self._notes.append(annotation.annotation)

    def update_header(self, data: dict) -> None:
        self.editor_view_parent.update_breadcrumb(data)

    def update_title(self) -> None:
        if self.file_path is None:
            title = self.text(0).replace("\n", "")
            self.idocument.set_first_line_text(title)

        else:
            name = Path(self.file_path).name

            if self.saved:
                self.idocument.set_name(name)
            else:
                self.idocument.set_name(f"⟲ {name}")

    def update_status_bar(self) -> None:
        self.status_bar.lang.setText(self.lexer_name.capitalize())

    def update_status_bar_cursor_pos(self) -> None:
        row, col = self.getCursorPosition()
        self.status_bar.line_col.setText(f"Row{row}, Col{col}")

    def update_document(self) -> None:
        if self.file_path is None:
            name = None
            tooltip = None
        else:
            name = Path(self.file_path).name
            tooltip = str(self.file_path)

        if self._lexer is not None and self.file_path is None:
            icon = getfn.get_icon_from_lexer(self.lexer_name)
        else:
            icon = getfn.get_qicon(getfn.get_icon_from_ext(self.file_path))

        self.idocument.set_data({
            "lexer_name": self.lexer_name,
            "name": name,
            "lexer": self._lexer,
            "tooltip": tooltip,
            "icon": icon,
            "file": self.file_path,
            "file_name": name,
        })

    def clone_this_editor(self, editor: object) -> None:
        self.setLexer(editor.lexer())
        self.setDocument(editor.document())
        self.lexer_name = editor.lexer_name
        row, col = editor.getCursorPosition()
        self.setCursorPosition(row, col)
        self.update_status_bar()
        self.update_document()
        if self.minimap:
            self.minimap.setDocument(self.document())
            self.minimap.setLexer(self.lexer())

    def mark_fold(self, line, mark, id) -> None:
        if line not in self.folded_lines:
            self.folded_lines.append(line)
        self.display_annotation(line, mark, id, "on_fold")

    def mouse_release_event(self, event: QMouseEvent) -> None:
        self.on_mouse_released.emit(event)
        for line in self.contractedFolds():
            self.mark_fold(line, "...", 5)

        for line in self.folded_lines:
            if not line in self.contractedFolds():
                self.folded_lines.remove(line)
                self.clear_annotations_by_line("on_fold", line)

    def mouse_press_event(self, event: QMouseEvent) -> None:
        self.on_mouse_pressed.emit(event)
        # word = self.wordAtPoint(event.pos()).lower()

        # cmenu = QMenu(self)
        # newAct = cmenu.addAction("Foo")
        # openAct = cmenu.addAction("Bar")
        # action = cmenu.exec_(self.mapToGlobal(event.pos()))

    def key_press_event(self, event: QKeyEvent) -> None:
        key = event.key()
        string = str(event.text())

        if key in range(65, 90):
            self.on_abcd_added.emit()

        if string in self.pre_complete_keys or key in range(65, 90):
            self.on_intellisense.emit(
                self, string)  # it make icode more fast and responsive

        if key in {32, 16777220}:
            self.on_word_added.emit()

        if key in {32, 16777217, 16777219, 16777220}:
            self.on_modify_key.emit()

        if string in self.closable_key_map.keys():
            self.on_close_char.emit(string)

    def mouse_move_event(self, event: QMouseEvent) -> None:
        self.on_mouse_moved.emit(event)

    def focus_in_event(self, event: QFocusEvent) -> None:
        self.on_focused.emit(event, self)

    def focus_out_event(self, event: QFocusEvent) -> None:
        QToolTip.hideText()

    def resize_event(self, event: QResizeEvent) -> None:
        self.on_resized.emit(event)
