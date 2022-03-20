from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QFrame, QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTreeView, QSplitter, QLabel, QListWidget
from PyQt5.QtCore import Qt, QThread, QObject, QProcess
from ui.igui import IStandardItem
from smartpy_utils import debug_formatter, DEBUG_STATUS_REGEX, DEBUG_RETURN_REGEX, DEBUG_CONTEXT_REGEX, code_debug_doc
from functions import getfn


class OutputErrors(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        desc = QLabel("<h5>Exceptions</h5>")

        self.output_errors = QListWidget(self)

        self.layout.addWidget(desc)
        self.layout.addWidget(self.output_errors)

    def clear(self):
        self.output_errors.clear()


class OutputTree(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.model = QStandardItemModel(self)
        self.output_tree = QTreeView(self)
        self.output_tree.clicked.connect(self.output_tree_clicked)
        self.output_tree.setModel(self.model)
        self.output_tree.header().hide()

        desc = QLabel("<h5>Object Tree</h5>")

        self.layout.addWidget(desc)
        self.layout.addWidget(self.output_tree)

    def build(self, stdout):
        root_title = DEBUG_STATUS_REGEX.findall(stdout)
        child_title = DEBUG_RETURN_REGEX.findall(stdout)

        if root_title:
            if len(root_title[0]) > 2:
                root_item = IStandardItem(
                    self.parent.icons.get_icon("code-error"),
                    f"Object: {root_title[0][0]} At Line: {root_title[0][1]} On:{root_title[0][2]}",
                    None,
                    None,
                )
                if child_title:
                    if len(child_title[0]) > 1:
                        child_item = IStandardItem(
                            self.parent.icons.get_icon("return"),
                            f"{child_title[0][1]}", None, None)
                        root_item.appendRow(child_item)
                self.model.appendRow(root_item)

    def clear(self):
        self.model.clear()

    def output_tree_clicked(self):
        pass


class ConsoleOutput(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.output_console = QPlainTextEdit()
        self.output_console.setPlaceholderText("Debug Console")
        self.output_console.setReadOnly(True)

        desc = QLabel("<h5>Console</h5>")
        self.layout.addWidget(desc)

        self.layout.addWidget(self.output_console)

    def append(self, text):
        self.output_console.appendPlainText(text)

    def clear(self):
        self.output_console.clear()


class Debug(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.env = None
        self.editor = None
        self.icons = getfn.get_smartcode_icons("code")
        self.parent = parent
        self.setObjectName("debug")
        self.process_debuger = QProcess(self)
        self.process_debuger.readyReadStandardOutput.connect(
            self.handle_stdout)
        self.process_debuger.readyReadStandardError.connect(self.handle_stderr)
        self.process_debuger.stateChanged.connect(self.handle_state)
        self.process_debuger.finished.connect(self.process_finished)
        self.process_debuger.setProcessChannelMode(0)
        self.init_ui()
        self.listen_slots()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.hbox = QHBoxLayout()
        self.btn_next_line = QPushButton("Next")
        self.btn_until_line = QPushButton("Until")
        self.btn_until_return = QPushButton("Return")
        self.btn_continue = QPushButton("Continue")
        self.btn_jump_to = QPushButton("Jump")
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("type line")
        self.hbox.addWidget(self.btn_next_line)
        self.hbox.addWidget(self.btn_until_line)
        self.hbox.addWidget(self.btn_until_return)
        self.hbox.addWidget(self.btn_continue)
        self.hbox.addWidget(self.btn_jump_to)
        self.hbox.addWidget(self.input_line)

        self.div = QSplitter(self)
        self.div.setOrientation(Qt.Vertical)

        vbox_message = QVBoxLayout()
        vbox_message.setContentsMargins(0, 0, 0, 0)

        self.start_debug_message = QLabel(self)
        self.start_debug_message.setWordWrap(True)
        self.start_debug_message.setText(code_debug_doc)

        self.btn_start_debug = QPushButton(self)
        self.btn_start_debug.setText("Run with Debug")

        vbox_message.addWidget(self.start_debug_message)
        vbox_message.addWidget(self.btn_start_debug)

        self.output_errors = OutputErrors(self)
        self.output_tree = OutputTree(self)
        self.output_console = ConsoleOutput(self)

        self.input_text = QLineEdit(self)
        self.input_text.setPlaceholderText(":")

        self.label_status = QLabel(self)
        self.label_status.setWordWrap(False)

        self.div.addWidget(self.output_errors)
        self.div.addWidget(self.output_tree)
        self.div.addWidget(self.output_console)

        self.layout.addLayout(self.hbox)
        self.layout.addLayout(vbox_message)
        self.layout.addWidget(self.div)
        self.layout.addWidget(self.input_text)
        self.layout.addWidget(self.label_status)
        self.setLayout(self.layout)

        self.output_tree.setVisible(False)
        self.output_errors.setVisible(False)

    def listen_slots(self):
        self.btn_next_line.clicked.connect(self.next_frame)
        self.btn_until_line.clicked.connect(self.continue_until_line)
        self.btn_until_return.clicked.connect(self.continue_until_return)
        self.btn_jump_to.clicked.connect(self.jump_to)
        self.btn_continue.clicked.connect(self.continue_debugging)
        self.input_text.returnPressed.connect(self.write_input)

    def message(self, text):
        self.output_console.append(text)

    def log(self, stdout):
        self.output_tree.build(stdout)

    def start(self, editor, code, file, interpreter):
        bin = interpreter.executable
        args = ["-m", "pdb", str(file)]
        self.start_process(bin, args)
        self.btn_start_debug.setVisible(False)
        self.start_debug_message.setVisible(False)
        self.output_tree.setVisible(True)
        self.output_errors.setVisible(True)

    def stop(self):
        self.process_debuger.terminate()
        self.output_tree.setVisible(False)
        self.output_errors.setVisible(False)
        self.btn_start_debug.setVisible(True)
        self.start_debug_message.setVisible(True)

    def clear(self):
        self.output_tree.clear()
        self.output_console.clear()
        self.output_errors.clear()

    def start_process(self, bin, args):
        state = self.process_debuger.state()

        if state == QProcess.NotRunning:
            self.process_debuger.start(bin, args)
        else:
            self.label_status.setText(
                "<h3 style='color:yellow'>ALREADY RUNNING</h3>")

    def handle_stderr(self):
        data = self.process_debuger.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        #self.message(stderr)
        self.label_status.setText(f"<h5 style='color:red'>{stderr}</h5>")

    def handle_stdout(self):
        data = self.process_debuger.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(debug_formatter(stdout))
        self.log(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: "<h5>Not running</h5>",
            QProcess.Starting: "<h5 style='color:yellow'>Starting</h5>",
            QProcess.Running: "<h5 style='color:green'>Running</h5>"
        }
        state_name = states[state]
        self.label_status.setText(state_name)

    def process_finished(self):
        self.label_status.setText(
            "<h5 style='color:green'>Process finished</h5>")

    def next_frame(self):
        command = "n" + "\n"
        self.process_debuger.write(command.encode("utf-8"))

    def continue_debugging(self):
        command = "c" + "\n"
        self.process_debuger.write(command.encode("utf-8"))

    def continue_until_return(self):
        command = "r" + "\n"
        self.process_debuger.write(command.encode("utf-8"))

    def continue_until_line(self):
        line = self.input_line.text()
        if len(line) > 0:
            command = "unt " + line + "\n"
            self.process_debuger.write(command.encode("utf-8"))

    def jump_to(self):
        line = self.input_line.text()
        if len(line) > 0:
            command = "j " + line + "\n"
            self.process_debuger.write(command.encode("utf-8"))

    def write_input(self):
        command = self.input_text.text() + "\n"
        self.process_debuger.write(command.encode("utf-8"))
