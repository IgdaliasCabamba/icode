from PyQt5.QtCore import QMimeData, QPoint, Qt, pyqtSignal, QSize
from PyQt5.QtGui import QCursor, QDrag, QPixmap, QRegion, QStandardItem, QMovie, QIcon
from PyQt5.QtWidgets import (
    QLabel,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QFrame,
    QTabWidget,
    QToolButton,
    QSizePolicy,
    QLineEdit,
    QHBoxLayout,
)

from functions import getfn
from .corners import GenericTabCorner
from .root import CategoryMixin, TabData, notebook_corner_style


class QGithubButton(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("github-button")
        self.parent = parent
        self.widget_primary = None
        self.widget_secondary = None
        self.size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def set_widget_primary(self, btn):
        self.widget_primary = btn
        self.layout.addWidget(self.widget_primary)

    def set_widget_secondary(self, btn):
        self.widget_secondary = btn
        self.layout.addWidget(self.widget_secondary)


class Animator(QLabel):
    def __init__(self, parent, animation=None) -> None:
        super().__init__(parent)
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

        self.animation = animation
        self._animation_size = QSize(32, 32)
        if self.animation is not None:
            self.set_animation(self.animation)

    @property
    def movie(self):
        return self._movie

    def set_animation(self, animation_path: str = None, play: bool = True) -> None:
        self.animation = animation_path
        self._movie = QMovie(self.animation)
        self.setMovie(self._movie)
        if play:
            self.play()

    def set_scaled_size(self, w: int, h: int):
        if self.animation is not None:
            self._animation_size = QSize(w, h)
            self._movie.setScaledSize(self._animation_size)

    def update_movie(self):
        if self.animation is not None:
            self._movie.setScaledSize(self._animation_size)

    def play(self, visiblity: bool = True):
        if self.animation is not None:
            self._movie.start()
            self.setVisible(visiblity)
            self.update_movie()

    def stop(self, visiblity: bool = False):
        if self.animation is not None:
            self._movie.stop()
            self.setVisible(visiblity)


class InputHistory(QLineEdit):

    key_pressed = pyqtSignal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("input")
        self.parent = parent
        self.commands_list = []
        self.current_command_index = 0
        self.returnPressed.connect(self.add_command)

    def add_command(self):
        text = self.text()
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
                        self.setText(
                            self.commands_list[self.current_command_index * -1]
                        )
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


class IListWidgetItem(QListWidgetItem):
    def __init__(
        self, icon: object, text: str, tooltip: str = None, item_data: dict = None
    ) -> None:
        super().__init__()
        self.setText(text)
        if icon is not None:
            self.setIcon(icon)
        self.setToolTip(tooltip)

        self.item_data = item_data

    def set_data(self, data):
        self.item_data = data


class IStandardItem(QStandardItem):
    def __init__(
        self,
        icon: object,
        text: str,
        tooltip: str = None,
        item_data: dict = None,
        level: int = 1,
    ) -> None:
        super().__init__()
        self.setText(text)
        if icon is not None:
            self.setIcon(icon)
        self.setToolTip(tooltip)
        self.level = level
        if level > 0:
            self.setAutoTristate(True)
            self.setCheckable(True)

        self.item_data = item_data


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

    def get_tab_data(self, idx: int = -1) -> TabData:
        if idx < 0:
            idx = self.currentIndex()

        return TabData(
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

        mimeData = IMimeData()
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


class IGenericNotebook(ITabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("bottom-notebook")
        self.init_ui()

    def init_ui(self):
        self.setDocumentMode(False)
        self.setMovable(False)
        self.setTabsClosable(False)

        self.corner = GenericTabCorner(self)
        self.setCornerWidget(self.corner)

        self.set_drag_and_drop(False)
        self.set_corner_style(notebook_corner_style)

    def set_tab_icon(self, icon: object, icon_path: str = False) -> None:
        pass

    def add_tab_and_get_index(self, widget, text):
        self.addTab(widget, text)
        return self.indexOf(widget)
