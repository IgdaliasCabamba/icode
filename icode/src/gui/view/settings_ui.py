from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from functions import getfn
from gui.view.code_viewer import GenericEditor
from smartsci.lexers.lexerjson import JSONLexer
from data import DATA_FILE
from functions import filefn
import hjson


class ConfigUi(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("settings")
        self.icons = getfn.get_smartcode_icons("config")
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)
        hbox = QHBoxLayout()
        self.timer = QTimer()

        self.settings_editor = GenericEditor(self)
        self.settings_editor.setCaretForegroundColor(QColor("gold"))
        self.settings_editor.setCaretLineBackgroundColor(QColor(180, 180, 180, 70))
        
        self.settings_editor.set_lexer(JSONLexer(self.settings_editor))
        
        self.vbox.addWidget(self.settings_editor)
        self.load_settings()
        
        self.settings_editor.textChanged.connect(self.change_status)
        self.timer.timeout.connect(self.save_settings)
    
    def load_settings(self):
        self.settings_editor.set_text(filefn.read_file(DATA_FILE))

    def save_settings(self):
        text = self.settings_editor.text()
        try:
            hjson.loads(text)
        except Exception as e:
            return
        filefn.write_to_file(text, DATA_FILE)
        self.timer.stop()
    
    def change_status(self):
        if self.timer.isActive():
            self.timer.stop()
        
        self.timer.start(3000)