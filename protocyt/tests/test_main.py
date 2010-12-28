# standart
import unittest
import struct
# internal
from . import utils

class _uint32(utils.TestSuite):
    tested_values = [0, 2**31, 2**32-1]
    T = 0
    encoded_values = ['00', '80 80 80 80 08', 'FF FF FF FF 0F']
    packed_size = '%02X' % 11

class _int32(utils.TestSuite):
    tested_values = [0, 2**31-1, -2**31]
    T = 0
    encoded_values = ['00', 'FF FF FF FF 07', '80 80 80 80 08']
    packed_size = '%02X' % 11

class _sint32(utils.TestSuite):
    tested_values = [0, 1, -1, 2**31-1, -2**31]
    T = 0
    encoded_values = ['00', '02', 'FF FF FF FF 0F', 'FE FF FF FF 0F', '01']
    packed_size = '%02X' % 13

class _fixed32(utils.TestSuite):
    tested_values = [0, 2**31, 2**32-1]
    T = 5
    encoded_values = ['00 00 00 00', '00 00 00 80', 'FF FF FF FF']
    packed_size = '%02X' % 12

class _sfixed32(utils.TestSuite):
    tested_values = [0, 1, -1]
    T = 5
    encoded_values = ['00 00 00 00', '01 00 00 00', 'FF FF FF FF']
    packed_size = '%02X' % 12

class _uint64(utils.TestSuite):
    tested_values = [0, 2**31, 2**32-1, 2**63, 2**64-1]
    T = 0
    encoded_values = ['00', '80 80 80 80 08', 'FF FF FF FF 0F',
        '80 80 80 80 80 80 80 80 80 01', 'FF FF FF FF FF FF FF FF FF 01']
    packed_size = '%02X' % 31

class _int64(utils.TestSuite):
    tested_values = [0, 2**31-1, -2**31, 2**63-1, -2**63]
    T = 0
    encoded_values = ['00', 'FF FF FF FF 07', '80 80 80 80 F8 FF FF FF FF 01',
        'FF FF FF FF FF FF FF FF 7F', '80 80 80 80 80 80 80 80 80 01']
    packed_size = '%02X' % 35

class _sint64(utils.TestSuite):
    tested_values = [0, 1, -1, 2**31-1, -2**31, 2**63-1, -2**63]
    T = 0
    encoded_values = ['00', '02', 'FF FF FF FF FF FF FF FF FF 01',
        'FE FF FF FF 0F', '81 80 80 80 F0 FF FF FF FF 01',
        'FE FF FF FF FF FF FF FF FF 01', '01']
    packed_size = '%02X' % 38

class _fixed64(utils.TestSuite):
    tested_values = [0, 2**31, 2**64-1]
    T = 1
    encoded_values = [
        '00 00 00 00 00 00 00 00',
        '00 00 00 80 00 00 00 00',
        'FF FF FF FF FF FF FF FF',
        ]
    packed_size = '%02X' % 24

class _sfixed64(utils.TestSuite):
    tested_values = [0, 1, -1]
    T = 1
    encoded_values = [
        '00 00 00 00 00 00 00 00',
        '01 00 00 00 00 00 00 00',
        'FF FF FF FF FF FF FF FF',
        ]
    packed_size = '%02X' % 24

class _bool(utils.TestSuite):
    tested_values = [False, True]
    T = 0
    encoded_values = ['00', '01']
    packed_size = '%02X' % 2

class _string(utils.TestSuite):
    def wrap_strings(s): return s.decode('utf-8') if hasattr(s, 'decode') else s
    tested_values = list(map(wrap_strings, ['', 'testing', ':)'*300,]))
    T = 2
    encoded_values = ['', '74 65 73 74 69 6E 67', ' '.join(['3A 29']*300)]
    extra_log = [
        [('cb', 'size', '00')],
        [('cb', 'size', '07')],
        [('cb', 'size', 'D8 04')],
        ]
    packed_size = 'E3 04'

class _bytes(utils.TestSuite):
    tested_values = [b'', b'testing', b':)'*300]
    T = 2
    encoded_values = ['', '74 65 73 74 69 6E 67',  ' '.join(['3A 29']*300)]
    extra_log = [
        [('cb', 'size', '00')],
        [('cb', 'size', '07')],
        [('cb', 'size', 'D8 04')],
        ]
    packed_size = 'E3 04'

def make_float(value):
    return struct.unpack('f', struct.pack('f', value))[0]

class _float(utils.TestSuite):
    tested_values = list(map(make_float, [
        0.0,
        4.94e-324, 1e-310, 7e-308, 6.626e-34,
        0.1, 0.5, 3.14, 263.44582062374053, 6.022e23, 1e30,
        -4.94e-324, -1e-310, -7e-308, -6.626e-34,
        -0.1, -0.5, -3.14, -263.44582062374053, -6.022e23, -1e30,
        ]))
    T = 5
    encoded_values = [
        '00 00 00 00', '00 00 00 00', '00 00 00 00', '00 00 00 00',
        'C6 2F 5C 08', 'CD CC CC 3D', '00 00 00 3F', 'C3 F5 48 40',
        '11 B9 83 43', 'A8 0A FF 66', 'CA F2 49 71', '00 00 00 80',
        '00 00 00 80', '00 00 00 80', 'C6 2F 5C 88', 'CD CC CC BD',
        '00 00 00 BF', 'C3 F5 48 C0', '11 B9 83 C3', 'A8 0A FF E6',
        'CA F2 49 F1'
        ]
    packed_size = '%02X' % 84

def make_double(value):
    return struct.unpack('d', struct.pack('d', value))[0]

class _double(utils.TestSuite):
    tested_values = list(map(make_double, [
        0.0,
        4.94e-324, 1e-310, 7e-308, 6.626e-34,
        0.1, 0.5, 3.14, 263.44582062374053, 6.022e23, 1e30,
        -4.94e-324, -1e-310, -7e-308, -6.626e-34,
        -0.1, -0.5, -3.14, -263.44582062374053, -6.022e23, -1e30,
        ]))
    T = 1
    encoded_values = [
        '00 00 00 00 00 00 00 00', '01 00 00 00 00 00 00 00',
        '2B E6 70 8B 68 12 00 00', 'E0 AE 5A A4 EE 2A 29 00',
        '02 5F 44 C5 F8 85 0B 39', '9A 99 99 99 99 99 B9 3F',
        '00 00 00 00 00 00 E0 3F', '1F 85 EB 51 B8 1E 09 40',
        '91 6D CE 14 22 77 70 40', '13 EA 57 F4 54 E1 DF 44',
        'EA 8C A0 39 59 3E 29 46', '01 00 00 00 00 00 00 80',
        '2B E6 70 8B 68 12 00 80', 'E0 AE 5A A4 EE 2A 29 80',
        '02 5F 44 C5 F8 85 0B B9', '9A 99 99 99 99 99 B9 BF',
        '00 00 00 00 00 00 E0 BF', '1F 85 EB 51 B8 1E 09 C0',
        '91 6D CE 14 22 77 70 C0', '13 EA 57 F4 54 E1 DF C4',
        'EA 8C A0 39 59 3E 29 C6'
        ]
    packed_size = 'A8 01'

def get_suites():
    for value in globals().values():
        if (isinstance(value, type)
        and issubclass(value, (unittest.TestSuite, unittest.TestCase))):
            yield value()

def test_all():
    from nose.tools import with_setup
    for suite in get_suites():
        for testCase in suite.get_tests():
            @with_setup(testCase.setUp, testCase.tearDown)
            def test():
                testCase.runTest()
            test.description = str(testCase)
            yield test

if __name__ == '__main__':
    alltests = unittest.TestSuite(get_suites())
    unittest.TextTestRunner(verbosity=2).run(alltests)
