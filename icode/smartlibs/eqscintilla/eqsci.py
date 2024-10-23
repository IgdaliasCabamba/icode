from typing import Dict, List, Union

from qtpy import QtGui
from qtpy.QtCore import QPoint, Signal
from PyQt5.Qsci import *


from .eqsci_panel_manager import EQsciPanelManager


class EQscintilla(QsciScintilla):
    # on_resized = Signal()
    on_painted = Signal(object)
    on_updated = Signal()
    on_key_pressed = Signal(object)
    on_key_released = Signal(object)
    on_mouse_moved = Signal(object)
    on_mouse_released = Signal(object)
    on_mouse_double_clicked = Signal(object)
    on_text_setted = Signal(str)
    on_mouse_wheel_activated = Signal(object)
    on_chelly_document_changed = Signal(object)
    post_on_key_pressed = Signal(object)


    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._panels_manager = EQsciPanelManager(self)
    
        self._last_mouse_pos = QPoint(0, 0)
        self.__build()

    def __build(self):
        self.setMouseTracking(True)

    def update_state(self):
        self.on_updated.emit()

    def update(self):
        self.update_state()
        return super().update()

    @property
    def panels_manager(self) -> EQsciPanelManager:
        return self._panels_manager

    @panels_manager.setter
    def panels_manager(self, new_manager: EQsciPanelManager) -> EQsciPanelManager:
        if new_manager is EQsciPanelManager:
            self._panels_manager = new_manager(self)
        elif isinstance(new_manager, EQsciPanelManager):
            self._panels_manager = new_manager


    def showEvent(self, event):
        super().showEvent(event)
        self.panels_manager.refresh()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        self.on_painted.emit(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        #self.on_resized.emit()
    
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> Union[None, object]:
        self.on_key_pressed.emit(event)
        super().keyPressEvent(event)
        self.post_on_key_pressed.emit(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        self.on_key_released.emit(event)
        return super().keyReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.on_mouse_wheel_activated.emit(event)
        return super().wheelEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_moved.emit(event)
        self._last_mouse_pos = event.pos()
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_released.emit(event)
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_double_clicked.emit(event)
        return super().mouseDoubleClickEvent(event)

    def setText(self, text: str) -> None:
        self.on_text_setted.emit(text)
        return super().setText(text)