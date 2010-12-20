# standart
import sys
import tempfile
import hashlib
import distutils.ccompiler
from lib2to3.pgen2.parse import ParseError
from Cython.Compiler.Main import compile as cython_compile, CompilationOptions
# internal
from .path import Path
from .parser import ProtoParser
from .compiler import CodeGenerator
from .templatable import DocTemplatable
from . import classes

__all__ = [
    'NoProtocolDefined',
    'NameNotDefined',
    'protocol_from_source',
    'protocol_from_file',
    'from_source',
    'from_file',
    'package_from_file',
    'main',
    'make_parser',
    ]

try:
    import sysconfig
except ImportError:
    from distutils import sysconfig

class NoProtocolDefined(DocTemplatable, RuntimeError):
    'Single protocol should be defined in source, but {0} was found'

class NameNotDefined(DocTemplatable, RuntimeError):
    """
    Output module name wasn't specified and wasn't found in protocol properties
    """

def protocol_from_source(source, lookupdir=None):
    if lookupdir is None:
        lookupdir = Path.cwd()

    protocyt_dir = Path.from_file(__file__).up()
    grammar_file = str(protocyt_dir / 'ProtobufGrammar.txt')
    parser = ProtoParser(grammar_file)

    tree = parser.parse_string(source)

    visitor = CodeGenerator(parser.grammar, lookupdir)

    parts = list(visitor.visit(tree))
    if len(parts)!=1:
        raise NoProtocolDefined(len(parts))
    else:
        return parts[0]

def protocol_from_file(filename):
    name = filename.filename
    with open(filename.str()) as stream:
        source = stream.read()
    return protocol_from_source(source, filename.up())

# Dependency injection to make protocol import other protocols
classes.Protocol.from_file = staticmethod(protocol_from_file)

def from_source(source, name=None, output_dir=None, check=False, keep=False):
    out_file = (output_dir / name).add_ext(sysconfig.get_config_var('SO'))

    protocol = protocol_from_source(source, output_dir)

    temp_dir = Path.from_file(tempfile.gettempdir()) / name
    if not temp_dir.exists():
        temp_dir.makedirs()

    protocol_data = protocol.data()

    source_chks = hashlib.sha1(source).hexdigest()
    protoc_chks = hashlib.sha1(protocol_data).hexdigest()
    if out_file.exists():
        if check:
            checkfile_name = (output_dir / name).add_ext('.checksum')
            if checkfile_name.exists():
                with checkfile_name.open('rt') as stream:
                    source_ctrl = stream.readline().strip()
                    output_ctrl = stream.readline().strip()
                    protoc_ctrl = stream.readline().strip()
                with out_file.open('rb') as stream:
                    output_chks = hashlib.sha1(stream.read()).hexdigest()
                if (source_chks == source_ctrl
                and output_chks == output_ctrl
                and protoc_chks == protoc_ctrl):
                    return False
        out_file.remove()

    if name is None:
        name = protocol.properties.get('package')
    if name is None:
        raise NameNotDefined()

    path = temp_dir / name
    pyx_file = path.add_ext('.pyx')
    with pyx_file.open('wb') as stream:
        stream.write(protocol_data)

    options = CompilationOptions(
        verbose=True,
        )
    cython_compile(pyx_file.str(), options=options)

    compiler = distutils.ccompiler.new_compiler(verbose=1)

    if sys.platform == 'win32':
        protocyt_dir = Path.from_file(__file__).up()
        compiler.add_include_dir(str(protocyt_dir / 'includes'))
        libs_dir = Path.from_file(sysconfig.get_config_var('BINDIR')) / 'libs'
        compiler.add_library_dir(libs_dir.str())

    python_path = Path.from_file(sys.exec_prefix)
    compiler.add_include_dir(sysconfig.get_python_inc())

    object_files = compiler.compile([path.add_ext('.c').str()],
        extra_postargs=['-fPIC'],
        output_dir=temp_dir.str())
    compiler.link_shared_lib(object_files, name, output_dir=temp_dir.str())

    compiler.move_file(
        compiler.library_filename(path.str(), 'shared'),
        out_file.str()
        )

    if not keep:
        temp_dir.remove()
        result = True
    else:
        result = temp_dir
    
    if check:
        checkfile_name = (output_dir / name).add_ext('.checksum')
        with out_file.open('rb') as stream:
            output_chks = hashlib.sha1(stream.read()).hexdigest()
        with checkfile_name.open('wt') as stream:
            stream.write('{0}\n{1}\n{2}\n'.format(
                source_chks, output_chks, protoc_chks))

    return result

def from_file(filename, output_dir=None, check=False, keep=True):
    name = filename.filename
    with open(filename.str()) as stream:
        source = stream.read()

    if output_dir is None:
        output_dir = filename.up()

    return from_source(source, name, output_dir, check=check, keep=keep)

def package_from_file(filename, output_dir=None):
    name = filename.filename
    with open(filename.str()) as stream:
        source = stream.read()

    if output_dir is None:
        output_dir = filename.up()
    output_dir = output_dir / name

    if output_dir.exists():
        output_dir.remove()

    output_dir.makedirs()

    proto_file = output_dir / '_core.proto'
    with open(proto_file.str(), 'wt') as stream:
        stream.write(source)

    from classes import ENVIRONMENT
    template = ENVIRONMENT.from_file(
        Path.from_file(__file__).up() / 'package.pytempl')

    package_file = output_dir / '__init__.py'

    with open(package_file.str(), 'wt') as stream:
        stream.write(template.render())

def main(options):
    filename = Path.from_file(options.input)
    if options.out_dir is None:
        output_dir = None
    else:
        output_dir = Path.from_file(options.out_dir)
    if options.package:
        package_from_file(filename, output_dir)
    else:
        result = from_file(filename, output_dir, keep=options.keep)
        if options.keep:
            print 'Temporary files places at {0:s}'.format(result)

def make_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
        type=str,
        help='Input protocol file.')
    parser.add_argument('--out-dir', '-o',
        type=str, dest='out_dir', default=None,
        help='Output directory where generated files will be placed.'
        'If you omit this option files will be generated in same dirrectory '
        'where input file placed.')
    parser.add_argument('--package', '-p',
        action='store_true', dest='package', default=False,
        help='If this option enabled compiler will generates package instead '
        'of module. Package will autocompile protocol if it is changed.')
    parser.add_argument('--keep', '-k',
        action='store_true', dest='keep', default=False,
        help="Keep intermediate files (*.pyx, *.c)")
    return parser

if __name__ == '__main__':
    main(make_parser().parse_args())
