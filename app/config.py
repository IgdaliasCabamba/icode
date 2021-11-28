from PyQt5.QtCore import Qt, QSettings
import smartlibs.jedit2 as ijson
from system import BASE_PATH, SYS_SEP

DATA_FILE=f"{BASE_PATH}{SYS_SEP}data{SYS_SEP}data.json"
CACHE_FILE = QSettings(BASE_PATH+SYS_SEP+".cache"+SYS_SEP+"user"+SYS_SEP+"cache.ini", QSettings.IniFormat)

def get_all() -> dict:

    return ijson.load(DATA_FILE)

def get_icons_package():

    return ijson.load(DATA_FILE)["icons-package"]

def get_icons_theme():

    return ijson.load(DATA_FILE)["icons-theme"]

def get_palette():

    return ijson.load(DATA_FILE)["palette"]

def get_qt_theme():
    
    return ijson.load(DATA_FILE)["qt-theme"]

def get_window_style():
    
    return ijson.load(DATA_FILE)["window-style"]

def get_theme():
    
    return ijson.load(DATA_FILE)["theme"]

def get_extensions():
    
    return ijson.load(DATA_FILE)["extensions"]

def save_window(window):
    if window.frame:
        window_object = window.frame
    else:
        window_object = window
        
    CACHE_FILE.setValue("window_geometry", window_object.geometry())
    CACHE_FILE.setValue("window_state", window_object.windowState())
    CACHE_FILE.setValue("div_main_state", window.div_main.saveState())
    CACHE_FILE.setValue("div_child_state", window.div_child.saveState())
    CACHE_FILE.setValue("side_right_visiblity", window.side_right.isVisible())
    CACHE_FILE.setValue("side_right_size", window.side_right.size())
    for i, action in enumerate(window.tool_bar.actions_list):
        if action.isChecked():
            CACHE_FILE.setValue("toolbar_action", i)
            break
            
        
    

def restore_window(window):
    window_geometry = CACHE_FILE.value("window_geometry")
    window_state = CACHE_FILE.value("window_state")
    side_right_visiblity = CACHE_FILE.value("side_right_visiblity")
    side_right_size = CACHE_FILE.value("side_right_size")
    div_main_state = CACHE_FILE.value("div_main_state")
    div_child_state = CACHE_FILE.value("div_child_state")
    toolbar_action=CACHE_FILE.value("toolbar_action")
    
    if window.frame:
        window_object = window.frame
    else:
        window_object = window
        
    if window_geometry is not None:
        window_object.setGeometry(window_geometry)
        window_object.center()
    else:
        window_object.setGeometry(0, 0, 1000, 600)
        window_object.center()
    
    if window_state is not None:
        state = int(window_state)
        if state == 0:
            window_object.setWindowState(Qt.WindowNoState)
        elif state == 1:
            window_object.setWindowState(Qt.WindowMaximized)
        elif state == 2:
            window_object.setWindowState(Qt.WindowMaximized)
        elif state == 4:
            window_object.setWindowState(Qt.WindowFullScreen)
        else:
            window_object.setWindowState(Qt.WindowActive)
    
    if side_right_visiblity is not None:
        if side_right_visiblity == "true":
            window.side_right.setVisible(True)
        else:
            window.side_right.setVisible(False)
    
    if side_right_size is not None:
        window.side_right.resize(side_right_size.width(), side_right_size.height())
    
    if div_main_state is not None:
        window.div_main.restoreState(div_main_state)
        
    if div_child_state is not None:
        window.div_child.restoreState(div_child_state)
    
    if toolbar_action is not None:
       window.tool_bar.actions_list[int(toolbar_action)].trigger()