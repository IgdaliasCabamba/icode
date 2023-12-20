from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.april.april_brain import *


class AssistantController(QObject):

    on_asked = pyqtSignal(str, dict)

    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view

        self._work_count = 0
        self.settings = {"all_response": False, "answer_count": 1}

        self.thread = QThread()
        self.brain = Brain(self)
        self.brain.moveToThread(self.thread)
        self.thread.start()
        self.thread.started.connect(self.run)
        self.brain.on_answered.connect(self.display_result)

        self.view.input.returnPressed.connect(self.search_answer)
        self.view.options.less_answers.triggered.connect(
            lambda: self.configure_ans_count(1))
        self.view.options.two_answers.triggered.connect(
            lambda: self.configure_ans_count(2))
        self.view.options.normal_answers.triggered.connect(
            lambda: self.configure_ans_count(3))
        self.view.options.all_answers.triggered.connect(
            lambda: self.configure_ans_count(20))

    def run(self):
        self.view.input.setEnabled(True)
        self.brain.run()

    def search_answer(self):

        text = self.view.input.text()
        self.view.add_message(text, "Me \uf866", 1)
        self.on_asked.emit(text, self.settings)
        self._work_count += 1
        self.view.animation.play(True)

    def display_result(self, res: str, type: int):
        res = res
        if type in {0, 1}:
            self.view.add_message(res, "April \uf860", 0, "text")

        elif type == 2:
            for ans in res:
                if isinstance(ans, dict):
                    if "answer" in ans.keys():
                        if ans["answer"] is not None:
                            self.view.add_message(ans["answer"],
                                                  "April \uf860", 0, "code")
        elif type == -1:
            self.view.add_message(res, "April \uf860", 0, "text")

        self._work_count -= 1
        if self._work_count < 1:
            self.view.animation.stop(False)

    def configure_ans_count(self, val):
        self.settings["answer_count"] = val

    def configure_res_type(self, val):
        self.settings["all_response"] = val
