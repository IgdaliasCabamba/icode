from PyQt5.QtWidgets import QPushButton, QToolButton, QLabel, QSizePolicy


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
