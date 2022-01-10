from PyQt5.QtCore import QObject, pyqtSignal, QFileSystemWatcher, QFile
from functions import filefn
from PyQt5.Qsci import QsciScintilla
import pathlib
from . import iconsts

class Connector(QObject):
    
    auto_save_file=pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.editor=parent
    
    def run(self):
        self.editor.on_text_changed.connect(self.update)
    
    def update(self):
        self.check_all()
        self.update_all()

    def check_all(self):
        if self.editor.menu.file.auto_save.isChecked():
            if self.editor.file_path is None:
                self.auto_save_file.emit()
            else:
                filefn.write_to_file(self.editor.text(), self.editor.file_path)
        
    def update_all(self):
        code_page=self.editor.SendScintilla(QsciScintilla.SCI_GETCODEPAGE)
        eol_mode=self.editor.eolMode()
        
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

        self.editor.status_bar.indentation.setText(f"Spaces: {self.editor.tabWidth()}")
        self.editor.status_bar.encode.setText(f"{code_name}")
        self.editor.status_bar.end_line_seq.setText(f"{eol_name}")

class IFile(QObject):
    
    on_file_deleted = pyqtSignal(str)
    on_file_modified = pyqtSignal(str)
    
    def __init__(self, parent:object):
        super().__init__(parent)
        self.editor = parent
        self.file_manager = QFileSystemWatcher(self)
        self.file_manager.fileChanged.connect(self.file_changed)
    
    def start_monitoring(self, file_path:str):
        self.file_manager.addPath(file_path)
    
    def file_changed(self, file):
        file_path = file
        if pathlib.Path(file).exists():
            self.on_file_modified.emit(file)
        else:
            self.on_file_deleted.emit(file)