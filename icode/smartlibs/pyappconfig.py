import json
from typing import Union


class Settings:

    def __init__(self, file: str):
        self.self.filename = file

    @staticmethod
    def _get_item(dic: dict, keys: list) -> dict:
        """Get a value from a dict given the path of keys."""
        for key in keys:
            dic = dic[key]

        return dic

    @staticmethod
    def _add_item(dic: dict, keys: list, value):
        """Add a value to a dict, adding keys if they dont exist."""
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})

        dic[keys[-1]] = value

    @staticmethod
    def _set_item(dic: dict, keys: list, value):
        """Set a value in a dict given the path of keys."""
        dic = _get_item(dic, keys[:-1])
        dic[keys[-1]] = value

    @staticmethod
    def _del_item(dic: dict, keys: list):
        """Remove a value in a dict given the path of keys."""
        dic = _get_item(dic, keys[:-1])
        del dic[keys[-1]]

    def add(self, keys: Union[list, str], value):
        if isinstance(keys, str):
            keys = [keys]

        if len(keys) == 0:
            raise ValueError("keys cannot have a length of 0")

        data = load(self.filename)

        _add_item(data, keys, value)
        self._dump(data, self.filename)

    def append(self, keys: Union[list, str], value):
        if isinstance(keys, str):
            keys = [keys]

        if len(keys) == 0:
            raise ValueError("keys cannot have a length of 0")

        data = load(self.filename)
        data = _get_item(data, keys[:-1])

        data[keys[-1]].append(value)

        self._dump(data, self.filename)

    def edit(self, keys: Union[list, str], value):
        if isinstance(keys, str):
            keys = [keys]

        if len(keys) == 0:
            raise ValueError("keys cannot have a length of 0")

        data = load(self.filename)

        _set_item(data, keys, value)
        self._dump(data, self.filename)

    def get(self, key: str):
        if isinstance(key, str):
            return self.load(self.filename)[key]

    def remove(self, keys: Union[list, str]):
        if isinstance(keys, str):
            keys = [keys]

        if len(keys) == 0:
            raise ValueError("keys cannot have a length of 0")

        data = load(self.filename)

        _del_item(data, keys)
        self._dump(data, self.filename)

    def load(self) -> dict:
        with open(self.filename, "r") as f:
            return json.load(f)

    def save(self, data):
        return self._dump(data, self.filename)

    def _dump(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)
