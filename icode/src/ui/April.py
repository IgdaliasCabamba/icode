from PyQt5.QtCore import (QEasingCurve, QPoint, QPropertyAnimation, QTimer,
                          pyqtSignal)
from PyQt5.QtGui import QColor
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (QButtonGroup, QFormLayout, QFrame,
                             QGraphicsDropShadowEffect, QLabel, QPushButton,
                             QRadioButton, QTabWidget, QVBoxLayout)
from qtwidgets import AnimatedToggle

import base.consts as iconsts
from data import april_cache
from functions import getfn


class April(QFrame):

    on_mode_changed = pyqtSignal(int)
    on_notify = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("April")
        self.parent = parent
        self.parent.resized.connect(self.update_ui)
        self.icons = getfn.get_smartcode_icons("April")
        self.mode = iconsts.APRIL.SMART
        self.water_timer = QTimer(self)
        self.water_timer.start(7000)  # 15 min = 900000
        self.water_timer.timeout.connect(self.alert_water)
        self.posture_timer = QTimer(self)
        self.posture_timer.timeout.connect(self.alert_posture)
        self.posture_timer.start(7000)  # 15 min = 900000

        self.mode_values = {
            "opt_full": iconsts.APRIL.FULL,
            "opt_low": iconsts.APRIL.LOW,
            "opt_smart": iconsts.APRIL.SMART,
        }
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.svg_widget = QSvgWidget(self.icons.get_path("produtivity"))
        self.svg_widget.setMaximumHeight(400)

        self.btn_group = QButtonGroup(self)

        self.power_label = QLabel(
            """<h2><span style="color:#11f2c8">\uf2dd&nbsp;</span><span style="color:#48cdd0">I</span><span style="color:#74afd6">c</span><span style="color:#9897db">o</span><span style="color:#c876e2">d</span><span style="color:#f458e8">e</span>&nbsp;<span style="color:#eb58eb">p</span><span style="color:#e158ed">o</span><span style="color:#db58ef">w</span><span style="color:#d458f1">e</span><span style="color:#c958f4">r</span></h2>"""
        )

        self.opt_full = QRadioButton("Full Power", self)
        self.opt_full.setObjectName("opt_full")
        self.opt_low = QRadioButton("Low Power", self)
        self.opt_low.setObjectName("opt_low")
        self.opt_smart = QRadioButton("Smart Mode", self)
        self.opt_smart.setObjectName("opt_smart")
        self.opt_smart.setChecked(True)

        self.btn_group.addButton(self.opt_low)
        self.btn_group.addButton(self.opt_full)
        self.btn_group.addButton(self.opt_smart)
        self.btn_group.buttonClicked.connect(self.change_mode)

        self.form = QFormLayout()

        self.remember_drink_water = AnimatedToggle(
            checked_color="#FFB000", pulse_checked_color="#44FFB000")
        self.remember_correct_posture = AnimatedToggle(
            checked_color="#FFB000", pulse_checked_color="#44FFB000")
        self.remember_drink_water.setMaximumWidth(70)
        self.remember_correct_posture.setMaximumWidth(70)

        self.remember_label = QLabel(
            """<h2><span style="color:#11f2c8">\uf59d&nbsp;</span><span style="color:#48cdd0">R</span><span style="color:#74afd6">e</span><span style="color:#9897db">m</span><span style="color:#c876e2">e</span><span style="color:#f458e8">m</span><span style="color:#eb58eb">b</span><span style="color:#e158ed">e</span><span style="color:#db58ef">r</span>&nbsp;<span style="color:#d458f1">m</span><span style="color:#c958f4">e</span></h2>"""
        )
        self.form.addRow("Drink water", self.remember_drink_water)
        self.form.addRow("Right posture", self.remember_correct_posture)

        self.layout.addWidget(self.svg_widget)
        self.layout.addWidget(self.power_label)
        self.layout.addWidget(self.opt_low)
        self.layout.addWidget(self.opt_full)
        self.layout.addWidget(self.opt_smart)
        self.layout.addWidget(self.remember_label)
        self.layout.addLayout(self.form)

        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setOffset(0, -1)
        self.drop_shadow.setColor(QColor(0, 0, 0))
        self.setGraphicsEffect(self.drop_shadow)

        self.anim = QPropertyAnimation(self, b"pos")

        self.setFixedWidth(400)
        self.setMinimumHeight(600)
        self.hide()

    def alert_water(self):
        if self.remember_drink_water.isChecked():
            btn_thanks = QPushButton("Thanks")
            self.parent.notificator.new_notification(title="Your health",
                                                     desc=f"Drink Water please",
                                                     widgets=[btn_thanks],
                                                     kill_action=btn_thanks.clicked)

    def alert_posture(self):
        if self.remember_correct_posture.isChecked():
            btn_thanks = QPushButton("Thanks")
            self.parent.notificator.new_notification(title="Your health",
                                                     desc=f"Right your posture please",
                                                     widgets=[btn_thanks],
                                                     kill_action=btn_thanks.clicked)

    def change_mode(self, btn):
        self.mode = self.mode_values[btn.objectName()]
        self.on_mode_changed.emit(self.mode)

    def update_position(self):
        y = (self.parent.geometry().height() - self.geometry().height()) - self.parent.status_bar.geometry().height() - 10
        w = self.parent.geometry().width() / 2
        x = int(w - self.geometry().width() / 2)
        self.move(x, y)
        return x, y

    def update_size(self):
        pass

    def update_ui(self):
        self.update_position()
        self.update_size()
        self.update()

    def appear(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.animate()

    def animate(self):
        x = self.geometry().x()
        y = self.geometry().y()
        self.anim.setStartValue(QPoint(x, self.geometry().height() + y))
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim.setEndValue(QPoint(x, y))
        self.anim.setDuration(1200)
        self.anim.start()
