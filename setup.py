from setuptools import setup

install_requires=[
    'cython >= 0.13',
    'jinja2 >= 2.5',
    'argparse',
    ]

setup(name='protocyt',
    version='0.1.5',
    description="Fast python port of protobuf",
    long_description="Compiles protobuf files into python extension modules using cython",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Programming Language :: Python"
        ],
    keywords='serialization data-format cython protobuf',
    author='Eugene Chernyshov',
    author_email='Chernyshov.Eugene@gmail.com',
    url='http://evgenus.github.com/protocyt/',
    license='LGPL',
    packages=['protocyt'],
    install_requires=install_requires,
    package_data=dict(
        protocyt = [
            'ProtobufGrammar.txt',
            'common.pytempl',
            'file.pytempl',
            'message.pytempl',
            'package.pytempl',
            'structure.pytempl',
            'includes/*.*',
            ]
        )
    )
