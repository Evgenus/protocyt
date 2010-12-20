# standart
import unittest
import inspect
import sys
# internal
from protocyt import protoc, path

def make_hex(string):
    return ' '.join('%02X' % ord(i) for i in string)

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

class OptionalTestCase(BaseTestCase):
    '''
    message Test {{
        optional {type} value = 1;
    }}
    '''
    def runTest(self):
        message1 = self.module.Test(value = self.tested_value)
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

        self.assertNotEqual(message1, message3)
        self.assertNotEqual(message1, message4)
        self.assertNotEqual(message2, message3)
        self.assertNotEqual(message2, message4)

        self.assertRaises(AttributeError, getattr, message3, 'value')
        self.assertRaises(AttributeError, getattr, message4, 'value')

class ImmSimpleTestCase(SimpleTestCase):
    '''
    message Test {{
        option immutable = true;
        required {type} value = 1;
    }}
    '''

class ImmRepeatableTestCase(RepeatableTestCase):
    '''
    message Test {{
        option immutable = true;
        repeated {type} value = 1;
    }}
    '''

class ImmOptionalTestCase(OptionalTestCase):
    '''
    message Test {{
        option immutable = true;
        optional {type} value = 1;
    }}
    '''

class TestSuite(unittest.TestSuite):
    tested_values = ()

    @classmethod
    def get_tests(cls):
        type_name = cls.__name__.replace('_', '')
        for number, value in enumerate(cls.tested_values):
            yield SimpleTestCase(type_name, value, number)
            yield ImmSimpleTestCase(type_name, value, number)

        yield RepeatableTestCase(type_name, cls.tested_values, 0)
        yield ImmRepeatableTestCase(type_name, cls.tested_values, 0)

        for number, value in enumerate(cls.tested_values):
            yield OptionalTestCase(type_name, value, number)
            yield ImmOptionalTestCase(type_name, value, number)

    def __init__(self, tests=[]):
        tests = list(tests)
        tests.extend(self.get_tests())
        unittest.TestSuite.__init__(self, tests)
