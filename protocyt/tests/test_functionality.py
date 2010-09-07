# standart
import unittest
import inspect
# internal
from protocyt import meta, protoc, classes

def make_hex(string):
    return ' '.join('%02X' % ord(i) for i in string)

class Class1(meta.ProtocoledClass):
    '''
    message Class1 {
      required int32 a = 1;
    }
    '''

class Class1_2(meta.ProtocoledClass):
    '''
    message Class1_2 {
      required int32 a = 1;
    }
    '''

class Class2(meta.ProtocoledClass):
    '''
    message Class2 {
      required string b = 2;
    }
    '''


class Class3(meta.ProtocoledClass):
    '''
    message Class3 {
      message Class1 {
        required int32 a = 1;
      }
      required Class1 c = 3;
    }
    '''

class Class4(meta.ProtocoledClass):
    '''
    message Class4 {
      repeated int32 d = 4;
      extensions 0 to max;
    }
    '''

class Class5(meta.ProtocoledClass):
    '''
    message Class5 {
      extensions 1;
      required int32 a = 1;
      required int32 b = 2;
    }
    '''


class FunctionalityTest(unittest.TestCase):
    def test_01(self):
        'bytearray output'
        instance = Class1(150)
        ba = bytearray()
        instance.serialize(ba)
        self.assertEqual(make_hex(str(ba)), '08 96 01')

    def test_02(self):
        'string output'
        instance = Class1(150)
        self.assertEqual(
            make_hex(instance.SerializePartialToString()), '08 96 01')

    def test_03(self):
        '__ne__'
        instance1 = Class1(150)
        instance2 = Class1(120)
        self.assertNotEqual(instance1, instance2)

    def test_04(self):
        '__ne__'
        instance1 = Class1(150)
        instance2 = Class1_2(150)
        self.assertNotEqual(instance1, instance2)

    def test_05(self):
        'output'
        instance = Class2('testing')
        ba = bytearray()
        instance.serialize(ba)
        self.assertEqual(make_hex(str(ba)), '12 07 74 65 73 74 69 6E 67')

    def test_06(self):
        'output'
        instance = Class3(Class3.Class1(150))
        ba = bytearray()
        instance.serialize(ba)
        self.assertEqual(make_hex(str(ba)), '1A 03 08 96 01')

    def test_07(self):
        'output'
        instance = Class4([3, 270, 86942])
        ba = bytearray()
        instance.serialize(ba)
        self.assertEqual(make_hex(str(ba)), '22 06 03 8E 02 9E A7 05')
        self.assertEqual(instance.Extensions['d'], instance.d)
        self.assertEqual(instance.Extensions.d, instance.d)

    def test_08(self):
        'Extensions get'
        instance = Class5(150, 350)
        self.assertEqual(instance.Extensions['a'], 150)

    def test_09(self):
        'Extensions set by attribute'
        instance = Class5(150, 350)
        instance.Extensions.a = 250
        self.assertEqual(instance.Extensions['a'], 250)
        self.assertEqual(instance.a, 250)

    def test_10(self):
        'Extensions set by item'
        instance = Class5(150, 350)
        instance.Extensions['a'] = 250
        self.assertEqual(instance.Extensions.a, 250)
        self.assertEqual(instance.a, 250)

    def test_11(self):
        'field not in Extensions get as item'
        instance = Class5(150, 350)
        self.assertRaises(KeyError, instance.Extensions.__getitem__, 'b')

    def test_12(self):
        'field not in Extensions get as attribute'
        instance = Class5(150, 350)
        self.assertRaises(AttributeError, getattr, instance.Extensions, 'b')

    def test_13(self):
        'field not in Extensions set by item'
        instance = Class5(150, 350)
        self.assertRaises(KeyError, instance.Extensions.__setitem__, 'b', 400)

    def test_14(self):
        'field not in Extensions set by attribute'
        instance = Class5(150, 350)
        self.assertRaises(AttributeError, setattr, instance.Extensions, 'b', 1)

    def test_15(self):
        'pretty method'
        protocol = protoc.protocol_from_source(inspect.cleandoc('''
            message Class3 {
              message Class1 {
                required int32 a = 1;
              }
              required Class1 c = 3;
            }
            '''))
        list(protocol.pretty(classes.State(protocol)))
