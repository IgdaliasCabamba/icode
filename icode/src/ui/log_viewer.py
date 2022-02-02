from PyQt5.QtWidgets import QFrame, QVBoxLayout, QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from functions import getfn

class ProblemStandardItem(QStandardItem):
    def __init__(self, icon, text, tooltip=None, item_data=None) -> None:
        super().__init__()
        self.setText(text)
        self.setIcon(icon)
        self.setToolTip(tooltip)
        
        self.item_data=item_data

class ProblemLogs(QFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("problems")
        self.icons = getfn.get_smartcode_icons("code")
        self.init_ui()
    
    def init_ui(self) -> None:
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5,5,5,5)

        self.problems_tree=QTreeView(self)
        self.problems_tree.header().hide()
        self.layout.addWidget(self.problems_tree)

        self.problems_model = QStandardItemModel(self)
        self.problems_tree.setModel(self.problems_model)

        self.app_problems = ProblemStandardItem(self.icons.get_icon("app-problem"), "APP")
        self.code_problems = ProblemStandardItem(self.icons.get_icon("code-problem"), "EDITORS")
        self.other_problems = ProblemStandardItem(self.icons.get_icon("app-problem"), "OTHERS")
        self.build_problems()

    def build_problems(self):
        self.problems_model.clear()
        self.problems_model.appendRow(self.app_problems)
        self.problems_model.appendRow(self.code_problems)
        self.problems_model.appendRow(self.other_problems)

        
        self.problems_tree.expand(
            self.problems_model.indexFromItem(
                self.app_problems
                )
            )
        self.problems_tree.expand(
            self.problems_model.indexFromItem(
                self.code_problems
                )
            )
        index = self.problems_model.indexFromItem(self.app_problems)
        self.problems_tree.setCurrentIndex(index)
        
    def add_problem(self, type, text, tooltip, data):
        if type == "app-problem":
            self.app_problems.appendRow(ProblemStandardItem("code-warning", text, tooltip, data))
        elif type == "code-problem":
            self.code_problems.appendRow(ProblemStandardItem("code-error", text, tooltip, data))
        else:
            self.other_problems.appendRow(ProblemStandardItem(type, text, tooltip, data))
