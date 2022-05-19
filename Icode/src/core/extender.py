import glob
import os
from typing import Union
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
            "functions":[],
            "icons":[]
        }
        self.loaded_extensions = []
        self.running_extensions = []
    
    def remove(self, ext:dict) -> None:
        """
        Remove the extension from his list
        
        Parameters
        ----------
        ext: dict 
            The extension
        
        Returns
        -------
        None
        """
        for key in self.extensions.keys(): #Remove the extension by category
            if ext in self.extensions[key]:
                self.extensions[key].remove(ext)

    def get_files(self) -> list:
        """
        Return all extensions init files
        
        Returns
        -------
        list
            A list of all __init__.json files under extensions path
        """
        return glob.glob(
                os.path.join(
                    "/",
                    os.environ["SMARTCODE_SRC_PATH"],
                    "smartcode",
                    "extensions")+INIT_EXTESNIONS_PATTERN,
                recursive=True
        )

    def build_ext(self, file:str, content:dict) -> object:
        """
        Prepare the extension based on init file
        
        Parameters
        ----------
        file: str
            The path of the __init__.json file

        content: dict
            A dict containing the content of the __init__.json file
            This file contains the instructions to build the extension
        
        Returns
        -------
        self
        """
        try:
            ext = dict()

            requirements = content["require"]["engines"]["icode"].replace("^", "")
            min_ver = requirements.split(".")
            if (
                int(min_ver[0]) >= ICODE_VERSION["MAJOR"]
                and int(min_ver[1]) >= ICODE_VERSION["MINOR"]
                and int(min_ver[2]) >= ICODE_VERSION["PATCH"]
                ):
                
                category = content["category"].lower()

                # Assigning the values to the extension

                ext["main"] = content["main"]
                ext["category"] = category

                ext["name"]=content["name"] 
                ext["path"] = str(pathlib.Path(file).parent)
                ext["uninstall"] = lambda: self.ext_manager.uninstall(ext) #Uninstall method, call this to remove the extension
                """
                Usage:
                    print(self.extensions[category][idx]["path"])
                    self.extensions[category][idx]["uninstall"]()
                    print(self.extensions[category][idx]["path"])
                """
                ext["enable"] = lambda: self.ext_manager.enable(ext) #Enable method, call this to enable the extension
                """        
                Usage:
                    print(self.extensions[category][idx]["enabled"])
                    self.extensions[category][idx]["enable"]()
                    print(self.extensions[category][idx]["enabled"])
                """
                ext["disable"] = lambda: self.ext_manager.disable(ext) #Disable method, call this to disable the extension
                """        
                Usage:
                    print(self.extensions[category][idx]["enabled"])
                    self.extensions[category][idx]["disable"]()
                    print(self.extensions[category][idx]["enabled"])
                """
                ext["publisher"] = content["publisher"]
                
                ext_data = self.ext_manager.extension_exists(ext["name"]) #checks if the extension is saved in the database and its state
                if isinstance(ext_data, dict):
                    ext["enabled"] = ext_data["enabled"] # restore extension state
                else:
                    ext["enabled"] = True #by default extensions are enabled
                    self.ext_manager.add(ext) #if not, add it to the database
                 
                for key in self.extensions.keys(): #Add the extension by category
                    if category in {key}:
                        self.extensions[key].append(ext)

        except Exception as e:
            logging.error(f"Failed to build extension because:", exc_info=True)
        
        return self

    def find_extensions(self) -> object:
        """
        Find extensions from init files
    
        Returns
        -------
        self
        """
        for ext in self.get_files():
            try:
                with open(ext, "r") as fext:
                    content = hjson.load(fext)
                    self.build_ext(ext, content)
            except Exception as e:
                logging.error(f"Failed to find extension: {ext} because:", exc_info=True)
                pass
        
        return self
    
    def load_extensions(self) -> object:
        """
        Load the extenions and append the Init class to list of running extensions(running_extensions)
        
        Returns
        -------
        self
        """
        
        all_extensions = []
        for key in self.extensions.keys():
            all_extensions.extend(self.extensions[key])

        for ext in all_extensions:
            if ext["enabled"] and ext["name"] != None: # check if extension is enabled
                
                package = pathlib.Path(ext["path"]).name
                module = ext['main'].split(".")[0]

                extension = importlib.import_module(name=f"extensions.{package}.src.{module}")
                if hasattr(extension, "run") and hasattr(extension, "stop"):
                    self.loaded_extensions.append(
                        (
                            ext,
                            extension,
                            {
                                "run":extension.run,
                                "stop":extension.stop,
                                "reload": lambda: importlib.reload(extension)
                            }
                        )
                    )

                logging.info(f"loaded: {extension}\n from: .src.{module} {package}")
        
        return self
    
    def init_extensions(self, data:dict) -> object:
        """
        Start the extents from a list of tuples containing the extents in index 1,
        passing the main class and the Qt6 instance

        Parameters
        ----------
        data: dict
            A dict containing the classes
        
        Returns
        -------
        self
        """
        for ext in self.loaded_extensions:
            self.running_extensions.append(ext[1].run(data))
        
        return self
    
    def get_plugin_list(self, only_running: bool = False) -> Union[list, dict]:
        """
        Parameters
        ----------
        only_running: bool
            If True return only the extensions that is ruuning
            else return all extensions
        
        Returns
        -------
        Union[list, dict]
        """
        if only_running:
            return self.running_extensions
        return self.extensions

    def finish_all(self) -> None:
        """
        Stop all running extensions
        Returns
        -------
        None
        """
        for ext in self.running_extensions:
            self.finish_one(ext)

    def finish_one(self, extension: object) -> None:
        """
        Stop the given extension
        
        Parameters
        ----------
        extension: object
            The extension to be stoped

        Returns
        -------
        None
        """
        if hasattr(extension, "stop"):
            extension.stop()
(
    Plugger()
    .find_extensions()
    .load_extensions()
    .init_extensions({"app":1, "qapp":2})
)
