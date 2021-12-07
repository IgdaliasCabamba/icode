from PyQt5.QtCore import QSettings
import data
import pathlib

class PythonApi(QSettings):
    def __init__(self, file_with_path:str, format=QSettings.IniFormat):
        super().__init__(file_with_path, format)
        self.file_path = file_with_path
        self.file_path_object = pathlib.Path(self.file_path)
        self.defaults = {"envs":None}

    def __create_data(self):
        for key, value in self.defaults.items():
            self.setValue(key, value)

    def get_default_envs(self):
        return data.python_envs

    def create_env(self, env_path):
        try:
            return jedi.create_environment(env_path)
        except Exception as e:
            print(e)
            return False
    
    def restore_envs(self):
        self._check_up()
        return self.value("envs")
    
    def save_env(self, env_path):
        key = "envs"
        self._check_up()
        if env_path is not None:
            
            base_list = self.value(key)
            if hasattr(base_list, "append"):
                base_list.append(value)
                self.setValue(key, base_list)
            else:
                self.setValue(key, [value])
            return None
    
    def _check_up(self):
        if not self.env_path_object.exists() and not self.env_path_object.is_dir():
            self.__create_data()