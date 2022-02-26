from PySide2 import QtCore, QtGui, QtWidgets
from qtwidgets import PowerBar


app = QtWidgets.QApplication([])
volume = PowerBar(["#053061", "#2166ac", "#4393c3", "#92c5de", "#d1e5f0", "#f7f7f7", "#fddbc7", "#f4a582", "#d6604d", "#b2182b", "#67001f"])
volume.setBarSolidPercent(0.8)
volume.setBarPadding(5)
volume.show()
app.exec_()





