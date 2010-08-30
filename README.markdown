Testing
-------

To check functionality of protocy you have to compile protocol for tests after
instalation executing:

    python -m protocyt.protoc protocyt/tests/protocol.proto
    
Then run tests using `nose`

    nosetests protocyt

Standart unittest are not provided yet.

Dependencies
------------

 - cython >= 0.13
 - jinja2
 - argparse


TODO
----

 - gain compatibility with *nix platform
 - gain compatibility with 64-bit systems
 - create protocol for classes via metaclasses, inheritance and docstrings
 - create autocompiling protocols as packages with compiler functionality