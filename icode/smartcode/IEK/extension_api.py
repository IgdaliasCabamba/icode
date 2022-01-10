import glob
import importlib
import os
import pathlib
import re
import textwrap

from settings import get_icons_package, get_icons_theme, get_palette
from data import ijson
from functions import filefn, getfn
from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QObject, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import base.consts as iconsts
from base.system import *
from base.icache import *
from base.isetting import *
from base.font_loader import *


def make_dirs(dirs:list):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)    

def export(type:str="extension", path:str=""):
    if path != "":
        path = path.replace(".","/")
        path = getfn.get_adjusted_path(path)
        add_path(type, path)

class BaseApi:
    def __init__(self):
        pass

    def source_path(self, default:str = "src"):
        return f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}{self.ext_name}{SYS_SEP}{default}{SYS_SEP}"
    
    def path_object_to(self, prefix:str, path:str="") -> object:
        if path != "":
            path = getfn.get_adjusted_path(path)
        return pathlib.Path(f"{self.source_path(prefix)}{path}")

    def path_to(self, prefix:str, path:str = "") -> str:
        if path != "":
            path = getfn.get_adjusted_path(path)
        return f"{self.source_path(prefix)}{path}"
    
    def object_is(self, object_:object, name:str) -> bool:
        object_name = getattr(object_, "objectName", None)
        if object_name is not None:
            if object_name() == name:
                return True
        
        return False
    
    def parse_attr(self, parent:object = None, name:str = None) -> None:
        if isinstance(parent, str) and name is None:
            name = parent
            parent = None

        if name is not None:
            if parent is None:
                parent = self

            splitted_name = name.split(".")
            tmp_name = None
            base_name = getattr(parent, splitted_name[0], None)
            splitted_name.pop(0)

            for item in splitted_name:
                tmp_name = getattr(base_name, item, None)
                if tmp_name is None:
                    break
                base_name = tmp_name
            
            return base_name
    
    def add_event(self, name:str, action:object):
        attr = self.parse_attr(name)
        if hasattr(attr, "connect"):
            attr.connect(action)
            

class StyleMaker:
    def __init__(self, main, path:object, vars:dict={}) -> None:
        self._sheet_object = pathlib.Path(path)
        self._text = self.get_content()
        self.main = main
        self.vars = vars
        if self.vars:
            self.compile_qsass()
    
    @property
    def text(self):
        return self._text
    
    def get_content(self, encode:str = "utf-8") -> str:
        return self._sheet_object.read_text(encode)
    
    def format_style(self, to_replace:list, to_place:list):
        if isinstance(to_replace, list) and isinstance(to_place, list):
            if len(to_replace) == len(to_place):
                for i in range(len(to_replace)):
                    self._text = self._text.replace(to_replace[i], to_place[i])

        if isinstance(to_replace, str) and isinstance(to_place, str):
            self._text = self._text.replace(to_replace, to_place)
    
    def compile_qsass(self):
        for key,value in self.vars.items():
            key = re.sub(r"\W", "", key)
            self._text = re.sub(fr"[$]\b{key}\b", value, self._text)
    
    def apply(self):
        self.main.qapp.setStyleSheet(self.text)
        self.main.ui.setStyleSheet(self.text)

class ModelUi(QObject, BaseApi):
    def __init__(self, data: dict, ext_name: str):
        super().__init__(data["app"])
        self.ext_name = ext_name
        self.__app = data["app"]
        self.__qapp = data["qt_app"]
        self.qpalette = get_palette()
        self.ui = self.app.ui
        self.__data = data
    
    @property
    def app(self):
        return self.__app

    @property
    def qapp(self):
        return self.__qapp
    
    def icons_path_to(self, icons_to:str):
        return f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}icons{SYS_SEP}{get_icons_package()}{SYS_SEP}{get_icons_theme()}{SYS_SEP}{icons_to}{SYS_SEP}"

    def is_light(self) -> bool:
        if self.qpalette in {"light", "white", 1, "day"}:
            return True
        return False

    def is_dark(self) -> bool:
        if self.qpalette in {"dark", "black", 0, "night"}:
            return True
        return False
    
    def paint_editor(self, widget, painter):
        if widget.objectName()=="editor-frame":            
            for editor in widget.editors:
                editor.on_style_changed.connect(painter)
                painter(editor)

    def palette_to_styles(self, dark:dict, light:dict):
        if self.is_dark():
            return StyleMaker(self, self.path_to("src", dark["styles"]), dark["vars"])

        elif self.is_light():
            return StyleMaker(self, self.path_to("src", light["styles"]), light["vars"])
        
        else:
            return StyleMaker(self, self.path_to("src", dark["styles"]), dark["vars"])
    
    def set_lexer_style(self, lexer:object, key:str, dark:str, light:str):
        if self.is_light():
            lexer.set_style_api(ijson.load(self.path_to("src", light))[key])
        else:
            lexer.set_style_api(ijson.load(self.path_to("src", dark))[key])
    
    def set_code_style(self, editor:object, editor_dark:object, editor_light:object, lexer_styler:object, lexer:object=None):
        if self.is_light():
            editor_light(editor)
        else:
            editor_dark(editor)
        
        if lexer is None:
            lexer_attr = getattr(editor, "lexer", None)
            if lexer_attr is not None:
                lexer = lexer_attr()
                lexer_styler(lexer)
        else:
            lexer_styler(lexer)

class ModelApp(QObject, BaseApi):
    def __init__(self, data: dict, ext_name: str):
        super().__init__(data["app"])
        self.ext_name = ext_name
        self.__app = data["app"]
        self.__qapp = data["qt_app"]
        self.qpalette = get_palette()
        self.ui = self.app.ui
        self.__data = data
    
    @property
    def app(self):
        return self.__app

    @property
    def qapp(self):
        return self.__qapp
