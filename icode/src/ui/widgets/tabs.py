from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QVBoxLayout,
)
from PyQt5.QtGui import QKeyEvent

from ..igui import EditorListWidgetItem, InputHistory

class ListWidget(QListWidget):
    
    on_next_request = pyqtSignal()
    on_select_request = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def keyPressEvent(self, event:QKeyEvent) -> None:
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event:QKeyEvent) -> None:
        super().keyReleaseEvent(event)
        if event.key() == Qt.Key_Control:
            self.on_select_request.emit()
        
class TabBrowser(QFrame):
    
    focus_out = pyqtSignal(object, object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self.index = 0
        self.notebook = None
        self._parent = parent
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()
    
    def init_ui(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.tab_list = ListWidget(self)
        self.tab_list.setObjectName("child")
        self.tab_list.setIconSize(QSize(16,16))
        self.tab_list.on_select_request.connect(self.select_tab)
        self.tab_list.itemActivated.connect(self.change_tab)

        self.layout.addWidget(self.tab_list)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)
    
    def select_tab(self):
        items = self.tab_list.selectedItems()
        for item in items:
            self.change_tab(item)

    def update_size(self):
        height = 0
        for i in range(self.tab_list.count()):
            if not self.tab_list.isRowHidden(i):
                height += self.tab_list.sizeHintForRow(i)
        
        if height > 400:
            height = 400
        self.tab_list.setFixedHeight(height)
        self.setFixedHeight(self.tab_list.size().height()+10)

    def change_tab(self, item):
        self.notebook.setCurrentWidget(item.data["object"])
        self.hide()
        
    def set_navigation(self, data):
        if data:
            self.notebook = data["notebook"]
            self.tab_list.clear()
            for tab in data["tabs"]:
                row = EditorListWidgetItem()
                row.setText(tab["title"])
                row.setIcon(tab["icon"])
                row.setToolTip(tab["tooltip"])
                row.set_data({"object":tab["widget"], "index":tab["index"]})
                self.tab_list.addItem(row)
        self.update_size()
    
    def next_item(self):
        self.index+=1
        if self.index >= self.tab_list.count():
           self.index = 0    
        self.tab_list.setCurrentRow(self.index)
    
    def select_tab(self):
        self.change_tab(self.tab_list.item(self.index))
        
    def run(self):
        self.index = 1
        self.tab_list.setCurrentRow(1)
        self.tab_list.setFocus()