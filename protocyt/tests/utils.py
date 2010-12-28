# standart
import unittest
import inspect
import itertools
import sys
# internal
from protocyt import protoc, path

def make_hex(string):
    if isinstance(string, str):
        return ' '.join('%02X' % ord(i) for i in string)
    else:
        return ' '.join('%02X' % i for i in string)

def make_type_tag(n, t):
    return '%02X' % (n<<3 | t)

class Debugger(object):
    def __init__(self):
        self.log = []
    def callback(self, name, bytes):
        self.log.append(('cb', name, make_hex(bytes)))
    def signal(self, type, name):
        self.log.append(('sg', type, name))

class BaseTestCase(unittest.TestCase):
    def __init__(self, tested_type, tested_value, index):
        unittest.TestCase.__init__(self)
        self.tested_type = tested_type
        self.tested_value = tested_value
        self.index = index

    def get_name(self):
        return '{0}_{1}_{2:02d}'.format(
            self.__class__.__name__,
            self.tested_type,
            self.index
            )

    def setUp(self):
        name = self.get_name()
        protoc.from_source(
            inspect.getdoc(self).format(type=self.tested_type),
            name,
            path.Path.from_file(__file__).up() / 'modules',
            check=True,
            keep=True,
            )
        module = __import__('modules.' + name, globals(), locals(), [], -1)
        self.module = getattr(module, name)

    def tearDown(self):
        if self.module.__name__ in sys.modules:
            del sys.modules[self.module.__name__]

    def __str__(self):
        return "{0}.{1}.{2}_{3:02d}({4!r})".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.tested_type,
            self.index,
            self.tested_value
            )

class BaseTestDebugCase(BaseTestCase):
    def __init__(self, tested_type, tested_value, T,
                encoded_value, extra_log, index):
        BaseTestCase.__init__(self, tested_type, tested_value, index)
        self.T = T
        self.extra_log = extra_log
        self.encoded_value = encoded_value

class SimpleTestCase(BaseTestCase):
    '''
    message Test {{
        required {type} value = 1;
    }}
    '''
    def runTest(self):
        message1 = self.module.Test(self.tested_value)
        ba = bytearray()
        message1.serialize(ba)
        message2 = self.module.Test.deserialize(ba)
        self.assertEqual(message1.value, message2.value)
        self.assertEqual(message1, message2)

class SimpleTestDebugCase(BaseTestDebugCase):
    '''
    option debug = true;
    message Test {{
        required {type} value = 1;
    }}
    '''
    def make_log(self):
        def shuffle():
            yield ('sg', 'enter', 'Test')
            yield ('cb', 'type', make_type_tag(1, self.T))
            yield ('sg', 'field', b'value')
            for extra in self.extra_log:
                yield extra
            yield ('cb', self.tested_type, self.encoded_value)
            yield ('sg', 'exit', 'Test')
        return list(shuffle())

    def make_data(self):
        def shuffle():
            yield make_type_tag(1, self.T)
            for extra in self.extra_log:
                yield extra[2]
            if self.encoded_value:
                yield self.encoded_value
        return ' '.join(shuffle())

    def runTest(self):
        debugger = Debugger()
        message1 = self.module.Test(self.tested_value)
        ba = bytearray()
        message1.serialize(ba)
        self.assertEqual(make_hex(ba), self.make_data())
        message2 = self.module.Test.deserialize(ba, debugger)
        self.assertEqual(debugger.log, self.make_log())
        self.assertEqual(message1.value, message2.value)
        self.assertEqual(message1, message2)

class RepeatableTestCase(BaseTestCase):
    '''
    message Test {{
        repeated {type} value = 1;
    }}
    '''
    def runTest(self):
        message1 = self.module.Test(self.tested_value)
        ba = bytearray()
        message1.serialize(ba)
        message2 = self.module.Test.deserialize(ba)
        self.assertEqual(message1.value, message2.value)
        self.assertEqual(message1, message2)

class RepeatableTestDebugCase(BaseTestDebugCase):
    '''
    option debug = true;
    message Test {{
        repeated {type} value = 1;
    }}
    '''
    def make_log(self):
        def shuffle():
            yield ('sg', 'enter', 'Test')
            tag = make_type_tag(1, self.T)
            for value, extra in zip(self.encoded_value, self.extra_log):
                yield ('cb', 'type', tag)
                yield ('sg', 'field', b'value')
                for _ in extra:
                    yield _
                yield ('cb', self.tested_type, value)
            yield ('sg', 'exit', 'Test')
        return list(shuffle())

    def make_data(self):
        def shuffle():
            tag = make_type_tag(1, self.T)
            for value, extra in zip(self.encoded_value, self.extra_log):
                yield tag
                for _ in extra:
                    yield _[2]
                if value:
                    yield value
        return ' '.join(shuffle())

    def runTest(self):
        debugger = Debugger()
        message1 = self.module.Test(self.tested_value)
        ba = bytearray()
        message1.serialize(ba)
        self.assertEqual(make_hex(ba), self.make_data())
        message2 = self.module.Test.deserialize(ba, debugger)
        self.assertEqual(message1.value, message2.value)
        self.assertEqual(message1, message2)
        self.assertEqual(debugger.log, self.make_log())

class RepeatablePackedTestCase(RepeatableTestCase):
    '''
    message Test {{
        repeated {type} value = 1 [packed=true];
    }}
    '''

class RepeatablePackedTestDebugCase(RepeatableTestDebugCase):
    '''
    option debug = true;
    message Test {{
        repeated {type} value = 1 [packed=true];
    }}
    '''

    def __init__(self, tested_type, tested_value, T,
                encoded_value, extra_log, packed_size, index):
        RepeatableTestDebugCase.__init__(self, tested_type, tested_value, T,
                encoded_value, extra_log, index)
        self.packed_size = packed_size
    def make_log(self):
        def shuffle():
            yield ('sg', 'enter', 'Test')
            tag = make_type_tag(1, 2)
            yield ('cb', 'type', tag)
            yield ('sg', 'field', b'value')
            yield ('cb', 'size', self.packed_size)
            for value in self.encoded_value:
                yield ('cb', self.tested_type, value)
            yield ('sg', 'exit', 'Test')
        return list(shuffle())

    def make_data(self):
        def shuffle():
            tag = make_type_tag(1, 2)
            yield tag
            yield self.packed_size
            for value, extra in zip(self.encoded_value, self.extra_log):
                for _ in extra:
                    yield _[2]
                if value:
                    yield value
        return ' '.join(shuffle())


class OptionalTestCase(BaseTestCase):
    '''
    message Test {{
        optional {type} value = 1;
    }}
    '''
    def runTest(self):
        message1 = self.module.Test(value=self.tested_value)
        ba = bytearray()
        message1.serialize(ba)
        message2 = self.module.Test.deserialize(ba)
        self.assertEqual(message1.value, message2.value)
        self.assertEqual(message1, message2)

        message3 = self.module.Test()
        ba = bytearray()
        message3.serialize(ba)
        message4 = self.module.Test.deserialize(ba)
        self.assertEqual(message3, message4)

        self.assertEqual(len(ba), 0)
        self.assertNotEqual(message1, message3)
        self.assertNotEqual(message1, message4)
        self.assertNotEqual(message2, message3)
        self.assertNotEqual(message2, message4)
        
        self.assertRaises(AttributeError, getattr, message3, 'value')
        self.assertRaises(AttributeError, getattr, message4, 'value')

class TestSuite(unittest.TestSuite):
    tested_values = ()
    extra_log = itertools.repeat([])

    @classmethod
    def get_tests(cls):
        type_name = cls.__name__.replace('_', '')
        for number, (value, encoded, extra) in enumerate(
                zip(cls.tested_values, cls.encoded_values, cls.extra_log)):
            yield SimpleTestCase(type_name, value, number)
            yield SimpleTestDebugCase(
                type_name, value, cls.T, encoded, extra, number)
            pass

        yield RepeatableTestCase(type_name, cls.tested_values, 0)
        yield RepeatableTestDebugCase(type_name, cls.tested_values, cls.T,
            cls.encoded_values, cls.extra_log, 0)
        
        yield RepeatablePackedTestCase(type_name, cls.tested_values, 0)
        yield RepeatablePackedTestDebugCase(type_name, cls.tested_values, cls.T,
            cls.encoded_values, cls.extra_log, cls.packed_size, 0)

        for number, value in enumerate(cls.tested_values):
            yield OptionalTestCase(type_name, value, number)

    def __init__(self, tests=[]):
        tests = list(tests)
        tests.extend(self.get_tests())
        unittest.TestSuite.__init__(self, tests)
