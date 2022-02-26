from PyQt5 import QtCore, QtWidgets
from qtwidgets import EqualizerBar

import random


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.equalizer = EqualizerBar(5, ['#0C0786', '#40039C', '#6A00A7', '#8F0DA3', '#B02A8F', '#CA4678', '#E06461',
                                          '#F1824C', '#FCA635', '#FCCC25', '#EFF821'])

        self.setCentralWidget(self.equalizer)

        self._timer = QtCore.QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.update_values)
        self._timer.start()

    def update_values(self):
        self.equalizer.setValues([
            min(100, v+random.randint(0, 50) if random.randint(0, 5) > 2 else v)
            for v in self.equalizer.values()
            ])




app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()





