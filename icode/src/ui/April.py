from PyQt5.QtWidgets import QFrame, QVBoxLayout, QButtonGroup, QRadioButton, QTabWidget, QGraphicsDropShadowEffect
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtGui import QColor
from data import april_cache
import base.consts as iconsts
from functions import getfn

class April(QFrame):
    
    on_mode_changed = pyqtSignal(int)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("April")
        self.parent = parent
        self.parent.resized.connect(self.update_ui)
        self.icons = getfn.get_smartcode_icons("April")
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
        
        self.svg_widget = QSvgWidget(self.icons.get_path("produtivity"))
        self.svg_widget.setMaximumHeight(300)
        
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
        
        self.layout.addWidget(self.svg_widget)
        self.layout.addWidget(self.opt_low)
        self.layout.addWidget(self.opt_full)
        self.layout.addWidget(self.opt_smart)
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setOffset(0, -1)
        self.drop_shadow.setColor(QColor(0,0,0))
        self.setGraphicsEffect(self.drop_shadow)
        
        self.anim = QPropertyAnimation(self, b"pos")
        
        self.setFixedWidth(400)
        self.setMinimumHeight(500)
        self.hide()
        
    def change_mode(self, btn):
        self.mode = self.mode_values[btn.objectName()]
        self.on_mode_changed.emit(self.mode)
    
    def update_position(self):
        y = (self.parent.geometry().height()-self.geometry().height())-self.parent.status_bar.geometry().height()-10
        w = self.parent.geometry().width()/2
        x = int(w-self.geometry().width()/2)
        self.move(x,y)
        return x, y
    
    def update_size(self):
        pass

    def update_ui(self):
        self.update_position()
        self.update_size()
        self.update()
    
    def appear(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.animate()
    
    def animate(self):
        x = self.geometry().x()
        y = self.geometry().y()
        self.anim.setStartValue(QPoint(x, self.geometry().height()+y))
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim.setEndValue(QPoint(x, y))
        self.anim.setDuration(1200)
        self.anim.start()