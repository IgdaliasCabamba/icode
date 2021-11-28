import pathlib
import pickledb

class CacheManager:
    def __init__(self, file_data):
        self.file_data = file_data
        self.file_path_object = pathlib.Path(self.file_data)
        self.defaults = {"files":[], "folders":[], "repositorys":[]}

    def _create_data(self, mode="w"):
        with open(self.file_data, mode) as file:
            json.dump(self.defaults, file)
        
    def save_to_list(self, value, key:str) -> None:
        try:
            if self.file_path_object.exists():
                try:
                    data = pickledb.load(self.file_data, True)
                    data.ladd(key, value)
                except Exception as e:
                    self._create_data("w")
                    print(e)
            else:
                self._create_data("x")
                
        except Exception as e:
            print(e)
            
    def restore_from_list(self, key:str, pos:int = -1):
        try:
            if self.file_path_object.exists():
                try:
                    
                    data = pickledb.load(self.file_data, True)
                    
                    if data.llen(key) > 0:
                        return data.lget(key, pos)
                    return None
                        
                except Exception as e:
                    print(e)
            else:
                self._create_data("x")
        
        except Exception as e:
            print(e)
            
        return None