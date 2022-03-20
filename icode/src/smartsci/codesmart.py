from typing import Union
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import QToolTip, QShortcut, QFrame, QMenu
from PyQt5.Qsci import *
from PyQt5.QtGui import QColor
from pathlib import Path
from base.system import SYS_NAME
from .coeditor import *
from .editor_core import Connector, KeyBoard
from .idocument import IDocument
from .imagesci import ImageScintilla
from functions import filefn, getfn
from .lexers import *

class EditorTip(QFrame):
    def __init__(self, parent:object) -> None:
        super().__init__(parent)
        self.parent = parent
    
class EditorBase(ImageScintilla):
    abcd = {"a","b","c","d","e","f","g","h","i","j","k","m","n","l","o","p","q","r","s","t","u","v","w","x","y","z"}
    pre_complete_keys = {".","(","[","{",",",";"," ","_"}
    closable_key_map = {
        "(":")",
        "[":"]",
        "{":"}",
        '"':'"',
        "'":"'"
    }
    on_key_pressed = pyqtSignal(object)
    
    def __init__(self, parent:object) -> None:
        super().__init__(parent)
        self.idocument = IDocument(self)
        self.parent=parent
        self.icons = getfn.get_smartcode_icons("smartsci")
        self.keyboard = KeyBoard(self)
        self.editable = True
        self.info_image = False
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

    def listen_sci_events(self) -> None:
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
        self.SendScintilla(QsciScintilla.SCI_SETVIRTUALSPACEOPTIONS, QsciScintilla.SCVS_RECTANGULARSELECTION)
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE, QsciScintilla.SC_MULTIPASTE_EACH)
    
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
    
    def set_minimap(self, minimap:object) -> None:
        self._minimap_box = minimap
        self.minimap=minimap.minimap
        self.scrollbar=minimap.scrollbar
        self.build_doc_map()
    
    def set_minimap_visiblity(self, visiblity:bool):
        if self.minimap:
            self._minimap_box.setVisible(visiblity)
    
    def set_mode(self, mode:int):
        if mode == 0:
            self.editable = False
            self.setLexer(None)
            self.setReadOnly(True)
        else:
            self.editable = True
            self.setReadOnly(False)
            if self.info_image:
                self.delete_image(self.info_image)
        
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

        mark_folderopen = self.icons.get_image("expand-arrow").scaled(QSize(12, 12))
        mark_folder = self.icons.get_image("forward").scaled(QSize(12, 12))
        mark_folderopenmind = self.icons.get_image("expand-arrow").scaled(QSize(12, 12))
        mark_folderend = self.icons.get_image("forward").scaled(QSize(12, 12))
        
        sym_1 = self.icons.get_image("debug-mark").scaled(QSize(12, 12))
        self.mark1 = self.markerDefine(sym_1, 1)

        self.markerDefine(mark_folderopen, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(mark_folder, QsciScintilla.SC_MARKNUM_FOLDER)
        self.markerDefine(mark_folderopenmind, QsciScintilla.SC_MARKNUM_FOLDEROPENMID)
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
        self.setAutoCompletionWordSeparators(["(",".","="])
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
        self.registerImage(10,self.icons.get_pixmap("*"))

        self.setCallTipsStyle(QsciScintilla.CallTipsNoContext)
        self.setCallTipsPosition(QsciScintilla.CallTipsAboveText)
        self.setCallTipsVisible(0)
    
    def build_shortcuts(self) -> None:
        self.master_completions = QShortcut("Ctrl+Space",self)
        self.undo_action = QShortcut("Ctrl+Z", self)

    def set_policys(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    
    def set_text(self, text:str, clear_do_history:bool = False) -> None:
        self.SendScintilla(QsciScintilla.SCI_SETTEXT, bytes(text, "utf-8"))
        if clear_do_history:
            self.SendScintilla(QsciScintilla.SCI_EMPTYUNDOBUFFER)
    
    def set_eol_mode(self, eol_mode:Union[int,str]) -> None:
        
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
    
    def set_eol_visible(self, visible:bool):
        self.setEolVisibility(visible)

    def update_lines(self) -> None:
        line_num=self.lines()
        if line_num in range(0, 10):
            self.setMarginWidth(0, "00")
        elif line_num in range(10, 100):
            self.setMarginWidth(0, "000")
        elif line_num in range(100, 1000):
            self.setMarginWidth(0, "0000")
        elif line_num in range(1000, 10000):
            self.setMarginWidth(0, "00000")
        elif line_num in range(10000, 100000):
            self.setMarginWidth(0, "000000")
        else:
            self.setMarginWidth(0, "00000000")

    def go_to_line(self, lineno) -> None:
        if self.lines() >= lineno:
            self.setCursorPosition(lineno, 0)
        
    def show_white_spaces(self) -> None:
        self.setWhitespaceVisibility(QsciScintilla.WsVisible)

    def hide_white_spaces(self) -> None:
        self.setWhitespaceVisibility(QsciScintilla.WsInvisible)
    
    def clear_indicator_range(self, line:int=0, column:int=0, until_line:int=-1, until_column:int=-1, indicator_id:int = 0, minimap:bool=True) -> None:
        if until_line == -1:
            until_line = self.lines()-1
            
        if until_column == -1:
            until_column = len(self.text(self.lines()-1))
            
        self.clearIndicatorRange(line, column, until_line, until_column, indicator_id)
        if minimap and self.minimap is not None:
            self.minimap.clearIndicatorRange(line, column, until_line, until_column, indicator_id)
    
    def add_indicator_range(self, line:int, column:int, until_line:int, until_column:int, indicator_id:int, fill_minimap:bool) -> None:
        self.fillIndicatorRange(line, column, until_line, until_column, indicator_id)
        if fill_minimap and self.minimap is not None:
            self.minimap.fillIndicatorRange(line, column, until_line, until_column, indicator_id)
    
    def mouseDoubleClickEvent(self, event:QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        # TODO
    
    def keyPressEvent(self, event:QKeyEvent) -> None:
        super().keyPressEvent(event)
        self.on_key_pressed.emit(event)
    
    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.mouse_release_event(event)
    
    def mousePressEvent(self, event:QMouseEvent) -> None:
        last_row, last_col = self.getCursorPosition()
        super().mousePressEvent(event)
        
        if event.buttons() == Qt.LeftButton and event.modifiers() == Qt.AltModifier:
            self.all_cursors_pos.append((last_row, last_col))
            self.add_cursors(event.pos(), last_row, last_col)
        
        else:    
            self.remove_cursors()
            
        self.mouse_press_event(event)
    
    def mouseMoveEvent(self, event:QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        self.mouse_move_event(event)
    
    def focusInEvent(self, event:QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focus_in_event(event)
    
    def focusOutEvent(self, event:QFocusEvent) -> None:
        super().focusOutEvent(event)
        self.focus_out_event(event)
    
    def resizeEvent(self, event:QResizeEvent) -> None:
        super().resizeEvent(event)
        self.resize_event(event)

    def undid(self) -> None:
        can = self.SendScintilla(QsciScintilla.SCI_CANUNDO)
        print(can)

class Editor(EditorBase):
    
    on_mouse_stoped = pyqtSignal(int, int, int)
    on_mouse_moved = pyqtSignal(object)
    on_mouse_pressed = pyqtSignal(object)
    on_mouse_released = pyqtSignal(object)
    on_cursor_pos_chnaged = pyqtSignal(int, int)
    on_lines_changed = pyqtSignal(int)
    on_selected = pyqtSignal(int, int, int, int)
    on_highlight_sel_request = pyqtSignal(int, int, int, int, bool, str, int, str)
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
    
    def __init__(self, parent:object, file=Union[str,None]) -> None:
        super().__init__(parent)
        self.setObjectName("codesmart")
        self.parent=parent
        self.file_watcher = self.parent.file_watcher
        self.editor_view_parent = parent
        self.menu=self.parent.parent.menu_bar
        self.status_bar=self.parent.parent.status_bar
        self.file_path=file
        self._lexer=None
        self.lexer_name="none"
        self.lexer_api=None
        self.minimap=False
        self._ide_mode = False
        self.edited = False
        self.saved = None
        self.saved_text = None
        self.folded_lines = []
        self.all_cursors_pos = []
        self.code_completers = []
        self.development_environment_components = []
        self.annotations_data = {
            "on_fold":[],
            "on_text_changed":[],
            "on_lines_changed":[],
            "on_cursor_pos_changed":[],
            "on_selection_changed":[],
            "permanent":[]
        }
        self.fold_indicators = {
            "lines":[],
            "image_id":[],
        }
        self.book_marks = {
            "book-mark":[],
            "break-point":[],
            "log-point":[]
        }
        
        self.intellisense_thread=QThread(self)
        self.intellisense_thread.start()
        self.intellisense_thread.setPriority(QThread.LowestPriority)

        self.development_environment_thread = QThread(self)
        self.coeditor = CoEditor(self)
        self.connector = Connector(self)
        self.connector.update_all()
        self.connector.moveToThread(self.development_environment_thread)
        self.coeditor.moveToThread(self.development_environment_thread)
        self.development_environment_thread.started.connect(self.run_schedule)
        
        self.editor_timer = QTimer(self)

        self.start()
    
    def start(self) -> None :
        if self.file_path is not None:
            self.set_text_from_file()
            self.saved = True
            
        else:
            self.define_lexer()
            self.saved = False
        
        self.update_document()
        self.listen_sci_events()
        self.coeditor.on_update_header.connect(self.update_header)
        self.coeditor.on_change_lexer.connect(self.set_lexer)
        self.coeditor.on_highlight_selection.connect(self.add_indicator_range)
        self.coeditor.on_highlight_text.connect(self.add_indicator_range)
        self.coeditor.on_clear_indicator_range.connect(self.clear_indicator_range)
        self.on_key_pressed.connect(self.key_press_event)
        self.development_environment_thread.start()
        self.development_environment_thread.setPriority(QThread.LowestPriority)

    @property
    def ide_mode(self) -> bool:
        return self._ide_mode
    
    def set_ide_mode(self, ide_mode:bool) -> None:
        if ide_mode:
            self._ide_mode = True
            self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        else:
            self._ide_mode = False
            self.setAutoCompletionSource(QsciScintilla.AcsDocument)
    
    def add_code_completer(self, completer:object, run:callable)  -> None:
        self.code_completers.append(completer)
        completer.moveToThread(self.intellisense_thread)
        if self.intellisense_thread.isRunning():
            run()
    
    def add_development_environment_component(self, component:object, run:callable)  -> None:
        self.development_environment_components.append(component)
        component.moveToThread(self.development_environment_thread)
        if self.development_environment_thread.isRunning():
            run()

    def run_schedule(self) -> None:
        self.connector.run()
        self.coeditor.run()
    
    def define_lexer(self, lexer=None) -> None:
        if self.editable:
            if self.file_path != None:
                lexer = getfn.get_lexer_from_extension(self.file_path)

            else:
                self._lexer=None
                self.lexer_name="none"

            if lexer != self._lexer:
                self.set_lexer(lexer)
            
            self.update_status_bar()
            self.update_document()

    def clear_lexer(self) -> None:
        if self.lexer() != None:
            self.lexer().deleteLater()
            self.lexer().setParent(None)
            self.setLexer(None)
            self.clearFolds()
            self.clearAnnotations()
            self.SendScintilla(QsciScintilla.SCI_CLEARDOCUMENTSTYLE)
        self._lexer = None

    def jump_to_line(self, lineno:Union[int, None]=None) -> None:
        self.go_to_line(lineno)

    def set_lexer(self, lexer:object) -> None:
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
                self.update_status_bar()
                self.update_document()

    def set_text_from_file(self, file_path:Union[str, None]=None) -> None:
        try:
            if file_path is None:
                code = filefn.read_file(self.file_path)
            else:
                code = filefn.read_file(file_path)
            self.setText(code)
            self.update_lines()
            self.define_lexer()
        except FileNotFoundError as e:
            self.info_image = self.add_image(self.icons.get_path("no-data"), (20, 5),  (500, 500))
            self.set_mode(0)
            message = "File does not exist try to recreate pressing Ctrl+S"
            self.insertAt(message, 0, 0)
    
    def save_file(self, file_path:str):
        self.file_path = file_path
        self.saved = True
        self.on_saved.emit(str(self.file_path))
        self.saved_text = self.text()
        self.update_status_bar()
        self.update_document()
        
    def _margin_left_clicked(self, margin_nr:int, line_nr:int, state:object) -> None:
        if self.markersAtLine(line_nr) == 0:
            self.markerAdd(line_nr, self.mark1)
        else:
            self.markerDelete(line_nr)

    def _margin_right_clicked(self, margin_nr:int, line_nr:int, state:object) -> None:
        pass
    
    def mouse_stoped(self, pos:int, x:int, y:int) -> None:
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

    def cursor_event(self, index:int, line:int) -> None:
        self.update_status_bar_cursor_pos()
        self.clear_annotations_by_type("on_cursor_pos_changed")
        self.on_cursor_pos_chnaged.emit(index, line)
        self.on_highlight_match_request.emit(index, line, self.hasSelectedText(), self.wordAtLineIndex(index, line), self.lines(), self.text())
        
    def add_cursors(self, point:object, last_row:int, last_col:int) -> None:
            
        pos = self.SendScintilla(QsciScintillaBase.SCI_POSITIONFROMPOINTCLOSE,
            point.x(),
            point.y()
        )
        
        if len(self.all_cursors_pos) > 1:
            for cur_pos in self.all_cursors_pos:
                offset = self.positionFromLineIndex(cur_pos[0], cur_pos[1])    
                self.SendScintilla(QsciScintilla.SCI_ADDSELECTION, offset, offset)
                
        else:
            offset = self.positionFromLineIndex(last_row, last_col)
            
            self.SendScintilla(QsciScintilla.SCI_SETSELECTION, offset, offset)
            
            self.SendScintilla(QsciScintilla.SCI_ADDSELECTION, pos, pos)

    def remove_cursors(self) -> None:
        self.all_cursors_pos.clear()
    
    def clear_annotations_by_type(self, type:str) -> None:
        if type in self.annotations_data.keys():
            for i in self.annotations_data[type]:
                self.annotations_data[type].remove(i)
                self.clearAnnotations(i)
    
    def clear_annotations_by_id(self, type:str, id:object) -> None:
        if type in self.annotations_data.keys():
            for i in self.annotations_data[type]:
                if id == i:
                    self.annotations_data[type].remove(i)
                    self.clearAnnotations(i)
    
    def selection_event(self) -> None:
        row_from, col_from, row_to, col_to = self.getSelection()
        self.clear_annotations_by_type("on_selection_changed")
        self.on_selected.emit(row_from, col_from, row_to, col_to)
        self.on_highlight_sel_request.emit(row_from, col_from, row_to, col_to, self.hasSelectedText(), self.selectedText(), self.lines(), self.text())
        self.clear_indicator_range(0, 0, -1, -1, 2, False)
        if row_from+col_from+row_to+col_to > 0:
            self.show_white_spaces()
        else:
            self.hide_white_spaces()
        
    def display_tooltip(self, data:dict) -> None:
        QToolTip.showText(self.mapToGlobal(data["pos"]), data["text"], self.viewport())
    
    def display_annotation(self, row:int, note:Union[str, list], type:int, event_to_remove:str, priority:int=0):
        if priority > 0 and len(self.annotation(row)) > 0:
            return
        
        if isinstance(note, list) or isinstance(note, QsciStyledText):
            self.annotate(row, note)
        else:
            self.annotate(row, note, type)
            
        if not event_to_remove in self.annotations_data.keys():
            self.annotations_data[event_to_remove] = []
        
        if not row in self.annotations_data[event_to_remove]:
            self.annotations_data[event_to_remove].append(row)
    
    def update_header(self, data:dict) -> None:
        self.editor_view_parent.set_info(data)
    
    def update_title(self) -> None:
        if self.file_path is None:
            title=self.text(0).replace('\n','')
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
            "lexer_name":self.lexer_name,
            "name":name,
            "lexer":self._lexer,
            "tooltip":tooltip,
            "icon":icon,
            "file":self.file_path,
            "file_name":name
        })    
    
    def copy_this_editor(self, editor:object) -> None:
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
    
    def mouse_release_event(self, event:QMouseEvent) -> None:
        self.on_mouse_released.emit(event)
        for line in self.contractedFolds():
            self.mark_fold(line, "...", 5)
        
        for line in self.folded_lines:
            if not line in self.contractedFolds():
                self.folded_lines.remove(line)
                self.clear_annotations_by_id("on_fold", line)
        
    def mouse_press_event(self, event:QMouseEvent) -> None:
        self.on_mouse_pressed.emit(event)
        #word = self.wordAtPoint(event.pos()).lower()
        
        #cmenu = QMenu(self)
        #newAct = cmenu.addAction("Foo")
        #openAct = cmenu.addAction("Bar")
        #action = cmenu.exec_(self.mapToGlobal(event.pos()))
    
    def key_press_event(self, event:QKeyEvent) -> None:
        key=event.key()
        string = str(event.text())
        
        if key in range(65, 90):
            self.on_abcd_added.emit()
        
        if string in self.pre_complete_keys or key in range(65, 90):
            self.on_intellisense.emit(self, string) # it make icode more fast and responsive
                
        if key in {32, 16777220}:
            self.on_word_added.emit()
        
        if key in {32, 16777217, 16777219, 16777220}:
            self.on_modify_key.emit()
        
        if string in self.closable_key_map.keys():
            self.on_close_char.emit(string)
            
    def mouse_move_event(self, event:QMouseEvent) -> None:
        self.on_mouse_moved.emit(event)
    
    def focus_in_event(self, event:QFocusEvent) -> None:
        self.on_focused.emit(event, self)
    
    def focus_out_event(self, event:QFocusEvent) -> None:
        QToolTip.hideText()
    
    def resize_event(self, event:QResizeEvent) -> None:
        self.on_resized.emit(event)
