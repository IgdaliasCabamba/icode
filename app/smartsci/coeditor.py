import pathlib
from PyQt5.Qsci import *
from PyQt5.QtCore import QObject, pyqtSignal
from functions import getfn, filefn
from . import iconsts

class CoEditor(QObject):
    
    on_update_header = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__()
        self.editor=parent
        self.indicator_ranges = []
    
    def run(self):
        self.make_headers()
        self.editor.idocument.on_changed.connect(self.make_headers)
        self.editor.on_text_changed.connect(self.text_changed)
        self.editor.on_saved.connect(self.editor_saved)
        self.editor.file_watcher.on_file_deleted.connect(self.file_deleted)
        self.editor.file_watcher.on_file_modified.connect(self.file_modified)
    
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