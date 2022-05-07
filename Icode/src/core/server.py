from PyQt6.QtCore import QObject, pyqtSignal
from .extender import Plugger

class Core(object):
    def __init__(self, app) -> None:
        self._app = app
        self.events = []
    
    def listen(self) -> None:
        """Start listen to all actions"""
        return self

    def _bind(self, event:object, action:object) -> None:
        """"Connect Qt signals to a given action"""
        event.connect(action)
        return self

class Server(QObject):

    on_stylesheet_changed = pyqtSignal(object)
    on_new_notebook = pyqtSignal(object)
    on_new_tab = pyqtSignal(object)
    on_new_editor = pyqtSignal(object)
    on_window_title_changed = pyqtSignal(str)
    on_commit_app = pyqtSignal(int)
    on_ide_mode_changed = pyqtSignal(int)
    on_current_editor_changed = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.__core = (
            Core(self)
            .listen()
            )
        self.plugger = Plugger(self)
        self.style = {
            "sheet":None,
            "qt":None
        }

    @property
    def avaliable_styles():
        return []