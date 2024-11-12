from PyQt5.QtCore import QMetaObject, QSize, Qt
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .style import WINDOW_STYLESHEET

MIN_HORIZONTAL_HANDLER_DISTANCE = 10
MIN_VERTICAL_HANDLER_DISTANCE = 10


class WindowDragger(QWidget):

    drag_max = Signal()
    double_clicked = Signal()

    def __init__(self, window, parent=None):
        super().__init__(parent)

        self._window = window
        self._mouse_pressed = False
        self.setCursor(Qt.ArrowCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def mousePressEvent(self, event):
        self._mouse_pressed = True
        self._mouse_pos = event.globalPos()
        self._window_pos = self._window.pos()

    def mouseMoveEvent(self, event):
        if self._mouse_pressed:
            self.setCursor(Qt.ClosedHandCursor)
            self._window.on_btn_restore_clicked()
            self._window.move(self._window_pos +
                              (event.globalPos() - self._mouse_pos))
            if self._window.pos().y() < 0:
                self._mouse_pressed = False
                self.setCursor(Qt.ArrowCursor)
                self.drag_max.emit()

    def mouseReleaseEvent(self, event):
        self._mouse_pressed = False
        self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()


class ModernWindow(QWidget):

    def __init__(
        self,
        w: object,
        window_controls_pos: int = 1,
        window_type: str = "window",
        parent=None,
        extra_buttons_right: list = [],
        extra_buttons_left: list = [],
    ) -> None:
        super().__init__(parent)
        self.setObjectName("modern-window")

        self.icon = None
        self._w = w
        self.window_controls_pos = window_controls_pos
        self.window_type = window_type.lower()
        self.extra_buttons_right = extra_buttons_right
        self.extra_buttons_left = extra_buttons_left
        self.is_vertical_handler = False
        self.is_horizontal_handler = False
        self.init_ui()

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(w)

        self.window_content.setLayout(content_layout)

        self.set_window_title(w.windowTitle())
        self.setGeometry(w.geometry())

        self._w.setAttribute(Qt.WA_DeleteOnClose, True)
        self._w.destroyed.connect(self.__child_was_closed)

    def init_ui(self):
        self.vbox_window = QVBoxLayout(self)
        self.vbox_window.setContentsMargins(0, 0, 0, 0)

        self.window_frame = QWidget(self)
        self.window_frame.mouseMoveEvent = self.on_main_move
        self.window_frame.mousePressEvent = self.on_main_press
        self.window_frame.mouseReleaseEvent = self.on_main_release
        self.window_frame.setObjectName("window-frame")

        self.vbox_frame = QVBoxLayout(self.window_frame)
        self.vbox_frame.setContentsMargins(0, 0, 0, 0)
        self.vbox_frame.setSpacing(0)

        self.title_bar = WindowDragger(self, self.window_frame)
        self.title_bar.setObjectName("title-bar")
        self.title_bar.setSizePolicy(
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))

        self.hbox_title = QHBoxLayout(self.title_bar)
        self.hbox_title.setContentsMargins(0, 0, 0, 0)

        self.lbl_title = QLabel("Title")
        self.lbl_title.setObjectName("lbl-title")
        self.lbl_title.setAlignment(Qt.AlignCenter)

        size_policy_buttons = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.tool_menu = QToolButton(self.title_bar)
        self.tool_menu.setObjectName("btn-menu")
        self.tool_menu.setIconSize(QSize(20, 20))
        self.tool_menu.setPopupMode(QToolButton.DelayedPopup)
        self.tool_menu.clicked.connect(self.on_tool_menu_clicked)
        self.tool_menu.setSizePolicy(size_policy_buttons)

        self.btn_minimize = QToolButton(self.title_bar)
        self.btn_minimize.setObjectName("btn-minimize")
        self.btn_minimize.setSizePolicy(size_policy_buttons)

        self.btn_restore = QToolButton(self.title_bar)
        self.btn_restore.setObjectName("btn-restore")
        self.btn_restore.setSizePolicy(size_policy_buttons)

        self.btn_maximize = QToolButton(self.title_bar)
        self.btn_maximize.setObjectName("btn-maximize")
        self.btn_maximize.setSizePolicy(size_policy_buttons)

        self.btn_close = QToolButton(self.title_bar)
        self.btn_close.setObjectName("btn-close")
        self.btn_close.setSizePolicy(size_policy_buttons)

        for lbtn in self.extra_buttons_left:
            lbtn.setSizePolicy(size_policy_buttons)
        for rbtn in self.extra_buttons_right:
            rbtn.setSizePolicy(size_policy_buttons)

        self.vbox_frame.addWidget(self.title_bar)

        self.window_content = QWidget(self.window_frame)
        self.vbox_frame.addWidget(self.window_content)

        self.vbox_window.addWidget(self.window_frame)

        if self.window_controls_pos == 0:
            self.hbox_title.addWidget(self.btn_close)
            self.hbox_title.addWidget(self.btn_minimize)
            self.hbox_title.addWidget(self.btn_restore)
            self.hbox_title.addWidget(self.btn_maximize)

            for lbtn in self.extra_buttons_left:
                self.hbox_title.addWidget(lbtn)

            self.hbox_title.addWidget(self.lbl_title)

            for rbtn in self.extra_buttons_rigth:
                self.hbox_title.addWidget(rbtn)

            self.hbox_title.addWidget(self.tool_menu)

        else:
            self.hbox_title.addWidget(self.tool_menu)

            for lbtn in self.extra_buttons_left:
                self.hbox_title.addWidget(lbtn)

            self.hbox_title.addWidget(self.lbl_title)

            for rbtn in self.extra_buttons_right:
                self.hbox_title.addWidget(rbtn)

            self.hbox_title.addWidget(self.btn_minimize)
            self.hbox_title.addWidget(self.btn_restore)
            self.hbox_title.addWidget(self.btn_maximize)
            self.hbox_title.addWidget(self.btn_close)

        self.set_window_flags(Qt.Window
                              | Qt.FramelessWindowHint
                              | Qt.WindowSystemMenuHint
                              | Qt.WindowCloseButtonHint
                              | Qt.WindowMinimizeButtonHint
                              | Qt.WindowMaximizeButtonHint)

        self.setStyleSheet(WINDOW_STYLESHEET)

        self.btn_close.clicked.connect(self.on_btn_close_clicked)
        self.btn_restore.clicked.connect(self.on_btn_restore_clicked)
        self.btn_minimize.clicked.connect(self.on_btn_minimize_clicked)
        self.btn_maximize.clicked.connect(self.on_btn_maximize_clicked)
        self.title_bar.drag_max.connect(self.on_title_bar_drag_max)
        self.title_bar.double_clicked.connect(self.on_title_bar_double_clicked)

    def __child_was_closed(self) -> None:
        self._w = None  # The child was deleted, remove the reference to it and close the parent window
        self.close()

    def closeEvent(self, event) -> None:
        if not self._w:
            event.accept()
        else:
            self._w.close()
            event.setAccepted(self._w.isHidden())

    def centralize(self) -> None:
        app_geo = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        app_geo.moveCenter(screen_center)
        self.move(app_geo.topLeft())

    def set_window_title(self, title: str) -> None:
        self.lbl_title.setText(title)

    def set_window_menu(self, menu) -> None:
        self.tool_menu.setMenu(menu)

    def set_window_icon(self, icon) -> None:
        self.icon = icon

    def set_menu_icon(self, icon) -> None:
        self.tool_menu.setIcon(icon)

    def set_title(self, title) -> None:
        super().setWindowTitle(title)
        self.lbl_title.setText(title)

    def _set_window_button_state(self, hint, state):
        btns = {
            Qt.WindowCloseButtonHint: self.btn_close,
            Qt.WindowMinimizeButtonHint: self.btn_minimize,
            Qt.WindowMaximizeButtonHint: self.btn_maximize,
        }
        button = btns.get(hint)

        maximized = bool(self.windowState() & Qt.WindowMaximized)

        if button == self.btn_maximize:  # special rules for max/restore
            self.btn_restore.setEnabled(state)
            self.btn_maximize.setEnabled(state)

            if maximized:
                self.btn_restore.setVisible(state)
                self.btn_maximize.setVisible(False)
            else:
                self.btn_maximize.setVisible(state)
                self.btn_restore.setVisible(False)
        else:
            button.setEnabled(state)

        allButtons = [
            self.btn_close,
            self.btn_minimize,
            self.btn_maximize,
            self.btn_restore,
        ]
        if True in [b.isEnabled() for b in allButtons]:
            for b in allButtons:
                b.setVisible(True)
            if maximized:
                self.btn_maximize.setVisible(False)
            else:
                self.btn_restore.setVisible(False)
            self.lbl_title.setContentsMargins(0, 0, 0, 0)
        else:
            for b in allButtons:
                b.setVisible(False)
            self.lbl_title.setContentsMargins(0, 2, 0, 0)

    def set_window_flag(self, Qt_WindowType, on=True):
        buttonHints = [
            Qt.WindowCloseButtonHint,
            Qt.WindowMinimizeButtonHint,
            Qt.WindowMaximizeButtonHint,
        ]

        if Qt_WindowType in buttonHints:
            self._set_window_button_state(Qt_WindowType, on)
        else:
            super().setWindowFlag(Qt_WindowType, on)

    def set_window_flags(self, Qt_WindowFlags):
        buttonHints = [
            Qt.WindowCloseButtonHint,
            Qt.WindowMinimizeButtonHint,
            Qt.WindowMaximizeButtonHint,
        ]
        for hint in buttonHints:
            self._set_window_button_state(hint, bool(Qt_WindowFlags & hint))

        super().setWindowFlags(Qt_WindowFlags)

    def on_btn_minimize_clicked(self):
        self.setWindowState(Qt.WindowMinimized)

    def on_btn_restore_clicked(self):
        if self.btn_maximize.isEnabled() or self.btn_restore.isEnabled():
            self.btn_restore.setVisible(False)
            self.btn_restore.setEnabled(False)
            self.btn_maximize.setVisible(True)
            self.btn_maximize.setEnabled(True)

        self.setWindowState(Qt.WindowNoState)

    def on_btn_maximize_clicked(self):
        if self.btn_maximize.isEnabled() or self.btn_restore.isEnabled():
            self.btn_restore.setVisible(True)
            self.btn_restore.setEnabled(True)
            self.btn_maximize.setVisible(False)
            self.btn_maximize.setEnabled(False)

        self.setWindowState(Qt.WindowMaximized)

    def on_btn_close_clicked(self):
        if self.window_type == "window":
            self.close()
        elif self.window_type == "dialog":
            self.hide()
        else:
            self.close()

    def on_title_bar_double_clicked(self):
        if not bool(self.windowState() & Qt.WindowMaximized):
            self.on_btn_maximize_clicked()
        else:
            self.on_btn_restore_clicked()

    def on_title_bar_drag_max(self):
        if not bool(self.windowState() & Qt.WindowMaximized):
            self.on_btn_maximize_clicked()
        else:
            self.on_btn_restore_clicked()

    def on_tool_menu_clicked(self):
        self.tool_menu.showMenu()

    def on_main_move(self, event):
        if self.is_horizontal_handler:
            w = event.pos().x()
            self.resize(w, self.geometry().height())

        elif self.is_vertical_handler:
            h = event.pos().y()
            self.resize(self.geometry().width(), h)

    def on_main_press(self, event):
        maximized = bool(self.windowState() & Qt.WindowMaximized)
        if not maximized:

            w, h = event.pos().x(), event.pos().y()

            if self.geometry().height() - h < MIN_VERTICAL_HANDLER_DISTANCE:
                self.setCursor(Qt.SizeVerCursor)
                self.is_vertical_handler = True

            elif w <= MIN_HORIZONTAL_HANDLER_DISTANCE or self.geometry().width(
            ) - w < MIN_HORIZONTAL_HANDLER_DISTANCE:
                self.setCursor(Qt.SizeHorCursor)
                self.is_horizontal_handler = True

    def on_main_release(self, event):
        self.is_vertical_handler = False
        self.is_horizontal_handler = False
        self.setCursor(Qt.ArrowCursor)
