# standart
import sys
import inspect
# internal
from .path import Path
from .protoc import from_source

class ProtocoledMeta(type):
    def __new__(mcs, name, bases, internals):
        doc = internals.get('__doc__')
        if doc is not None:
            scope = sys._getframe(1).f_locals
            module_name = internals.get('__module__')
            protocol_name = '_'.join(
                (module_name.replace('_', '').replace('.', '_'), name)
                )
            module = sys.modules[module_name]
            output_dir = Path.from_file(module.__file__).up()
            from_source(inspect.cleandoc(doc), protocol_name, output_dir, True)
            protocol = __import__(protocol_name, scope, scope, [], -1)
            base = getattr(protocol, name)
            return type.__new__(mcs, name, bases + (base,), internals)
        else:
            return type.__new__(mcs, name, bases, internals)

class ProtocoledClass(object):
    __metaclass__ = ProtocoledMeta
