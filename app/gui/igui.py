from PyQt5.QtCore import QMimeData, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QDrag, QPixmap, QRegion, QStandardItem
from PyQt5.QtWidgets import (QLabel, QListWidgetItem, QPushButton, QScrollArea,
                             QTabWidget, QToolButton, QSizePolicy, QLineEdit)

from functions import getfn

from .base import CategoryMixin, TabData

class InputHistory(QLineEdit):
    
    key_pressed = pyqtSignal(object)

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setObjectName("input")
        self.parent = parent
        self.commands_list = []
        self.current_command_index = 0
        self.returnPressed.connect(self.add_command)
    
    def add_command(self):
        text=self.text()
        if self.commands_list:
            if text != self.commands_list[-1]:
                self.commands_list.append(text)
        else:
            self.commands_list.append(text)
    
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == 16777235:
            if self.commands_list:
                if self.current_command_index < len(self.commands_list):
                    self.current_command_index += 1
                    try:
                        self.setText(self.commands_list[self.current_command_index*-1])
                    except IndexError:
                        self.setText(self.commands_list[0])

        elif event.key() == 16777237:
            if self.current_command_index > 0:
                self.current_command_index -= 1
                try:
                    self.setText(self.commands_list[self.current_command_index])
                except IndexError:
                    self.setText(self.commands_list[-1])

class HeaderPushButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

class HeaderToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

class HeaderLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

class ScrollLabel(QScrollArea):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("scroll-label")
        
        self.setWidgetResizable(True)
        self.label = QLabel(self)
        self.setWidget(self.label)

        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
    
    def setText(self, text):
        self.label.setText(text)
    
    def setWordWrap(self, on):
        self.label.setWordWrap(on)
    
    def setAlignment(self, alignment):
        self.label.setAlignment(alignment)

class EditorListWidgetItem(QListWidgetItem):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.data = None

    def set_data(self, data):
        self.data = data

class TerminalListWidgetItem(QListWidgetItem):
    def __init__(self, icon, text, tooltip=None, item_data=None) -> None:
        super().__init__()
        self.setText(text)
        if icon is not None:
            self.setIcon(icon)
        self.setToolTip(tooltip)
        
        self.item_data=item_data


class IListWidgetItem(QListWidgetItem):
    def __init__(self, icon, text, tooltip=None, item_data=None) -> None:
        super().__init__()
        self.setText(text)
        if icon is not None:
            self.setIcon(icon)
        self.setToolTip(tooltip)
        
        self.item_data=item_data

class DoctorStandardItem(QStandardItem):
    def __init__(self, icon, text, tooltip=None, item_data=None) -> None:
        super().__init__()
        self.setText(text)
        if icon is not None:
            self.setIcon(icon)
        self.setToolTip(tooltip)
        self.setAutoTristate(False)
        
        self.item_data=item_data

class IStandardItem(QStandardItem):
    def __init__(self, icon, text, tooltip=None, item_data=None, level=1) -> None:
        super().__init__()
        self.setText(text)
        if icon is not None:
            self.setIcon(icon)
        self.setToolTip(tooltip)
        self.level=level
        if level > 0:
            self.setAutoTristate(True)
            self.setCheckable(True)
        
        self.item_data=item_data

class IMimeData(QMimeData):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tab_data = None
    
    def set_tab_data(self, tab_data):
        self._tab_data = tab_data
    
    @property
    def tab_data(self):
        return self._tab_data

class ITabWidget(QTabWidget, CategoryMixin):
    
    tab_closed = pyqtSignal(object)
    last_tab_closed = pyqtSignal(object)
    on_tab_added=pyqtSignal()
    widget_added=pyqtSignal(object)
    on_resized = pyqtSignal()
    on_user_event = pyqtSignal(object)
    on_tab_droped = pyqtSignal(object, object, object)
    on_tab_data = pyqtSignal(object)
    
    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        self.drag_and_drop = True
        
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.tabBar().setMouseTracking(True)
    
    def get_tab_data(self, idx:int = -1) -> TabData:
        if idx < 0:
            idx = self.currentIndex()
        
        return TabData(
            title=self.tabText(idx),
            tooltip=self.tabToolTip(idx),
            whatsthis=self.tabWhatsThis(idx),
            widget = self.widget(idx),
            icon=self.tabIcon(idx)
            )

    def set_corner_style(self, style:str) -> None:
        self.setStyleSheet(style)
    
    def set_drag_and_drop(self, flag:bool) -> bool:
        self.drag_and_drop = flag
        return self.drag_and_drop
        
    def mouseMoveEvent(self, e:object) -> None:
        if e.buttons() != Qt.RightButton:
            return
        
        if not self.drag_and_drop:
            return
        
        self.on_user_event.emit(self)
        tab_data = self.get_tab_data()

        globalPos = self.mapToGlobal(e.pos())
        tabbar = self.tabBar()
        pos_in_tab = tabbar.mapFromGlobal(globalPos)
        index_tab = tabbar.tabAt(e.pos())
        tabRect = tabbar.tabRect(index_tab)

        pixmap = QPixmap(tabRect.size())
        tabbar.render(pixmap,QPoint(),QRegion(tabRect))
        
        mimeData = IMimeData()
        mimeData.set_tab_data(tab_data)

        drag = QDrag(tabbar)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        cursor = QCursor(Qt.OpenHandCursor)
        drag.setHotSpot(e.pos() - pos_in_tab)
        drag.setDragCursor(cursor.pixmap(),Qt.MoveAction)
        dropAction = drag.exec_(Qt.MoveAction)
        
    def dragEnterEvent(self, event):
        if not self.drag_and_drop:
            return
        
        self.on_user_event.emit(self)
        
        event.accept()
        if event.source().parentWidget() != self:
            return

    def dragLeaveEvent(self, event):
        if not self.drag_and_drop:
            return
        
        self.on_user_event.emit(self)
        event.accept()

    def dropEvent(self, event):
        if not self.drag_and_drop or event.source().parentWidget() == self:
            return
        
        try:
        
            self.on_user_event.emit(self)
            
            event.setDropAction(Qt.MoveAction)
            event.accept()
            
            tab_data = event.mimeData().tab_data
            self.on_tab_data.emit(tab_data)
            self.add_tab_and_get_index(tab_data.widget, tab_data.title)
            self.on_tab_droped.emit(event, self, tab_data)
        
        except Exception as e:
            print(e)
            pass
            
    def tabInserted(self, index):
        super().tabInserted(index)
        self.setCurrentIndex(index)
        self.on_tab_added.emit()
        widget_object=self.widget(index)
        self.widget_added.emit(widget_object)
        self.on_user_event.emit(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.on_resized.emit()