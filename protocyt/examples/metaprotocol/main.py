from protocyt import meta

class Test(meta.ProtocoledClass):
    '''
    message Test {
        required int32 value = 1;
    }
    '''

def make_hex(string):
    return ' '.join('%02X' % ord(i) for i in string)

if __name__=='__main__':
    print "I am inherited from class in compiled protocol"
    print "This is my methods",
    print [name for name in dir(Test) if not name.startswith('_')]
    inst1 = Test(100500)
    ba = bytearray()
    inst1.serialize(ba)
    print "My instances could be serialized", make_hex(str(ba))
    inst2 = Test.deserialize(ba)
    print "... and deserialized"
    assert inst1 == inst2