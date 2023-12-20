from PyQt5.QtCore import QObject, pyqtSignal


class Var(QObject):

    on_value_changed = pyqtSignal(object)

    def __init__(self, value=None, reactions=[]) -> None:
        super().__init__()
        self._value = value
        self._reactions = reactions

    def _set_value(self, value):
        self._value = value
        self.on_value_changed.emit(self._value)
        self.__changed()

    def _get_value(self, value):
        return self._value

    def add_reaction(self, reaction):
        self._reactions.append(reaction)

    def remove_reaction(self, reaction):
        if reaction in self._reactions:
            self._reactions.remove(reaction)

    def __changed(self):
        for reaction in self._reactions:
            reaction(self._value)


class RString(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, str):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, str):
            self._set_value(new)

        return self


class RInt(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, int):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, int):
            self._set_value(new)

        return self


class RDict(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, dict):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, dict):
            self._set_value(new)


class RList(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, list):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, list):
            self._set_value(new)


class RSet(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, set):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, set):
            self._set_value(new)


class RBool(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, bool):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, bool):
            self._set_value(new)


class RFloat(Var):

    def __init__(self, value, reactions=[]):
        super().__init__(reactions=reactions)
        self.__init(value)

    def __init(self, value):
        if isinstance(value, float):
            self._set_value(value)

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, new):
        if isinstance(new, float):
            self._set_value(new)


class RConst:

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def del_value(self):
        del self.__value
