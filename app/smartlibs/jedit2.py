#See Jedit2(https://pypi.org/project/jedit2/) for get more info, this is a sample copy
import hjson as json

def _get_item(dic: dict, keys: list) -> dict:
	"""Get a value from a dict given the path of keys."""
	for key in keys:
		dic = dic[key]

	return dic

def _add_item(dic: dict, keys: list, value):
	"""Add a value to a dict, adding keys if they dont exist."""
	for key in keys[:-1]:
		dic = dic.setdefault(key, {})

	dic[keys[-1]] = value

def _set_item(dic: dict, keys: list, value):
	"""Set a value in a dict given the path of keys."""
	dic = _get_item(dic, keys[:-1])
	dic[keys[-1]] = value

def _del_item(dic: dict, keys: list):
	"""Remove a value in a dict given the path of keys."""
	dic = _get_item(dic, keys[:-1])
	del dic[keys[-1]]

def add(keys: list, value, filename):
	if len(keys) == 0:
		raise ValueError("keys cannot have a length of 0")

	data = load(filename)

	_add_item(data, keys, value)
	_dump(data, filename)

def append(keys: list, value, filename):
	if len(keys) == 0:
		raise ValueError("keys cannot have a length of 0")

	data = load(filename)
	data = _get_item(data, keys[:-1])

	data[keys[-1]].append(value)

	_dump(data, filename)

def edit(keys: list, value, filename):
	if len(keys) == 0:
		raise ValueError("keys cannot have a length of 0")

	data = load(filename)

	_set_item(data, keys, value)
	_dump(data, filename)

def remove(keys: list, filename):
	if len(keys) == 0:
		raise ValueError("keys cannot have a length of 0")

	data = load(filename)
	
	_del_item(data, keys)
	_dump(data, filename)

def load(filename) -> dict:
	with open(filename, "r") as f:
		return json.load(f)

def save(data, filename):
	return _dump(data, filename)

def _dump(data, filename):
	with open(filename, "w") as f:
		json.dump(data, f, indent=4)
