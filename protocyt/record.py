'''
Holding Record class.
'''

__all__ = [
    'Record',
    ]

class Record(dict):
    """
    This class is derived from dict.
    Gives access to items as if they are attributes.
    """
    __slots__ = ()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __delattr__(self, key):
        self.__delitem__(key)

    def setvalue(self, key, value):
        "Set's value of a key and returns that value"
        self[key] = value
        return value

    def copy(self):
        'Creates a shallow copy of instance'
        return self.__class__(self)
