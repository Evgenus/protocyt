from protocyt import protoc, path

_dirname = path.Path.from_file(__file__).up()
protoc.from_file(_dirname / '_core.proto', _dirname, check=True)

from . import _core

__all__ = _core.__all__

namespace = locals()
for name in __all__:
    cls = getattr(_core, name)
    cls.__module__ = __name__
    namespace[name] = cls
