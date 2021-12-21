from PyQt5.QtWidgets import QFrame, QVBoxLayout, QButtonGroup, QRadioButton, QTabWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from smartlibs.icodeframe import iwindow
from data import april_cache
import components.consts as iconsts

class April(QFrame):
    
    on_mode_changed = pyqtSignal(int)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("April")
        self.parent = parent
        self.mode = iconsts.APRIL.SMART
        self.mode_values = {
            "opt_full":iconsts.APRIL.FULL,
            "opt_low":iconsts.APRIL.LOW,
            "opt_smart":iconsts.APRIL.SMART,
        }
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.btn_group = QButtonGroup(self)
        
        self.opt_full = QRadioButton("Full Power", self)
        self.opt_full.setObjectName("opt_full")
        self.opt_low= QRadioButton("Low Power", self)
        self.opt_low.setObjectName("opt_low")
        self.opt_smart = QRadioButton("Smart Mode", self)
        self.opt_smart.setObjectName("opt_smart")
        self.opt_smart.setChecked(True)
        
        self.btn_group.addButton(self.opt_low)
        self.btn_group.addButton(self.opt_full)
        self.btn_group.addButton(self.opt_smart)
        self.btn_group.buttonClicked.connect(self.change_mode)
        
        self.layout.addWidget(self.opt_low)
        self.layout.addWidget(self.opt_full)
        self.layout.addWidget(self.opt_smart)
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setOffset(0, -1)
        self.drop_shadow.setColor(QColor("#1064eb"))
        self.setGraphicsEffect(self.drop_shadow)
                
        self.resize(300, 400)
        self.move(500, 280)
        self.hide()
        
    
    def change_mode(self, btn):
        self.mode = self.mode_values[btn.objectName()]
        self.on_mode_changed.emit(self.mode)
    
    def appear(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
        