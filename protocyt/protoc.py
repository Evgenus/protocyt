# standart
import sys
import tempfile
import distutils.ccompiler
from lib2to3.pgen2.parse import ParseError
from Cython.Compiler.Main import compile as cython_compile
# internal
from .path import Path
from .parser import ProtoParser
from .compiler import CoreGenerator
from .templatable import DocTemplatable
from . import classes

def from_file(filename, output_dir=None):
    name = filename.filename
    with open(filename.str()) as stream:
        source = stream.read()

    if output_dir is None:
        output_dir = filename.up()

    from_source(source, name, output_dir)

class NoProtocolDefined(DocTemplatable, RuntimeError):
    'Single protocol should be defined in source, but {0} was found'

class NameNotDefined(DocTemplatable, RuntimeError):
    """
    Output module name wasn't specified and wasn't found in protocol properties
    """

def from_source(source, name=None, output_dir=None):
    protocyt_dir = Path.from_file(__file__).up()
    grammar_file = str(protocyt_dir / 'ProtobufGrammar.txt')
    parser = ProtoParser(grammar_file)

    tree = parser.parse_string(source)

    temp_dir = Path.from_file(tempfile.gettempdir()) / name
    if not temp_dir.exists():
        temp_dir.makedirs()

    visitor = CoreGenerator(parser.grammar)

    parts = list(visitor.visit(tree))
    if len(parts)!=1:
        raise NoProtocolDefined(len(parts))
    else:
        protocol = parts[0]

    if name is None:
        name = protocol.properties.get('package')
    if name is None:
        raise NameNotDefined()

    path = temp_dir / name
    pyx_file = path.add_ext('.pyx')
    with pyx_file.open('wb') as stream:
        stream.write(protocol.data())

    cython_compile(pyx_file.str())

    compiler = distutils.ccompiler.new_compiler()

    compiler.add_include_dir(str(protocyt_dir / 'includes'))

    python_path = Path.from_file(sys.exec_prefix)
    compiler.add_include_dir(str(python_path / 'include'))

    compiler.add_library_dir(str(python_path / 'libs'))

    object_files = compiler.compile([path.add_ext('.c').str()],
        output_dir=temp_dir.str())
    compiler.link_shared_lib(object_files, name, output_dir=temp_dir.str())

    out_file = (output_dir / name).add_ext('.pyd')
    if out_file.exists():
        out_file.remove()

    compiler.move_file(
        compiler.shared_object_filename(path.str()),
        out_file.str()
        )

def main(options):
    filename = Path.from_file(options.input)
    if options.out_dir is None:
        output_dir = None
    else:
        output_dir = Path.from_file(options.out_dir)
    from_file(filename, output_dir)

def make_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
        type=str)
    parser.add_argument('--out-dir', '-o',
        type=str, dest='out_dir', default=None)
    return parser

if __name__ == '__main__':
    main(make_parser().parse_args())

