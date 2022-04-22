class CategoryMixin(object):
    def __init__(self, **kwargs):
        super(CategoryMixin, self).__init__(**kwargs)
        self._categories = set()

    def categories(self):
        return self._categories

    def add_category(self, c):
        if c in self._categories:
            return
        self._categories.add(c)

    def remove_category(self, c):
        if c not in self._categories:
            return
        self._categories.remove(c)
