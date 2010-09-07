# standart
import sys
import unittest
import inspect
# internal
from protocyt import path, protoc

class PackagesTest(unittest.TestCase):
    def setUp(self):
        self.path = path.Path.from_file(__file__).up()
        package = self.path / 'package'

    def test_01(self):
        source = inspect.cleandoc('''
        message Test {
            required int32 a = 1;
        }
        ''')
        proto_file = self.path / 'package.proto'
        with proto_file.open('wt') as stream:
            stream.write(source)
        protoc.package_from_file(proto_file, self.path)
        proto_file.remove()
        import package
        ba = bytearray()
        package.Test(150).serialize(ba)
        package.Test.deserialize(ba)
        del sys.modules[package.__name__]
        path = self.path / 'package'
        stat1 = path.stat()
        import package
        stat2 = path.stat()
        self.assertEqual(stat1, stat2)

    def tearDown(self):
        for path in (self.path / 'package').glob('__init__.*'):
            path.remove()
