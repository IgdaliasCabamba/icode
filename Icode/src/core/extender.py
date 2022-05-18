import glob
import os
import hjson
import logging
from .version import ICODE_VERSION
import pathlib
import shutil
from tinydb import TinyDB, Query
from .routes import DATA_ROUTES
from .iconsts import *
import importlib

class ExtManager:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.db = TinyDB(DATA_ROUTES["extensions_db"])
        self.ext_query = Query()
        self.db_extensions = self.db.all()
    
    def extension_exists(self, ext_name:str) -> object :
        for item in self.db_extensions:
            if ext_name in item["name"]:
                return item
        return False
    
    def add(self, ext):
        self.db.insert({'name': ext["name"], 'enabled':ext["enabled"], "path":ext["path"]})
    
    def enable(self, ext):
        self.db.update({'enabled': True}, self.ext_query.name == ext["name"])
        ext["enabled"] = True
    
    def disable(self, ext):
        self.db.update({'enabled': False}, self.ext_query.name == ext["name"])
        ext["enabled"] = False
    
    def install(self, url):
        pass
    
    def uninstall(self, ext):
        shutil.rmtree(ext["path"])
        self.db.remove(self.ext_query.name == ext["name"])
        self.parent.remove(ext)


class Plugger:
    def __init__(self) -> None:
        self.ext_manager = ExtManager(self)
        self.extensions = {
            "themes":[],
            "lexer_styles":[],
            "functions":[]
        }
        self.running_extensions = []
    
    def remove(self, ext):
        if ext in self.extensions["themes"]:
            self.extensions["themes"].remove(ext)
        
        elif ext in self.extensions["lexer_styles"]:
            self.extensions["lexer_styles"].remove(ext)
        
        elif ext in self.extensions["functions"]:
            self.extensions["functions"].remove(ext)

    def get_files(self) -> list:
        """Return all extensions init files"""
        return glob.glob(
                os.path.join(
                    "/",
                    os.environ["SMARTCODE_SRC_PATH"],
                    "smartcode",
                    "extensions")+INIT_EXTESNIONS_PATTERN,
                recursive=True
        )

    def build_ext(self, file, content:dict) -> None:
        """Prepare the extension based on init file"""
        try:
            ext = {
                "name":None,
                "path":None,
                "enable":None,
                "disable":None,
                "remove":None,
                "enabled":True,
                "main":None
            }
            requirements = content["require"]["engines"]["icode"].replace("^", "")
            min_ver = requirements.split(".")
            if (
                int(min_ver[0]) >= ICODE_VERSION["MAJOR"]
                and int(min_ver[1]) >= ICODE_VERSION["MINOR"]
                and int(min_ver[2]) >= ICODE_VERSION["PATCH"]
                ):
                
                category = content["category"].lower()
                ext["main"] = content["main"]

                ext["name"]=content["name"]
                ext["path"] = str(pathlib.Path(file).parent)
                ext["uninstall"] = lambda: self.ext_manager.uninstall(ext)
                ext["enable"] = lambda: self.ext_manager.enable(ext)
                ext["disable"] = lambda: self.ext_manager.disable(ext)
                
                ext_data = self.ext_manager.extension_exists(ext["name"])
                if isinstance(ext_data, dict):
                    ext["enabled"] = ext_data["enabled"]
                else:
                    self.ext_manager.add(ext)
                
                if category.lower() in {"themes"}:
                    self.extensions["themes"].append(ext)
                
                elif category.lower() in {"lexer_styles"}:
                    self.extensions["lexer_styles"].append(ext)

                elif category.lower() in {"functions"}:
                    self.extensions["functions"].append(ext)

        except Exception as e:
            logging.error(f"Failed to build extension because:", exc_info=True)

    def find_extensions(self) -> None:
        """Find extensions from init files"""
        for ext in self.get_files():
            try:
                with open(ext, "r") as fext:
                    content = hjson.load(fext)
                    self.build_ext(ext, content)
            except Exception as e:
                logging.error(f"Failed to load extension: {ext} because:", exc_info=True)
                pass
        
        return self
        
        #print(self.extensions["themes"][0]["enabled"])
        #self.extensions["themes"][0]["enable"]()
        #print(self.extensions["themes"][0]["enabled"])
        #self.extensions["themes"][0]["disable"]()
        #print(self.extensions["themes"][0]["path"])
        #self.extensions["themes"][0]["uninstall"]()
        #print(self.extensions["themes"][0]["path"])
        #print(self.extensions["themes"][0]["enabled"])
    
    def load_extensions(self) -> None:
        """Load the extenions and append the Init class to list of running extensions(running_extensions)"""
        for ext in self.extensions["functions"]:
            if ext["enabled"] and ext["name"] != None: # check if extension is enabled
                
                package = pathlib.Path(ext["path"]).name
                module = ext['main'].split(".")[0]

                extension = importlib.import_module(name=f"extensions.{package}.src.{module}")
                self.running_extensions.append(extension.Init)

                logging.info(f"loaded: {extension}\n from: .src.{module} {package}")

(
    Plugger()
    .find_extensions()
    .load_extensions()
)
