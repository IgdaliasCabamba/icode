from PyQt5.QtWidgets import QFrame
from functions import getfn
import config

class ConfigUi(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.icons = getfn.get_application_icons("config")
        self.parent = parent
