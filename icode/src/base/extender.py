import importlib
from typing import Union
import frameworks.jedit2 as ijson

class Extender:
    def __init__(self) -> None:
        self.extensions=[]

    def load_plugin(self, plugin, data) -> Union[object, bool]:
        try:
            package_info=importlib.import_module(".package", plugin)
            name=package_info.PACKAGE["__name__"]
            if name != None:
                extension=importlib.import_module(f".src.{name}", plugin)
                self.extensions.append(extension)
            else:
                return False
            try:
                extension.Init(data)
            except Exception as e:
                print(f"Crash Failed to load:{plugin} because {e}")
                return e
                
            return extension
        
        except ModuleNotFoundError as e:
            print(e)
            return False
    
    def get_plugin_list(self) -> list:
        return self.extensions
    
    def exit_all(self) -> None:
        for ext in self.extensions:
            self.finish_one(ext)
    
    def finish_one(self, extension: object) -> None:
        if hasattr(extension, "finish"):
            extension.finish()

class Plugin(Extender):
    def __init__(self) -> None:
        super().__init__()
    
    def run_ui_plugin(self, config, data) -> None:
        config=ijson.load(config)

        if config["theme"] or config["theme"] is not None:
            self.load_plugin(config["theme"], data) 
        else:
            self.load_plugin("icode_default_theme", data)
    
    def run_app_plugin(self, config, data) -> None:
        config=ijson.load(config)
        if config["extensions"]:
            for extension in config["extensions"]:
                self.load_plugin(extension, data)