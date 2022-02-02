from PyQt5.QtWidgets import (
    QFrame, QListWidget, QVBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QTreeView,
    QListWidget, QHBoxLayout
    )
    
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from smartpy_api import python_api
from ui.igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem
from frameworks.qroundprogressbar import QRoundProgressBar

class DeepAnalyze(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("deep_analyze")
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.readme = QLabel(self)
        self.readme.setText("""
            <small>
                Get advanced diagnosis for your code,
                get data such as:
                <ul>
                    <li>Cyclomatic Complexity</li>
                    <li>Maintainability Index</li>
                </ul>
                <p>
                    click 
                    <strong>
                        <a href="www.github.io">here</a>
                    </strong>
                    to learn more
                    <strong>
                    or
                    </strong>
                </p>
            </small>
        """)
        self.readme.setWordWrap(True)
        
        self.btn_get_diagnosis = QPushButton("Get Diagnosis", self)
        
        self.status = QRoundProgressBar(self)
        self.status.setMinimumSize(100,100)
        self.status.setBarStyle(QRoundProgressBar.BarStyle.LINE)
        self.status.setRange(0,100)
        self.status.setValue(30)
        
        
        
        self.layout.addWidget(self.readme)
        self.layout.addWidget(self.status)
        self.layout.addWidget(self.btn_get_diagnosis)
        self.layout.setAlignment(self.readme, Qt.AlignTop)
        self.layout.setAlignment(self.btn_get_diagnosis, Qt.AlignTop)