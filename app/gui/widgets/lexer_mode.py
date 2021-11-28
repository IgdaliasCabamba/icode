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
from smartlibs.jedit2 import edit

class LexerMode(QFrame):
    
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

        self.lang_input = InputHistory(self)
        self.lang_input.setObjectName("child")
        self.lang_input.textChanged.connect(self.search_lang)
        self.lang_input.returnPressed.connect(self.select_language)
        self.lang_input.setMinimumHeight(30)

        self.lang_list = QListWidget(self)
        self.lang_list.setObjectName("child")
        self.lang_list.setIconSize(QSize(16,16))
        self.lang_list.itemActivated.connect(self.mirror_in_editor)
        self.lang_list.setMinimumHeight(30)

        self.layout.addWidget(self.lang_input)
        self.layout.addWidget(self.lang_list)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)

    def search_lang(self, text):
        if len(text) > 1:
        
            results = self.lang_list.findItems(text, Qt.MatchContains)
    
            for i in range(self.lang_list.count()):
                self.lang_list.setRowHidden(i, True)

            for row_item in results:
                i = self.lang_list.row(row_item)
                self.lang_list.setRowHidden(i, False)
            
            if len(results) > 0:
                i = self.lang_list.row(results[0])
                self.lang_list.setCurrentRow(i)

        else:
            for i in range(self.lang_list.count()):
                self.lang_list.setRowHidden(i, False)
        
        self.update_size()
    
    def select_language(self):
        items = self.lang_list.selectedItems()
        for item in items:
            self.mirror_in_editor(item)

    def update_size(self):
        height = 0
        for i in range(self.lang_list.count()):
            if not self.lang_list.isRowHidden(i):
                height += self.lang_list.sizeHintForRow(i)

        self.lang_list.setFixedHeight(height+10)
        self.setFixedHeight(self.lang_input.size().height()+self.lang_list.size().height()+20)

    def mirror_in_editor(self, item):
        for editor in self.api.current_editors:
            editor.set_lexer(item.data["object"])
        self.hide()
        
    def set_langs(self, data=False):    
        if data:
            self.lang_list.clear()
            for lang in data:
                row = EditorListWidgetItem()
                row.setText(lang["name"].title())
                row.setIcon(lang["icon"])
                row.set_data({"object":lang["lexer"]})
                self.lang_list.addItem(row)
        self.update_size()
    
    def run(self):
        self.lang_list.setCurrentRow(0)
        self.lang_input.setFocus()