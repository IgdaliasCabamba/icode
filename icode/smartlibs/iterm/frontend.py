# from my other project at: https://github.com/IgdaliasCabamba/pyuxterm-qt-client/blob/main/app/src/terminal_frontend.py

import os

import requests
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.QtWebChannel import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import *

from .backend import PyuxtermProcessThread


class TerminalWidget(QWebEngineView):
    
    def __init__(self, parent, command, theme="default", font_name="Monospace", font_size=16, max_tries: int = 3):
        super().__init__(parent)
        self.command = command
        self.port = None
        self.theme = theme
        self.font_name = font_name
        self.max_tries = max_tries
        self.__url = None
        self.__loaded = False
        self.__load_tries = 0
        self.qurl = None
        self.setObjectName("terminal")
        self.show()

    def spawn(self, port):
        
        self.port = port

        command = [os.path.join(os.environ["QTX_TERM_ROOT_PATH"], "bin", "pyuxterm"), f"--command={self.command}", f"--port={self.port}", "--theme=elemental"]

        self.backend = PyuxtermProcessThread(command)
        self.backend.on_ready.connect(self.loaded)
        self.backend.start()

        self.__url = f"http://127.0.0.1:{port}"
        self.qurl = QUrl(self.__url)
        self.setUrl(self.qurl)
        self.show()

    def loaded(self):
        if self.__load_tries <= self.max_tries:
            if self.backend.is_serving(self.__url):
                self.__loaded = True
                self.setUrl(self.qurl)
                return self
            else:
                QTimer().singleShot(4000*self.__load_tries, self.loaded)

            self.__load_tries += 1


    def send_post(self, data: QJsonDocument, request: QNetworkRequest) -> None:
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(lambda response: print(
            str(response.readAll(), 'utf-8')))

        self.nam.post(request, data)

    def send_input(self, text: str) -> None:
        if self.__loaded:
            json = {
                "eval": {
                    ">>>": "PtyInterface.input_(text=" + "'" + text + "'" + ")",
                    "async": False
                }
            }
            payload = QJsonDocument(json)

            url = f"{self.__url}/"
            request = QNetworkRequest(QUrl(url))
            request.setHeader(
                QNetworkRequest.ContentTypeHeader, "application/json")

            self.send_post(payload.toJson(), request)

        else:
            QTimer().singleShot(3600, lambda: self.send_input(text))