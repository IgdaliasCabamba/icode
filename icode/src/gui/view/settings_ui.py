from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from functions import getfn
from gui.view.code_viewer import GenericEditor
from smartsci.lexers.lexerjson import JSONLexer
from data import DATA_FILE
from functions import filefn


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

        self.settings_editor = GenericEditor(self)
        self.settings_editor.setCaretForegroundColor(QColor("gold"))
        self.settings_editor.setCaretLineBackgroundColor(QColor(180, 180, 180, 70))
        
        self.settings_editor.set_lexer(JSONLexer(self.settings_editor))
        
        self.btn_save_settings = QPushButton("Save settings")
        self.btn_save_settings.clicked.connect(self.save_settings)
        
        self.lbl_status = QLabel("<strong style='color:cyan'>Unmodified</strong>", self)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        
        self.vbox.addWidget(self.settings_editor)
        self.vbox.addLayout(hbox)
        hbox.addWidget(self.btn_save_settings)
        hbox.addWidget(self.lbl_status)
        self.load_settings()
        
        self.settings_editor.textChanged.connect(self.change_status)
    
    def load_settings(self):
        self.settings_editor.set_text(filefn.read_file(DATA_FILE))

    def save_settings(self):
        filefn.write_to_file(self.settings_editor.text(), DATA_FILE)
        self.lbl_status.setText("<strong style='color:green'>Saved</strong>")
    
    def change_status(self):
        self.lbl_status.setText("<strong style='color:crimen'>Modified</strong>")