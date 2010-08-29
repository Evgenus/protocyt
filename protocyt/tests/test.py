import protocol
from nose.tools import *

def make_hex(string):
    return ' '.join('%02X' % ord(i) for i in string)

# 1. Simple message with string

def test1_1():
    'bytearray output'
    instance = protocol.Test1(150)
    ba = bytearray()
    instance.serialize(ba)
    eq_(make_hex(str(ba)), '08 96 01')

def test1_2():
    'string output'
    instance = protocol.Test1(150)
    eq_(make_hex(instance.SerializePartialToString()), '08 96 01')

def test1_3():
    '__eq__'
    instance1 = protocol.Test1(150)
    instance2 = protocol.Test1(150)
    eq_(instance1, instance2)

def test1_4():
    '__ne__'
    instance1 = protocol.Test1(150)
    instance2 = protocol.Test1(120)
    assert_not_equal(instance1, instance2)

def test1_5():
    '__ne__'
    instance1 = protocol.Test1(150)
    instance2 = protocol.Test1_2(150)
    assert_not_equal(instance1, instance2)

def test1_6():
    '__eq__ after deserialization'
    instance1 = protocol.Test1(150)
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test1.deserialize(ba)
    eq_(instance1.a, instance2.a)
    eq_(instance1, instance2)

# 2. Message with string

def test2_1():
    'output'
    instance = protocol.Test2('testing')
    ba = bytearray()
    instance.serialize(ba)
    eq_(make_hex(str(ba)), '12 07 74 65 73 74 69 6E 67')

def test2_2():
    '__eq__ after deserialization'
    instance1 = protocol.Test2('testing')
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test2.deserialize(ba)
    eq_(instance1.b, instance2.b)
    eq_(instance1, instance2)

# 3. Compount message

def test3_1():
    'output'
    instance = protocol.Test3(protocol.Test1(150))
    ba = bytearray()
    instance.serialize(ba)
    eq_(make_hex(str(ba)), '1A 03 08 96 01')

def test3_2():
    '__eq__ after deserialization'
    instance1 = protocol.Test3(protocol.Test1(150))
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test3.deserialize(ba)
    eq_(instance1.c.a, instance2.c.a)
    eq_(instance1.c, instance2.c)
    eq_(instance1, instance2)

# 4. Message with repeated field

def test4_1():
    'output'
    instance = protocol.Test4([3, 270, 86942])
    ba = bytearray()
    instance.serialize(ba)
    eq_(make_hex(str(ba)), '22 06 03 8E 02 9E A7 05')
    eq_(instance.Extensions['d'], instance.d)
    eq_(instance.Extensions.d, instance.d)

def test4_2():
    '__eq__ after deserialization'
    instance1 = protocol.Test4([3, 270, 86942])
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test4.deserialize(ba)
    eq_(instance1, instance2)

# 5. Multy-field message with Extensions

def test5_1():
    'Extensions get'
    instance = protocol.Test5(150, 350)
    eq_(instance.Extensions['a'], 150)

def test5_2():
    'Extensions set by attribute'
    instance = protocol.Test5(150, 350)
    instance.Extensions.a = 250
    eq_(instance.Extensions['a'], 250)
    eq_(instance.a, 250)

def test5_3():
    'Extensions set by item'
    instance = protocol.Test5(150, 350)
    instance.Extensions['a'] = 250
    eq_(instance.Extensions.a, 250)
    eq_(instance.a, 250)

@raises(KeyError)
def test5_4():
    'field not in Extensions get as item'
    instance = protocol.Test5(150, 350)
    instance.Extensions['b']

@raises(AttributeError)
def test5_5():
    'field not in Extensions get as attribute'
    instance = protocol.Test5(150, 350)
    instance.Extensions.b

@raises(KeyError)
def test5_6():
    'field not in Extensions set by item'
    instance = protocol.Test5(150, 350)
    instance.Extensions['b'] = 400

@raises(AttributeError)
def test5_7():
    'field not in Extensions set by attribute'
    instance = protocol.Test5(150, 350)
    instance.Extensions.b = 400

def test5_8():
    '__eq__ after deserialization'
    instance1 = protocol.Test5(150, 350)
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test5.deserialize(ba)
    eq_(instance1.a, instance2.a)
    eq_(instance1.b, instance2.b)
    eq_(instance1, instance2)

# 6. Scoped message type

def test6():
    'output'
    eq_(protocol.Test6_SubMessage, protocol.Test6.SubMessage)
    instance = protocol.Test6.SubMessage(150)
    ba = bytearray()
    instance.serialize(ba)
    eq_(make_hex(str(ba)), '08 96 01')

# 7. Compound message with scoped message type

def test7():
    '__eq__ after deserialization'
    instance1 = protocol.Test7(protocol.Test7.SubMessage(150))
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test7.deserialize(ba)
    eq_(instance1.d.a, instance2.d.a)
    eq_(instance1.d, instance2.d)
    eq_(instance1, instance2)

# 8. Repeated field of messages

def test8():
    '__eq__ after deserialization'
    instance1 = protocol.Test8([
        protocol.Test8.SubMessage('a', 1),
        protocol.Test8.SubMessage('b', 2),
        protocol.Test8.SubMessage('c', 3),
        ])
    ba = bytearray()
    instance1.serialize(ba)
    instance2 = protocol.Test8.deserialize(ba)
    eq_(instance1.values, instance2.values)
    eq_(instance1, instance2)
