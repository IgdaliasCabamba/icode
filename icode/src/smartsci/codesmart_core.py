import pathlib
from pathlib import Path
from typing import Union

from PyQt5.Qsci import *
from PyQt5.Qsci import QsciScintilla, QsciScintillaBase
from PyQt5.QtCore import (
    QFile,
    QFileSystemWatcher,
    QObject,
    QSize,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QMenu, QShortcut, QToolTip

from core.system import SYS_NAME
from functions import filefn, getfn

from . import iconsts
from .codesmart_utils import *
from .idocument import IDocument
from smartlibs.eqscintilla import EQscintilla
from .lexers import *


class SmartAnnotation:

    def __init__(self, all_notes, annotation, row):
        self.annotation = annotation
        self.row = row
        self._content = str()
        if isinstance(self.annotation, list):
            if self.annotation in all_notes:
                self.annotation.append(QsciStyledText(" "),
                                       216)  # 216 is the AnnotationLabel style

            for item in self.annotation:
                if isinstance(item, QsciStyledText):
                    self._content += item.text()
                elif isinstance(item, str):
                    self._content += item
        else:
            self._content = annotation

    @property
    def content(self):
        return self._content


class KeyBoard:
    """Trying to extend the default qscintilla's keyboard shortcuts"""

    def __init__(self, editor):
        self.editor = editor
        self.init_bindings()

    def init_bindings(self):
        commands = self.editor.standardCommands()
        command = commands.boundTo(Qt.ControlModifier | Qt.ShiftModifier
                                   | Qt.Key_T)
        if command is not None:
            command.setKey(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_B)

        # self.undo_shortcut = QShortcut(Qt.ControlModifier | Qt.Key_Z, self.editor)
        # self.redo_shortcut = QShortcut(Qt.ControlModifier | Qt.Key_Y, self.editor)


class Connector(QObject):

    auto_save_file = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.editor = parent

    def run(self):
        self.editor.on_text_changed.connect(self.update)

    def update(self):
        self.check_all()
        self.update_all()

    def check_all(self):
        if self.editor.menu.file.auto_save.isChecked():
            if self.editor.file_path is None:
                self.save_file()
                self.auto_save_file.emit()
            else:
                filefn.write_to_file(self.editor.text(), self.editor.file_path)

    def update_all(self):
        code_page = self.editor.SendScintilla(QsciScintilla.SCI_GETCODEPAGE)
        eol_mode = self.editor.eolMode()

        if eol_mode == iconsts.EOL_WINDOWS:
            eol_name = "CRLF"
        elif eol_mode == iconsts.EOL_MAC:
            eol_name = "CR"
        else:
            eol_name = "LF"

        if code_page == iconsts.CODE_PAGE_JAPANESE:
            code_name = "Japanese Shift-JIS"
        elif code_page == iconsts.CODE_PAGE_SIMPLIFIED_CHINESE:
            code_name = "Simplified Chinese GBK"
        elif code_page == iconsts.CODE_PAGE_KOREAN_UNIFIED:
            code_name = "Korean Unified Hangul Code"
        elif code_page == iconsts.CODE_PAGE_TRADITIONAL_CHINESE:
            code_name = "Traditional Chinese Big5"
        elif code_page == iconsts.CODE_PAGE_KOREAN_JOHAB:
            code_name = "Korean Johab"
        else:
            code_name = "UTF-8"

        indent_type = "Spaces:"
        if self.editor.indentationsUseTabs():
            indent_type = "Tabs:"

        self.editor.status_bar.indentation.setText(indent_type)
        self.editor.status_bar.indentation_size.setText(
            str(self.editor.tabWidth()))
        self.editor.status_bar.encode.setText(f"{code_name}")
        self.editor.status_bar.end_line_seq.setText(f"{eol_name}")

    def save_file(self):
        filefn.write_to_file(self.editor.text(), self.editor.file_path)


class IFile(QObject):

    on_file_deleted = pyqtSignal(str)
    on_file_modified = pyqtSignal(str)

    def __init__(self, parent: object):
        super().__init__(parent)
        self.editor = parent
        self.file_manager = QFileSystemWatcher(self)
        self.file_manager.fileChanged.connect(self.file_changed)

    def start_monitoring(self, file_path: str):
        self.file_manager.addPath(file_path)

    def file_changed(self, file):
        file_path = file
        if pathlib.Path(file).exists():
            self.on_file_modified.emit(file)
        else:
            self.on_file_deleted.emit(file)


class Debugger(QObject):

    def __init__(self, parent: object):
        super().__init__(parent)
        self.editor = parent
        self._current_line = 0
        self._book_marks = {
            "book-marks": [],
            "break-points": [],
            "log-points": []
        }

    @property
    def current_line(self):
        return self._current_line

    @property
    def breakpoints(self):
        return self._book_marks["break-points"]

    def set_current_line(self, line: int):
        line -= 1
        if line != self._current_line:
            last_line = self._current_line
            self._current_line = line

            if self.editor.markersAtLine(last_line) != 0:
                self.editor.markerDelete(last_line)

        if self.editor.markersAtLine(line) == 0:
            self.editor.markerAdd(line, self.editor.mark2)
            self.editor.setCursorPosition(line, 0)

    def add_break_point(self, line):
        self.editor.markerAdd(line, self.editor.mark1)
        self._book_marks["break-points"].append(line)

    def remove_break_point(self, line):
        self.editor.markerDelete(line)
        if line in self._book_marks["break-points"]:
            self._book_marks["break-points"].remove(line)


class SmartScintilla(EQscintilla):

    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.code_completers = []
        self.development_environment_components = []

        self.intellisense_thread = QThread(self)
        self.intellisense_thread.start()
        self.intellisense_thread.setPriority(QThread.LowestPriority)

    def add_code_completer(self, completer: object, run: callable) -> None:
        self.code_completers.append(completer)
        completer.moveToThread(self.intellisense_thread)
        if self.intellisense_thread.isRunning():
            run()


class EditorBase(SmartScintilla):
    abcd = {
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "m",
        "n", "l", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
         "y", "z",
    }
    pre_complete_keys = {".", "(", "[", "{", ",", ";", " ", "_"}
    closable_key_map = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
    on_key_pressed = pyqtSignal(object)

    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.idocument = IDocument(self)
        self.icons = getfn.get_smartcode_icons("smartsci")
        self.keyboard = KeyBoard(self)
        self.debugger = Debugger(self)
        self.editable = True
        self.build()

    def build(self) -> None:
        self.build_text()
        self.build_styles()
        self.build_margin()
        self.build_autocompletion()
        self.build_indicators()
        self.build_shortcuts()
        self._configure_qscintilla()
        self.set_policys()

    def _listen_sci_events(self) -> None:
        self.linesChanged.connect(self.lines_event)
        self.textChanged.connect(self.text_event)
        self.cursorPositionChanged.connect(self.cursor_event)
        self.selectionChanged.connect(self.selection_event)
        self.marginClicked.connect(self._margin_left_clicked)
        self.marginRightClicked.connect(self._margin_right_clicked)
        self.undo_action.activated.connect(self.undid)
        self.SCN_DWELLSTART.connect(self.mouse_stoped)

    def _configure_qscintilla(self) -> None:
        self.setBraceMatching(QsciScintilla.StrictBraceMatch)
        self.setAnnotationDisplay(QsciScintilla.ANNOTATION_INDENTED)
        self.SendScintilla(QsciScintilla.SCI_SETBUFFEREDDRAW, 0)
        self.SendScintilla(QsciScintilla.SCI_SETCODEPAGE, 65001)
        self.SendScintilla(QsciScintilla.SCI_SETLINEENDTYPESALLOWED, 1)
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, 1)
        self.SendScintilla(QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, 1)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, False)
        self.SendScintilla(QsciScintilla.SCI_SETFOLDFLAGS, 0)
        self.SendScintilla(QsciScintilla.SCI_SETMOUSEDWELLTIME, 500)
        self.SendScintilla(QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, 1)
        self.SendScintilla(
            QsciScintilla.SCI_SETVIRTUALSPACEOPTIONS,
            QsciScintilla.SCVS_RECTANGULARSELECTION,
        )
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE,
                           QsciScintilla.SC_MULTIPASTE_EACH)

    def build_indicators(self) -> None:
        self.indicatorDefine(QsciScintilla.SquiggleIndicator, 1)
        self.indicatorDefine(QsciScintilla.FullBoxIndicator, 2)
        self.indicatorDefine(QsciScintilla.FullBoxIndicator, 3)
        self.indicatorDefine(QsciScintilla.TextColorIndicator, 4)
        self.setIndicatorForegroundColor(QColor("red"), 1)
        self.setIndicatorForegroundColor(QColor(52, 143, 235, 150), 2)
        self.setIndicatorForegroundColor(QColor(52, 143, 235, 25), 3)
        self.setIndicatorForegroundColor(QColor("#5387e0"), 4)
        self.setIndicatorHoverStyle(QsciScintilla.ThinCompositionIndicator, 4)
        self.setIndicatorHoverForegroundColor(QColor("#5387e0"), 4)

    def set_minimap(self, minimap_panel: object) -> None:
        self._minimap_panel = minimap_panel
        self.minimap = minimap_panel.minimap
        self.scrollbar = minimap_panel.scrollbar
        self.build_doc_map()

    def set_minimap_visiblity(self, visiblity: bool):
        if self.minimap:
            self._minimap_panel.setVisible(visiblity)

    def set_mode(self, mode: int):
        if mode == 0:
            self.editable = False
            self.setLexer(None)
            self.setReadOnly(True)
        else:
            self.editable = True
            self.setReadOnly(False)

    def update_editor_ui(self) -> None:
        self.scrollbar.update_position()
        self.minimap.scroll_map()

    def build_doc_map(self) -> None:
        self.minimap.setDocument(self.document())
        self.minimap.setLexer(self.lexer())
        self.SCN_UPDATEUI.connect(self.update_editor_ui)

    def build_margin(self) -> None:
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginType(1, QsciScintilla.SymbolMargin)

        self.setMarginWidth(1, "00")
        self.setMarginWidth(0, 8)

        self.setMarginLineNumbers(0, True)

        self.setMarginSensitivity(0, True)
        self.setMarginSensitivity(1, True)

        self.setFolding(QsciScintilla.PlainFoldStyle, 2)

        mark_folderopen = self.icons.get_image("expand-arrow").scaled(
            QSize(12, 12))
        mark_folder = self.icons.get_image("forward").scaled(QSize(12, 12))
        mark_folderopenmind = self.icons.get_image("expand-arrow").scaled(
            QSize(12, 12))
        mark_folderend = self.icons.get_image("forward").scaled(QSize(12, 12))

        sym_1 = self.icons.get_image("debug-breakpoint").scaled(QSize(12, 12))
        sym_2 = self.icons.get_image("debug-mark").scaled(QSize(12, 12))
        self.mark1 = self.markerDefine(sym_1, 1)
        self.mark2 = self.markerDefine(sym_2, 2)

        self.markerDefine(mark_folderopen, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(mark_folder, QsciScintilla.SC_MARKNUM_FOLDER)
        self.markerDefine(mark_folderopenmind,
                          QsciScintilla.SC_MARKNUM_FOLDEROPENMID)
        self.markerDefine(mark_folderend, QsciScintilla.SC_MARKNUM_FOLDEREND)

        self.update_lines()
        self.setMarginMarkerMask(1, 0b1111)

    def build_text(self) -> None:
        self.setUtf8(True)
        if SYS_NAME == "windows":
            self.setEolMode(QsciScintilla.EolWindows)
        elif SYS_NAME == "darwin":
            self.setEolMode(QsciScintilla.EolMac)
        else:
            self.setEolMode(QsciScintilla.EolUnix)

        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)
        self.setCaretLineVisible(True)
        self.setTabDrawMode(QsciScintilla.TabStrikeOut)

    def build_styles(self) -> None:
        self._font = getfn.get_native_font()
        self.setFont(self._font)
        self.setCaretWidth(2)

    def build_autocompletion(self) -> None:
        self.setAutoCompletionWordSeparators(["(", ".", "="])
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)
        self.setAutoCompletionCaseSensitivity(False)

        self.registerImage(1, self.icons.get_pixmap("function"))
        self.registerImage(2, self.icons.get_pixmap("keyword"))
        self.registerImage(3, self.icons.get_pixmap("class"))
        self.registerImage(4, self.icons.get_pixmap("module"))
        self.registerImage(5, self.icons.get_pixmap("instance"))
        self.registerImage(6, self.icons.get_pixmap("statement"))
        self.registerImage(7, self.icons.get_pixmap("param"))
        self.registerImage(8, self.icons.get_pixmap("path"))
        self.registerImage(9, self.icons.get_pixmap("property"))
        self.registerImage(10, self.icons.get_pixmap("*"))

        self.setCallTipsStyle(QsciScintilla.CallTipsNoContext)
        self.setCallTipsPosition(QsciScintilla.CallTipsAboveText)
        self.setCallTipsVisible(0)

    def build_shortcuts(self) -> None:
        self.master_completions = QShortcut("Ctrl+Space", self)
        self.undo_action = QShortcut("Ctrl+Z", self)

    def set_policys(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def set_text(self, text: str, clear_do_history: bool = False) -> None:
        self.SendScintilla(QsciScintilla.SCI_SETTEXT, bytes(text, "utf-8"))
        if clear_do_history:
            self.SendScintilla(QsciScintilla.SCI_EMPTYUNDOBUFFER)

    def set_eol_mode(self, eol_mode: Union[int, str]) -> None:

        if isinstance(eol_mode, str):
            if eol_mode == "windows":
                self.setEolMode(QsciScintilla.EolWindows)
            elif eol_mode == "windows":
                self.setEolMode(QsciScintilla.EolMac)
            elif eol_mode == "unix":
                self.setEolMode(QsciScintilla.EolUnix)

            self.convertEols(self.eolMode())

        elif isinstance(eol_mode, int):
            self.setEolMode(eol_mode)
            self.convertEols(self.eolMode())

    def set_eol_visible(self, visible: bool):
        self.setEolVisibility(visible)

    def define_lexer(self, lexer=None) -> None:
        if self.editable:
            if self.file_path != None:
                lexer = getfn.get_lexer_from_extension(self.file_path)

            else:
                self._lexer = None
                self.lexer_name = "none"

            if lexer != self._lexer:
                self.set_lexer(lexer)
                

    def clear_lexer(self) -> None:
        if self.lexer() != None:
            self.lexer().deleteLater()
            self.lexer().setParent(None)
            self.setLexer(None)
            self.clearFolds()
            self.clearAnnotations()
            self.SendScintilla(QsciScintilla.SCI_CLEARDOCUMENTSTYLE)
        self._lexer = None


    def jump_to_line(self, lineno: Union[int, None] = None) -> None:
        self.go_to_line(lineno)


    def set_lexer(self, lexer: object) -> None:
        if self.editable:
            if not isinstance(self.lexer(), lexer):
                self.clear_lexer()
                self._lexer = lexer(self)
                self.lexer_name = str(self._lexer.language())
                self.setLexer(self._lexer)

                self.lexer_api = QsciAPIs(self.lexer())

                if self.minimap:
                    self.minimap.set_lexer(self.lexer())

                self.on_style_changed.emit(self)
                self.on_lexer_changed.emit(self)


    def update_lines(self) -> None:
        factor = 1
        for i in range(0, 8):
            if (self.lines()/(10**factor)) < 1:
                break
            factor += 1

        self.setMarginWidth(0, "0"*(factor+1))

    def go_to_line(self, lineno) -> None:
        if self.lines() >= lineno:
            self.setCursorPosition(lineno, 0)

    def show_white_spaces(self) -> None:
        self.setWhitespaceVisibility(QsciScintilla.WsVisible)

    def hide_white_spaces(self) -> None:
        self.setWhitespaceVisibility(QsciScintilla.WsInvisible)

    def clear_indicator_range(
        self,
        line: int = 0,
        column: int = 0,
        until_line: int = -1,
        until_column: int = -1,
        indicator_id: int = 0,
        minimap: bool = True,
    ) -> None:
        if until_line == -1:
            until_line = self.lines() - 1

        if until_column == -1:
            until_column = len(self.text(self.lines() - 1))

        self.clearIndicatorRange(line, column, until_line, until_column,
                                 indicator_id)
        if minimap and self.minimap is not None:
            self.minimap.clearIndicatorRange(line, column, until_line,
                                             until_column, indicator_id)

    def add_indicator_range(
        self,
        line: int,
        column: int,
        until_line: int,
        until_column: int,
        indicator_id: int,
        fill_minimap: bool,
    ) -> None:
        self.fillIndicatorRange(line, column, until_line, until_column,
                                indicator_id)
        if fill_minimap and self.minimap is not None:
            self.minimap.fillIndicatorRange(line, column, until_line,
                                            until_column, indicator_id)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        super().keyPressEvent(event)
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

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        for line in self.contractedFolds():
            self.mark_fold(line, "...", 5)

        for line in self.folded_lines:
            if not line in self.contractedFolds():
                self.folded_lines.remove(line)
                self.clear_annotations_by_line("on_fold", line)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        last_row, last_col = self.getCursorPosition()
        super().mousePressEvent(event)

        if event.buttons() == Qt.LeftButton and event.modifiers(
        ) == Qt.AltModifier:
            self.all_cursors_pos.append((last_row, last_col))
            self.add_cursors(event.pos(), last_row, last_col)

        else:
            self.remove_cursors()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        QToolTip.hideText()

    def undid(self) -> None:
        can = self.SendScintilla(QsciScintilla.SCI_CANUNDO)
        print(can)
