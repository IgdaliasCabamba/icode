import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QIODevice, QByteArray, QProcess

import requests

class PyuxtermProcessThread(QThread):
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
    

    def __init__(self, command):
        super().__init__()
        self.command = command
        
    def run(self):
        
        process = QProcess()
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.start(self.command[0], self.command[1:])
        self.on_ready.emit()

        while process.waitForReadyRead():
            output = process.readAllStandardOutput().data().decode('utf-8')
            if output:
                self.output_ready.emit(output.strip())

        process.waitForFinished()
        self.finished.emit()
