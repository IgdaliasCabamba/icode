from PyQt5.QtCore import Qt
import frameworks.jedit2 as ijson
from base.system import BASE_PATH, SYS_SEP
from data import qt_cache, DATA_FILE, TERMINALS_FILE
import base.consts as iconsts
from base.memory import *

ORIENTATIONS = {
    0: Qt.Vertical,
    1: Qt.Vertical,
    2: Qt.Horizontal,
    3: Qt.Horizontal
}

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

def save_window(window, app):
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
    
    #--------------------------------------
    
    def get_direction(dir):
        return ORIENTATIONS[dir]
            
    data = []
    for notebook in window.isplitter.splited_widgets:
        childs = []
        for i in range(notebook["widget"].count()):
            widget = notebook["widget"].widget(i)
            if app.widget_is_code_editor(widget):
                
                content_path = str(widget.file)    
                content = widget.editor.text()
                selection = widget.editor.getSelection()
                cursor_pos = widget.editor.getCursorPosition()
                lexer = widget.editor.lexer_name
                vbar = widget.editor.verticalScrollBar().value()
                hbar = widget.editor.horizontalScrollBar().value()
                if widget.file is None:
                    content_path = None
                
                tab_data = notebook["widget"].get_tab_data(i)
                
                childs.append({
                    "editor":{
                        "path":content_path,
                        "text":content,
                        "selection":selection,
                        "cursor":cursor_pos,
                        "lexer":lexer,
                        "hbar":hbar,
                        "vbar":vbar
                        },
                    "notebook":{
                        "title":tab_data.title,
                        "tooltip":tab_data.tooltip,
                        "whatsthis":tab_data.whatsthis,
                        "index":i
                        }
                    })
        
        data.append({
            "id":notebook["id"],
            "ref":notebook["ref"],
            "direction":get_direction(notebook["direction"]),
            "childs":childs
            })
                    
                    
    MEMORY["icode"]["editing"] = data
    save_memory()
            
def restore_window(window, app, getfn):
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
    
    #--------------------------------------
    
    for item in MEMORY["icode"]["editing"]:
        id = item["id"]
        ref = item["ref"]
        direction = item["direction"]
        childs = item["childs"]
        
        if id == 1:
            notebook = app.ui.notebook
        else:
            if ref is None:
                notebook_parent = None
            else:
                notebook_parent = app.ui.notebooks[ref]
            
            if childs:    
                notebook = app.create_new_notebook(direction, notebook_parent, False)
            else:
                continue
            
                
        for child in childs:
            
            lexer_name = child["editor"]["lexer"]
            file = child["editor"]["path"]
            code = child["editor"]["text"]
            cursor = child["editor"]["cursor"]
            selection = child["editor"]["selection"]
            scroll_v = child["editor"]["hbar"]
            scroll_h = child["editor"]["vbar"]
            title = child["notebook"]["title"]
            icon = getfn.get_icon_from_lexer(lexer_name)
            
            editor = app.get_new_editor(notebook, file)
            editor.editor.set_text(code)
            index = notebook.add_tab_and_get_index(editor, title)
            notebook.setTabIcon(index, icon)
            
            for code_editor in editor.editors:
                code_editor.set_lexer(getfn.get_lexer_from_name(lexer_name))
                code_editor.setCursorPosition(cursor[0], cursor[1])
                code_editor.verticalScrollBar().setValue(scroll_v)
                code_editor.horizontalScrollBar().setValue(scroll_h)
                code_editor.setSelection(selection[0], selection[1], selection[2], selection[3])
                
            app.on_new_editor.emit(editor)
        
    MEMORY["icode"]["editing"] = []
    save_memory()

def icwd(new_dir):
    MEMORY["icode"]["paths"]["current-path"] = str(new_dir)

def ipwd():
    return MEMORY["icode"]["paths"]["current-path"]