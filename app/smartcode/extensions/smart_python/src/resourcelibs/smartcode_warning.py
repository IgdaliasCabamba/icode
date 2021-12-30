from PyQt5.QtWidgets import (
    QFrame, QListWidget, QVBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QTreeView,
    QListWidget, QHBoxLayout
    )
from itertools import zip_longest
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from smartpy_api import python_api
from igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem

class CodeWarningsCore(QObject):
    
    on_warnings_loaded = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def run(self):
        self.parent.on_get_warnings.connect(self.get_warnings)

    def format_warnings(self, results, editor):
        warnings_list=[]

        if results["warnings"] and results["lines"]:
            for warning, line in zip_longest(results["warnings"], results["lines"]):
                row = IListWidgetItem(
                    self.parent.icons.get_icon("code-warning"),
                    str(warning),
                    f"line: {str(line+1)}",
                    {"editor":editor, "line":line}
                    )
                warnings_list.append(row)
        
        return warnings_list
    
    def get_warnings(self, editor):
        warnings = python_api.get_code_warnings(editor)
        warnings_rows = self.format_warnings(warnings, editor)
        self.on_warnings_loaded.emit(warnings_rows)

class CodeWarnings(QFrame):
    
    on_fix_bugs_clicked = pyqtSignal(object)
    on_get_warnings = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ilab-warnings")
        self.parent=parent
        self.icons = getfn.get_application_icons("code")
        
        self.thread_lab = QThread(self)
        
        self.brain = CodeWarningsCore(self)
        self.brain.on_warnings_loaded.connect(self.display_warnings)
        self.brain.moveToThread(self.thread_lab)
        self.thread_lab.started.connect(self.run_tasks)
        self.thread_lab.start()
        self.init_ui()
    
    def run_tasks(self):
        self.brain.run()

    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)

        self.display=QListWidget(self)
        self.display.itemClicked.connect(self.mirror_in_editor)
        self.display.setVisible(False)
        
        self.fix_bugs_btn=QPushButton(self)
        self.fix_bugs_btn.clicked.connect(self.on_fix_bugs)
        self.fix_bugs_btn.setVisible(False)
        
        self.readme = QLabel(self)
        self.readme.setText("""
            <small>
                Get warnings for your code,
                problems related to pep8 in
                your code will be detected and
                presented here, with the option
                to fix some of them!
                to use this functionality click
                on get warnings, here or on icode labs
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
        
        self.btn_get_warnings=QPushButton("Get Warnings", self)

        self.layout.addWidget(self.display)
        self.layout.addWidget(self.fix_bugs_btn)
        self.layout.addWidget(self.readme)
        self.layout.addWidget(self.btn_get_warnings)
        
        self.layout.setAlignment(self.readme, Qt.AlignTop)
        self.layout.setAlignment(self.btn_get_warnings, Qt.AlignTop)
    
    def on_fix_bugs(self):
        self.on_fix_bugs_clicked.emit(self.editor)

    def get_warnings(self, editor):
        self.editor=editor
        self.on_get_warnings.emit(editor)

    def display_warnings(self, data):
        self.fix_bugs_btn.setVisible(False)
        self.display.clear()

        for item in data:
            self.display.addItem(item)
        
        if self.display.count() > 0:
            self.fix_bugs_btn.setText(f"Try to FIX {len(data)} Bugs")
            self.fix_bugs_btn.setVisible(True)
            self.display.setVisible(True)
            self.readme.setVisible(False)
            self.btn_get_warnings.setVisible(False)

    def mirror_in_editor(self, item):
        editor = item.item_data["editor"]
        line = item.item_data["line"]

        line_from = line
        index_from = 0
        line_to = line
        index_to = editor.lineLength(line)

        editor.setSelection(line_from, index_from, line_to, index_to)