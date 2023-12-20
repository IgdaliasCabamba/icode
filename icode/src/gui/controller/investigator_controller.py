from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.searcher import *


class SearcherController(QObject):

    on_searched = pyqtSignal(str, str, str, int, dict)

    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view
        self.explorer = application_core.file_explorer
        self.folder = application_core.file_explorer.folder

        self.query_history = []
        self._work_count = 0

        self.thread = QThread()
        self.engine = SearchEngine(self)
        self.engine.on_results.connect(self.display_results)
        self.engine.moveToThread(self.thread)
        self.thread.start()
        self.thread.started.connect(self.run)

        self.view.input_find.returnPressed.connect(lambda: self.do_search(0))
        self.view.input_replace.returnPressed.connect(
            lambda: self.do_search(1))
        self.view.btn_replace_all.clicked.connect(lambda: self.do_search(1))
        self.view.btn_change_search_mode.clicked.connect(
            lambda: self.view.btn_change_search_mode.showMenu())

    def display_results(self, results, query):
        self.view.display_results(results, query)

        self._work_count -= 1
        if self._work_count < 1:
            self.view.animation.stop(False)

    def run(self):
        self.engine.run()

    def validate(self, text):
        if len(text.replace(" ", "")) <= 0:
            return False

        return True

    def do_search(self, event):
        find_text = self.view.input_find.text()
        if self.validate(find_text):
            replace_text = self.view.input_replace.text()
            self.folder = self.explorer.folder

            if self.folder is None:
                self.view.display.show_open_folder()
                return

            args = {
                "cs": self.view.search_options_menu.case_sensitive.isChecked(),
                "ss": self.view.search_options_menu.search_subdirs.isChecked(),
                "bf": self.view.search_options_menu.break_on_find.isChecked(),
            }

            self.on_searched.emit(find_text, replace_text, self.folder, event,
                                  args)
            self.query_history.append(find_text)
            self._work_count += 1
            self.view.animation.play(True)
        else:
            self.view.display.show_text(
                "<p style='color:yellow'>Please Type Some Thing to Search</p>")
