from PyQt5.QtWidgets import QFrame, QSplitter, QFrame, QStackedLayout, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal

from . import CategoryMixin


class Splitter(QSplitter):

    def __init__(self, **kwargs):
        super(Splitter, self).__init__(**kwargs)

    def child_at(self, pos):

        if not self.rect().contains(pos):
            return None
        for i in range(self.count()):
            for w in (self.widget(i), self.handle(i)):
                if w.geometry().contains(pos):
                    return w

    def parent_manager(self):

        w = self.parent()
        while not isinstance(w, ISplitter):
            w = w.parent()
        return w

    def widgets(self):
        return [self.widget(i) for i in range(self.count())]

    children = widgets

    def remove_child(self, widget):
        assert self.isAncestorOf(widget)
        assert self is not widget

        widget.setParent(None)

    def replace_child(self, child, new):
        assert child is not new
        assert self is not child
        assert self is not new
        assert self.isAncestorOf(child)

        idx = self.indexOf(child)
        child.setParent(None)
        self.insertWidget(idx, new)


class ISplitter(QFrame, CategoryMixin):
    
    UP = 0

    DOWN = 1

    LEFT = 2

    RIGHT = 3

    ORIENTATIONS = {
        UP: Qt.Vertical,
        DOWN: Qt.Vertical,
        LEFT: Qt.Horizontal,
        RIGHT: Qt.Horizontal,
    }

    MOVES = {UP: -1, DOWN: 1, LEFT: -1, RIGHT: 1}
    
    SplitterClass = Splitter
    on_last_tab_closed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.main = parent
        self.notebooks_list = []
        self.splited_widgets = []
        self.index = 0

        self.root = self.SplitterClass(orientation=Qt.Horizontal)

        layout = QStackedLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.root)

        self.add_category("splitmanager")

    def add_notebook(self, notebook: QTabWidget):
        self.notebooks_list.append(notebook)

    def splitAt(self, current_widget, direction, new_widget) -> None:
        if current_widget is None:
            parent = self.root
            idx = 0
        else:
            assert self.isAncestorOf(current_widget)

            if hasattr(current_widget.parent, "root"):
                parent = current_widget.parent.root
            else:
                parent = current_widget.parent

            idx = parent.indexOf(current_widget)

        orientation = ISplitter.ORIENTATIONS[direction]
        if parent.orientation() == orientation:
            oldsize = parent.sizes()
            if oldsize:
                oldsize[idx] //= 2
                oldsize.insert(idx, oldsize[idx])

            if direction in (ISplitter.DOWN, ISplitter.RIGHT):
                idx += 1

            parent.insertWidget(idx, new_widget)

            if oldsize:
                parent.setSizes(oldsize)
        else:
            refocus = current_widget and current_widget.hasFocus()

            new_split = self.SplitterClass(orientation=orientation)

            if current_widget:
                oldsize = parent.sizes()
                if direction in (ISplitter.DOWN, ISplitter.RIGHT):
                    new_split.addWidget(current_widget)
                    parent.insertWidget(idx, new_split)
                    new_split.addWidget(new_widget)

                else:
                    new_split.addWidget(new_widget)
                    parent.insertWidget(idx, new_split)
                    new_split.addWidget(current_widget)

                parent.setSizes(oldsize)
                new_split.setSizes([100, 100])
                current_widget.set_new_parent(new_split)

            else:
                new_split.addWidget(new_widget)
                parent.insertWidget(idx, new_split)

            if refocus:
                current_widget.setFocus()

        self.index += 1
        self.add_splited_widget(self.index, current_widget, direction,
                                new_widget)
        self.update_size()

    def add_splited_widget(self, id, ref, direction, new_widget):
        ref_id = None

        for item in self.splited_widgets:
            if id == item["id"]:
                return

        for item in self.splited_widgets:
            if ref is not None:
                if ref == item["ref"]:
                    ref_id = item["id"]

        self.splited_widgets.append({
            "id": id,
            "ref": ref_id,
            "direction": direction,
            "widget": new_widget
        })

    def update_size(self) -> None:
        x = []

        for i in range(self.root.count()):
            x.append(2)

        self.root.setSizes(x)

    def notebook_last_tab_closed(self) -> None:
        if self.is_empty:
            self.on_last_tab_closed.emit()

    @property
    def is_empty(self) -> bool:
        x = 0
        for notebook in self.notebooks_list:
            if notebook.count() > 0:
                continue
            else:
                x += 1

        if x == len(self.notebooks_list):
            return True
        return False
