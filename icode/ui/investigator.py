from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMenu, QPushButton,
                             QVBoxLayout, QAction)

from base.searcher import *
from data import user_cache
from functions import getfn, pathlib
from .igui import HeaderPushButton, InputHistory, Animator

class FindOptions(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
                
        self.case_sensitive = QAction("Case Sensitive", self)
        self.case_sensitive.setCheckable(True)
        self.addAction(self.case_sensitive)
        
        self.search_subdirs = QAction("Search Subdirs", self)
        self.search_subdirs.setCheckable(True)
        self.addAction(self.search_subdirs)
        
        self.break_on_find = QAction("Break on Find", self)
        self.break_on_find.setCheckable(True)
        self.addAction(self.break_on_find)
        
        self.case_sensitive.triggered.connect(self.update_cache)
        self.search_subdirs.triggered.connect(self.update_cache)
        self.break_on_find.triggered.connect(self.update_cache)
        
        self.restore_from_cache()
    
    def update_cache(self):
        user_cache.setValue("isearch/cs", self.case_sensitive.isChecked())
        user_cache.setValue("isearch/ss", self.search_subdirs.isChecked())
        user_cache.setValue("isearch/bf", self.break_on_find.isChecked())
    
    def restore_from_cache(self):
        cs = getfn.get_bool_from_str(user_cache.value("isearch/cs"))
        ss = getfn.get_bool_from_str(user_cache.value("isearch/ss"))
        bf = getfn.get_bool_from_str(user_cache.value("isearch/bf"))
        
        if isinstance(cs, bool):
            self.case_sensitive.setChecked(cs)
        if isinstance(ss, bool):
            self.search_subdirs.setChecked(ss)
        if isinstance(bf, bool):
            self.break_on_find.setChecked(bf)
        
        
class IListItem(QListWidgetItem):
    def __init__(self, name, tip, item_data:dict):
        super().__init__()
        self.icon=QIcon(getfn.get_icon_from_ext(name))
        self.title=name
        self.tip=tip
        self.item_data=item_data

        self.setText(self.title)
        self.setIcon(self.icon)
        self.setToolTip(self.tip)

class Results(QFrame):
    on_open_file_request=pyqtSignal(str, str)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        self.list_view=QListWidget(self)
        self.list_view.itemDoubleClicked.connect(self.open_file_from_item)
        self.list_view.setVisible(False)
        self.list_view.setIconSize(QSize(16, 16))
        
        self.label=QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setVisible(False)
        self.label.linkActivated.connect(self.option_clicked)

        self.layout.addWidget(self.list_view)
        self.layout.addWidget(self.label)
    
    def open_file_from_item(self, item):
        self.on_open_file_request.emit(item.item_data["file"], item.item_data["query"])

    def clear(self):
        self.list_view.clear()
    
    def show_text(self, text):
        self.list_view.setVisible(False)
        self.label.setText(text)
        self.label.setVisible(True)

    def show_open_folder(self):
        self.show_text("<p>Please <a href='#open_folder'>select</a> a folder to search</p>")

    def option_clicked(self, href):
        self.label.setText("")
        if href=="#open_folder":
            self.parent.explorer.open_folder()

    def set_results(self, results, query):
        self.clear()
        for item in results:
            obj_path=pathlib.Path(item)
            
            row=IListItem(obj_path.name, item, {"file":item, "query":query})
            
            self.list_view.addItem(row)
        
        self.label.setVisible(False)
        self.list_view.setVisible(True)

class Searcher(QFrame):
     
    on_searched=pyqtSignal(str, str, str, int, dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.explorer=parent.explorer
        self.folder = self.explorer.folder
        self.icons = getfn.get_application_icons("search")
        self.search_options_menu = FindOptions(self)
        self.query_history = []
        self._work_count = 0
    
        self.thread=QThread()
        self.engine=SearchEngine(self)
        self.engine.on_results.connect(self.display_results)
        self.engine.moveToThread(self.thread)
        self.thread.start()
        self.thread.started.connect(self.run)
    
        self.init_ui()
        
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.input_find=InputHistory(self)
        self.input_find.returnPressed.connect(lambda: self.do_search(0))
        self.input_find.setPlaceholderText("Find")
        self.input_replace=InputHistory(self)
        self.input_replace.returnPressed.connect(lambda: self.do_search(1))
        self.input_replace.setPlaceholderText("Replace")

        self.display=Results(self)

        self.top_info=QLabel("<small>SEARCH</small>")
        self.top_info.setWordWrap(True)
        
        self.animation = Animator(self, self.icons.get_path("loading"))
        self.animation.setMaximumHeight(16)
        self.animation.set_scaled_size(64, 16)
        self.animation.stop(False)
        
        self.btn_change_search_mode = HeaderPushButton(self)
        self.btn_change_search_mode.setMenu(self.search_options_menu)
        self.btn_change_search_mode.clicked.connect(lambda: self.btn_change_search_mode.showMenu())
        self.btn_change_search_mode.setObjectName("searcher-header-button")
        self.btn_change_search_mode.setIcon(self.icons.get_icon("options"))
        
        self.btn_reload_search = HeaderPushButton(self)
        self.btn_reload_search.setObjectName("searcher-header-button")
        self.btn_reload_search.setIcon(self.icons.get_icon("reload"))
        
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.header_layout.addWidget(self.animation)
        self.header_layout.addWidget(self.btn_reload_search)
        self.header_layout.addWidget(self.btn_change_search_mode)
        self.header_layout.setAlignment(self.animation, Qt.AlignLeft)
        
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.input_find)
        self.layout.addWidget(self.input_replace)
        self.layout.addWidget(self.display)

    def do_search(self, event):
        find_text=self.input_find.text()
        replace_text=self.input_replace.text()
        self.folder = self.explorer.folder
        
        if self.folder is None:
            self.display.show_open_folder()
            return
        
        args={
            "cs":self.search_options_menu.case_sensitive.isChecked(),
            "ss":self.search_options_menu.search_subdirs.isChecked(),
            "bf":self.search_options_menu.break_on_find.isChecked()
        }
        
        self.on_searched.emit(find_text, replace_text, self.folder, event, args)
        self.query_history.append(find_text)
        self._work_count += 1
        self.animation.play(True)
    
    def display_results(self, results, query):
        if results:
            self.display.set_results(results, query)
        else:
            self.display.clear()
            self.display.show_text("Files not found")
        self._work_count -= 1
        if self._work_count < 1:
            self.animation.stop(False)

    def run(self):
        self.engine.run()
    
    def validate(self, text):        
        if text.replace(" ", "") == "":
            return False

        return True