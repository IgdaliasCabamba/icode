from .corners import BottomTabCorner, MainTabCorner
from .code_searcher import FindReplace
from .root import TabData, notebook_corner_style
from .igui import ITabWidget
from PyQt5.QtCore import QEvent, Qt, QObject, pyqtSignal

class TabRegister:
    def __init__(self, tab_data):
        self.data = tab_data

class AltTabPressEater(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and (event.key() == 16777217 or event.key() == 16777218):
            return True
        else:
            return QObject.eventFilter(self, obj, event)

class NoteBookEditor(ITabWidget):
    
    on_tab_changed = pyqtSignal(int)

    def __init__(self, parent, ui):
        super().__init__(parent)
        self.widget_list=[]
        self.parent=parent
        self.ui = ui
        self.tabs = []
        self.navigation = []
        self.time_line = []
        self.add_category('tabwidget')
        self.filter = AltTabPressEater()
        self.installEventFilter(self.filter)
        self.init_ui()
        
    
    def init_ui(self):
        
        self.find_replace = FindReplace(self.parent, self)
        self.corner=MainTabCorner(self)
        self.setCornerWidget(self.corner)
        
        self.tabCloseRequested.connect(self.close_tab)
        self.on_tab_added.connect(self.tab_added)
        self.set_corner_style(notebook_corner_style)
        self.on_tab_data.connect(self.update_tab_data)
        self.currentChanged.connect(self.tab_changed)
    
    def set_new_parent(self, parent):
        self.parent = parent
    
    def set_tab_icon(self, icon:object, icon_path:str=False) -> None:
        pass
    
    def close_tab(self, index=None):
        if self.count() == 0:
            return

        elif index is None :
            index=self.currentIndex()
        
        widget = self.widget(index)
        self.time_line.remove(widget)

        tab_data=TabData(
            title=self.tabText(index),
            tooltip=self.tabToolTip(index),
            whatsthis=str(self.tabWhatsThis(index)),
            widget=widget,
            icon=self.tabIcon(index)
            )
        
        self.widget_list.append(tab_data)
        self.removeTab(index)
        self.tab_closed.emit(widget)
        self.on_user_event.emit(self)
        
        if self.count() <= 0:
            self.last_tab_closed.emit(self)
            self.hide()
    
    def open_last_closed_tab(self):
        if self.widget_list:
            index = self.add_tab_and_get_index(self.widget_list[-1].widget, self.widget_list[-1].title)
            self.setTabIcon(index, self.widget_list[-1].icon)
            self.setTabToolTip(index, self.widget_list[-1].tooltip)
            self.setTabWhatsThis(index, self.widget_list[-1].whatsthis)
            
            self.widget_list.pop(-1)

    def add_tab_and_get_index(self, widget, text):
        self.addTab(widget, text)
        idx = self.indexOf(widget)
        self.update_navigation()
        return idx
        

    def tab_added(self, idx:int=None):
        self.on_user_event.emit(self)
        if idx is not None:
            self.tabs.append(self.get_tab_data(idx))
        self.show()
        self.update_navigation()
    
    def update_tab_data(self, tab_data):
        tab_data.widget.notebook = self
    
    def update_navigation(self):
        self.navigation.clear()
        
        for x in self.time_line:
            i = self.indexOf(x)
            data = self.get_tab_data(i)
            self.navigation.append({
                "title":data.title,
                "tooltip":data.tooltip,
                "whatsthis":data.whatsthis,
                "widget":data.widget,
                "icon":data.icon,
                "index":i
            })
    
    def tab_changed(self, idx):
        self.on_tab_changed.emit(idx)
        widget = self.widget(idx)
        if widget in self.time_line:
            self.time_line.remove(widget)
            self.time_line.insert(0, widget)
        else:
            self.time_line.insert(0, widget)
        self.update_navigation()

    def get_navigation(self):
        self.update_navigation()
        return self.navigation
        

class SideBottomNotebook(ITabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.setObjectName("bottom-notebook")
        self.init_ui()
    
    def init_ui(self):
        self.setDocumentMode(False)
        self.setMovable(False)
        self.setTabsClosable(False)

        self.corner = BottomTabCorner(self)
        self.setCornerWidget(self.corner)

        self.set_drag_and_drop(False)
        self.set_corner_style(notebook_corner_style)
    
    def set_tab_icon(self, icon:object, icon_path:str=False) -> None:
        pass

    def add_tab_and_get_index(self, widget, text):
        self.addTab(widget, text)
        return self.indexOf(widget)