'''
Holding Path class.
'''

# standart
import os
import os.path
import glob
import shutil
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
# internal
from .templatable import DocTemplatable

__all__ = [
    'Path',
    ]

class Path(object):
    """
    Segmented path abstraction. You can use it to manipulate file/directory
    paths of URLs.

    Examples:

        >>> Path('a/b/c').str()
        '/a/b/c'
        >>> Path(['a', 'b', 'c']).str()
        '/a/b/c'
        >>> Path('a/b/c', ['d', 'e', 'f']).str()
        '/a/b/c/d/e/f'
        >>> Path('a/b/c', ['d', 'e', 'f'], Path('g/h')).str()
        '/a/b/c/d/e/f/g/h'
        >>> Path(['a', 'b'], ['..', 'c']).str()
        '/a/c'
        >>> Path(['a', 'b'], ['.', 'c']).str()
        '/a/b/c'
    """

    class ExtentionReplaceError(DocTemplatable, ValueError):
        "Last segment in path {0!r} is not file name or have no extention."

    class InvalidPartError(DocTemplatable, ValueError):
        "Path part {0!r} can't be spliten into segments"

    class SegmentTypeError(DocTemplatable, TypeError):
        "Paths serment should be a string {0}"

    string = None
    def __init__(self, *paths, **kwargs):
        """
        Accepts list of arguments which could be strings, lists, tuples or
        other instances of Path class. For strings path should be separated by
        '/' (regular slash!).
        """
        self.prefix = kwargs.pop('prefix', '')
        self.segments = []
        for part in paths:
            if isinstance(part, str):
                part = part.split('/')
            elif hasattr(part, '__iter__'):
                pass
            else:
                raise self.InvalidPartError(part)
            for segment in part:
                if not isinstance(segment, str):
                    raise self.SegmentTypeError(part)
                if segment   == '..':
                    self.segments.pop()
                elif segment == '.' :
                    pass
                elif segment        :
                    self.segments.append(segment)

    def __len__(self):
        'Segments amount in path'
        return len(self.segments)

    def __iter__(self):
        'Iterator over segments'
        return iter(self.segments)

    def __hash__(self):
        'Hash for Path instance is computed from default string representation.'
        return hash(str(self))

    def __eq__(self, other):
        """
        Equality check function. Compares only two instances of Path class.
        To compare with other types use string representaion or explicit Path
        construction object to be compared with.
        """
        if not isinstance(other, Path):
            return False
        return (self.prefix==other.prefix) and (self.segments==other.segments)

    def __truediv__(self, name):
        """
        Allows to construct Path by dividing several Paths.
        New instance ot Path class will be obtained as the result of each
        division.
        
        Example:

            >>> str(Path('a') / 'b' / 'c') # preferred usage
            '/a/b/c'
            >>> str(Path('a') / 'b/c')
            '/a/b/c'
            >>> str(Path('a/b/c') / ['d', 'e', 'f'])
            '/a/b/c/d/e/f'
            >>> str(Path('a/b/c') / ['d', 'e', 'f'] / Path('g/h'))
            '/a/b/c/d/e/f/g/h'
        """
        return self.__class__(self.segments, name, prefix=self.prefix)
    __div__ = __truediv__

    def __getitem__(self, names):
        """
        Allows to construct Path using square brackets.
        New instance ot Path class will be obtained as the result of each
        brackets use.

        Example:

            >>> Path('a')['b']['c'].str()
            '/a/b/c'
            >>> Path('a')['b/c'].str()
            '/a/b/c'
            >>> Path('a/b/c')[('d', 'e'), 'f'].str()
            '/a/b/c/d/e/f'
            >>> Path('a/b/c')['d', 'e', 'f', Path('g/h')].str()
            '/a/b/c/d/e/f/g/h'
        """
        if isinstance(names, tuple):
            return self.__class__(self.segments, *names, prefix=self.prefix)
        else:
            return self.__class__(self.segments, names, prefix=self.prefix)

    def __call__(self, *names):
        """
        Allows to construct Path using round calling-brackets.
        New instance ot Path class will be obtained as the result of each
        brackets use.

        Example:

            >>> Path('a')('b')('c').str()
            '/a/b/c'
            >>> Path('a')('b/c').str()
            '/a/b/c'
            >>> Path('a/b/c')(('d', 'e'), 'f').str()
            '/a/b/c/d/e/f'
            >>> Path('a/b/c')('d', 'e', 'f', Path('g/h')).str()
            '/a/b/c/d/e/f/g/h'
        """
        return self.__class__(self.segments, *names, prefix=self.prefix)

    def up(self, count=1):
        """
        Returns new Path instance without last `count` segments.
        If `count` is 0, returns new instance of Path.
        If path is empty returns new empty path.

        Example:

            >>> Path('a/b/c/d').up().str()
            '/a/b/c'
            >>> Path('a/b/c/d').up(2).str()
            '/a/b'
            >>> Path('a/b/c/d').up(-3).str()
            '/a/b/c'
        """
        if count == 0:
            return self.__class__(self.segments, prefix=self.prefix)
        else:
            return self.__class__(self.segments[:-count], prefix=self.prefix)

    def head(self):
        """
        Returns first segment of path as string.
        
        Example:

            >>> Path('a/b/c/d').head()
            'a'
        """
        return self.segments[0]

    def tail(self, count=1):
        """
        Returns new path instance without first `count` segments.

        Example:

            >>> Path('a/b/c/d').tail().str()
            '/b/c/d'
            >>> Path('a/b/c/d').tail(2).str()
            '/c/d'
            >>> Path('a/b/c/d').tail(-3).str()
            '/b/c/d'
        """
        return self.__class__(self.segments[count:], prefix=self.prefix)

    def ext(self, new_ext=None):
        """
        Replaces extension of last path segment, assuming that instance
        represents file path.
        If `new_ext` argument is None or omited returns found extension
        Raises exception if no extension was found.
        """
        name, old_ext = os.path.splitext(self.segments[-1])
        if new_ext is None:
            return old_ext
        if not old_ext:
            raise self.ExtentionReplaceError(old_ext)
        filename = name + ('' if new_ext.startswith('.') else '.') + new_ext
        return self.__class__(self.segments[:-1], filename, prefix=self.prefix)

    def add_ext(self, new_ext):
        """
        Adds or replaces extension of last path segment, assuming that instance
        represents file path. No errors if no extension was found.
        """
        name, _ = os.path.splitext(self.segments[-1])
        filename = name + ('' if new_ext.startswith('.') else '.') + new_ext
        return self.__class__(self.segments[:-1], filename, prefix=self.prefix)

    @property
    def filename(self):
        """
        Returns last segment in path without extension
        """
        name, _ = os.path.splitext(self.segments[-1])
        return name

    def __bool__(self):
        """
        Checks Path instance to be empty.
        """
        return bool(self.segments)
    __nonzero__ = __bool__

    def __repr__(self):
        """
        Returns verbose representaion.
        """
        return '<{0} prefix={1} segments={2} at 0x{3:08x}>'.format(
            self.__class__.__name__, self.prefix, self.segments, id(self))

    def __str__(self):
        """
        Calculates, stores in cache and returns string representation of path.
        """
        if self.string is None:
            path = [self.prefix]
            path.extend(self.segments)
            self.string = '/'.join(path)
        return self.string

    def str(self, front=False, back=False, prefix=True):
        """
        Extended string representation generator.
        Allows to omit prefix or add slash before first and after last segments.
        """
        return (
            ('/' if front else '') +
            str(self) if prefix else '/'.join(self.segments)  +
            ('/' if back else ''))

    def startswith(self, root):
        """
        Checks path to be subpath of `root` argument.

        Example:

            >>> Path('a/b/c/d').startswith(Path('a/b'))
            True
            >>> Path('a/b')['../c'].startswith(Path('a/b'))
            False
        """
        if not isinstance(root, Path):
            raise ValueError('Path expected, %r found' % type(root).__name__)
        root_length = len(root.segments)
        if len(self.segments) < root_length:
            return False
        return (self.segments[:root_length] == root.segments and
                self.prefix == root.prefix)

    def exists(self):
        """
        Checks path to be a path of existing file or directory.
        """
        return os.path.exists(self.str())

    def isfile(self):
        """
        Checks path to be a path of existing file.
        """
        return os.path.isfile(self.str())

    def isdir(self):
        """
        Checks path to be a path of existing directory.
        """
        return os.path.isdir(self.str())

    def listdir(self):
        """
        Returns list of directory contents, assuming that instance
        represents directory path.
        """
        return os.listdir(self.str())

    def makedirs(self):
        """
        Creates directory at instance path. Creates all necessary directories
        to made path accessible.
        """
        return os.makedirs(self.str())

    def remove(self):
        """
        Removes file or directory at instance path.
        If path is not exists OSError will be raisen.
        """
        if self.isfile():
            return os.remove(self.str())
        else:
            return shutil.rmtree(self.str())

    def open(self, *args):
        """
        Returns file descriptor, assuming that instance represents file path.
        """
        return open(self.str(), *args)

    def iterfiles(self, topdown=True, onerror=None, followlinks=False):
        """
        Iterates over all files in current path subtree and yields Path's
        objects of found files.
        """
        generator = os.walk(self.str(), topdown, onerror, followlinks)
        for root, _, files in generator:
            for name in files:
                yield self.__class__.from_file(root, name)

    def glob(self, pattern):
        for path in glob.iglob(str(self / pattern)):
            yield self.__class__.from_file(path)

    @classmethod
    def from_file(cls, *paths):
        """
        Creates Path instance from string representations of file path.
        """
        drive, path = os.path.splitdrive(os.path.abspath(os.path.join(*paths)))
        return cls(path.split(os.sep), prefix=drive)

    @classmethod
    def from_url(cls, path):
        """
        Creates Path instance from string representations of URL.
        """
        scheme, netloc, path, _, _, _ = urlparse.urlparse(path)
        return cls(path, prefix=scheme+'://'+netloc)

    @classmethod
    def cwd(cls):
        """
        Returns Path object of current working directory
        """
        return cls.from_file(os.getcwd())

    def stat(self):
        """
        Returns stat for path
        """
        return os.stat(self.str())