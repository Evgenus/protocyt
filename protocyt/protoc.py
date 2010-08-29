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

def main(options):
    filename = Path.from_file(options.input)

    protocyt_dir = Path.from_file(__file__).up()
    grammar_file = str(protocyt_dir / 'ProtobufGrammar.txt')
    parser = ProtoParser(grammar_file)
    with open(filename.str()) as stream:
        tree = parser.parse_string(stream.read())

    name = filename.filename

    temp_dir = Path.from_file(tempfile.gettempdir()) / name
    if not temp_dir.exists():
        temp_dir.makedirs()

    path = temp_dir / name
    pyx_file = path.add_ext('.pyx')
    with pyx_file.open('wb') as stream:
        visitor = CoreGenerator(parser.grammar)
        for part in visitor.visit(tree):
            stream.write(part.data())

    cython_compile(pyx_file.str())

    compiler = distutils.ccompiler.new_compiler()

    compiler.add_include_dir(str(protocyt_dir / 'includes'))
    
    python_path = Path.from_file(sys.exec_prefix)
    compiler.add_include_dir(str(python_path / 'include'))

    compiler.add_library_dir(str(python_path / 'libs'))

    object_files = compiler.compile([path.add_ext('.c').str()],
        output_dir=temp_dir.str())
    compiler.link_shared_lib(object_files, name, output_dir=temp_dir.str())

    if options.out_dir is not None:
        output_dir = Path.from_file(options.out_dir)
    else:
        output_dir = filename.up()

    out_file = (output_dir / name).add_ext('.pyd')
    if out_file.exists():
        out_file.remove()

    compiler.move_file(
        compiler.shared_object_filename(path.str()),
        out_file.str()
        )

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

