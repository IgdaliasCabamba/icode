from typing import Dict, List, Union

from qtpy import QtGui
from qtpy.QtCore import QPoint, Signal
from PyQt5.Qsci import *


from .eqsci_panel_manager import EQsciPanelManager


class EQscintilla(QsciScintilla):
    # on_resized = Signal()
    on_key_pressed = Signal(object)
    on_key_released = Signal(object)
    on_text_setted = Signal(str)
    on_mouse_wheel_activated = Signal(object)
    on_mouse_stoped = Signal(int, int, int)
    on_mouse_moved = Signal(object)
    on_mouse_pressed = Signal(object)
    on_mouse_released = Signal(object)
    on_mouse_double_clicked = Signal(object) 
    on_cursor_pos_chnaged = Signal(int, int)
    on_lines_changed = Signal(int)
    on_selected = Signal(int, int, int, int)
    on_highlight_sel_request = Signal(int, int, int, int, bool, str, int,
                                          str)
    on_highlight_match_request = Signal(int, int, bool, str, int, str)
    on_focused = Signal(object, object)
    on_unfocused = Signal(object, object)
    on_resized = Signal(object)
    on_style_changed = Signal(object)
    on_lexer_changed = Signal(object)
    on_word_added = Signal()
    on_modify_key = Signal()
    on_text_changed = Signal()
    on_document_changed = Signal(object)
    on_saved = Signal(str)
    on_abcd_added = Signal()
    on_complete = Signal(dict)
    on_close_char = Signal(str)
    on_intellisense = Signal(object, str)
    on_clear_annotation = Signal(list, int, str)
    on_painted = Signal(object)
    on_updated = Signal()

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
        self.on_resized.emit(event)
    
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> Union[None, object]:
        self.on_key_pressed.emit(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        self.on_key_released.emit(event)
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.on_mouse_wheel_activated.emit(event)
        super().wheelEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_moved.emit(event)
        self._last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_pressed.emit(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_released.emit(event)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        self.on_mouse_double_clicked.emit(event)
        super().mouseDoubleClickEvent(event)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        super().focusInEvent(event)
        self.on_focused.emit(event, self)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super().focusOutEvent(event)
        self.on_unfocused.emit(event, self)

    def setText(self, text: str) -> None:
        self.on_text_setted.emit(text)
        return super().setText(text)