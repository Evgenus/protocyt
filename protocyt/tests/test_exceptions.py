# standart
import unittest
# internal
from protocyt import meta

class Class1(meta.ProtocoledClass):
    '''
    message Test1 {
        required int32 a = 1;
    }
    message Class1 {
      required Test1 c = 3;
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
      repeated int32 d = 4;
    }
    '''

class ExceptionsTest(unittest.TestCase):
    def test_1(self):
        'bad message'
        ba = bytearray('\x1a\x03')
        self.assertRaises(Exception, Class1.deserialize, ba)

    def test_2(self):
        'bad message'
        ba = bytearray('\x00')
        self.assertRaises(Exception, Class1.deserialize, ba)

    def test_3(self):
        'bad tag'
        ba = bytearray('\x1a\x03\xF8')
        self.assertRaises(Exception, Class1.deserialize, ba)

    def test_4(self):
        'bad number'
        ba = bytearray('\x1a\x03\x08\xFF')
        self.assertRaises(Exception, Class1.deserialize, ba)

    def test_5(self):
        'bad string'
        ba = bytearray('\x12\x07\x74\x65\x73\x74\x69')
        self.assertRaises(Exception, Class2.deserialize, ba)

    def test_6(self):
        'bad repeated field'
        ba = bytearray('\x22\x07\x03\x8E\x02\x9E\xA7\x05')
        self.assertRaises(Exception, Class3.deserialize, ba)

    def test_7(self):
        'bad repeated field'
        ba = bytearray('\x22\x06\x03\x8E\x02\x9E\xA7\xF5')
        self.assertRaises(Exception, Class3.deserialize, ba)

