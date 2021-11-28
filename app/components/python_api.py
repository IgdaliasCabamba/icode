import pickledb
import pathlib
import data

class PythonApi:
    def __init__(self, env_file_path):
        self.env_file_path = env_file_path
        self.env_path_object = pathlib.Path(self.env_file_path)
    
    def _create_file(self):
        with open(self.env_file_path, "x") as file:
            json.dump({"envs":[]}, file)

    def get_default_envs(self):
        return data.python_envs

    def create_env(self, env_path):
        try:
            return jedi.create_environment(env_path)
        except Exception as e:
            print(e)
            return False
    
    def save_env(self, env_path):
        if env_path is not None:
            try:
                if self.env_path_object.exists() and self.env_path_object.is_dir():
                    data = pickledb.load(self.env_file_path, True)
                    data.ladd("envs", str(env_path))
            
            except Exception as e:
                print(e)
                self.create_file()