from PyQt5.QtCore import Qt
import frameworks.jedit2 as ijson
from base.system import BASE_PATH, SYS_SEP
from data import qt_cache, DATA_FILE
import base.consts as iconsts

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
        
    qt_cache.setValue("window_geometry", window_object.geometry())
    qt_cache.setValue("window_state", window_object.windowState())
    qt_cache.setValue("div_main_state", window.div_main.saveState())
    qt_cache.setValue("div_child_state", window.div_child.saveState())
    qt_cache.setValue("side_right_visiblity", window.side_right.isVisible())
    qt_cache.setValue("side_right_size", window.side_right.size())
    for i, action in enumerate(window.tool_bar.actions_list):
        if action.isChecked():
            qt_cache.setValue("toolbar_action", i)
            break
            
def restore_window(window):
    window_geometry = qt_cache.value("window_geometry")
    window_state = qt_cache.value("window_state")
    side_right_visiblity = qt_cache.value("side_right_visiblity")
    side_right_size = qt_cache.value("side_right_size")
    div_main_state = qt_cache.value("div_main_state")
    div_child_state = qt_cache.value("div_child_state")
    toolbar_action=qt_cache.value("toolbar_action")
    
    if window.frame:
        window_object = window.frame
    else:
        window_object = window
        
    if window_geometry is not None:
        window_object.setGeometry(window_geometry)
        window_object.center()
    else:
        window_object.setGeometry(iconsts.MAINWINDOW_BASE_GEOMETRY)
        window_object.center()
    
    if window_state is not None:
        state = int(window_state)
    
        if state == iconsts.WINDOW_NO_STATE:
            window_object.setWindowState(Qt.WindowNoState)
        elif state == iconsts.WINDOW_MINIMIZED:
            window_object.setWindowState(Qt.WindowMaximized)
        elif state == iconsts.WINDOW_MAXIMIZED:
            window_object.setWindowState(Qt.WindowMaximized)
        elif state == iconsts.WINDOW_FULLSCREEN:
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