from PyQt5.QtWidgets import QLabel, QScrollArea


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
