# standart
import unittest
import struct
# internal
from . import utils

class _uint32(utils.TestSuite):
    tested_values = [0, 2**31, 2**32-1]

class _int32(utils.TestSuite):
    tested_values = [0, 2**31-1, -2**31]

class _sint32(utils.TestSuite):
    tested_values = [0, 1, -1, 2**31-1, -2**31]

class _fixed32(utils.TestSuite):
    tested_values = [0, 2**31, 2**32-1]

class _sfixed32(utils.TestSuite):
    tested_values = [0, 1, -1]

class _uint64(utils.TestSuite):
    tested_values = [0, 2**31, 2**32-1, 2**63, 2**64-1]

class _int64(utils.TestSuite):
    tested_values = [0, 2**31-1, -2**31, 2**63-1, -2**63]

class _sint64(utils.TestSuite):
    tested_values = [0, 1, -1, 2**31-1, -2**31, 2**63-1, -2**63]

class _fixed64(utils.TestSuite):
    tested_values = [0, 2**31, 2**64-1]

class _sfixed64(utils.TestSuite):
    tested_values = [0, 1, -1]

class _bool(utils.TestSuite):
    tested_values = [False, True]

class _string(utils.TestSuite):
    tested_values = ['', 'testing', ':)'*300]

def make_float(value):
    return struct.unpack('f', struct.pack('f', value))[0]

class _float(utils.TestSuite):
    tested_values = map(make_float, [
        0.0,
        4.94e-324, 1e-310, 7e-308, 6.626e-34,
        0.1, 0.5, 3.14, 263.44582062374053, 6.022e23, 1e30,
        -4.94e-324, -1e-310, -7e-308, -6.626e-34,
        -0.1, -0.5, -3.14, -263.44582062374053, -6.022e23, -1e30,
        ])

def make_double(value):
    return struct.unpack('d', struct.pack('d', value))[0]

class _double(utils.TestSuite):
    tested_values = map(make_double, [
        0.0,
        4.94e-324, 1e-310, 7e-308, 6.626e-34,
        0.1, 0.5, 3.14, 263.44582062374053, 6.022e23, 1e30,
        -4.94e-324, -1e-310, -7e-308, -6.626e-34,
        -0.1, -0.5, -3.14, -263.44582062374053, -6.022e23, -1e30,
        ])

def get_suites():
    for value in globals().itervalues():
        if (isinstance(value, type)
        and issubclass(value, (unittest.TestSuite, unittest.TestCase))):
            yield value()

def test_all():
    for suite in get_suites():
        for test in suite.get_tests():
            yield test

if __name__ == '__main__':
    alltests = unittest.TestSuite(get_suites())
    unittest.TextTestRunner(verbosity=2).run(alltests)
