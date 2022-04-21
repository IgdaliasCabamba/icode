# TODO: Refactor

from typing import Union
from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QTimer,
    QPropertyAnimation,
    QPoint,
    QEasingCurve,
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
)

from smartlibs.qtmd import HeaderPushButton
from functions import getfn
from .widgets import Notification
from core.char_utils import get_unicon


class Notificator(QFrame):

    on_mode_changed = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("notify")
        self.view = parent
        self.icons = getfn.get_smartcode_icons("notificator")
        self.widget_list = []
        self._editor = None
        self._editor_widget = None
        self._current_editors = []
        self.already_loaded = False
        self.timer = QTimer(self)
        self.timer.singleShot(3600, self.load)
        self.setProperty("displaying", False)
        self.view.resized.connect(self.update_ui)
        self.view.on_editor_changed.connect(self.set_current_editor)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.header_widget = QFrame(self)
        self.header_widget.setObjectName("Header")
        self.header_widget.setFixedHeight(40)

        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(10, 2, 10, 2)

        self.label_info = QLabel("No New Notifications", self.header_widget)
        self.label_info.setSizePolicy(
            QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        )

        self.btn_clear_notifications = HeaderPushButton(self)
        self.btn_clear_notifications.setIcon(self.icons.get_icon("clear"))
        self.btn_clear_notifications.clicked.connect(self.clear_all)

        self.btn_close_panel = HeaderPushButton(self)
        self.btn_close_panel.setIcon(self.icons.get_icon("hide"))
        self.btn_close_panel.clicked.connect(self.close_all)

        self.header_layout.addWidget(self.label_info)
        self.header_layout.addWidget(self.btn_clear_notifications)
        self.header_layout.addWidget(self.btn_close_panel)
        self.header_layout.setAlignment(self.label_info, Qt.AlignLeft)
        self.header_widget.setLayout(self.header_layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("main-area")

        self.widget = QFrame(self)
        self.widget.setObjectName("main-frame")
        self.vbox = QVBoxLayout(self.widget)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(1)
        self.widget.setLayout(self.vbox)

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.setVisible(False)

        self.layout.addWidget(self.header_widget)
        self.layout.setAlignment(self.header_widget, Qt.AlignTop)
        self.layout.addWidget(self.scroll_area)

        self.anim = QPropertyAnimation(self, b"pos")

        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setOffset(0, 2)
        self.drop_shadow.setColor(QColor(0, 0, 0))
        self.setGraphicsEffect(self.drop_shadow)

        self.setFixedWidth(450)
        self.setVisible(False)
        self.update_ui()

    def set_api(self, api):
        self.api = api

    @property
    def current_editors(self):
        return self._current_editors

    @property
    def current_editor(self) -> object:
        return self._editor

    @property
    def current_editor_widget(self) -> object:
        return self._editor_widget

    def set_current_editor(self, editor_widget: object) -> None:
        self._editor_widget = editor_widget
        self._editor = editor_widget.editor
        self._current_editors = editor_widget.editors

    def new_notification(
        self,
        title: str,
        desc: str,
        widgets: list,
        time: Union[int, float] = 10000,
        kill_action: object = None,
    ) -> object:
        if time <= 3600:
            time *= 2
        new_notification = Notification(self, title, desc, widgets, time)
        self.notificate(new_notification)
        if kill_action is not None:
            kill_action.connect(lambda: self.kill(new_notification))
        return new_notification

    def notificate(self, widget: object) -> None:
        self.widget_list.append(widget)
        widget.on_displayed.connect(self.hide_notification)
        self.display_notification(widget)

    def kill(self, notification: object) -> None:
        if notification in self.widget_list:
            self.widget_list.remove(notification)
            notification.clear()
            self.update_ui()

    def clear_all(self):
        for widget in self.widget_list:
            widget.clear()
        self.widget_list.clear()
        self.scroll_area.setVisible(False)
        self.update_ui()

    def close_all(self):
        self.setVisible(False)

    def hide_notification(self, notification):
        if notification in self.widget_list:
            notification.setVisible(False)
            self.update_ui()
            for x in self.widget_list:
                if x.isVisible():
                    return
            self.setVisible(False)
            self.scroll_area.setVisible(False)
            self.setProperty("displaying", False)

    def display_notification(self, notification):
        self.vbox.insertWidget(0, notification)
        self.setProperty("displaying", True)
        if self.already_loaded:
            self.scroll_area.setFocus()
            self.setVisible(True)
        self.scroll_area.setVisible(True)
        self.update_ui()

    @property
    def diplaying_notifications(self):
        active = []
        for x in self.widget_list:
            if x.isVisible():
                active.append(x)
        return active

    def update_position(self):
        y = (
            self.view.geometry().height()
            - self.geometry().height()
            - self.view.status_bar.geometry().height()
            - 10
        )
        w = self.view.geometry().width()
        x = int(w - self.geometry().width()) - 10
        self.move(x, y)

    def update_size(self):
        h = self.scroll_area.minimumSizeHint().height()
        if self.widget_list:
            for x in self.widget_list:
                if x.isVisible():
                    h += x.geometry().height()
        else:
            h = 40

        if h >= self.view.geometry().height() - self.view.geometry().height() / 2:
            h = self.view.geometry().height() - int(self.view.geometry().height() / 2)

        self.setFixedHeight(h)

    def update_ui(self):
        self.update_size()
        self.update_position()
        self.style().polish(self)
        self.update()
        notifications_count = len(self.widget_list)
        if notifications_count <= 0:
            self.label_info.setText("No New Notifications")
        elif notifications_count > 0 and notifications_count <= 9:
            self.label_info.setText(f"{notifications_count} Notifications")
        else:
            self.label_info.setText(f"9{get_unicon('nf', 'mid-plus')}, Notifications")

    def appear(self):
        """Show or hide the Notifications and update the visiblity of notifications"""
        if self.isVisible():
            self.setVisible(False)
            self.update_ui()
        else:
            self.setVisible(True)
            for x in self.widget_list:
                x.setVisible(True)
                self.scroll_area.setVisible(True)
            self.update_ui()
            self.animate()

    def animate(self):
        x = self.geometry().x()
        y = self.geometry().y()
        self.anim.setStartValue(QPoint(x, self.geometry().height() + y))
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim.setEndValue(QPoint(x, y))
        self.anim.setDuration(600)
        self.anim.start()
        self.show()

    def load(self):
        """Loading at first time preparing the widget"""
        self.already_loaded = True
        if self.widget_list:
            self.setVisible(True)
            self.scroll_area.setVisible(True)
        self.update_ui()
