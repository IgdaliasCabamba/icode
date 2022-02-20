# -*- coding: utf-8 -*-

# Small modifications for py3qtermwidget at https://github.com/meramsey/py3qtermwidget 
# Added a simple toolbar and customizable color_map

from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsItem, QScrollBar, QShortcut
from PyQt5.QtCore import QRect, Qt, pyqtSignal
from PyQt5.QtGui import (QClipboard, QPainter, QFont, QBrush, QColor,
                            QPen, QContextMenuEvent)
from .backend import Session
import pyperclip

DEBUG = False
DEFAULT_COLOR_MAP = False

class TerminalWidget(QWidget):
    """ The main Widget """
    keymap = {
            Qt.Key_Backspace: chr(127),
            Qt.Key_Escape: chr(27),
            Qt.Key_AsciiTilde: chr(126),
            Qt.Key_Up: "~A",
            Qt.Key_Down: "~B",
            Qt.Key_Left: "~D",
            Qt.Key_Right: "~C",
            Qt.Key_PageUp: "~1",
            Qt.Key_PageDown: "~2",
            Qt.Key_Home: "~H",
            Qt.Key_End: "~F",
            Qt.Key_Insert: "~3",
            Qt.Key_Delete: "~4",
            Qt.Key_F1: "~a",
            Qt.Key_F2: "~b",
            Qt.Key_F3: "~c",
            Qt.Key_F4: "~d",
            Qt.Key_F5: "~e",
            Qt.Key_F6: "~f",
            Qt.Key_F7: "~g",
            Qt.Key_F8: "~h",
            Qt.Key_F9: "~i",
            Qt.Key_F10: "~j",
            Qt.Key_F11: "~k",
            Qt.Key_F12: "~l",
        }

    session_closed = pyqtSignal()

    def __init__(self, parent=None, command:str=None,
                color_map:dict = DEFAULT_COLOR_MAP, font_name:str="Monospace",
                font_size:int=16) -> None:
        super().__init__(parent)
        
        # Geting the colors from dictionary and passing to lists
        # because the base project use list instead dict
        
        self.past_command = QShortcut("Ctrl+Shift+V", self)
        self.past_command.activated.connect(self.past)
        self.copy_command = QShortcut("Ctrl+Shift+C", self)
        self.copy_command.activated.connect(self.copy)
        
        self.zoom_in_command = QShortcut("Ctrl+-", self)
        self.zoom_in_command.activated.connect(self.zoom_in)
        self.zoom_out_command = QShortcut("Ctrl++", self)
        self.zoom_out_command.activated.connect(self.zoom_out)
        
        self.foreground_color_map = {int(key):str(value) for key,value in color_map["fg"].items()}
        self.background_color_map = {int(key):str(value) for key,value in color_map["bg"].items()}
        
        self.parent().setTabOrder(self, self)
        self.setFocusPolicy(Qt.WheelFocus)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setCursor(Qt.IBeamCursor)
        font = QFont(font_name)
        font.setPixelSize(font_size)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Scrollbar a basic QScrollBar widget in Terminal
        self.scrollBar = QScrollBar(self)
        self.scrollBar.setCursor(Qt.ArrowCursor)
        self.scrollBar.setMinimum(0)
        self.scrollBar.setMaximum(0)
        self.scrollBar.setValue(0)
        self.scrollBar.valueChanged.connect(self.on_scrollbar_value_changed)
        
        # WORK in progress
        self._last_update = None
        self._screen = []
        self._screen_history = []
        self._history_index = 0
        self._history_lines = 1000
        self._text = []
        self._cursor_rect = None
        self._cursor_col = 0
        self._cursor_row = 0
        self._press_pos = None
        self._selection = None
        
        self._session = None
        self._dirty = False
        self._blink = False
        self._clipboard = QApplication.clipboard()
        self.command = command
        
        QApplication.instance().lastWindowClosed.connect(Session.close_all)
        if command is not None and command:
            self.execute(self.command)
            
    def on_scrollbar_value_changed(self, value:int) -> None:
        try:
            """ Changing the _history_index of Terminal to passed value"""
            self._history_index = value
            self.update()
        except Exception as e:
            print("TerminalWidget: ", e)

    def execute(self, command:str) -> object:
        try:
            self._session = Session()
            self._session.start(command)
            self._timer_id = None
            # start timer either with high or low priority
            if self.hasFocus():
                self.focusInEvent(None)
            else:
                self.focusOutEvent(None)
            
            return self._session
        except Exception as e:
            print("TerminalWidget: ", e)
    
    def copy(self):
        try:
            text = self.text_selection()
            if len(text) > 1 and isinstance(text, str):
                pyperclip.copy(text)
        except Exception as e:
            print("TerminalWidget: ", e)
    
    def past(self):
        try:
            text = pyperclip.paste()
            if len(text) > 1 and isinstance(text, str):
                self.send(text.encode("utf-8"))
        except Exception as e:
            print("TerminalWidget: ", e)

    def send(self, s):
        try:
            self._session.write(s)
        except Exception as e:
            print("TerminalWidget: ", e)

    def stop(self):
        try:
            self._session.stop()
        except Exception as e:
            print("TerminalWidget: ", e)

    def pid(self):
        try:
            return self._session.pid()
        except Exception as e:
            print("TerminalWidget: ", e)

    def setFont(self, font):
        try:
            super().setFont(font)
            self._update_metrics()
        except Exception as e:
            print("TerminalWidget: ", e)

    def focusNextPrevChild(self, next):
        try:
            if not self._session.is_alive():
                return True
            return False
        except Exception as e:
            print("TerminalWidget: ", e)

    def focusInEvent(self, event):
        try:
            if not self._session.is_alive():
                return
            if self._timer_id is not None:
                self.killTimer(self._timer_id)
            self._timer_id = self.startTimer(0)#250
            self.update_screen()
        except Exception as e:
            print("TerminalWidget: ", e)

    def focusOutEvent(self, event):
        try:
            if not self._session.is_alive():
                return
            # reduced update interval 
            # -> slower screen updates
            # -> but less load on main app which results in better responsiveness
            if self._timer_id is not None:
                self.killTimer(self._timer_id)
            self._timer_id = self.startTimer(500)#750
        except Exception as e:
            print("TerminalWidget: ", e)

    def resizeEvent(self, event):
        try:
            self._columns, self._rows = self._pixel2pos(self.width() - self.scrollBar.width(), self.height())
            if self._columns > 0 and self._rows > 0:
                self._session.resize(self._columns, self._rows)
        except Exception as e:
            print("TerminalWidget: ", e)
        
        # Adjust the geometry of scrollbar to side right and 16px of width
        self.scrollBar.setGeometry(QRect(self.width() - 16, 0, 16, self.height()))

    def closeEvent(self, event):
        try:
            if not self._session.is_alive():
                return
            self._session.close()
        except Exception as e:
            print("TerminalWidget: ", e)
    
    def store_history(self, lines:int, screen) -> None:
        try:
            """ Save the terminal history and adjust the range of scrollbar"""
            
            self._screen_history.extend(screen[:lines])
            self._history_index = len(self._screen_history)
            
            if self._history_index > self._history_lines:
                index = self._history_index - self._history_lines
                self._screen_history = self._screen_history[index:]
                self._history_index = len(self._screen_history)

            self.scrollBar.setMaximum(self._history_index)
            self.scrollBar.setValue(self._history_index)
        except Exception as e:
            print("TerminalWidget: ", e)

    def timerEvent(self, event):
        try:
            """ get the new screen, paint this and save history"""
            if not self._session.is_alive():
                if self._timer_id is not None:
                    self.killTimer(self._timer_id)
                    self._timer_id = None
                if DEBUG:
                    print("Session closed")
                self.session_closed.emit()
                return
            last_change = self._session.last_change()
            if not last_change:
                return
            if not self._last_update or last_change > self._last_update:
                self._last_update = last_change
                
                old_screen = self._screen
                old_cursor_row = self._cursor_row
                (self._cursor_col, self._cursor_row), self._screen = self._session.dump()
                self._update_cursor_rect()
                
                if old_screen != self._screen:
                    self._dirty = True
                    if old_cursor_row != self._cursor_row:
                        self.store_history(old_cursor_row, old_screen)
            
            # TODO: Nice cursor animations
            if not self.hasFocus():
                self._blink = not self._blink
            self.update()
        except Exception as e:
            print("TerminalWidget: ", e)

    def _update_metrics(self):
        try:
            fm = self.fontMetrics()
            self._char_height = fm.height()
            self._char_width = fm.width("W")
        except Exception as e:
            print("TerminalWidget: ", e)

    def _update_cursor_rect(self):
        try:
            cx, cy = self._pos2pixel(self._cursor_col, self._cursor_row)
            self._cursor_rect = QRect(cx, cy, self._char_width, self._char_height)
        except Exception as e:
            print("TerminalWidget: ", e)

    def _reset(self):
        try:
            self._update_metrics()
            self._update_cursor_rect()
            self.resizeEvent(None)
            self.update_screen()
        except Exception as e:
            print("TerminalWidget: ", e)

    def update_screen(self):
        try:
            self._dirty = True
            self.update()
        except Exception as e:
            print("TerminalWidget: ", e)
    
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            self._paint_screen(painter)
            if self._cursor_rect is not None and self.scrollBar.maximum() == self._history_index:
                self._paint_cursor(painter)
            if self._selection:
                self._paint_selection(painter)
        except Exception as e:
            print("TerminalWidget: ", e)

    def _pixel2pos(self, x, y):
        try:
            col = int(round(x / self._char_width))
            row = int(round(y / self._char_height))
            return col, row
        except Exception as e:
            print("TerminalWidget: ", e)

    def _pos2pixel(self, col, row):
        try:
            x = col * self._char_width
            y = row * self._char_height
            return x, y
        except Exception as e:
            print("TerminalWidget: ", e)

    def _paint_cursor(self, painter):
        try:
            if self._blink and not self.hasFocus():
                color = "#aaa"
            else:
                color = "#fff"
                
            if painter != None:
                painter.setPen(QPen(QColor(color)))
                painter.drawRect(self._cursor_rect)
        except Exception as e:
            print("TerminalWidget: ", e)

    def _paint_screen(self, painter):
        try:
            # Speed hacks: local name lookups are faster
            vars().update(QColor=QColor, QBrush=QBrush, QPen=QPen, QRect=QRect)
            
            background_color_map = self.background_color_map
            foreground_color_map = self.foreground_color_map
            
            char_width = self._char_width
            char_height = self._char_height
            painter_drawText = painter.drawText
            painter_fillRect = painter.fillRect
            painter_setPen = painter.setPen
            painter_setFont = painter.setFont
            align = Qt.AlignTop | Qt.AlignLeft
            # set defaults
            background_color = background_color_map[14]
            foreground_color = foreground_color_map[15]
            brush = QBrush(QColor(background_color))
            painter_fillRect(self.rect(), brush)
            pen = QPen(QColor(foreground_color))
            painter_setPen(pen)
            y = 0
            text = []
            viewscreen = (self._screen_history + self._screen)[self._history_index:self._history_index + len(self._screen)]
            
            for row, line in enumerate(viewscreen):
                col = 0
                text_line = ""
                for item in line:
                    if isinstance(item, str):
                        x = col * char_width
                        length = len(item)
                        rect = QRect(x, y, x + char_width * length, y + char_height)
                        painter_fillRect(rect, brush)
                        painter_drawText(rect, align, item)
                        col += length
                        text_line += item
                    else:
                        foreground_color_idx, background_color_idx, underline_flag = item
                        foreground_color = foreground_color_map[foreground_color_idx]
                        background_color = background_color_map[background_color_idx]
                        pen = QPen(QColor(foreground_color))
                        brush = QBrush(QColor(background_color))
                        painter_setPen(pen)
                    
                # Clear last column            
                rect = QRect(col * char_width, y, self.width(), y + char_height)
                brush = QBrush(QColor(background_color))
                painter_fillRect(rect, brush)
                
                y += char_height
                text.append(text_line)

            # Store text
            self._text = text
            
            # Clear last lines
            rect = QRect(0, y, self.width(), self.height())
            brush = QBrush(QColor(background_color))
            painter_fillRect(rect, brush)
        except Exception as e:
            print("TerminalWidget: ", e)

    def _paint_selection(self, painter):
        try:
            pcol = QColor(200, 200, 200, 50)
            pen = QPen(pcol)
            bcol = QColor(230, 230, 230, 50)
            brush = QBrush(bcol)
            painter.setPen(pen)
            painter.setBrush(brush)
            for (start_col, start_row, end_col, end_row) in self._selection:
                x, y = self._pos2pixel(start_col, start_row)
                width, height = self._pos2pixel(end_col - start_col, end_row - start_row)
                rect = QRect(x, y, width, height)
                painter.fillRect(rect, brush)
        except Exception as e:
            print("TerminalWidget: ", e)

    def zoom_in(self):
        try:
            font = self.font()
            font.setPixelSize(font.pixelSize() + 2)
            self.setFont(font)
            self._reset()
        except Exception as e:
            print("TerminalWidget: ", e)

    def zoom_out(self):
        try:
            font = self.font()
            font.setPixelSize(font.pixelSize() - 2)
            self.setFont(font)
            self._reset()
        except Exception as e:
            print("TerminalWidget: ", e)

    return_pressed = pyqtSignal()
    
    # TODO: allow to user use utf-8 text!
    def keyPressEvent(self, event):
        try:
            text = str(event.text())
            key = event.key()
            modifiers = event.modifiers()
            ctrl = modifiers == Qt.ControlModifier
                    
            if text and key != Qt.Key_Backspace:
                self.send(text.encode("utf-8"))
            else:
                s = self.keymap.get(key)
                if s:
                    self.send(s.encode("utf-8"))
                elif DEBUG:
                    print("Unknown key combination")
                    print("Modifiers:", modifiers)
                    print("Key:", key)
                    for name in dir(Qt):
                        if not name.startswith("Key_"):
                            continue
                        value = getattr(Qt, name)
                        if value == key:
                            print("Symbol: Qt.%s" % name)
                    print("Text: %r" % text)
            event.accept()
            if key in (Qt.Key_Enter, Qt.Key_Return):
                self.return_pressed.emit()
        except Exception as e:
            print("TerminalWidget: ", e)

    def mousePressEvent(self, event):
        try:
            button = event.button()
            if button == Qt.RightButton:
                ctx_event = QContextMenuEvent(QContextMenuEvent.Mouse, event.pos())
                self.contextMenuEvent(ctx_event)
                self._press_pos = None
            elif button == Qt.LeftButton:
                self._press_pos = event.pos()
                self._selection = None
                self.update_screen()
            elif button == Qt.MiddleButton:
                self._press_pos = None
                self._selection = None
                text = str(self._clipboard.text(QClipboard.Selection))
                self.send(text.encode("utf-8"))
                # self.update_screen()
        except Exception as e:
            print("TerminalWidget: ", e)

    def mouseReleaseEvent(self, QMouseEvent):
        pass  # self.update_screen()

    def _selection_rects(self, start_pos, end_pos):
        try:
            sx, sy = start_pos.x(), start_pos.y()
            start_col, start_row = self._pixel2pos(sx, sy)
            ex, ey = end_pos.x(), end_pos.y()
            end_col, end_row = self._pixel2pos(ex, ey)
            if start_row == end_row:
                if ey > sy or end_row == 0:
                    end_row += 1
                else:
                    end_row -= 1
            if start_col == end_col:
                if ex > sx or end_col == 0:
                    end_col += 1
                else:
                    end_col -= 1
            if start_row > end_row:
                start_row, end_row = end_row, start_row
            if start_col > end_col:
                start_col, end_col = end_col, start_col
            if end_row - start_row == 1:
                return [(start_col, start_row, end_col, end_row)]
            else:
                return [
                    (start_col, start_row, self._columns, start_row + 1),
                    (0, start_row + 1, self._columns, end_row - 1),
                    (0, end_row - 1, end_col, end_row)
                ]
        except Exception as e:
            print("TerminalWidget: ", e)

    def text(self, rect=None):
        try:
            if rect is None:
                return "\n".join(self._text)
            else:
                text = []
                (start_col, start_row, end_col, end_row) = rect
                for row in range(start_row, end_row):
                    text.append(self._text[row][start_col:end_col])
                return text
        except Exception as e:
            print("TerminalWidget > text: ", e)

    def text_selection(self):
        try:
            text = []
            for (start_col, start_row, end_col, end_row) in self._selection:
                for row in range(start_row, end_row):
                    text.append(self._text[row][start_col:end_col])
            return "\n".join(text)
        except Exception as e:
            print("TerminalWidget: ", e)

    def column_count(self):
        return self._columns

    def row_count(self):
        return self._rows

    def mouseMoveEvent(self, event):
        try:
            if self._press_pos:
                move_pos = event.pos()
                self._selection = self._selection_rects(self._press_pos, move_pos)

                sel = self.text_selection()
                if DEBUG:
                    print("%r copied to xselection" % sel)
                self._clipboard.setText(sel, QClipboard.Selection)

                self.update_screen()
        except Exception as e:
            print("TerminalWidget: ", e)

    def mouseDoubleClickEvent(self, event):
        try:
            self._press_pos = None
            # double clicks create a selection for the word under the cursor
            pos = event.pos()
            x, y = pos.x(), pos.y()
            col, row = self._pixel2pos(x, y)
            line = self._text[row]
            # find start of word
            start_col = col
            found_left = 0
            while start_col > 0:
                char = line[start_col]
                if not char.isalnum() and char not in ("_",):
                    found_left = 1
                    break
                start_col -= 1
            # find end of word
            end_col = col
            found_right = 0
            while end_col < self._columns:
                char = line[end_col]
                if not char.isalnum() and char not in ("_",):
                    found_right = 1
                    break
                end_col += 1
            self._selection = [(start_col + found_left, row, end_col - found_right + 1, row + 1)]

            sel = self.text_selection()
            if DEBUG:
                print("%r copied to xselection" % sel)
            self._clipboard.setText(sel, QClipboard.Selection)
            
            self.update_screen()
        except Exception as e:
            print("TerminalWidget: ", e)

    def inputMethodEvent(self, event):
        try:
            super().inputMethodEvent(event)
            
            text=event.commitString()
            self.send(text.encode("utf-8"))
            
        except Exception as e:
            print("TerminalWidget: ", e)
    
    def is_alive(self):
        try:
            return (self._session and self._session.is_alive()) or False
        except Exception as e:
            print("TerminalWidget: ", e)