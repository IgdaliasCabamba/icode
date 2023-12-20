from PyQt5.QtCore import pyqtSignal, QMimeData, Qt, QPoint
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtGui import QPixmap, QCursor, QDrag, QRegion
from .widgetcategory import CategoryMixin
from dataclasses import dataclass


@dataclass
class MovableTabData:
    title: str
    tooltip: str
    whatsthis: str
    widget: object
    icon: object


class MovableMimeData(QMimeData):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tab_data = None

    def set_tab_data(self, tab_data):
        self._tab_data = tab_data

    @property
    def tab_data(self):
        return self._tab_data


class MovableTabWidget(QTabWidget, CategoryMixin):

    tab_closed = pyqtSignal(object)
    last_tab_closed = pyqtSignal(object)
    on_tab_added = pyqtSignal(int)
    widget_added = pyqtSignal(object)
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

    def get_tab_data(self, idx: int = -1) -> MovableTabData:
        if idx < 0:
            idx = self.currentIndex()

        return MovableTabData(
            title=self.tabText(idx),
            tooltip=self.tabToolTip(idx),
            whatsthis=self.tabWhatsThis(idx),
            widget=self.widget(idx),
            icon=self.tabIcon(idx),
        )

    def set_corner_style(self, style: str) -> None:
        self.setStyleSheet(style)

    def set_drag_and_drop(self, flag: bool) -> bool:
        self.drag_and_drop = flag
        return self.drag_and_drop

    def mouseMoveEvent(self, e: object) -> None:
        if e.buttons() != Qt.RightButton:
            return

        if not self.drag_and_drop:
            return

        self.on_user_event.emit(self)

        globalPos = self.mapToGlobal(e.pos())
        tabbar = self.tabBar()
        pos_in_tab = tabbar.mapFromGlobal(globalPos)
        index_tab = tabbar.tabAt(e.pos())
        tabRect = tabbar.tabRect(index_tab)
        tab_data = self.get_tab_data(index_tab)

        pixmap = QPixmap(tabRect.size())
        tabbar.render(pixmap, QPoint(), QRegion(tabRect))

        mimeData = MovableMimeData()
        mimeData.set_tab_data(tab_data)

        drag = QDrag(tabbar)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        cursor = QCursor(Qt.OpenHandCursor)
        drag.setHotSpot(e.pos() - pos_in_tab)
        drag.setDragCursor(cursor.pixmap(), Qt.MoveAction)
        dropAction = drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if not self.drag_and_drop:
            return

        self.on_user_event.emit(self)

        event.accept()
        if event.source() is not None:
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
        self.on_tab_added.emit(index)
        widget_object = self.widget(index)
        self.widget_added.emit(widget_object)
        self.on_user_event.emit(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.on_resized.emit()
