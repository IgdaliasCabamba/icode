from PyQt5.QtWidgets import (
    QFrame, QListWidget, QVBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QHBoxLayout, QGridLayout
    )
    
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from smartpy_api import python_api
from ui.igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem
from frameworks.qroundprogressbar import QRoundProgressBar

class DataViewer(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("data_viewer")
        self.parent = parent
        self.icons = getfn.get_smartcode_icons("code")
        self.init_ui()
    
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        
        self.vbox_left = QVBoxLayout()
        self.inspect_objects = QListWidget(self)
        self.vbox_left.addWidget(self.inspect_objects)
        
        self.vbox_right = QVBoxLayout()
        
        self.complexity_bar = QRoundProgressBar(self)
        self.complexity_bar.setMinimumSize(150,150)
        self.complexity_bar.setBarStyle(QRoundProgressBar.BarStyle.DONUT)
        self.complexity_bar.setRange(0,80)
        self.complexity_bar.setValue(30)
        
        self.label_rank = QLabel(self)
        self.label_rank.setWordWrap(False)
        
        self.quality_label = QLabel(self)
        self.vbox_right.addWidget(self.complexity_bar)
        self.vbox_right.addWidget(self.label_rank)
        self.vbox_right.addWidget(self.quality_label)
        
        self.layout.addLayout(self.vbox_left)
        self.layout.addLayout(self.vbox_right)
        
    
    def run(self, code, editor):
        text = "Hellow World"
        
        results = python_api.get_code_analyze(code)
        
        if results is not None:
            for result in results:
                self.inspect_objects.addItem(
                    IListWidgetItem(
                        self.icons.get_icon("class"),
                        result.name,
                        None,
                        {"editor":editor, "object":result}
                    )
                )
        
        self.label_rank.setText(text)
        

class DeepAnalyze(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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
        self.data_viewer = DataViewer(self)
        self.data_viewer.setVisible(False)
        
        self.layout.addWidget(self.readme)
        self.layout.addWidget(self.btn_get_diagnosis)
        self.layout.addWidget(self.data_viewer)
        self.layout.setAlignment(self.readme, Qt.AlignTop)
        self.layout.setAlignment(self.btn_get_diagnosis, Qt.AlignTop)
        
    def do_analyze(self, code, editor):
        self.readme.setVisible(False)
        self.btn_get_diagnosis.setVisible(False)
        self.data_viewer.run(code, editor)
        self.data_viewer.setVisible(True)