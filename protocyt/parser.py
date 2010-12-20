# standart
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import driver

__all__ = [
    'ProtoParser',
    ]

class PNode(Node):
    def __init__(self, grammar, *args, **kwargs):
        self.grammar = grammar
        super(PNode, self).__init__(*args, **kwargs)
    def __repr__(self):
        """Return a canonical string representation."""
        return "%s(%s, %r)" % (self.__class__.__name__,
           self.grammar.number2symbol.get(self.type), self.children)
    def pretty(self, tab=4):
        yield '%s %s, ' % (
            self.__class__.__name__,
            self.grammar.number2symbol.get(self.type)
            )
        for child in self.children:
            if isinstance(child, PNode):
                for line in child.pretty(tab):
                    yield ' '*tab + line
            else:
                for line in child.__repr__().splitlines():
                    yield ' '*tab + line

class ProtoParser(object):
    def pconvert(self, gr, raw_node):
        type, value, context, children = raw_node
        if children or type in gr.number2symbol:
            return PNode(gr, type, children, context=context)
        else:
            return Leaf(type, value, context=context)

    def __init__(self, grammar_file):
        self.grammar = driver.load_grammar(grammar_file)
        self.driver = driver.Driver(self.grammar, convert=self.pconvert)

    def parse_string(self, src):
        src_patch = src.replace('//', '#//')
        return self.driver.parse_string(src_patch)
