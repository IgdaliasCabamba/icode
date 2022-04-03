from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
)

from ..igui import IListWidgetItem, InputHistory
from PyQt5.QtGui import QColor

from functions import getfn


class EOLMode(QFrame):

    focus_out = pyqtSignal(object, object)

    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.input_edit = InputHistory(self)
        self.input_edit.setPlaceholderText("Goto")
        self.input_edit.setObjectName("child")
        self.input_edit.returnPressed.connect(self.select_eol)
        self.input_edit.textChanged.connect(self.search_eol)

        self.eol_modes = QListWidget(self)
        self.eol_modes.setObjectName("child")
        self.eol_modes.setIconSize(QSize(16, 16))
        self.eol_modes.itemActivated.connect(self.mirror_in_editor)

        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.eol_modes)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)

    def search_eol(self, text):
        if text.startswith("!"):
            if len(text) > 1:
                eol = text.split("!")[1]

                results = self.eol_modes.findItems(eol, Qt.MatchContains)

                for i in range(self.eol_modes.count()):
                    self.eol_modes.setRowHidden(i, True)

                for row_item in results:
                    i = self.eol_modes.row(row_item)
                    self.eol_modes.setRowHidden(i, False)

                if len(results) > 0:
                    i = self.eol_modes.row(results[0])
                    self.eol_modes.setCurrentRow(i)

            else:
                for i in range(self.eol_modes.count()):
                    self.eol_modes.setRowHidden(i, False)

            self.update_size()

        elif text.startswith((":", "@", ">", "#")):
            self.api.run_by_id(self, text)

    def select_eol(self):
        items = self.eol_modes.selectedItems()
        for item in items:
            self.mirror_in_editor(item)

    def update_size(self):
        height = 0
        for i in range(self.eol_modes.count()):
            if not self.eol_modes.isRowHidden(i):
                height += self.eol_modes.sizeHintForRow(i)

        self.eol_modes.setFixedHeight(height + 10)
        self.setFixedHeight(
            self.input_edit.size().height() + self.eol_modes.size().height() + 20
        )

    def mirror_in_editor(self, item):
        for editor in self.api.current_editors:
            editor.set_eol_mode(item.item_data["object"])
        self.hide()

    def set_eols(self, data=False):
        if data:
            self.eol_modes.clear()
            for eol in data:
                row = IListWidgetItem(
                    eol["icon"], eol["name"].title(), None, {"object": eol["mode"]}
                )
                self.eol_modes.addItem(row)
        self.update_size()

    def run(self):
        self.input_edit.setFocus()
        self.input_edit.setText("!")
