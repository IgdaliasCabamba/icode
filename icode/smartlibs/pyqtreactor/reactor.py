import requests
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class ReqBackEnd(QObject):

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


class RRequest(QObject):

    on_get_raw = pyqtSignal(str, object)

    def __init__(self, parent):
        super().__init__(parent)
        self._stack = []
        self.parent = parent
        self.http_thread = QThread(self)
        self.backend = ReqBackEnd(self)
        self.backend.on_result.connect(self.return_response)
        self.backend.on_error.connect(self.return_log)
        self.backend.moveToThread(self.http_thread)
        self.http_thread.started.connect(self._run_schedule)
        self.http_thread.start()

    def _run_schedule(self):
        self.backend.run()
        for item in self._stack:
            self.on_get_raw.emit(item[0], item[1])

    def get_raw(self, url, callback):
        if self.backend.status:
            self.on_get_raw.emit(url, callback)
        else:
            self._stack.append((url, callback))
        return self

    def return_response(self, response, callback):
        callback(response)
        return self

    def return_log(self, error, callback):
        callback(error)
        return self


class Reactor(QObject):

    on_done = pyqtSignal(object)
    on_error = pyqtSignal(object)

    def __init__(self, action, *param, **params):
        super().__init__()
        self._action = action
        self.react(*param, **params)

    def then(self, callback):
        if hasattr(self, "result"):
            callback(self.result)
        return self

    def catch(self, catcher):
        if hasattr(self, "error"):
            catcher(self.error)
        return self

    def react(self, *args, **kwargs):
        try:
            self.result = self._action(*args, **kwargs)
            self.on_done.emit(self.result)

        except Exception as e:
            self.error = e
            self.on_error.emit(self.error)
