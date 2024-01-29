class FakeRow:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._data = tuple(value for value in kwargs.values())

    def __getitem__(self, n):
        return self._data[n]
