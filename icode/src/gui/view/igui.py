from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QListWidgetItem
from functions import getfn
from smartlibs.qtmd import MovableTabWidget
from .utils import notebook_corner_style
from .corners import GenericTabCorner


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


class IGenericNotebook(MovableTabWidget):
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
