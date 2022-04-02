from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSplitter, QScrollBar, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.Qsci import *
from . import iconsts

class MiniMap(QsciScintilla):
    def __init__(self, editor, parent) -> None:
        super().__init__(parent)
        self.editor=editor
        self.parent=parent
        self.build()
    
    def build(self):
        self.setColor(self.editor.color())
        self.setPaper(self.editor.paper())
        self.setFont(self.editor.font())

        self.SendScintilla(QsciScintilla.SCI_SETCARETSTYLE, False)
        self.SendScintilla(QsciScintilla.SCI_SETBUFFEREDDRAW, False)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, False)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, False)
        self.zoomTo(iconsts.MINIMAP_MINIMUM_ZOOM)
        self.SendScintilla(QsciScintilla.SCI_SETREADONLY, True)
        self.SendScintilla(QsciScintilla.SCI_HIDESELECTION, True)
        self.SendScintilla(QsciScintilla.SCI_SETCURSOR, iconsts.MINIMAP_CURSOR)
        self.setExtraAscent(iconsts.MINIMAP_EXTRA_ASCENT)
        self.setExtraDescent(iconsts.MINIMAP_EXTRA_DESCENT)
        
        self.indicatorDefine(QsciScintilla.StraightBoxIndicator, 1)
        self.indicatorDefine(QsciScintilla.FullBoxIndicator, 2)
        self.indicatorDefine(QsciScintilla.FullBoxIndicator, 3)
        self.indicatorDefine(QsciScintilla.TextColorIndicator, 4)
        self.setIndicatorForegroundColor(QColor("red"), 1)
        self.setIndicatorForegroundColor(QColor(52, 143, 235, 150), 2)
        self.setIndicatorForegroundColor(QColor(52, 143, 235, 25), 3)
        self.setIndicatorForegroundColor(QColor("#5387e0"), 4)
        self.setIndicatorHoverStyle(QsciScintilla.ThinCompositionIndicator, 4)
        self.setIndicatorHoverForegroundColor(QColor("#5387e0"), 4)

        for i in range(1, 5):
            self.SendScintilla(
                QsciScintilla.SCI_MARKERDEFINE, i, QsciScintilla.SC_MARK_EMPTY)
        self.SendScintilla(QsciScintilla.SCI_SETMARGINWIDTHN, 1, 0)

        self.setMouseTracking(True)
        self.setCaretLineVisible(True)

        self.slider = SliderArea(self)
        self.slider.show()

        self.setFixedWidth(iconsts.MINIMAP_FIXED_WIDTH)
    
    def clear_lexer(self):
        if self.lexer() != None:
            self.lexer().deleteLater()
            self.lexer().setParent(None)
            self.setLexer(None)
            self.clearFolds()
            self.clearAnnotations()
            self.SendScintilla(QsciScintilla.SCI_CLEARDOCUMENTSTYLE)
    
    def set_lexer(self, lexer):
        self.clear_lexer()
        self.setLexer(lexer)
    
    def update_scrollbar_value(self, value):
        self.verticalScrollBar().setValue(value)
        
    def on_mouse_enter(self):
        self.slider.change_transparency(iconsts.MINIMAP_SLIDER_OPACITY_MID)

    def on_mouse_leave(self):
        self.slider.change_transparency(iconsts.MINIMAP_SLIDER_OPACITY_MIN)

    def line_from_position(self, point):
        position = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT,
                                      point.x(), point.y())
        return self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, position)
    
    def scroll_area(self, pos_parent, line_area):
        line = self.line_from_position(pos_parent)
        self.editor.verticalScrollBar().setValue(line - line_area)
    
    def scroll_map(self):
        first_visible_line = self.editor.SendScintilla(QsciScintilla.SCI_GETFIRSTVISIBLELINE)

        num_doc_lines = self.editor.SendScintilla(QsciScintilla.SCI_GETLINECOUNT)

        num_visible_lines = self.editor.SendScintilla(QsciScintilla.SCI_DOCLINEFROMVISIBLE, num_doc_lines)

        lines_on_screen = self.editor.SendScintilla(QsciScintilla.SCI_LINESONSCREEN)

        if num_visible_lines > lines_on_screen:
            last_top_visible_line = num_visible_lines - lines_on_screen

            num_map_visible_lines = self.SendScintilla(QsciScintilla.SCI_DOCLINEFROMVISIBLE, num_doc_lines)

            lines_on_screenm = self.SendScintilla(QsciScintilla.SCI_LINESONSCREEN)

            last_top_visible_linem = num_map_visible_lines - lines_on_screenm

            portion = first_visible_line / last_top_visible_line

            first_visible_linem = round(last_top_visible_linem * portion)

            self.verticalScrollBar().setValue(first_visible_linem)

            higher_pos = self.editor.SendScintilla(
                QsciScintilla.SCI_POSITIONFROMPOINT, 0, 0)
            y = self.SendScintilla(
                QsciScintilla.SCI_POINTYFROMPOSITION, 0, higher_pos)

            self.slider.move(0, y)

        self.current_scroll_value = self.editor.verticalScrollBar().value()

    def fold(self, line):
        self.foldLine(line)
    
    def shutdown(self):
        self._editor.SCN_UPDATEUI.disconnect()
        self._editor.SCN_ZOOM.disconnect()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        line = self.line_from_position(event.pos())
        self.editor.jump_to_line(line)

        los = self.editor.SendScintilla(QsciScintilla.SCI_LINESONSCREEN) / 2
        scroll_value = self.editor.verticalScrollBar().value()

        if self.current_scroll_value < scroll_value:
            self.editor.verticalScrollBar().setValue(scroll_value + los)
        else:
            self.editor.verticalScrollBar().setValue(scroll_value - los)
    
    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.editor.wheelEvent(event)

class MiniMapBox(QFrame):
    def __init__(self, editor, parent) -> None:
        super().__init__(parent)
        self.setObjectName("minimap")
        self.editor=editor
        self.parent=parent
        self.can_shadow = False
        self.init_ui()
    
    def init_ui(self):
        self.layout=QHBoxLayout(self)
        self.layout.setContentsMargins(6,0,0,0)
        self.setLayout(self.layout)

        self.minimap=MiniMap(self.editor, self)
        self.scrollbar=ScrollBar(self.editor, self)
        self.layout.addWidget(self.minimap)
        self.layout.addWidget(self.scrollbar)
    
        self.setFixedWidth(iconsts.MINIMAP_BOX_FIXED_WIDTH)
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(iconsts.MINIMAP_BOX_SHADOW_BLURRADIUS)
        self.drop_shadow.setOffset(iconsts.MINIMAP_BOX_SHADOW_Y_OFFSET, iconsts.MINIMAP_BOX_SHADOW_X_OFFSET)
        self.drop_shadow.setColor(QColor(0,0,0))
        self.drop_shadow.setEnabled(False)
        self.minimap.setGraphicsEffect(self.drop_shadow)
    
        self.editor.horizontalScrollBar().valueChanged.connect(self.update_drop_shadow)
        self.editor.on_resized.connect(self.update_lines)
        self.editor.linesChanged.connect(self.update_lines)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.minimap.on_mouse_leave()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.minimap.on_mouse_enter()
    
    def activate_shadow(self):
        self.minimap.setGraphicsEffect(self.goe)
    
    def disable_shadow(self):
        self.minimap.setGraphicsEffect(None)
    
    def update_lines(self):
        row, col = self.editor.getCursorPosition()
        width = self.editor.fontMetrics().boundingRect(self.editor.text(row)).width()
        if (width-self.editor.geometry().width())*-1 < iconsts.MINIMAP_SHADOW_MIN_TEXT_WIDTH:
            self.drop_shadow.setEnabled(True)
            self.can_shadow = True

        else:
            self.drop_shadow.setEnabled(False)
            self.can_shadow = False

            for row in range(self.editor.lines()):
                width = self.editor.fontMetrics().boundingRect(self.editor.text(row)).width()
                if (width-self.editor.geometry().width())*-1 < iconsts.MINIMAP_SHADOW_MIN_TEXT_WIDTH:
                    self.drop_shadow.setEnabled(True)
                    self.can_shadow = True
                    break
    
    def update_drop_shadow(self, value):
        if self.editor.horizontalScrollBar().maximum() - value <= 1:
            self.drop_shadow.setEnabled(False)
        elif self.editor.horizontalScrollBar().value() <= 1 and self.can_shadow:
            self.drop_shadow.setEnabled(True)

class ScrollBar(QScrollBar):

    def __init__(self, editor, parent) -> None:
        super().__init__(parent)
        self.parent=parent
        self.editor=editor
        self.sliderMoved.connect(self.moved)
    
    def moved(self):
        self.editor.verticalScrollBar().setValue(self.value())
    
    def update_position(self):
        self.setValue(self.editor.verticalScrollBar().value())
        self.setRange(0, self.editor.verticalScrollBar().maximum())
        

class SliderArea(QFrame):

    def __init__(self, minimap):
        super().__init__(minimap)
        self.setObjectName("minimap-slider")
        self.minimap = minimap
        self.pressed = False
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        self.change_transparency(iconsts.MINIMAP_SLIDER_OPACITY_MIN)
        self.setFixedSize(iconsts.MINIMAP_SLIDER_AREA_FIXED_SIZE)
    
    def change_transparency(self, bg:int):
        self.setStyleSheet("#minimap-slider{background-color:rgba(255,255,255,%d)}"%bg)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.pressed = True
        self.setCursor(Qt.ClosedHandCursor)
        first_visible_line = self.minimap.editor.SendScintilla(QsciScintilla.SCI_GETFIRSTVISIBLELINE)
        pos_parent = self.mapToParent(event.pos())
        position = self.minimap.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT, pos_parent.x(), pos_parent.y())
        line = self.minimap.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, position)
        self.line_on_visible_area = (line - first_visible_line) + 1

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.pressed = False
        self.setCursor(Qt.OpenHandCursor)
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.pressed:
            pos = self.mapToParent(event.pos())
            self.minimap.scroll_area(pos, self.line_on_visible_area)
    
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.change_transparency(iconsts.MINIMAP_SLIDER_OPACITY_MID)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.change_transparency(iconsts.MINIMAP_SLIDER_OPACITY_MAX)