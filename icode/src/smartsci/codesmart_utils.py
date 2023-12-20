import pathlib
from PyQt5.Qsci import *
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from functions import getfn, filefn
from . import iconsts, get_unicon
from .lexers import *
import re
import time


class CoEditor(QObject):

    on_change_lexer = pyqtSignal(object)
    on_highlight_text = pyqtSignal(int, int, int, int, int, bool)
    on_highlight_selection = pyqtSignal(int, int, int, int, int, bool)
    on_clear_indicator_range = pyqtSignal(int, int, int, int, int, bool)
    on_remove_annotations = pyqtSignal(str, list)

    def __init__(self, parent):
        super().__init__()
        self.editor = parent
        self.timer = QTimer(self)
        self.last_highlight_word = None

    def run(self):
        if self.editor.parent.is_text:
            self.editor.on_highlight_sel_request.connect(
                self.highlight_selection)
            self.editor.on_highlight_match_request.connect(
                self.highlight_match)
            self.editor.on_word_added.connect(
                lambda: self.timer.singleShot(500, self.set_lexer_from_code))
            self.editor.on_close_char.connect(self.close_char)
            self.editor.on_intellisense.connect(self.intellisense_editor)
            self.editor.on_clear_annotation.connect(
                self.prepare_annotations_garbage)

    def close_char(self, char):
        row, col = self.editor.getCursorPosition()
        char_to_close = self.editor.closable_key_map[char]
        can_close = getfn.get_char_is_closable(col, self.editor.text(row))
        if not can_close:
            self.editor.insertAt(char_to_close, row, col)

    def set_lexer_from_code(self):
        if self.editor.file_path is None:
            lexer = getfn.get_lexer_from_code(self.editor.text())
            if lexer is not None and callable(lexer):
                self.on_change_lexer.emit(lexer)

    def highlight_selection(
        self,
        row_from: int,
        col_from: int,
        row_to: int,
        col_to: int,
        has_selection: bool,
        selected_text: str,
        lines: int,
        all_text: str,
    ):
        if has_selection:
            ocurs = {}
            text = all_text.splitlines()
            val = re.escape(selected_text)
            try:
                for line in range(len(text)):
                    for match in re.finditer(val, text[line]):
                        if not line in ocurs.keys():
                            ocurs[line] = []
                        ocurs[line].append(match.span())

                for line, match in ocurs.items():
                    for span in match:
                        from_col, to_col = span
                        if row_from != line or col_from != from_col:
                            self.on_highlight_selection.emit(
                                line, from_col, line, to_col, 2, True)

            except Exception as e:
                print("highlight_selection Exception: ", e)

    def highlight_match(
        self,
        index: int,
        line: int,
        has_selection: bool,
        word: str,
        lines: int,
        all_text: str,
    ):
        if not has_selection:
            if self.last_highlight_word != word:
                self.on_clear_indicator_range.emit(0, 0, -1, -1, 3, False)
                ocurs = {}
                text = all_text.splitlines()
                self.last_highlight_word = word
                val = re.escape(word)
                try:
                    for line in range(len(text)):
                        for match in re.finditer(val, text[line]):
                            if not line in ocurs.keys():
                                ocurs[line] = []
                            ocurs[line].append(match.span())

                    for line, match in ocurs.items():
                        for span in match:
                            from_col, to_col = span
                            self.on_highlight_text.emit(
                                line, from_col, line, to_col, 3, False)

                except Exception as e:
                    print("highlight_match Exception: ", e)

    def intellisense_editor(self, editor, string):
        line, index = editor.getCursorPosition()
        editor.on_complete.emit({
            "code": editor.text(),
            "file": editor.file_path,
            "cursor-pos": editor.getCursorPosition(),
            "lexer-api": editor.lexer_api,
            "lexer-name": editor.lexer_name,
            "event-text": string,
            "word": editor.wordAtLineIndex(line, index),
        })

    def prepare_annotations_garbage(self, annotations_data, lines, type):
        notes_map = []
        notes_to_remove = []

        for line in range(lines):
            annotation = self.editor.annotation(line)
            if len(annotation) > 0:
                notes_map.append({"note": annotation, "line": line})

        for note in annotations_data:
            for item in notes_map:
                if item["note"] == note.content:
                    notes_to_remove.append({
                        "note": note,
                        "line": item["line"]
                    })
        self.on_remove_annotations.emit(type, notes_to_remove)
