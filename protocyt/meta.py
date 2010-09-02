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
            module_name = internals.get('__module__')
            protocol_name = '_'.join(
                (module_name.replace('.', '_'), name, 'protocol')
                )
            module = sys.modules[module_name]
            output_dir = Path.from_file(module.__file__).up()
            from_source(inspect.cleandoc(doc), module_name, output_dir, True)
            protocol = __import__(module_name, globals(), locals(), [], -1)
            base = getattr(protocol, name)
            return type.__new__(mcs, name, bases + (base,), internals)
        else:
            return type.__new__(mcs, name, bases, internals)

class ProtocoledClass(object):
    __metaclass__ = ProtocoledMeta

class Test(ProtocoledClass):
    '''
    message Test {
        required int32 value = 1;
    }
    '''

print dir(Test)