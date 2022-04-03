import pathlib
from PyQt5.QtCore import QSettings


class CacheManager(QSettings):
    def __init__(
        self,
        file_with_path: str,
        format: object = QSettings.IniFormat,
        optimization: int = 3,
    ):
        super().__init__(file_with_path, format)
        self.file_path = file_with_path
        self.file_path_object = pathlib.Path(self.file_path)
        self.optimization = optimization
        self.defaults = {}

    def __create_data(self):
        for key, value in self.defaults.items():
            self.setValue(key, value)

    def save_to_list(self, value, key: str) -> None:
        self._check_up()

        base_list = self.value(key)
        if isinstance(base_list, list):
            if self.optimization == 3:
                if value in base_list:
                    base_list.remove(value)

            if value is not None:
                base_list.append(value)

            self.setValue(key, base_list)
        else:
            self.setValue(key, [value])
        return None

    def restore_from_list(self, key: str, pos: int = -1):
        self._check_up()

        base_list = self.value(key)
        if isinstance(base_list, list):
            try:
                return base_list[pos]
            except Exception as e:
                print(e)
        return None

    def get_all_from_list(self, key: str):
        self._check_up()

        base_list = self.value(key)
        if isinstance(base_list, list):
            return base_list
        return None

    def remove_list_data(self, key: str, until: int) -> None:
        self.remove(key)

    def erase_all(self):
        self.clear()

    def _check_up(self):
        if not self.file_path_object.exists():
            self.__create_data()
