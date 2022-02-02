from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame, QGridLayout,
    QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel
)
from PyQt5.QtGui import QColor

from ui.igui import EditorListWidgetItem, InputHistory
from functions import getfn

class SymbolExplorer(QFrame):
    
    focus_out = pyqtSignal(object, object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        self.icons = getfn.get_smartcode_icons("code")
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()
    
    def init_ui(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.symbol_input = InputHistory(self)
        self.symbol_input.setObjectName("child")
        self.symbol_input.textChanged.connect(self.search_symbol)
        self.symbol_input.returnPressed.connect(self.select_symbol)
        self.symbol_input.setMinimumHeight(24)

        self.symbol_list = QListWidget(self)
        self.symbol_list.setObjectName("child")
        self.symbol_list.setIconSize(QSize(16,16))
        self.symbol_list.itemActivated.connect(self.mirror_in_editor)
        self.symbol_list.setMinimumHeight(30)
        self.symbol_list.setMaximumHeight(500)

        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.symbol_list)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)
    
    def add_row(self, symbol, editor):
        row=EditorListWidgetItem()
        row.setText(f"{symbol.name}")
        row.setToolTip(f"line: {symbol.line_number}, level:{symbol.level}")
        row.setIcon(self.icons.get_icon(symbol.type))
        row.set_data({"line":symbol.line_number, "name":symbol.name, "editor":editor})
        self.symbol_list.addItem(row)

    def search_symbol(self, text):
        if text.startswith("@") and len(text) > 1:
            href = text.split("@")[1]
        
            results = self.symbol_list.findItems(href, Qt.MatchContains)
    
            for i in range(self.symbol_list.count()):
                self.symbol_list.setRowHidden(i, True)

            for row_item in results:
                i = self.symbol_list.row(row_item)
                self.symbol_list.setRowHidden(i, False)
            
            if len(results) > 0:
                i = self.symbol_list.row(results[0])
                self.symbol_list.setCurrentRow(i)
        
        elif text.startswith((":",">")):
            self.api.run_by_id(self, text)

        else:
            for i in range(self.symbol_list.count()):
                self.symbol_list.setRowHidden(i, False)
        
        self.update_size()
    
    def select_symbol(self):
        items = self.symbol_list.selectedItems()
        for item in items:
            self.mirror_in_editor(item)

    def update_size(self):
        height = 0
        for i in range(self.symbol_list.count()):
            if not self.symbol_list.isRowHidden(i):
                height += self.symbol_list.sizeHintForRow(i)

        self.symbol_list.setFixedHeight(height+10 if height < 500 else 500)
        self.setFixedHeight(self.symbol_input.size().height()+self.symbol_list.size().height()+20)

    def mirror_in_editor(self, item):
        editor=item.data["editor"]
        name=item.data["name"]
        line=item.data["line"]
        try:
            
            line_from, index_from, line_to, index_to = getfn.get_selection_from_item_data(editor, name, line)
            editor.setCursorPosition(line_from+1, index_to)
            editor.setSelection(line_from, index_from, line_to, index_to)
                
        except Exception as e:
            print(e)
        
        self.hide()
        
    def set_symbols(self, data=False):    
        if data:
            
            editor = self.api.get_current_editor()
        
            self.symbol_list.clear()
            
            for element in data:
                self.add_row(element, editor)
                
                for element in element.children:
                    self.add_row(element, editor)
                
                    for element in element.children:
                        self.add_row(element, editor)
                        
                        for element in element.children:
                            self.add_row(element, editor)
                    
        self.update_size()
    
    def run(self):
        self.symbol_list.setCurrentRow(0)
        self.symbol_input.setFocus()
        self.symbol_input.setText("@")