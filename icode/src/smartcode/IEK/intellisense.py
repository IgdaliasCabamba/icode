from PyQt5.QtCore import QThread, QObject, pyqtSignal
import sip


class Worker(QObject):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.parent.on_add.connect(self.add_completions)
        self.parent.on_remove.connect(self.remove_completions)

    def add_completions(self, lexer_api, completions) -> None:
        for completion in completions:
            lexer_api.add(completion)
        lexer_api.prepare()

    def remove_completions(self, lexer_api, completions) -> None:
        for completion in completions:
            lexer_api.remove(completion)
        lexer_api.prepare()


class IIntellisense(QObject):

    on_add = pyqtSignal(object, object)
    on_remove = pyqtSignal(object, object)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.worker_thread = QThread(self)
        self.worker = Worker(self)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.worker_thread.started.connect(self.worker.run)

    def add(self, lexer_api, completions):
        if not sip.isdeleted(lexer_api):
            self.on_add.emit(lexer_api, completions)

    def remove(self, lexer_api, completions):
        if not sip.isdeleted(lexer_api):
            self.on_remove.emit(lexer_api, completions)
