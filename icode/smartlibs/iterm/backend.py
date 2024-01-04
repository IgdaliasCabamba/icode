import time
from PyQt5.QtCore import pyqtSignal, QProcess

import requests

class PyuxtermProcess(QProcess):
    finished = pyqtSignal()
    on_ready = pyqtSignal()
    output_ready = pyqtSignal(str)

    @staticmethod
    def is_serving(url: str):
        try:
            head = requests.head(url)
            if head.status_code == 200:
                return True
            else:
                return False

        except requests.exceptions.RequestException as e:
            return None
    

    def __init__(self, command, url):
        super().__init__()
        self.command = command
        self.url = url
        self.setProcessChannelMode(QProcess.MergedChannels)
        
    def serve(self):
        self.start(self.command[0], self.command[1:])
        
        tries = 1
        while not self.is_serving(self.url):
            time.sleep(5*tries)
            tries += 1

        self.on_ready.emit()

        while self.waitForReadyRead():
            output = self.readAllStandardOutput().data().decode('utf-8')
            if output:
                self.output_ready.emit(output.strip())

        self.waitForFinished()
        self.finished.emit()
