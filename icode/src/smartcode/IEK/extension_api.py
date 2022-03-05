import glob
import importlib
import os
import pathlib
import re
import textwrap
from typing import Union

import langserver
from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import base.consts as iconsts
import settings
from base.code_api import *
from base.font_loader import *
from base.icache import *
from base.isetting import *
from base.system import *
from data import ijson
from functions import *
from settings import *


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

    def source_path(self, name:str = "src"):
        return f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}{self.ext_name}{SYS_SEP}{name}{SYS_SEP}"
    
    def path_object_to(self, prefix:str, path:str="") -> object:
        if path != "":
            path = getfn.get_adjusted_path(path)
        return pathlib.Path(f"{self.source_path(prefix)}{path}")

    def path_to(self, prefix:str, path:str = "") -> str:
        if path != "":
            path = getfn.get_adjusted_path(path)
        return f"{self.source_path(prefix)}{path}"
    
    def local_storage_to(self, type:str, *names, make:bool=False) -> str:
        if type == "data":
            return BASE_PATH+SYS_SEP+"data"+SYS_SEP+"extensions"+SYS_SEP+self.ext_name+SYS_SEP+os.path.join(*names)
        elif type == "cache":
            return BASE_PATH+SYS_SEP+".cache"+SYS_SEP+"extensions"+SYS_SEP+self.ext_name+SYS_SEP+os.path.join(*names)
        else:
            if len(names) >=2:
                return self.path_to(names[0], names[1])
    
    def object_is(self, object_:object, name:str) -> bool:
        object_name = getattr(object_, "objectName", None)
        if object_name is not None:
            if object_name() == name:
                return True
        
        return False
    
    def parse_attr(self, parent:object=None, attrs:list = []) -> None:
        if parent is None:
            parent = self
        
        if attrs:
            swap_attr = None
            base_attr = getattr(parent, attrs[0], None)
            attrs.pop(0)

            for attr in attrs:
                swap_attr = getattr(base_attr, attr, None)
                if swap_attr is None:
                    break
                base_attr = swap_attr
            
            return base_attr
    
    def do_on(self, action:object, *names:tuple):
        attrs = []
        for arg in names:
            if isinstance(arg, str):
                attrs.append(arg)
        
        attr = self.parse_attr(self, attrs)
        if hasattr(attr, "connect"):
            attr.connect(action)

class StyleMaker:
    def __init__(self, main, path:Union[list, str], vars:dict={}) -> None:
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

    def get_styles(self, dark:dict, light:dict):
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
