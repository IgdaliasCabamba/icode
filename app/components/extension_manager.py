import importlib
import smartlibs.jedit2 as ijson

class Ext:
    def __init__(self):
        self.extensions=[]

    def load_plugin(self, plugin, data):
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
                print(e)
                return e
                
            return extension
        
        except ModuleNotFoundError as e:
            print(e)
            return False
    
    def get_plugin_list(self) -> list:
        return self.extensions
    
    def exit_all(self):
        for ext in self.extensions:
            ext.finish()

class Plugin(Ext):
    def __init__(self):
        super().__init__()
    
    def run_ui_plugin(self, config, data) -> None:
        config=ijson.load(config)

        if config["theme"] or config["theme"] is not None:
            self.load_plugin(config["theme"], data) 
        else:
            self.load_plugin("icode_default_theme", data)
    
    def run_app_plugin(self, config, data):
        config=ijson.load(config)
        if config["extensions"]:
            for extension in config["extensions"]:
                self.load_plugin(extension, data)