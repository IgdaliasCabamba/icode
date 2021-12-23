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
from igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem

class CodeDoctorCore(QObject):
    
    on_diagnosis_loaded = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def run(self):
        self.parent.on_get_analyze.connect(self.do_analyze)
    
    def format_diagnosis(self, results, editor):
        code_metrics = DoctorStandardItem(self.parent.icons.get_icon("code-metric"), 'CODE METRICS', None, None)
        code_errors = DoctorStandardItem(self.parent.icons.get_icon("code-syntax-error"), 'CODE ERRORS', None, None)

        if results["analyze"]:
            items_metrics_list = [
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Lines of code: {results["analyze"].loc}',
                    None,
                    None
                    ),
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Source lines of code: {results["analyze"].lloc}',
                    None,
                    None
                    ),
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Logical lines of code: {results["analyze"].sloc}',
                    None,
                    None
                    ),
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Python comment lines: {results["analyze"].comments}',
                    None,
                    None
                    ),
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Lines multi-line strings: {results["analyze"].multi}',
                    None,
                    None
                    ),
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Lines which are just comments: {results["analyze"].single_comments}',
                    None,
                    None
                    ),
                DoctorStandardItem(
                    self.parent.icons.get_icon("code-data"),
                    f'Blank lines: {results["analyze"].blank}',
                    None,
                    None
                    )
            ]
            for item in items_metrics_list:
                code_metrics.appendRow(item)
        else:
            pass

        if results["syntax_errors"]:
            
            for error in results["syntax_errors"]:
                row=DoctorStandardItem(
                        self.parent.icons.get_icon("code-error"),
                        f"{error.get_message()}",
                        f"from ({error.line},{error.column}) to ({error.until_line+1},{error.until_column})",
                        {"editor": editor, "error":error}
                    )
                code_errors.appendRow(row)

        else:
            row=DoctorStandardItem(
                    self.parent.icons.get_icon("good"),
                    f"No errors found 🙂",
                    None,
                    None
                    )
            code_errors.appendRow(row)
            
        return [code_metrics, code_errors]
    
    def do_analyze(self, code, editor):
        diagnosis=getfn.get_python_diagnosis(code)
        code_info=self.format_diagnosis(diagnosis, editor)
        self.on_diagnosis_loaded.emit(code_info)
        
class CodeDoctor(QFrame):
    
    on_get_analyze = pyqtSignal(object, object)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.icons = getfn.get_application_icons("code")
        
        self.thread_lab = QThread(self)
        
        self.brain = CodeDoctorCore(self)
        self.brain.on_diagnosis_loaded.connect(self.display_diagnosis)
        self.brain.moveToThread(self.thread_lab)
        self.thread_lab.started.connect(self.run_tasks)
        self.thread_lab.start()
        self.init_ui()
    
    def run_tasks(self):
        self.brain.run()

    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)

        self.model=QStandardItemModel(self)
        self.tree=QTreeView(self)
        self.tree.clicked.connect(self.tree_clicked)
        self.tree.setModel(self.model)
        self.tree.header().hide()
        self.tree.setVisible(False)
        
        self.readme = QLabel(self)
        self.readme.setText("""
            <small>
                Get basic diagnosis for your code,
                get data such as:
                <ul>
                    <li>number of lines</li>
                    <li>coments</li>
                    <li>logic lines of code</li>
                    <li>blank lines</li>
                    <li>syntax errors and more.</li>
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
        
        self.layout.addWidget(self.readme)
        self.layout.addWidget(self.btn_get_diagnosis)
        self.layout.setAlignment(self.readme, Qt.AlignTop)
        self.layout.setAlignment(self.btn_get_diagnosis, Qt.AlignTop)
        
        self.layout.addWidget(self.tree)
    
    def tree_clicked(self, index):
        item=self.model.itemFromIndex(index)
        if item.item_data is not None:
            if item.item_data["editor"] is not None:
                self.mirror_in_editor(item)
    
    def mirror_in_editor(self, item):
        editor = item.item_data["editor"]
        error = item.item_data["error"]
        line_from = error.line
        index_from = error.column
        line_to = error.until_line
        index_to = error.until_column
        
        editor.setSelection(line_from, index_from, line_to, index_to)

    def do_analyze(self, code, editor):
        self.on_get_analyze.emit(code, editor)

    def display_diagnosis(self, data): 
        self.model.clear()
        self.tree.setVisible(True)
        self.readme.setVisible(False)
        self.btn_get_diagnosis.setVisible(False)
        for item in data:
            self.model.appendRow(item)
            index = self.model.indexFromItem(item)
            self.tree.expand(index)