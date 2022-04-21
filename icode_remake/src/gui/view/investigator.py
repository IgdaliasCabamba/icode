# TODO: Refactor

from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QSizePolicy,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QAction,
)

from core.searcher import *
from data import user_cache
from functions import getfn, pathlib
from .igui import IListWidgetItem
from smartlibs.qtmd import HeaderPushButton, InputHistory, Animator


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


class FindPanel(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("finder")
        self.parent = parent
        self.options_menu = FindOptions(self)
        self.icons = getfn.get_smartcode_icons("finder")
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.input_edit = InputHistory(self)
        self.input_edit.setMaximumHeight(32)
        self.input_edit.setPlaceholderText("Find...")

        self.btn_find_next = QPushButton(self)
        self.btn_find_next.setIcon(self.icons.get_icon("next"))

        self.btn_find_prev = QPushButton(self)
        self.btn_find_prev.setIcon(self.icons.get_icon("prev"))

        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.btn_find_next)
        self.layout.addWidget(self.btn_find_prev)


class ReplacePanel(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.icons = getfn.get_smartcode_icons("replacer")
        self.setObjectName("replacer")
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.input_edit = InputHistory(self)
        self.input_edit.setMaximumHeight(30)
        self.input_edit.setPlaceholderText("Replace...")

        self.btn_replace_all = QPushButton(self)
        self.btn_replace_all.setIcon(self.icons.get_icon("replace-all"))

        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.btn_replace_all)

        self.setVisible(False)


class Results(QFrame):
    on_open_file_request = pyqtSignal(str, str)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.list_view = QListWidget(self)
        self.list_view.itemDoubleClicked.connect(self.open_file_from_item)
        self.list_view.setVisible(False)
        self.list_view.setIconSize(QSize(16, 16))

        self.label = QLabel(self)
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
        self.show_text(
            "<p>Please <a href='#open_folder'>select</a> a folder to search</p>"
        )

    def option_clicked(self, href):
        self.label.setText("")
        if href == "#open_folder":
            self.parent.explorer.open_folder()

    def set_results(self, results, query):
        self.clear()
        for item in results:
            obj_path = pathlib.Path(item)

            row = IListWidgetItem(
                getfn.get_qicon(getfn.get_icon_from_ext(obj_path.name)),
                obj_path.name,
                item,
                {"file": item, "query": query},
            )

            self.list_view.addItem(row)

        self.label.setVisible(False)
        self.list_view.setVisible(True)


class Searcher(QFrame):

    on_searched = pyqtSignal(str, str, str, int, dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("search-panel")
        self.parent = parent
        self.explorer = parent.explorer
        self.folder = None #self.explorer.folder
        self.icons = getfn.get_smartcode_icons("search")
        self.search_options_menu = FindOptions(self)
        self.query_history = []
        self._work_count = 0

        self.thread = QThread()
        self.engine = SearchEngine(self)
        self.engine.on_results.connect(self.display_results)
        self.engine.moveToThread(self.thread)
        self.thread.start()
        self.thread.started.connect(self.run)

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)

        self.panel_layout = QHBoxLayout()
        self.panel_layout.setContentsMargins(0, 0, 0, 0)

        sub_layout = QGridLayout()
        sub_layout.setContentsMargins(2, 2, 2, 2)

        self.finder = FindPanel(self)
        self.replacer = ReplacePanel(self)

        self.btn_mode = QPushButton(self)
        self.btn_mode.setIcon(self.icons.get_icon("collapse"))
        self.btn_mode.setObjectName("btn-expand-collapse")
        self.btn_mode.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.btn_mode.clicked.connect(self.change_mode)

        self.input_find = self.finder.input_edit
        self.input_find.returnPressed.connect(lambda: self.do_search(0))
        self.input_replace = self.replacer.input_edit
        self.input_replace.returnPressed.connect(lambda: self.do_search(1))
        self.btn_replace_all = self.replacer.btn_replace_all
        self.btn_replace_all.clicked.connect(lambda: self.do_search(1))

        self.display = Results(self)

        self.top_info = QLabel("<small>SEARCH</small>")
        self.top_info.setWordWrap(True)

        self.animation = Animator(self, self.icons.get_path("loading"))
        self.animation.setMaximumHeight(16)
        self.animation.set_scaled_size(64, 16)
        self.animation.stop(False)

        self.btn_change_search_mode = HeaderPushButton(self)
        self.btn_change_search_mode.setMenu(self.search_options_menu)
        self.btn_change_search_mode.clicked.connect(
            lambda: self.btn_change_search_mode.showMenu()
        )
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
        self.layout.addLayout(self.panel_layout)
        sub_layout.addWidget(self.finder, 1, 1)
        sub_layout.addWidget(self.replacer, 2, 1)
        self.panel_layout.addWidget(self.btn_mode)
        self.panel_layout.addLayout(sub_layout)
        self.layout.addWidget(self.display)

    def do_search(self, event):
        find_text = self.input_find.text()
        if self.validate(find_text):
            replace_text = self.input_replace.text()
            self.folder = self.explorer.folder

            if self.folder is None:
                self.display.show_open_folder()
                return

            args = {
                "cs": self.search_options_menu.case_sensitive.isChecked(),
                "ss": self.search_options_menu.search_subdirs.isChecked(),
                "bf": self.search_options_menu.break_on_find.isChecked(),
            }

            self.on_searched.emit(find_text, replace_text, self.folder, event, args)
            self.query_history.append(find_text)
            self._work_count += 1
            self.animation.play(True)
        else:
            self.display.show_text(
                "<p style='color:yellow'>Please Type Some Thing to Search</p>"
            )

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
        if len(text.replace(" ", "")) <= 0:
            return False

        return True

    def change_mode(self):
        self.replacer.setVisible(not self.replacer.isVisible())
        if self.replacer.isVisible():
            self.expand()
        else:
            self.collapse()

    def expand(self):
        self.btn_mode.setIcon(self.icons.get_icon("expand"))
        self.replacer.setVisible(True)

    def collapse(self):
        self.btn_mode.setIcon(self.icons.get_icon("collapse"))
        self.replacer.setVisible(False)
