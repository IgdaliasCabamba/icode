import core.consts as iconsts
from core.char_utils import get_unicon
from data import april_cache
from functions import getfn
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QPushButton


class AprilController(QObject):

    on_mode_changed = pyqtSignal(int)
    on_notify = pyqtSignal(object)

    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view

        self.mode_values = {
            "opt_full": iconsts.APRIL.FULL,
            "opt_low": iconsts.APRIL.LOW,
            "opt_smart": iconsts.APRIL.SMART,
        }
        self.run()

    def run(self):

        self.mode = iconsts.APRIL.SMART
        self.water_timer = QTimer(self)
        self.water_timer.start(7000)  # 15 min = 900000
        self.water_timer.timeout.connect(self.alert_water)
        self.posture_timer = QTimer(self)
        self.posture_timer.timeout.connect(self.alert_posture)
        self.posture_timer.start(7000)  # 15 min = 900000

        self.view.btn_group.buttonClicked.connect(self.change_mode)

    def change_mode(self, btn):
        self.mode = self.mode_values[btn.objectName()]
        self.on_mode_changed.emit(self.mode)

    def alert_water(self):
        if self.view.remember_drink_water.isChecked():
            btn_thanks = QPushButton("Thanks")
            self.application_core.notificator.new_notification(
                title="Your health",
                desc=f"Drink Water please",
                widgets=[btn_thanks],
                kill_action=btn_thanks.clicked,
            )

    def alert_posture(self):
        if self.view.remember_correct_posture.isChecked():
            btn_thanks = QPushButton("Thanks")
            self.application_core.notificator.new_notification(
                title="Your health",
                desc=f"Right your posture please",
                widgets=[btn_thanks],
                kill_action=btn_thanks.clicked,
            )
