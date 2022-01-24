from PyQt5.QtCore import QObject, pyqtSignal, QFileSystemWatcher, QFile, Qt
from functions import filefn
from PyQt5.Qsci import QsciScintilla, QsciScintillaBase
import pathlib
from . import iconsts

class KeyBoard:
    def __init__(self, editor):
        self.editor = editor
        def init_bindings(self):
            self.bindings = {
                "Down" : QsciScintillaBase.SCI_LINEDOWN,
                "Down+Shift" : QsciScintillaBase.SCI_LINEDOWNEXTEND,
                "Down+Ctrl" : QsciScintillaBase.SCI_LINESCROLLDOWN,
                "Down+Alt+Shift" : QsciScintillaBase.SCI_LINEDOWNRECTEXTEND,
                "Up" : QsciScintillaBase.SCI_LINEUP,
                "Up+Shift" : QsciScintillaBase.SCI_LINEUPEXTEND,
                "Up+Ctrl" : QsciScintillaBase.SCI_LINESCROLLUP,
                "Up+Alt+Shift" : QsciScintillaBase.SCI_LINEUPRECTEXTEND,
                "[+Ctrl" : QsciScintillaBase.SCI_PARAUP,
                "[+Ctrl+Shift" : QsciScintillaBase.SCI_PARAUPEXTEND,
                "]+Ctrl" : QsciScintillaBase.SCI_PARADOWN,
                "]+Ctrl+Shift" : QsciScintillaBase.SCI_PARADOWNEXTEND,
                "Left" : QsciScintillaBase.SCI_CHARLEFT,
                "Left+Shift" : QsciScintillaBase.SCI_CHARLEFTEXTEND,
                "Left+Ctrl" : QsciScintillaBase.SCI_WORDLEFT,
                "Left+Shift+Ctrl" : QsciScintillaBase.SCI_WORDLEFTEXTEND,
                "Left+Alt+Shift" : QsciScintillaBase.SCI_CHARLEFTRECTEXTEND,
                "Right" : QsciScintillaBase.SCI_CHARRIGHT,
                "Right+Shift" : QsciScintillaBase.SCI_CHARRIGHTEXTEND,
                "Right+Ctrl" : QsciScintillaBase.SCI_WORDRIGHT,
                "Right+Shift+Ctrl" : QsciScintillaBase.SCI_WORDRIGHTEXTEND,
                "Right+Alt+Shift" : QsciScintillaBase.SCI_CHARRIGHTRECTEXTEND,
                "/+Ctrl" : QsciScintillaBase.SCI_WORDPARTLEFT,
                "/+Ctrl+Shift" : QsciScintillaBase.SCI_WORDPARTLEFTEXTEND,
                "\\+Ctrl" : QsciScintillaBase.SCI_WORDPARTRIGHT,
                "\\+Ctrl+Shift" : QsciScintillaBase.SCI_WORDPARTRIGHTEXTEND,
                "Home" : QsciScintillaBase.SCI_VCHOME,
                "Home+Shift" : QsciScintillaBase.SCI_VCHOMEEXTEND,
                #settings.Editor.Keys.go_to_start : QsciScintillaBase.SCI_DOCUMENTSTART,
                #settings.Editor.Keys.select_to_start : QsciScintillaBase.SCI_DOCUMENTSTARTEXTEND,
                "Home+Alt" : QsciScintillaBase.SCI_HOMEDISPLAY,
                "Home+Alt+Shift" : QsciScintillaBase.SCI_VCHOMERECTEXTEND,
                "End" : QsciScintillaBase.SCI_LINEEND,
                "End+Shift" : QsciScintillaBase.SCI_LINEENDEXTEND,
                #settings.Editor.Keys.go_to_end : QsciScintillaBase.SCI_DOCUMENTEND,
                #settings.Editor.Keys.select_to_end : QsciScintillaBase.SCI_DOCUMENTENDEXTEND,
                "End+Alt" : QsciScintillaBase.SCI_LINEENDDISPLAY,
                "End+Alt+Shift" : QsciScintillaBase.SCI_LINEENDRECTEXTEND,
                #settings.Editor.Keys.scroll_up : QsciScintillaBase.SCI_PAGEUP,
                #settings.Editor.Keys.select_page_up : QsciScintillaBase.SCI_PAGEUPEXTEND,
                "PageUp+Alt+Shift" : QsciScintillaBase.SCI_PAGEUPRECTEXTEND,
                #settings.Editor.Keys.scroll_down : QsciScintillaBase.SCI_PAGEDOWN,
                #settings.Editor.Keys.select_page_down : QsciScintillaBase.SCI_PAGEDOWNEXTEND,
                "PageDown+Alt+Shift" : QsciScintillaBase.SCI_PAGEDOWNRECTEXTEND,
                "Delete" : QsciScintillaBase.SCI_CLEAR,
                "Delete+Shift" : QsciScintillaBase.SCI_CUT,
                #settings.Editor.Keys.delete_end_of_word: QsciScintillaBase.SCI_DELWORDRIGHT,
                #settings.Editor.Keys.delete_end_of_line : QsciScintillaBase.SCI_DELLINERIGHT,
                "Insert" : QsciScintillaBase.SCI_EDITTOGGLEOVERTYPE,
                "Insert+Shift" : QsciScintillaBase.SCI_PASTE,
                "Insert+Ctrl" : QsciScintillaBase.SCI_COPY,
                "Escape" : QsciScintillaBase.SCI_CANCEL,
                "Backspace" : QsciScintillaBase.SCI_DELETEBACK,
                "Backspace+Shift" : QsciScintillaBase.SCI_DELETEBACK,
                #settings.Editor.Keys.delete_start_of_word : QsciScintillaBase.SCI_DELWORDLEFT,
                "Backspace+Alt" : QsciScintillaBase.SCI_UNDO,
                #settings.Editor.Keys.delete_start_of_line : QsciScintillaBase.SCI_DELLINELEFT,
                #settings.Editor.Keys.undo : QsciScintillaBase.SCI_UNDO,
                #settings.Editor.Keys.redo : QsciScintillaBase.SCI_REDO,
                #settings.Editor.Keys.cut : QsciScintillaBase.SCI_CUT,
                #settings.Editor.Keys.copy : QsciScintillaBase.SCI_COPY,
                #settings.Editor.Keys.paste : QsciScintillaBase.SCI_PASTE,
                #settings.Editor.Keys.select_all : QsciScintillaBase.SCI_SELECTALL,
                #settings.Editor.Keys.indent : QsciScintillaBase.SCI_TAB,
                #settings.Editor.Keys.unindent : QsciScintillaBase.SCI_BACKTAB,
                "Return" : QsciScintillaBase.SCI_NEWLINE,
                "Return+Shift" : QsciScintillaBase.SCI_NEWLINE,
                "Add+Ctrl" : QsciScintillaBase.SCI_ZOOMIN,
                "Subtract+Ctrl" : QsciScintillaBase.SCI_ZOOMOUT,
                "Divide+Ctrl" : QsciScintillaBase.SCI_SETZOOM,
                #settings.Editor.Keys.line_cut : QsciScintillaBase.SCI_LINECUT,
                #settings.Editor.Keys.line_delete : QsciScintillaBase.SCI_LINEDELETE,
                #settings.Editor.Keys.line_copy : QsciScintillaBase.SCI_LINECOPY,
                #settings.Editor.Keys.line_transpose : QsciScintillaBase.SCI_LINETRANSPOSE,
                #settings.Editor.Keys.line_selection_duplicate : QsciScintillaBase.SCI_SELECTIONDUPLICATE,
                "U+Ctrl" : QsciScintillaBase.SCI_LOWERCASE,
                "U+Ctrl+Shift" : QsciScintillaBase.SCI_UPPERCASE,
            }
        self.scintilla_keys = {
                "down" : QsciScintillaBase.SCK_DOWN,
                "up" : QsciScintillaBase.SCK_UP,
                "left" : QsciScintillaBase.SCK_LEFT,
                "right" : QsciScintillaBase.SCK_RIGHT,
                "home" : QsciScintillaBase.SCK_HOME,
                "end" : QsciScintillaBase.SCK_END,
                "pageup" : QsciScintillaBase.SCK_PRIOR,
                "pagedown" : QsciScintillaBase.SCK_NEXT,
                "delete" : QsciScintillaBase.SCK_DELETE,
                "insert" : QsciScintillaBase.SCK_INSERT,
                "escape" : QsciScintillaBase.SCK_ESCAPE,
                "backspace" : QsciScintillaBase.SCK_BACK,
                "tab" : QsciScintillaBase.SCK_TAB,
                "return" : QsciScintillaBase.SCK_RETURN,
                "add" : QsciScintillaBase.SCK_ADD,
                "subtract" : QsciScintillaBase.SCK_SUBTRACT,
                "divide" : QsciScintillaBase.SCK_DIVIDE,
                "win" : QsciScintillaBase.SCK_WIN,
                "rwin" : QsciScintillaBase.SCK_RWIN,
                "menu" : QsciScintillaBase.SCK_MENU,
            }
        self.valid_modifiers = [
                QsciScintillaBase.SCMOD_NORM, 
                QsciScintillaBase.SCMOD_SHIFT, 
                QsciScintillaBase.SCMOD_CTRL, 
                QsciScintillaBase.SCMOD_ALT, 
                QsciScintillaBase.SCMOD_SUPER, 
                QsciScintillaBase.SCMOD_META
            ]
        commands = self.editor.standardCommands()
        command = commands.boundTo(Qt.ControlModifier | Qt.ShiftModifier| Qt.Key_T)
        if command is not None:
            command.setKey(Qt.ControlModifier | Qt.ShiftModifier| Qt.Key_B)
            
        #self.ctrl_z_shortcut = QShortcut(Qt.ControlModifier | Qt.Key_Z, self.editor)
        #self.ctrl_y_shortcut = QShortcut(Qt.ControlModifier | Qt.Key_Y, self.editor)


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