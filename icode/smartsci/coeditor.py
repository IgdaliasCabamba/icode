import pathlib
from PyQt5.Qsci import *
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from functions import getfn, filefn
from . import iconsts
from .lexers import *
import re
import time

class CoEditor(QObject):
    
    on_update_header = pyqtSignal(dict)
    on_change_lexer = pyqtSignal(object)
    on_highlight_text = pyqtSignal(int, int, int, int, int, bool)
    on_highlight_selection = pyqtSignal(int, int, int, int, int, bool)

    def __init__(self, parent):
        super().__init__()
        self.editor=parent
        self.timer = QTimer(self)
        self.last_highlight_word = None
    
    def run(self):
        self.make_headers()
        self.editor.idocument.on_changed.connect(self.make_headers)
        self.editor.on_text_changed.connect(self.text_changed)
        self.editor.on_saved.connect(self.editor_saved)
        self.editor.on_selected.connect(self.highlight_selection)
        self.editor.on_cursor_pos_chnaged.connect(self.highlight_match)
        self.editor.file_watcher.on_file_deleted.connect(self.file_deleted)
        self.editor.file_watcher.on_file_modified.connect(self.file_modified)
        self.editor.on_word_added.connect(lambda: self.timer.singleShot(500, self.set_lexer_from_code))
    
    def make_headers(self):
        if self.editor.file_path is None:
            self.on_update_header.emit({"text":" Unsaved >", "widget":self.editor.parent.up_info0})
        else:
            widgets = [
                self.editor.parent.up_info0,
                self.editor.parent.up_info1,
                self.editor.parent.up_info2,
                self.editor.parent.up_info3,
                self.editor.parent.up_info4,
                self.editor.parent.up_info5,
                self.editor.parent.up_info6,
                self.editor.parent.up_info7
                ]
            path_levels = getfn.get_path_splited(self.editor.idocument.file)
            while len(path_levels) > len(widgets):
                path_levels.pop(0)
                
            i = 0
            for path in path_levels:
                if path.replace(" ", "") == "":
                    continue
                if i < len(widgets):
                    self.on_update_header.emit({"text":" "+str(path)+" >", "widget":widgets[i]})
                else:
                    break
                    self.on_update_header.emit({"text":" "+str(self.editor.idocument.file_name)+" >", "widget":widgets[i]})
                i+=1
            #self.on_update_header.emit({"text":" "+str(self.editor.idocument.file_name)+" >", "widget":self.editor.parent.up_info7})
        self.on_update_header.emit({"widget":self.editor.parent.up_info0, "icon":self.editor.idocument.icon})
    
    def file_deleted(self, file):
        self.on_update_header.emit({"text":"D", "widget":self.editor.parent.file_info, "type":"red"})
    
    def file_modified(self, file):
        if filefn.read_file(file) != self.editor.text():
            self.on_update_header.emit({"text":"M", "widget":self.editor.parent.file_info, "type":"red"})
    
    def text_changed(self):
        if self.editor.file_path is not None:
            self.on_update_header.emit({"text":"M", "widget":self.editor.parent.file_info, "type":"orange"})
        else:
            self.on_update_header.emit({"text":"U", "widget":self.editor.parent.file_info, "type":"orange"})
    
    def editor_saved(self):
        self.on_update_header.emit({"text":"S", "widget":self.editor.parent.file_info, "type":"green"})
        
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
    
    def highlight_selection(self, row_from:int, col_from:int, row_to:int, col_to:int):
        if self.editor.hasSelectedText():
            ocurs = {}
            sel_text = self.editor.selectedText()
            try:
                for line in range(self.editor.lines()):
                    val = re.escape(sel_text)
                    for match in re.finditer(val, self.editor.text(line)):
                        if not line in ocurs.keys():
                            ocurs[line]=[]
                        ocurs[line].append(match.span())
                
                for line, match in ocurs.items():
                    for span in match:
                        from_col, to_col = span
                        if row_from != line or col_from != from_col:
                            self.on_highlight_selection.emit(line, from_col, line, to_col, 2, True)
                            
            except Exception as e:
                print("highlight_selection Exception: ", e)
    
    def highlight_match(self, index, line):
        if not self.editor.hasSelectedText():
            word = self.editor.wordAtLineIndex(index, line)
            if self.last_highlight_word != word:
                self.editor.clear_indicator_range(0, 0, -1, -1, 3, False)
                ocurs = {}
                self.last_highlight_word = word
                try:
                    for line in range(self.editor.lines()):
                        val = re.escape(word)
                        for match in re.finditer(val, self.editor.text(line)):
                            if not line in ocurs.keys():
                                ocurs[line]=[]
                            ocurs[line].append(match.span())
                    
                    for line, match in ocurs.items():
                        for span in match:
                            from_col, to_col = span
                            self.on_highlight_text.emit(line, from_col, line, to_col, 3, False)
                                
                except Exception as e:
                    print("highlight_match Exception: ", e)