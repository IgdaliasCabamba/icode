from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QHBoxLayout,
    QGridLayout,
)

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from smartpy_api import python_api, visitors
from ui.igui import ScrollLabel, IListWidgetItem, IStandardItem
from frameworks.qroundprogressbar import QRoundProgressBar
from smartpy_utils import format_analyze_rank, deep_analyze_doc


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
        self.inspect_objects.currentRowChanged.connect(self.show_data)
        self.vbox_left.addWidget(self.inspect_objects)

        self.vbox_right = QVBoxLayout()

        bar_desc = QLabel("<strong>Object Complexity</strong>")
        bar_desc.setAlignment(Qt.AlignCenter)

        self.complexity_bar = QRoundProgressBar(self)
        self.complexity_bar.setMinimumSize(160, 160)
        self.complexity_bar.setBarStyle(QRoundProgressBar.BarStyle.DONUT)
        self.complexity_bar.setRange(0, 47)
        self.complexity_bar.setValue(0)

        self.label_rank = QLabel(self)
        self.label_rank.setAlignment(Qt.AlignCenter)
        self.label_rank.setWordWrap(False)

        self.quality_label = QLabel(self)
        self.quality_label.setWordWrap(True)

        self.vbox_right.addWidget(bar_desc)
        self.vbox_right.addWidget(self.complexity_bar)
        self.vbox_right.addWidget(self.label_rank)
        self.vbox_right.addWidget(self.quality_label)

        self.layout.addLayout(self.vbox_left)
        self.layout.addLayout(self.vbox_right)

    def run(self, code, editor):
        self.inspect_objects.clear()

        results = python_api.get_code_analyze(code)

        if results is not None:
            for result in results:
                if isinstance(result, visitors.Function):
                    icon_category = "function"
                elif isinstance(result, visitors.Class):
                    icon_category = "class"
                else:
                    icon_category = "*"

                rank = python_api.get_analyze_rank(result.complexity)
                self.inspect_objects.addItem(
                    IListWidgetItem(
                        self.icons.get_icon(icon_category),
                        result.name,
                        None,
                        {"editor": editor, "object": result, "rank": rank},
                    )
                )

    def show_data(self, row):
        item = self.inspect_objects.item(row)
        if item is not None:
            editor = item.item_data["editor"]
            result = item.item_data["object"]
            rank = format_analyze_rank(item.item_data["rank"])
            self.complexity_bar.setValue(result.complexity)
            self.label_rank.setText(rank[0])
            self.quality_label.setText(rank[1])


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
        self.readme.setText(deep_analyze_doc)
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
