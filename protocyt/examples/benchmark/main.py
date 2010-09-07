# standart
import sys
import cPickle as pickle
from time import time
from operator import itemgetter
from functools import partial
import webbrowser
from collections import defaultdict
# internal
from protocyt import path
from package import Node

def createNode(size, stop):
    if stop>0:
        return Node([
            Node.Child('{0}_{1}'.format(stop, i), createNode(size, stop-1))
            for i in range(size)
            ])
    else:
        return Node([])

if __name__=='__main__':
    def test(size, stop):
        count = sum(size**i for i in range(stop+1))
        yield 'count', count

        def wrap_testing(name, tester):
            print name,
            start = time()
            counter = 0
            while time() - start < 1 or counter < 10:
                counter+=1
                tester()
                sys.stdout.write('.')
            end = time()
            print
            result = 1000 * (end - start) / counter
            print '{0:.3f} milliseconds per {1}'.format(result, name)

            yield name, result

        print 'Initialization [{0}-{1}] {2}'.format(size, stop, count)
        tree = createNode(size, stop)

# ____________________________________________________________________________ #

        def test_serialize():
            tree.serialize(bytearray())

        def test_deserialize(ba):
            Node.deserialize(ba)

        def test_dumps():
            pickle.dumps(tree, 2)

        def test_loads(data):
            pickle.loads(data)


        ba = bytearray()
        tree.serialize(ba)
        data = pickle.dumps(tree, 2)

        tests = (
            ('serialize', test_serialize),
            ('deserialize', partial(test_deserialize, ba)),
            ('pickle.dumps', test_dumps),
            ('pickle.loads', partial(test_loads, data)),
            )

        for name, tester in tests:
            for _ in wrap_testing(name, tester):
                yield _

    tests = [
        ('small',   2, 9),
        ('medium',  2, 12),
        ('big',     2, 15),

        ('small',   4, 6),
        ('medium',  4, 7),
        ('big',     4, 8),

        ('small',   8, 3),
        ('medium',  8, 4),
        ('big',     8, 5),
        ]
    start = time()
    
    class WrappedOutput(object):
        def __init__(self, wrapped):
            self.wrapped = wrapped
            self.buff = ''
        def write(self, text):
            self.buff+=text
            self.wrapped.write(text)
        def flush(self):
            self.wrapped.flush()
        def __str__(self):
            return self.buff

    sys.stdout = WrappedOutput(sys.stdout)
    
    lines = [(name, tuple(test(size, stop))) for name, size, stop in tests]
    print 'Total test running time {0:.3f} seconds'.format(time()-start)
    from protocyt.classes import ENVIRONMENT
    root = path.Path.from_file(__file__).up()
    template_file = root / 'result.template'
    template = ENVIRONMENT.from_file(template_file)
    result_file = path.Path.from_file(__file__).up() / 'result.html'

    results = defaultdict(list)
    bars = []
    for name, line in sorted(lines, key=lambda x: x[1][2]):
        for key, value in line:
            if key not in bars:
                bars.append(key)
        results[name].append(dict(line))

    with result_file.open('wb') as stream:
        stream.write(template.render(
            results=sorted(results.iteritems(), key=itemgetter(0)),
            bars=bars,
            output=str(sys.stdout),
            ))

    webbrowser.open(result_file.str())
