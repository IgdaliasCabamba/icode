from PyQt5.QtCore import QObject


class GitController(QObject):
    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view
