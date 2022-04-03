import requests
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class BackEnd(QObject):

    on_result = pyqtSignal(str, object)
    on_error = pyqtSignal(str, object)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.status = False

    def run(self):
        self.status = True
        self.parent.on_get_raw.connect(self.get_raw)

    def get_raw(self, url, callback):
        try:
            resp = requests.get(url)
            if resp.ok:
                self.on_result.emit(resp.text, callback)
            else:
                self.on_error.emit(resp.text, callback)

        except Exception as e:
            print(e)


class Request(QObject):

    on_get_raw = pyqtSignal(str, object)

    def __init__(self, parent):
        super().__init__(parent)
        self._stack = []
        self.parent = parent
        self.http_thread = QThread(self)
        self.backend = BackEnd(self)
        self.backend.on_result.connect(self.return_response)
        self.backend.on_error.connect(self.return_log)
        self.backend.moveToThread(self.http_thread)
        self.http_thread.started.connect(self.run_schedule)
        self.http_thread.start()

    def run_schedule(self):
        self.backend.run()
        for item in self._stack:
            self.on_get_raw.emit(item[0], item[1])

    def get_raw(self, url, callback):
        if self.backend.status:
            self.on_get_raw.emit(url, callback)
        else:
            self._stack.append((url, callback))

    def return_response(self, response, callback):
        callback(response)

    def return_log(self, error, callback):
        print(error)
        callback(error)
