'''
Holding DocTemplatable class
'''

__all__ = [
    'DocTemplatable',
    ]

class DocTemplatable(object):
    """
    User defined exception classes mixin. Allows to define exception message in
    doc-strings nd format them using new-style string formatting
    
    Example:
        >>> class InvalidName(DocTemplatable, NameError):
        ...    'Name `{0}` is invalid in my world'
        ...
        >>> print InvalidName('BadName')
        Name `BadName` is invalid in my world

        >>> class InvalidAttribute(DocTemplatable, AttributeError):
        ...    'Name `{name}` is invalid in my world'
        ...
        >>> print InvalidAttribute(name='BadName')
        Name `BadName` is invalid in my world
    """
    args = ()
    def __init__(self, *args, **kwargs):
        super(DocTemplatable, self).__init__(*args)
        self.args = args
        self.kwargs = kwargs
    def __str__(self):
        return self.__doc__.format(*self.args, **self.kwargs)
