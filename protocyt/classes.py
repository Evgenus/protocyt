'''
This module holds classes to represent protocol structure and performs code
generation.
'''

# standart
import re
from textwrap import dedent
from collections import deque
from heapq import heappush, heappop
import __builtin__
# external
import jinja2
# internal
from .path import Path

class JinjaEnvironment(jinja2.Environment):
    'Few helpers added to environment'
    def from_file(self, path):
        with path.open('rt') as stream:
            return self.from_string(stream.read())

ENVIRONMENT = JinjaEnvironment(
    block_start_string='<%',
    block_end_string='>',
    variable_start_string='${',
    variable_end_string='}',
    comment_start_string='<%doc>',
    comment_end_string='</%doc>',
    line_statement_prefix='%',
    line_comment_prefix='##~',
    )

def makedict(names, default=None):
    'Creates dict from list of keys encoded into string and default value'
    return dict.fromkeys(names.split(','), default)

def mergedicts(*dicts):
    'Merges pack of dicts updating them into empty dict in same order'
    result = {}
    for one in dicts:
        result.update(one)
    return result

class State(object):
    'Code generation context'
    def __init__(self, protocol):
        self.protocol = protocol
        self.namespace = []
    def push_ns(self, name):
        'Dive into message generation'
        self.namespace.append(name)
        return name
    def pop_ns(self):
        'Rise from message'
        return self.namespace.pop()
    def find_name(self, *name):
        'Search message by given short in current namespace'
        path = list(self.namespace)
        while path:
            result = self.protocol.find_name(*(tuple(path) + name))
            if result:
                return result
            else:
                path.pop()
        result = self.protocol.find_name(*name)
        if result:
            return result
        else:
            raise NameError(name)
    def get_ns(self):
        "Gettin full name for current message knowing it's namespace path"
        return '_'.join(self.namespace)
    def __str__(self):
        return 'State{0!r}'.format(self.__dict__)

class Property(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    def set(self, where):
        for name, value in self.kwargs.iteritems():
            where.set_property(name, value)

class Field(object):
    TYPE_TAG = mergedicts(
        makedict('int32,int64,uint32,uint64,sint32,sint64,bool,enum', 0),
        makedict('fixed64,sfixed64,double', 1),
        makedict('string,bytes,message,repeated', 2),
        makedict('fixed32,sfixed32,float', 5),
        )
    def __init__(self, index, name, type, default=None):
        self.index = int(index)
        self.name = name
        self.type = type
        self.default = default
    def set(self, where):
        where.set_field(self)
    def get_tag(self, state):
        tag = self.TYPE_TAG.get(self.kind)
        if tag is not None:
            return tag
        tag = self.TYPE_TAG.get(self.type)
        if tag is not None:
            return tag
        tag = self.TYPE_TAG[state.find_name(self.type).tag]
        return tag
    def pretty(self, state):
        tag = self.TYPE_TAG.get(self.type)
        if tag is None:
            tag = self.TYPE_TAG[state.find_name(self.type).tag]
        yield 'Field: {name} {type} {kind} {tag}'.format(
            tag=tag,
            **self.__dict__)

class Enum(object):
    tag = 'enum'
    def __init__(self, name):
        self.name = name
    def set(self, where):
        where.set_enum(self)
    def pretty(self, state):
        yield 'Enum: {name}'.format(**self.__dict__)

class Part(object):
    '''
    Basic renderable type
    '''
    def indent1(self, line, tab=1):
        return '    '*tab+line
    def indent(self, text, tab=1):
        return ''.join(
            self.indent1(line, tab)
            for line in text.splitlines(True)
            )
    def title(self, char, text, size=80):
        length = len(text)
        first = (size - length)/2 - 3
        last = size - 6 - first - length
        return '# ' + (char*first) + ' ' + text + ' ' + (char*last) + ' #'

    def render(self, state):
        return self.template.render(
            this=self,
            state=state,
            **__builtin__.__dict__)

class Extension(object):
    def __init__(self, start, end=None):
        self.start = start
        if end is None:
            self.end = self.start
        else:
            self.end = end
    def set(self, where):
        where.add_extension(self)
    def get_range(self, max_index):
        start = int(self.start)
        end = max_index if self.end == 'max' else int(self.end)
        return range(start, end+1)

class Compond(Part):
    '''
    Base class for compound entities like protocol and message
    '''
    def __init__(self):
        self.messages = {}
        self.enums = {}
        self.messages_order = []
    def set_message(self, message):
        self.messages[message.name] = message
        self.messages_order.append(message.name)
    def set_enum(self, enum):
        self.enums[enum.name] = enum
    def pretty(self, state):
        for name, message in self.messages.iteritems():
            for part in message.pretty(state):
                yield self.indent1(part)
        for name, enum in self.enums.iteritems():
            for part in enum.pretty(state):
                yield self.indent1(part)

class Message(Compond):
    '''
    Represents single message
    '''
    template = ENVIRONMENT.from_file(
        Path.from_file(__file__).up() / 'message.pytempl')
    structure = ENVIRONMENT.from_file(
        Path.from_file(__file__).up() / 'structure.pytempl')
    tag = 'message'
    max_index = 0
    fullname = None
    def __init__(self, name, doc):
        self.name = name
        self.doc = doc
        self.fields_repeated = []
        self.fields_required = []
        self.fields_optional = []
        self.fields_by_name = {}
        self.fields_by_index = {}
        self.extensions = []
        self.extended_fields = dict()
        super(Message, self).__init__()

    def set_field(self, field):
        heappush(getattr(self, 'fields_'+field.kind), (field.index, field))
        self.max_index = max(self.max_index, field.index)
        self.fields_by_index[field.index] = field
        self.fields_by_name[field.name] = field

    def add_extension(self, extension):
        self.extensions.append(extension)

    def compile_extensions(self):
        extension_range = set()
        for extension in self.extensions:
            extension_range.update(extension.get_range(self.max_index))
        for index in extension_range:
            field = self.fields_by_index.get(index)
            if field is not None:
                self.extended_fields[field.name] = field

    def render(self, state):
        self.compile_extensions()
        state.push_ns(self.name)
        self.fullname = state.get_ns()
        result = super(Message, self).render(state)
        state.pop_ns()
        return result

    def render_structure(self, state):
        state.push_ns(self.name)
        result = self.structure.render(
            this=self,
            state=state,
            **__builtin__.__dict__)
        state.pop_ns()
        return result

    def set(self, where):
        where.set_message(self)
    def pretty(self, state):
        yield 'Message: {name}'.format(**self.__dict__)
        state.push_ns(self.name)
        for name, field in self.fields_by_name.iteritems():
            for part in field.pretty(state):
                yield self.indent1(part)
        for part in super(Message, self).pretty(state):
            yield part
        state.pop_ns()

class Protocol(Compond):
    template = ENVIRONMENT.from_file(
        Path.from_file(__file__).up() / 'file.pytempl')
    apply_filter = False
    def __init__(self):
        self.properties = {}
        super(Protocol, self).__init__()
    def set_property(self, name, value):
        self.properties[name] = value
    def pretty(self, state):
        yield 'Protocol: {properties!r}'.format(**self.__dict__)
        for part in super(Protocol, self).pretty(state):
            yield part
    def data(self):
        state = State(self)
        return self.render(state)
    def find_name(self, *name):
        parts = deque(name)
        root = self
        while parts:
            part = parts.popleft()
            if part in root.messages:
                root = root.messages[part]
            else:
                if part in root.enums:
                    if parts:
                        return None
                    else:
                        return root.enums[part]
                else:
                    return None
        return root
