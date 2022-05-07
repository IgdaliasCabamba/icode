from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import pyqtSignal

class MainWindow(QMainWindow):
    
    on_resized = pyqtSignal()
    on_focused_buffer = pyqtSignal(object)
    on_editor_changed = pyqtSignal(object)
    on_new_notebook = pyqtSignal(object)
    on_tab_buffer_focused = pyqtSignal(object)
    on_close = pyqtSignal(object)

    def __init__(self, icode, qapp):
        super().__init__()
        self.setObjectName("main-window")
        self._icode = icode
        self._qapp = qapp