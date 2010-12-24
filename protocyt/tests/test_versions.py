# standart
import unittest
# internal
from protocyt import meta

class Old1(meta.ProtocoledClass):
    '''
    message Old1 {
      required int32 a = 1;
      repeated int32 b = 2;
      optional int32 c = 3;
      required int32 d = 4;
      repeated int32 e = 5;
      optional int32 f = 6;
    }
    '''

class New1(meta.ProtocoledClass):
    '''
    message New1 {
      required int32 d = 4;
      repeated int32 e = 5;
      optional int32 f = 6;
      required int32 g = 7;
      repeated int32 h = 8;
      optional int32 i = 9;
    }
    '''

class Old1p(meta.ProtocoledClass):
    '''
    message Old1p {
      required int32 a = 1;
      repeated int32 b = 2 [packed=true];
      optional int32 c = 3;
      required int32 d = 4;
      repeated int32 e = 5 [packed=true];
      optional int32 f = 6;
    }
    '''

class New1p(meta.ProtocoledClass):
    '''
    message New1p {
      required int32 d = 4;
      repeated int32 e = 5 [packed=true];
      optional int32 f = 6;
      required int32 g = 7;
      repeated int32 h = 8 [packed=true];
      optional int32 i = 9;
    }
    '''

class Old2(meta.ProtocoledClass):
    '''
    message Old2 {
      message SubMessage {
        required int32 a = 1;
      }
      required SubMessage a = 1;
    }
    '''

class New2(meta.ProtocoledClass):
    '''
    message New2 {
      required int32 a = 1;
    }
    '''

class Old3(meta.ProtocoledClass):
    '''
    message Old3 {
      message SubMessage {
        required fixed32 a = 1;
      }
      required SubMessage a = 1;
    }
    '''

class New3(meta.ProtocoledClass):
    '''
    message New3 {
      message SubMessage {
        required float a = 1;
      }
      required SubMessage a = 1;
    }
    '''

class Old4(meta.ProtocoledClass):
    '''
    message Old4 {
      required int32 a = 1;
      required int32 b = 2;
    }
    '''

class New4(meta.ProtocoledClass):
    '''
    message New4 {
      required int32 a = 2;
      required int32 b = 1;
    }
    '''

class Old5(meta.ProtocoledClass):
    '''
    message Old5 {
      required uint32 a = 1;
    }
    '''

class New5(meta.ProtocoledClass):
    '''
    message New5 {
      required int32 a = 1;
    }
    '''

class Old6(meta.ProtocoledClass):
    '''
    message Old6 {
      message SubMessage {
        required int32 a = 1;
      }
      required SubMessage a = 1;
    }
    '''

class New6(meta.ProtocoledClass):
    '''
    message New6 {
      required string a = 1;
    }
    '''

class ExceptionsTest(unittest.TestCase):
    def test_1(self):
        'changed fields set, some fields was skiped'
        ba = bytearray()
        Old1(a=1, b=[1, 2, 3], c=4, d=5, e=[6, 7, 8], f=9).serialize(ba)
        instance = New1.deserialize(ba)
        self.assertFalse(hasattr(instance, 'a'))
        self.assertFalse(hasattr(instance, 'b'))
        self.assertFalse(hasattr(instance, 'c'))

        self.assertTrue(hasattr(instance, 'd'))
        self.assertTrue(hasattr(instance, 'e'))
        self.assertTrue(hasattr(instance, 'f'))

        self.assertFalse(hasattr(instance, 'g'))
        self.assertTrue(hasattr(instance, 'h'))
        self.assertTrue(hasattr(instance, 'i'))

    def test_1p(self):
        'changed fields set, some fields was skiped'
        ba = bytearray()
        Old1p(a=1, b=[1, 2, 3], c=4, d=5, e=[6, 7, 8], f=9).serialize(ba)
        instance = New1p.deserialize(ba)
        self.assertFalse(hasattr(instance, 'a'))
        self.assertFalse(hasattr(instance, 'b'))
        self.assertFalse(hasattr(instance, 'c'))

        self.assertTrue(hasattr(instance, 'd'))
        self.assertTrue(hasattr(instance, 'e'))
        self.assertTrue(hasattr(instance, 'f'))

        self.assertFalse(hasattr(instance, 'g'))
        self.assertTrue(hasattr(instance, 'h'))
        self.assertTrue(hasattr(instance, 'i'))

    def test_2(self):
        'bad message'
        ba = bytearray()
        Old2(a=Old2.SubMessage(1)).serialize(ba)
        self.assertRaises(Exception, New2.deserialize, ba)

    def test_3(self):
        'type changed but size is compatible'
        ba = bytearray()
        Old3(a=Old3.SubMessage(1)).serialize(ba)
        instance1 = Old3.deserialize(ba)
        instance2 = New3.deserialize(ba)
        self.assertEqual(instance1.a.a, 1)
        self.assertNotEqual(instance2.a.a, 1)
        self.assertTrue(isinstance(instance2.a.a, float))

    def test_4(self):
        'order changed'
        ba = bytearray()
        Old4(1, 2).serialize(ba)
        instance1 = Old4.deserialize(ba)
        instance2 = New4.deserialize(ba)
        self.assertEqual(instance1.a, instance2.b)
        self.assertEqual(instance1.b, instance2.a)

    def test_5(self):
        'unsigned -> signed'
        ba = bytearray()
        Old5(2**31).serialize(ba)
        instance1 = Old5.deserialize(ba)
        instance2 = New5.deserialize(ba)
        self.assertEqual(instance2.a, -2**31)

    def test_6(self):
        'message -> string'
        ba = bytearray()
        Old6(a=Old6.SubMessage(150)).serialize(ba)
        instance1 = Old6.deserialize(ba)
        instance2 = New6.deserialize(ba)
        self.assertEqual(instance2.a, '\x08\x96\x01')
        ba_sub = bytearray(instance2.a)
        sub = Old6.SubMessage.deserialize(ba_sub)
        self.assertEqual(sub.a, 150)

