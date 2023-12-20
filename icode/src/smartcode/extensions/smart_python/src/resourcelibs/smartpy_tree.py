from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QTreeView,
    QListWidget,
    QHBoxLayout,
)

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from smartpy_api import python_api
from gui.view.igui import IListWidgetItem, IStandardItem


class CodeTreeCore(QObject):

    on_model_loaded = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.parent.on_get_tree.connect(self.get_code_parse)

    def get_code_parse(self, code, editor):
        try:
            python_tree = python_api.get_python_node_tree(code)
            self.classes = self.parent.classes
            self.functions = self.parent.functions
            self.variables = self.parent.variables
            self.modules = self.parent.modules
            if python_tree:

                for element in python_tree:
                    tree_item = f"{element.name}"

                    if element.type == "class":
                        class_row = IStandardItem(
                            self.parent.icons.get_icon(element.type),
                            tree_item,
                            f"line: {element.line_number}, level:{element.level}",
                            {
                                "line": element.line_number,
                                "name": element.name,
                                "editor": editor,
                            },
                            1,
                        )
                        self.classes.appendRow(class_row)

                        for child_element in element.children:
                            child_tree_item = IStandardItem(
                                self.parent.icons.get_icon(child_element.type),
                                f"{child_element.name}",
                                f"line: {child_element.line_number}, level:{child_element.level}",
                                {
                                    "line": child_element.line_number,
                                    "name": child_element.name,
                                    "editor": editor,
                                },
                                2,
                            )
                            class_row.appendRow(child_tree_item)

                    elif element.type == "function":
                        function_row = IStandardItem(
                            self.parent.icons.get_icon(element.type),
                            tree_item,
                            f"line: {element.line_number}, level:{element.level}",
                            {
                                "line": element.line_number,
                                "name": element.name,
                                "editor": editor,
                            },
                            1,
                        )
                        self.functions.appendRow(function_row)

                        for child_element in element.children:
                            child_tree_item = IStandardItem(
                                self.parent.icons.get_icon(child_element.type),
                                f"{child_element.name}",
                                f"line({child_element.line_number}, level:{child_element.level}",
                                {
                                    "line": child_element.line_number,
                                    "name": child_element.name,
                                    "editor": editor,
                                },
                                2,
                            )
                            function_row.appendRow(child_tree_item)

                    elif element.type == "global_variable":
                        variable_row = IStandardItem(
                            self.parent.icons.get_icon(element.type),
                            tree_item,
                            f"line: {element.line_number}, level:{element.level}",
                            {
                                "line": element.line_number,
                                "name": element.name,
                                "editor": editor,
                            },
                            1,
                        )
                        self.variables.appendRow(variable_row)

                    elif element.type == "import":
                        module_row = IStandardItem(
                            self.parent.icons.get_icon(element.type),
                            tree_item,
                            f"line: {element.line_number}, level:{element.level}",
                            {
                                "line": element.line_number,
                                "name": element.name,
                                "editor": editor,
                            },
                            1,
                        )
                        self.modules.appendRow(module_row)

            self.on_model_loaded.emit()
        except RuntimeError:
            pass


class CodeTree(QTreeView):

    on_get_tree = pyqtSignal(str, object)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.icons = getfn.get_smartcode_icons("code")
        self.code = None
        self.file = None

        self.thread_tree = QThread(self)
        self.tree_object = CodeTreeCore(self)
        self.tree_object.on_model_loaded.connect(self.render_tree)
        self.tree_object.moveToThread(self.thread_tree)
        self.thread_tree.started.connect(self.run_tasks)
        self.thread_tree.start()
        self.init_ui()

    def run_tasks(self):
        self.tree_object.run()

    def init_ui(self):
        self.header().hide()
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        self.setUniformRowHeights(True)
        self.model.itemChanged.connect(self.mirror_in_editor)
        self.clicked.connect(self.tree_clicked)
        self.prepare_tree()

    def tree_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if item.level > 0:
            if item.item_data["editor"] is not None:
                self.mirror_in_editor(item)

    def mirror_in_editor(self, item):
        if item.level > 0:
            editor = item.item_data["editor"]
            name = item.item_data["name"]
            line = item.item_data["line"]
            try:
                if item.text() != name:

                    if getfn.get_selection_from_item_data(editor, name, line):
                        (
                            line_from,
                            index_from,
                            line_to,
                            index_to,
                        ) = getfn.get_selection_from_item_data(
                            editor, name, line)
                        editor.setCursorPosition(line_from + 1, index_to)
                        editor.setSelection(line_from, index_from, line_to,
                                            index_to)
                        editor.replaceSelectedText(item.text())

                        item.item_data["name"] = editor.text(line - 1)
                else:
                    (
                        line_from,
                        index_from,
                        line_to,
                        index_to,
                    ) = getfn.get_selection_from_item_data(editor, name, line)
                    editor.setCursorPosition(line_from + 1, index_to)
                    editor.setSelection(line_from, index_from, line_to,
                                        index_to)

            except Exception as e:
                print(e)
                return
        return

    def prepare_tree(self):
        file_name = "None"
        file = self.file
        if file is not None:
            file_name = self.file.name

        self.doc = IStandardItem(self.icons.get_icon("file"),
                                 f"DOCUMENT:{file_name}", f"{file}", None, 0)
        self.doc.setCheckable(False)
        self.model.appendRow(self.doc)

        self.modules = IStandardItem(self.icons.get_icon("import"), "MODULES",
                                     None, None, 0)
        self.modules.setCheckable(False)
        self.model.appendRow(self.modules)

        self.classes = IStandardItem(self.icons.get_icon("class"), "CLASSES",
                                     None, None, 0)
        self.classes.setCheckable(False)
        self.model.appendRow(self.classes)

        self.functions = IStandardItem(self.icons.get_icon("function"),
                                       "FUNCTIONS", None, None, 0)
        self.functions.setCheckable(False)
        self.model.appendRow(self.functions)

        self.variables = IStandardItem(self.icons.get_icon("global_variable"),
                                       "VARIABLES", None, None, 0)
        self.model.appendRow(self.variables)

    def build_tree(self, editor):
        self.code = editor.text()
        self.file = Path(editor.file_path)

        self.model.clear()
        self.prepare_tree()

        self.on_get_tree.emit(self.code, editor)

    def render_tree(self):
        for row in [self.classes, self.variables, self.functions]:
            index = self.model.indexFromItem(row)
            self.expand(index)
