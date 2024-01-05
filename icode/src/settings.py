from dataclasses import dataclass
from PyQt5.QtCore import Qt
import smartlibs.mjson as ijson
from core.system import ROOT_PATH
from data import qt_cache, DATA_FILE, TERMINALS_FILE, EDITOR_FILE
import core.consts as iconsts
from core.memory import *


@dataclass
class SettingsCache:
    settings: dict = None


settings_cache = SettingsCache()


def get_settings() -> dict:
    try:
        data = ijson.load(DATA_FILE)
        settings_cache.settings = data
        return data
    except:
        return settings_cache.settings


def get_font():
    return get_settings()["font"]


def get_icons_package():

    return get_settings()["icons-package"]


def get_icons_theme():

    return get_settings()["icons-theme"]


def get_palette():

    return get_settings()["palette"]


def get_qt_theme():

    return get_settings()["qt-theme"]


def get_window_style():

    return get_settings()["window-style"]


def get_theme():

    return get_settings()["theme"]


def get_extensions():

    return get_settings()["extensions"]


def save_window(window, app):
    """Save The Main Window"""
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
    """Save The Notebooks and Editors"""

    data = []
    for notebook in window.isplitter.splited_widgets:
        childs = []
        for i in range(notebook["widget"].count()):
            widget = notebook["widget"].widget(i)
            if widget.objectName() == "editor-frame":

                editor_state = widget.save_state()
                tab_data = notebook["widget"].get_tab_data(i)

                childs.append({
                    "editor": editor_state,
                    "notebook": {
                        "title": tab_data.title,
                        "tooltip": tab_data.tooltip,
                        "whatsthis": tab_data.whatsthis,
                        "index": i,
                    },
                })

        data.append({
            "id": notebook["id"],
            "ref": notebook["ref"],
            "direction": iconsts.ORIENTATIONS[notebook["direction"]],
            "childs": childs,
        })

    MEMORY["icode"]["editing"] = data
    save_memory()


def restore_window(window, app, getfn):
    """Restore the Main Window"""
    window_geometry = qt_cache.value("window_geometry")
    window_state = qt_cache.value("window_state")
    side_right_visiblity = qt_cache.value("side_right_visiblity")
    side_right_size = qt_cache.value("side_right_size")
    div_main_state = qt_cache.value("div_main_state")
    div_child_state = qt_cache.value("div_child_state")
    toolbar_action = qt_cache.value("toolbar_action")

    if window.frame:
        window_object = window.frame
    else:
        window_object = window

    if window_geometry is not None:
        window_object.setGeometry(window_geometry)
        window_object.centralize()
    else:
        window_object.setGeometry(iconsts.MAINWINDOW_BASE_GEOMETRY)
        window_object.centralize()

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
        window.side_right.resize(side_right_size.width(),
                                 side_right_size.height())

    if div_main_state is not None:
        window.div_main.restoreState(div_main_state)

    if div_child_state is not None:
        window.div_child.restoreState(div_child_state)

    if toolbar_action is not None:
        window.tool_bar.actions_list[int(toolbar_action)].trigger()
    """Restore the Notebooks and Editors"""

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
                notebook = app.create_new_notebook(direction, notebook_parent,
                                                   False)
            else:
                continue

        for child in childs:
            title = child["notebook"]["title"]
            icon = getfn.get_icon_from_lexer(child["editor"]["lexer"])

            editor = app.new_editor(notebook, child["editor"]["path"])
            editor.restore_state(child["editor"])

            index = notebook.add_tab_and_get_index(editor, title)
            notebook.setTabIcon(index, icon)

            app.on_new_editor.emit(editor)

    MEMORY["icode"]["editing"] = []
    save_memory()


def icwd(new_dir):
    MEMORY["icode"]["paths"]["current-path"] = str(new_dir)


def ipwd():
    return MEMORY["icode"]["paths"]["current-path"]
