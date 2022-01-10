from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame, QGridLayout,
    QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel
)

from ..igui import EditorListWidgetItem, InputHistory
from PyQt5.QtGui import QColor

from functions import getfn

class SpaceMode(QFrame):
    
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
        self.input_edit.returnPressed.connect(self.select_space)
        self.input_edit.textChanged.connect(self.search_space)
        
        self.space_modes = QListWidget(self)
        self.space_modes.setObjectName("child")
        self.space_modes.setIconSize(QSize(16,16))
        self.space_modes.itemActivated.connect(self.mirror_in_editor)
    
        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.space_modes)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)
            
    def search_space(self, text):
        if text.startswith("#"):
            if len(text) > 1:
                space = text.split("#")[1]

                results = self.space_modes.findItems(space, Qt.MatchContains)
        
                for i in range(self.space_modes.count()):
                    self.space_modes.setRowHidden(i, True)

                for row_item in results:
                    i = self.space_modes.row(row_item)
                    self.space_modes.setRowHidden(i, False)
                
                if len(results) > 0:
                    i = self.space_modes.row(results[0])
                    self.space_modes.setCurrentRow(i)

            else:
                for i in range(self.space_modes.count()):
                    self.space_modes.setRowHidden(i, False)
        
            self.update_size()
        
        elif text.startswith((":","@",">","!")):
            self.api.run_by_id(self, text)
    
    def mirror_in_editor(self, item):
        for editor in self.api.current_editors:
            editor.set_space_mode(item.data["object"])
        self.hide()
    
    def select_space(self):
        items = self.space_modes.selectedItems()
        for item in items:
            self.mirror_in_editor(item)
    
    def update_size(self):
        height = 0
        for i in range(self.space_modes.count()):
            if not self.space_modes.isRowHidden(i):
                height += self.space_modes.sizeHintForRow(i)

        self.space_modes.setFixedHeight(height+10)
        self.setFixedHeight(self.input_edit.size().height()+self.space_modes.size().height()+20)
    
    def set_spaces(self, data=False):    
        if data:
            self.space_modes.clear()
            for space in data:
                row = EditorListWidgetItem()
                row.setText(space["name"].title())
                row.setIcon(space["icon"])
                row.set_data({"action":space["action"]})
                self.space_modes.addItem(row)
        self.update_size()
        
    def run(self):
        self.input_edit.setFocus()
        self.input_edit.setText("#")
