from .system import SYS_SEP, BASE_PATH
from PyQt5.QtCore import QSettings

class DataManager(QSettings):
    def __init__(self, file_with_path:str, format=QSettings.IniFormat):
        super().__init__(file_with_path, format)
        self.file_path = f"{BASE_PATH}{SYS_SEP}data{SYS_SEP}{file_with_path}"
    
    def save_to_list(self, value, key:str) -> None:            
        base_list = self.value(key)
        if hasattr(base_list, "append"):
            base_list.append(value)
            self.setValue(key, base_list)
        else:
            self.setValue(key, [value])
        return None
            
    def restore_from_list(self, key:str, pos:int = -1):
        base_list = self.value(key)
        if isinstance(base_list, list):
            try:
                return base_list[pos]
            except Exception as e:
                print(e)
        return None
            
    def get_all_from_list(self, key:str):        
        base_list = self.value(key)
        if isinstance(base_list, list):
            return base_list
        return None
    
    def save_to_dict(self, value, key:str) -> None:            
        base_list = self.value(key)
        if hasattr(base_list, "items"):
            base_list.append(value)
            self.setValue(key, base_list)
        else:
            self.setValue(key, [value])
        return None
            
    def restore_from_dict(self, key:str, pos:int = -1):
        base_list = self.value(key)
        if isinstance(base_list, list):
            try:
                return base_list[pos]
            except Exception as e:
                print(e)
        return None
            
    def get_all_from_dict(self, key:str):        
        base_list = self.value(key)
        if isinstance(base_list, list):
            return base_list
        return None
    
    # TODO
    def remove_list_data(self, key:str, until:int) -> None:
        self.remove(key)
    
    def erase_all(self):
        self.clear()
    
    def export_to_json(self, file_name):
        pass
    
    def import_from_json(self, file_name):
        pass