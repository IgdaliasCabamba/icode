from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal


class InputHistory(QLineEdit):

    key_pressed = pyqtSignal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("input")
        self.parent = parent
        self.commands_list = []
        self.current_command_index = 0
        self.returnPressed.connect(self.add_command)

    def add_command(self):
        text = self.text()
        if self.commands_list:
            if text != self.commands_list[-1]:
                self.commands_list.append(text)
        else:
            self.commands_list.append(text)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == 16777235:
            if self.commands_list:
                if self.current_command_index < len(self.commands_list):
                    self.current_command_index += 1
                    try:
                        self.setText(
                            self.commands_list[self.current_command_index * -1]
                        )
                    except IndexError:
                        self.setText(self.commands_list[0])

        elif event.key() == 16777237:
            if self.current_command_index > 0:
                self.current_command_index -= 1
                try:
                    self.setText(self.commands_list[self.current_command_index])
                except IndexError:
                    self.setText(self.commands_list[-1])
