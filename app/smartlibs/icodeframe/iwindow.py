from PyQt5.QtCore import Qt, QMetaObject, pyqtSignal as Signal, pyqtSlot as Slot, QSize
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolButton,
                            QLabel, QDesktopWidget, QSizePolicy)
from ._utils import QT_VERSION, PLATFORM, _FL_STYLESHEET
import system

class WindowDragger(QWidget):
    
    dragMax = Signal()
    doubleClicked = Signal()

    def __init__(self, window, parent=None):
        super().__init__(parent)

        self._window = window
        self._mousePressed = False
        self.setCursor(Qt.ArrowCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def mousePressEvent(self, event):
        self._mousePressed = True
        self._mousePos = event.globalPos()
        self._windowPos = self._window.pos()

    def mouseMoveEvent(self, event):
        if self._mousePressed:
            self.setCursor(Qt.ClosedHandCursor)
            self._window.on_btnRestore_clicked()
            self._window.move(self._windowPos +
                              (event.globalPos() - self._mousePos))
            if self._window.pos().y() < 0:
                self._mousePressed=False
                self.setCursor(Qt.ArrowCursor)
                self.dragMax.emit()

    def mouseReleaseEvent(self, event):
        self._mousePressed = False
        self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class ModernWindow(QWidget):

    def __init__(self, w:object, window_style:str, window_type:str = "window", parent=None):
        super().__init__(parent)
        self.setObjectName("modern-window")
        
        self.icon=None
        self._w = w
        self.window_style = window_style.lower()
        self.window_type = window_type.lower()
        self.main_h_is_pressed=False
        self.main_w_is_pressed=False
        self.allowed_buttons = []
        self.setupUi()

        contentLayout = QHBoxLayout()
        contentLayout.setContentsMargins(0, 0, 0, 0)
        contentLayout.setSpacing(0)
        contentLayout.addWidget(w)

        self.windowContent.setLayout(contentLayout)

        self.setWindowTitle(w.windowTitle())
        self.setGeometry(w.geometry())

        self._w.setAttribute(Qt.WA_DeleteOnClose, True)
        self._w.destroyed.connect(self.__child_was_closed)

        self.border_radius=None

    def setupUi(self):
        self.vboxWindow = QVBoxLayout(self)
        self.vboxWindow.setContentsMargins(0, 0, 0, 0)

        self.windowFrame = QWidget(self)
        self.windowFrame.mouseMoveEvent=self.on_main_move
        self.windowFrame.mousePressEvent=self.on_main_press
        self.windowFrame.mouseReleaseEvent=self.on_main_release
        self.windowFrame.setObjectName('windowFrame')

        self.vboxFrame = QVBoxLayout(self.windowFrame)
        self.vboxFrame.setContentsMargins(0, 0, 0, 0)
        self.vboxFrame.setSpacing(0)

        self.titleBar = WindowDragger(self, self.windowFrame)
        self.titleBar.setObjectName('titleBar')
        self.titleBar.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
                                                QSizePolicy.Fixed))

        self.hboxTitle = QHBoxLayout(self.titleBar)
        self.hboxTitle.setContentsMargins(0, 0, 0, 0)

        self.lblTitle = QLabel('Title')
        self.lblTitle.setObjectName('lblTitle')
        self.lblTitle.setAlignment(Qt.AlignCenter)

        spButtons = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.toolMenu=QToolButton(self.titleBar)
        self.toolMenu.setObjectName("btnMenu")
        self.toolMenu.setIconSize(QSize(20,20))
        self.toolMenu.setPopupMode(QToolButton.DelayedPopup)
        self.toolMenu.clicked.connect(self.on_toolMenu_clicked)
        self.toolMenu.setSizePolicy(spButtons)

        self.btnMinimize = QToolButton(self.titleBar)
        self.btnMinimize.setObjectName('btnMinimize')
        self.btnMinimize.setSizePolicy(spButtons)

        self.btnRestore = QToolButton(self.titleBar)
        self.btnRestore.setObjectName('btnRestore')
        self.btnRestore.setSizePolicy(spButtons)

        self.btnMaximize = QToolButton(self.titleBar)
        self.btnMaximize.setObjectName('btnMaximize')
        self.btnMaximize.setSizePolicy(spButtons)

        self.btnClose = QToolButton(self.titleBar)
        self.btnClose.setObjectName('btnClose')
        self.btnClose.setSizePolicy(spButtons)

        self.vboxFrame.addWidget(self.titleBar)

        self.windowContent = QWidget(self.windowFrame)
        self.vboxFrame.addWidget(self.windowContent)

        self.vboxWindow.addWidget(self.windowFrame)

        if PLATFORM == "Darwin":
            self.hboxTitle.addWidget(self.btnClose)
            self.hboxTitle.addWidget(self.btnMinimize)
            self.hboxTitle.addWidget(self.btnRestore)
            self.hboxTitle.addWidget(self.btnMaximize)
            self.hboxTitle.addWidget(self.lblTitle)
            self.hboxTitle.addWidget(self.toolMenu)
        else:
            self.hboxTitle.addWidget(self.toolMenu)
            self.hboxTitle.addWidget(self.lblTitle)
            self.hboxTitle.addWidget(self.btnMinimize)
            self.hboxTitle.addWidget(self.btnRestore)
            self.hboxTitle.addWidget(self.btnMaximize)
            self.hboxTitle.addWidget(self.btnClose)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setStyleSheet(_FL_STYLESHEET)
        
        if self.window_style == "icode":
            self.setAttribute(Qt.WA_TranslucentBackground)

        # automatically connect slots
        QMetaObject.connectSlotsByName(self)
        self.build_window(self.window_style)
        self.allowed_buttons.append(self.btnClose)
        self.allowed_buttons.append(self.btnMaximize)
        self.allowed_buttons.append(self.btnMinimize)
        self.allowed_buttons.append(self.btnRestore)
    
    def update_window_borders(self, state:str):
        if self.border_radius:
            if state == "max":
                self._w.status_bar.setStyleSheet("#status-bar {border-radius:0}")
                self.titleBar.setStyleSheet("#titleBar {border-radius:0}")
                self.windowFrame.setStyleSheet("#windowFrame {border-radius: 0 0 0 0}")
            elif state == "res":
                self._w.setStyleSheet("#main-window {background-color: transparent;}")
                self._w.status_bar.setStyleSheet("#status-bar {border-bottom-left-radius:7px; border-bottom-right-radius:7px}")
                self.titleBar.setStyleSheet("#titleBar {border-top-left-radius:7px; border-top-right-radius:7px}")
                self.windowFrame.setStyleSheet("#windowFrame {border-radius: 7px 7px 7px 7px}")
    
    def build_window(self, window_style) -> None:
        if window_style == "icode":
            self.border_radius=True
            self._w.setStyleSheet("#main-window {background-color: transparent;}")
            self.windowFrame.setStyleSheet("#windowFrame {border-radius: 7px 7px 7px 7px}")
            self.titleBar.setStyleSheet("#titleBar {border-top-left-radius:7px; border-top-right-radius:7px}")
            self._w.status_bar.setStyleSheet("#status-bar {border-bottom-left-radius:7px; border-bottom-right-radius:7px}")
        elif window_style == "custom":
            self.border_radius=False

    def __child_was_closed(self) -> None:
        self._w = None  # The child was deleted, remove the reference to it and close the parent window
        self.close()
        system.end(0)

    def closeEvent(self, event) -> None:
        if not self._w:
            event.accept()
        else:
            self._w.close()
            event.setAccepted(self._w.isHidden())
    
    def center(self) -> None:
        app_geo = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        app_geo.moveCenter(screen_center)
        self.move(app_geo.topLeft())
    
    def set_allowed_buttons(self, buttons_set:set):
        self.allowed_buttons.clear()
        if "close" in buttons_set:
            self.allowed_buttons.append(self.btnClose)
        else:
            self.btnClose.hide()
        if "min" in buttons_set:
            self.allowed_buttons.append(self.btnMinimize)
        else:
            self.btnMinimize.hide()
        if "max" in buttons_set or "restore" in buttons_set:
            self.allowed_buttons.append(self.btnMaximize)
            self.allowed_buttons.append(self.btnRestore)
        else:pass
        # TODO
        
            
    def set_window_title(self, title:str) -> None:
        self.lblTitle.setText(title)
        
    def setWindowMenu(self, menu) ->None:
        self.toolMenu.setMenu(menu)
    
    def setWindowIcon(self, icon) ->None:
        self.icon=icon
    
    def setMenuIcon(self, icon) -> None:
        self.toolMenu.setIcon(icon)

    def setWindowTitle(self, title) -> None:
        super(ModernWindow, self).setWindowTitle(title)
        self.lblTitle.setText(title)

    def _setWindowButtonState(self, hint, state):
        btns = {
            Qt.WindowCloseButtonHint: self.btnClose,
            Qt.WindowMinimizeButtonHint: self.btnMinimize,
            Qt.WindowMaximizeButtonHint: self.btnMaximize
        }
        button = btns.get(hint)

        maximized = bool(self.windowState() & Qt.WindowMaximized)

        if button == self.btnMaximize:  # special rules for max/restore
            self.btnRestore.setEnabled(state)
            self.btnMaximize.setEnabled(state)

            if maximized:
                self.btnRestore.setVisible(state)
                self.btnMaximize.setVisible(False)
            else:
                self.btnMaximize.setVisible(state)
                self.btnRestore.setVisible(False)
        else:
            button.setEnabled(state)

        allButtons = [self.btnClose, self.btnMinimize, self.btnMaximize, self.btnRestore]
        if True in [b.isEnabled() for b in allButtons]:
            for b in allButtons:
                b.setVisible(True)
            if maximized:
                self.btnMaximize.setVisible(False)
            else:
                self.btnRestore.setVisible(False)
            self.lblTitle.setContentsMargins(0, 0, 0, 0)
        else:
            for b in allButtons:
                b.setVisible(False)
            self.lblTitle.setContentsMargins(0, 2, 0, 0)

    def setWindowFlag(self, Qt_WindowType, on=True):
        buttonHints = [Qt.WindowCloseButtonHint, Qt.WindowMinimizeButtonHint, Qt.WindowMaximizeButtonHint]

        if Qt_WindowType in buttonHints:
            self._setWindowButtonState(Qt_WindowType, on)
        else:
            super().setWindowFlag(Qt_WindowType, on)

    def setWindowFlags(self, Qt_WindowFlags):
        buttonHints = [Qt.WindowCloseButtonHint, Qt.WindowMinimizeButtonHint, Qt.WindowMaximizeButtonHint]
        for hint in buttonHints:
            self._setWindowButtonState(hint, bool(Qt_WindowFlags & hint))

        super().setWindowFlags(Qt_WindowFlags)
    

    @Slot()
    def on_btnMinimize_clicked(self):
        self.setWindowState(Qt.WindowMinimized)

    @Slot()
    def on_btnRestore_clicked(self):
        if self.btnMaximize.isEnabled() or self.btnRestore.isEnabled():
            self.btnRestore.setVisible(False)
            self.btnRestore.setEnabled(False)
            self.btnMaximize.setVisible(True)
            self.btnMaximize.setEnabled(True)

        self.setWindowState(Qt.WindowNoState)
        self.update_window_borders("res")

    @Slot()
    def on_btnMaximize_clicked(self):
        if self.btnMaximize.isEnabled() or self.btnRestore.isEnabled():
            self.btnRestore.setVisible(True)
            self.btnRestore.setEnabled(True)
            self.btnMaximize.setVisible(False)
            self.btnMaximize.setEnabled(False)

        self.setWindowState(Qt.WindowMaximized)
        self.update_window_borders("max")

    @Slot()
    def on_btnClose_clicked(self):
        if self.window_type == "window":
            self.close()
        elif self.window_type == "dialog":
            self.hide()
        else:
            self.close()

    @Slot()
    def on_titleBar_doubleClicked(self):
        if not bool(self.windowState() & Qt.WindowMaximized):
            self.on_btnMaximize_clicked()
        else:
            self.on_btnRestore_clicked()
    
    @Slot()
    def on_titleBar_dragMax(self):
        if not bool(self.windowState() & Qt.WindowMaximized):
            self.on_btnMaximize_clicked()
        else:
            self.on_btnRestore_clicked()

    @Slot()
    def on_toolMenu_clicked(self):
        self.toolMenu.showMenu()
    
    def on_main_move(self, event):
        if self.main_w_is_pressed:
            w=event.pos().x()
            self.resize(w,self.geometry().height())
        
        elif self.main_h_is_pressed:
            h=event.pos().y()
            self.resize(self.geometry().width(),h)

    def on_main_press(self, event):
        maximized = bool(self.windowState() & Qt.WindowMaximized)
        if not maximized:
        
            w,h=event.pos().x(),event.pos().y()
            
            if self.geometry().height() - h < 10:
                self.setCursor(Qt.SizeVerCursor)
                self.main_h_is_pressed=True
            
            elif w <= 10 or self.geometry().width() - w < 10:
                self.setCursor(Qt.SizeHorCursor)
                self.main_w_is_pressed=True
    
    def on_main_release(self, event):
        self.main_is_pressed=False
        self.main_h_is_pressed=False
        self.main_w_is_pressed=False
        self.setCursor(Qt.ArrowCursor)