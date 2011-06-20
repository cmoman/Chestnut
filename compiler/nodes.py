from lepl import *
from collections import namedtuple, defaultdict
from templates import *
from symboltable import scalar_types, data_types
from symboltable import SymbolTable, Scope, Keyword, Variable, Window, Data, ParallelFunction, SequentialFunction, DisplayWindow
import random, numpy

symbolTable = SymbolTable()

def check_is_symbol(name, environment=symbolTable):
    if not environment.lookup(name):
        raise CompilerException("Error, the symbol '%s' was used but it hasn't been declared yet" % name)

def check_type(symbol, *requiredTypes):
    if type(symbol) not in requiredTypes:
        if len(requiredTypes) == 1:
            raise CompilerException("Error, the symbol '%s' is a %s, but a symbol of type %s was expected" % \
                    (symbol.name, type(symbol), requiredTypes[0]))
        else:
            raise CompilerException("Error, the symbol '%s' is a %s, but one of %s was expected" % \
                    (symbol.name, type(symbol), ','.join(requiredTypes)))


def check_dimensions_are_equal(leftData, rightData):
    assert type(leftData) == type(rightData) == Data
    if (not leftData.width == rightData.width) or (not leftData.height == rightData.height):
        raise CompilerException("Error, '%s' (%s, %s) and '%s' (%s, %s) have different dimensions." % \
         (rightData.name, rightData.width, rightData.height, leftData.name, leftData.width, leftData.height))


def extract_line_info(function):
    def wrapper(obj, env=defaultdict(bool)):
        node_info = obj # obj[0:-2]
        start_line, end_line = (0, 0) #obj[-2:]
        return function(obj, node_info, start_line, end_line, env)
    return wrapper

class Type(str):
    def to_cpp(self, env=None):
        return type_map[self]
    def evaluate(self, env):
        return

#helpers so that we don't get errors about undefined to_cpp methods
class Symbol(str):
    def to_cpp(self, env=None):
        check_is_symbol(self)
        return self
    def evaluate(self, env):
        symbol = env.lookup(self)
        if type(symbol) == Variable:
            return symbol.value
        elif type(symbol) == Data:
            return symbol
        else:
            raise Exception

class String(str):
    def to_cpp(self, env=None):
        return self
    def evaluate(self, env):
        return self
class Integer(int):
    to_cpp = lambda self, env=None: str(self)
    evaluate = lambda self, env: self
class Real(float):
    to_cpp = lambda self, env=None: str(self)
    evaluate = lambda self, env: self
class Bool(object):
    def __init__(self, value):
        self._value = bool(value == 'yes')
    def __nonzero__(self):
        return self._value
    def to_cpp(self, env=None):
        return str(self._value).lowercase()
    def evaluate(self, env):
        return self._value

#helper to convert sub-members into strings
def cpp_tuple(obj, env=defaultdict(bool)):
    return tuple(map(lambda element: element.to_cpp(env), obj))

#helper to do nice code indenting
def indent(code, indent_first_line=True):
    if indent_first_line:
        code = '  ' + code
    return code.replace('\n', '\n  ')

#helper functions to check for errors and to print them in a nice way
class CompilerException(Exception): pass
class InternalException(Exception): pass

#helper functions to emulate return, break
class InterpreterException(Exception): pass
class InterpreterReturn(Exception): pass
class InterpreterBreak(Exception): pass

class RuntimeWindow:
    def __init__(self, x, y, data):
        self.data = data
        self.x = x
        self.y = y

    def prop(self, prop):
        properties = { 'topLeft' : self.topLeft,
                    'top' : self.top,
                    'topRight' : self.topRight,
                    'left' : self.left,
                    'center' : self.center,
                    'bottomLeft' : self.bottomLeft,
                    'bottom' : self.bottom,
                    'bottomRight' : self.bottomRight,
                    'x' : self.x,
                    'y' : self.y,
                    'width' : self.width,
                    'height' : self.height }

        return properties[prop]



    @property
    def width(self):
        return self.data.width
    @property
    def height(self):
        return self.data.height

    @property
    def topLeft(self):
        return self.data.at((self.x-1) % self.width, (self.y-1) % self.height)

    @property
    def top(self):
        return self.data.at((self.x) % self.width, (self.y-1) % self.height)

    @property
    def topRight(self):
        return self.data.at((self.x+1) % self.width, (self.y-1) % self.height)

    @property
    def left(self):
        return self.data.at((self.x-1) % self.width, (self.y) % self.height)

    @property
    def center(self):
        return self.data.at((self.x) % self.width, (self.y) % self.height)

    @property
    def right(self):
        return self.data.at((self.x+1) % self.width, (self.y) % self.height)

    @property
    def bottomLeft(self):
        return self.data.at((self.x-1) % self.width, (self.y+1) % self.height)

    @property
    def bottom(self):
        return self.data.at((self.x) % self.width, (self.y+1) % self.height)

    @property
    def bottomRight(self):
        return self.data.at((self.x+1) % self.width, (self.y+1) % self.height)





### Nodes ###
# Operators
class Not(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "!%s" % cpp_tuple(self, env)
    def evaluate(self, env):
        return not self[0].evaluate(env)
class Neg(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "-%s" % cpp_tuple(self, env)
    def evaluate(self, env):
        return -self[0].evaluate(env)

class Mul(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s * %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) * self[1].evaluate(env)
class Div(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "((float)%s / %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) / self[1].evaluate(env)
class Mod(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "((int)%s %% %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) % self[1].evaluate(env)

class Add(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s + %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) + self[1].evaluate(env)
class Sub(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s - %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) - self[1].evaluate(env)

class LessThan(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s < %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) < self[1].evaluate(env)
class LessThanOrEqual(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s <= %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) <= self[1].evaluate(env)
class GreaterThan(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s > %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) > self[1].evaluate(env)
class GreaterThanOrEqual(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s >= %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) >= self[1].evaluate(env)

class Equal(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s == %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) == self[1].evaluate(env)
class NotEqual(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s != %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return not (self[0].evaluate(env) == self[1].evaluate(env))

class BooleanAnd(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s && %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) and self[1].evaluate(env)

class BooleanOr(List):
    def to_cpp(self, env=defaultdict(bool)):
        return "(%s || %s)" % cpp_tuple(self, env)
    def evaluate(self, env):
        return self[0].evaluate(env) or self[1].evaluate(env)

class Assignment(List):
    def to_cpp(self, env=defaultdict(bool)):
        return '%s = %s' % cpp_tuple(self, env)
    def evaluate(self, env):
        symbol = env.lookup(self[0])
        symbol.value = self[1].evaluate(env)
        return symbol.value
# End Operators

# Other structures
class Program(List): pass

class VariableDeclaration(List):
    def to_cpp(self, env=defaultdict(bool)):
        type, name = self[0], self[1]
        symbolTable.add(Variable(name, type))
        if len(self) == 3: # we have an initialization
            env = defaultdict(bool, variable_to_assign=name)
            return '%s %s;\n%s' % cpp_tuple(self, env)
        else:
            return '%s %s;' % cpp_tuple(self, env)
    def evaluate(self, env):
        type, name = self[0], self[1]
        var = env.add(Variable(name, type))
        if len(self) == 3: # we have an initialization
            var.value = self[2].evaluate(env)


class DataDeclaration(List):
  def to_cpp(self, env=defaultdict(bool)):
    if len(self) == 2: #only name and type, no size or initialization
      type_, name = self
      symbolTable.add(Data(name, type_, 0, 0)) #TODO: fix to not have 0,0 for uninitialized

    elif len(self) == 3: # adds a size
      type_, name, size = self
      symbolTable.add(Data(name, type_, size.width, size.height))
      return create_data(type_, name, size)

    elif len(self) == 4: # adds an initialization
      type_, name, size, initialization = self
      symbolTable.add(Data(name, type_, size.width, size.height))
      env = defaultdict(bool, data_to_assign=name)
      return '%s\n %s' % (create_data(type_, name, size), initialization.to_cpp(env))

  def evaluate(self, env):
    if len(self) == 2: #only name and type, no size or initialization
      type_, name = self
      env.add(Data(name, type_, 0, 0)) #TODO: fix to not have 0,0 for uninitialized

    elif len(self) == 3: # adds a size
      type_, name, size = self
      env.add(Data(name, type_, size.width, size.height))

    elif len(self) == 4: # adds an initialization
      type_, name, size, initialization = self
      symbol = env.add(Data(name, type_, size.width, size.height))

      symbol.value = initialization.evaluate(env)

host_function_template = """\
%(location)s%(type)s %(function_name)s(%(parameters)s) %(block)s
"""
class SequentialFunctionDeclaration(List):
    def to_cpp(self, env=defaultdict(bool)):
        env = defaultdict(bool, sequential=True)
        type_, name, parameters, block = self
        symbolTable.add(SequentialFunction(name, type_, parameters, ok_for_device=True, node=self))
        symbolTable.createScope()
        for parameter in parameters:
            symbolTable.add(Variable(name=parameter.name, type=parameter.type))


        environment = { 'function_name' : name,
                        'type' : type_,
                        'location' : '__host__ __device__\n',
                        'parameters' : ', '.join(map(lambda param: '%s %s' % param, tuple(parameters))),
                        'block' : block.to_cpp(env) }

        host_function = host_function_template % environment

        symbolTable.removeScope()
        return host_function

    def evaluate(self, env):
        type_, name, parameters, block = self
        env.add(SequentialFunction(name, type_, parameters, ok_for_device=True, node=self))

    def run(self, arguments, env):
        type_, name, parameters, block = self
        env.createScope()

        for parameter, argument in zip(parameters, arguments):
            symbol = env.add(Variable(name=parameter.name, type=parameter.type))
            symbol.value = argument # argument was evaluated before the function call 

        result = block.evaluate(env)

        env.removeScope()
        return result

class ParallelFunctionDeclaration(List):
    def to_cpp(self, env=defaultdict(bool)):
        type_, name, parameters, block = self
        symbolTable.add(ParallelFunction(name, type_, parameters, node=self))
        symbolTable.createScope()

        windowCount = 0
        for parameter in parameters:
            if parameter.type in data_types:
                symbolTable.add(Window(name=parameter.name, number=windowCount))
                windowCount += 1
            else:
                symbolTable.add(Variable(name=parameter.name, type=parameter.type))

        device_function = create_device_function(self)

        symbolTable.removeScope()
        return device_function

    def evaluate(self, env):
        type_, name, parameters, block = self
        env.add(ParallelFunction(name, type_, parameters, node=self))

    def run(self, arguments, env):
        name, parameters, block = self
        env.createScope()

        for parameter, argument in zip(parameters, arguments):
            symbol = env.add(Variable(name=parameter.name, type=parameter.type))
            symbol.value = argument # argument was evaluated before the function call 

        result = block.evaluate(env)

        env.removeScope()
        return result

class Parameters(List): pass
class Block(List):
    @extract_line_info
    def to_cpp(self, block, start_line, end_line, env):
        print 'start: %s, end: %s' % (start_line, end_line)
        symbolTable.createScope()
        cpp = '{\n' + indent('\n'.join(cpp_tuple(block, env))) + '\n}'
        symbolTable.removeScope()
        return cpp
    @extract_line_info
    def evaluate(self, block, start_line, end_line, env):
        env.createScope()
        for statement in self:
            statement.evaluate(env)
        env.removeScope()


class VariableInitialization(List):
    def to_cpp(self, env=defaultdict(bool)):
        return '%s = %s;' % (env['variable_to_assign'], self[0].to_cpp(env))
    def evaluate(self, env):
        return self[0].evaluate(env)

class DataInitialization(List):
    def to_cpp(self, env=defaultdict(bool)):
        return self[0].to_cpp(env)
    def evaluate(self, env):
        return self[0].evaluate(env)


display_template = """\
{
  FunctionIterator _start = makeStartIterator(%(input)s.width, %(input)s.height);

  thrust::copy(thrust::make_transform_iterator(_start, %(display_function)s_functor<%(template_types)s>(%(input)s)),
               thrust::make_transform_iterator(_start+%(input)s.length(), %(display_function)s_functor<%(template_types)s>(%(input)s)),
               _%(input)s_display.displayData());
}
_%(input)s_display.updateGL();
_app.processEvents();
"""
class DataDisplay(List):
    def to_cpp(self, env=defaultdict(bool)):
        data = symbolTable.lookup(self[0])

        print self
        if len(self) == 2:
            display_function = symbolTable.lookup(self[1])
            check_type(display_function, ParallelFunction)
            if display_function.type != 'Color':
                raise CompilerException("Display function '%s' returns data of type '%s'. Display functions must return 'Color'."
                        % (display_function.name, display_function.type))
            parameters = display_function.parameters
            if len(parameters) != 1:
                raise CompilerException("Display function '%s' takes %d parameters. Display functions must only take 1 parameter"
                        % (display_function.name, len(parameters)))
            #if data.type != parameters[0].type:
            #    raise CompilerException("Display function takes a parameter of type '%s' but the data '%s' is of the type '%s'"
            #            % (parameters[0].type, data.name, data.type))

            display_function = display_function.name
        else:
            display_function = '_chestnut_default_color_conversion'

        template_types = 'color, %s' % type_map[data.type]

        display_env = { 'input' : data.name,
                        'template_types' : template_types,
                        'display_function' : display_function }

        code = ""
        if not data.has_display:
            data.has_display = True
            symbolTable.displayWindows.append(DisplayWindow(data.name, 'Chestnut Output [%s]' % data.name, data.width, data.height))
        code += display_template % display_env
        return code

    def evaluate(self, env):
        pass

print_template = """
{
  // Create host vector to hold data
  thrust::host_vector<%(type)s> hostData(%(length)s);

  // transfer data back to host
  %(data)s.copyTo(hostData);

  printArray2D(hostData, %(width)s, %(height)s);
}
"""
class DataPrint(List):
    def to_cpp(self, env=defaultdict(bool)):
        data = self[0]
        check_is_symbol(data)
        data = symbolTable.lookup(data)
        check_type(data, Data)
        return print_template % { 'data' : data.name,
                                  'type' : type_map[data.type],
                                  'width' : data.width,
                                  'height' : data.height,
                                  'length' : data.width*data.height }
    def evaluate(self, env):
        data = self[0]
        data = env.lookup(data)

        print data.value

class Print(List):
    def to_cpp(self, env=defaultdict(bool)):
        num_format_placeholders = self[0].to_cpp(env).count('%s')
        num_args = len(self)-1

        if num_format_placeholders != num_args:
            raise CompilerException("Error, there are %s format specifiers but %s arguments to print()" % \
                    (num_format_placeholders, num_args))
        format_substrings = self[0].to_cpp(env).split('%s')

        code = 'std::cout'
        for substring, placeholder in zip(format_substrings[:-1], cpp_tuple(self[1:], env)):
            code += ' << "%s"' % substring
            code += ' << %s' % placeholder
        code += ' << "%s" << std::endl' % format_substrings[-1]

        return code
    def evaluate(self, env):
        text = self[0]
        args = map(lambda arg: arg.evaluate(env), self[1:])

        print(text % tuple(args))



sequential_function_call_template = """\
%(function_name)s(%(arguments)s)
"""
class SequentialFunctionCall(List):
    def to_cpp(self, env=defaultdict(bool)):
        function = self[0]
        arguments = self[1:][0]

        check_is_symbol(function)
        function = symbolTable.lookup(function)
        check_type(function, SequentialFunction)

        if not len(arguments) == len(function.parameters):
            print arguments
            raise CompilerException("Error, sequential function ':%s' takes %s parameters but %s were given" % \
                    (function.name, len(function.parameters), len(arguments)))


        return sequential_function_call_template % { 'function_name' : function.name,
                                                     'arguments' : ', '.join(cpp_tuple(arguments, env)) }

    def evaluate(self, env):
        function = self[0]
        arguments = map(lambda obj: obj.evaluate(env), self[1:][0])

        #check_is_symbol(function)
        function = env.lookup(function)
        #check_type(function, SequentialFunction)

        try:
            function.node.run(arguments, env)
        except InterpreterBreak:
            raise InterpreterException('Error: caught break statement outside of a loop in function %s', function.name)
        except InterpreterReturn as return_value:
            return return_value[0]


class Size(List):
    @property
    def width(self): return self[0]
    @property
    def height(self): return self[1]

class Parameter(List):
    @property
    def type(self): return self[0]
    @property
    def name(self): return self[1]

class Statement(List):
    def to_cpp(self, env=defaultdict(bool)):
        return ''.join(cpp_tuple(self, env)) + ';'
    def evaluate(self, env):
        return self[0].evaluate(env)

class Expressions(List):
    def to_cpp(self, env=defaultdict(bool)):
        return ''.join(cpp_tuple(self, env))



coordinates = {
        'x' : '_x',
        'y' : '_y',
        'width' : '_width',
        'height' : '_height' }

color_properties = { # Screen is apparently BGR not RGB
        'red' : 'z',
        'green' : 'y',
        'blue' : 'x',
        'alpha' : 'w' }


property_template = """\
%(name)s.%(property)s(%(parameters)s)\
"""
class Property(List):
    def to_cpp(self, env=defaultdict(bool)):
        name, property_ = self
        check_is_symbol(name)
        symbol = symbolTable.lookup(name)


        #check_type(symbol, Variable) #TODO: Support Data properties


        #TODO: Pull in support for window nums other than 0
        if type(symbol) == Window:
            if property_ not in ['topLeft', 'top', 'topRight', 'left', 'center', 'right', 'bottomLeft', 'bottom', 'bottomRight']:
                raise CompilerException("Error, property '%s' not part of the data window '%s'" % (property_, name))
            return property_template % { 'name' : name,
                                         'property' : property_,
                                         'parameters' : coordinates['x'] + ', ' + coordinates['y'] }
        elif type(symbol) == Keyword and symbol.name == 'parallel':
            if property_ in coordinates:
                return coordinates[property_];
            else:
                raise CompilerError('Property %s not found for function %s' % (property_, name))
        elif type(symbol) == Variable:
            if symbol.type == 'Color':
                return '%s.%s' % (symbol.name, color_properties[property_])
        else:
            print symbolTable
            print self
            raise Exception

    def evaluate(self, env):
        check_is_symbol(self[0], env)
        symbol = env.lookup(self[0])
        #check_type(symbol, Variable)

        if type(symbol) == Window:
            return symbol.value.prop(self[1])

        else:
            print self
            raise Exception


class Return(List):
    def to_cpp(self, env=defaultdict(bool)):
        return 'return %s;' % self[0].to_cpp(env)
    def evaluate(self, env):
        raise InterpreterReturn(self[0].evaluate(env))

class Break(List):
    def to_cpp(self, env=defaultdict(bool)):
        return 'break;'
    def evaluate(self, env):
        raise InterpreterBreak

class If(List):
    def to_cpp(self, env=defaultdict(bool)):
        if len(self) == 2: # simple if (condition) {statement}
          return 'if (%s) %s' % cpp_tuple(self, env)
        elif len(self) == 3: # full if (condition) {statement} else {statement}
          return 'if (%s) %s else %s' % cpp_tuple(self, env)
        else:
          raise InternalException("Wrong type of if statement with %s length" % len(self))
    def evaluate(self, env):
        if len(self) == 2: # simple if (condition) {statement}
            condition, statement = self
            if condition.evaluate(env):
                statement.evaluate(env)
        elif len(self) == 3: # full if (condition) {statement} else {statement}
            condition, if_statement, else_statement
            if condition.evaluate(env):
                if_statement.evaluate(env)
            else:
                else_statement.evaluate(env)

        else:
          raise InternalException("Wrong type of if statement with %s length" % len(self))


class While(List):
    def to_cpp(self, env=defaultdict(bool)):
        return 'while (%s) %s' % cpp_tuple(self, env)
    def evaluate(self, env):
        expression, statement = self
        while (True):
            result = expression.evaluate(env)
            if not result:
                break
            try:
                statement.evaluate(env)
            except InterpreterBreak:
                break

class Read(List): pass
class Write(List): pass


class ParallelAssignment(List):
    def to_cpp(self, env=defaultdict(bool)):
        env = defaultdict(bool, data_to_assign=self[0])
        return self[1].to_cpp(env)

    def evaluate(self, env):
        name = self[0]
        data = env.lookup(name)

        if type(data) == Data:
            data.value = self[1].evaluate(env, data)
        elif type(data) == Variable:
            data = self[1].evaluate(env, data)



#TODO: Fix up for new-style arrays
random_template = """\
{
  // A CPU-driven random function that fills the data
  // Create host vector to hold the random numbers
  thrust::host_vector<%(type)s> randoms(%(data)s.width*%(data)s.height);

  // Generate the random numbers
  thrust::generate(randoms.begin(), randoms.end(), rand);

  // Copy data from CPU to GPU
  thrust::copy(randoms.begin(), randoms.end(), %(data)s.thrustPointer());

  // Mod between %(min_value)s and %(max_value)s
  thrust::for_each(%(data)s.thrustPointer(), %(data)s.thrustEndPointer(), randoms_helper_functor(%(min_value)s, %(max_value)s));
}
"""
class ParallelRandom(List):
    def to_cpp(self, env=defaultdict(bool)):
        output = env['data_to_assign']
        if not output:
            raise InternalException("The environment '%s' doesn't have a 'data_to_assign' variable set" % env)
        check_is_symbol(output)
        output = symbolTable.lookup(output)
        check_type(output, Data)

        if len(self) == 2:
            min_limit, max_limit = cpp_tuple(self[0:2])
        else:
            min_limit, max_limit = ('0', 'INT_MAX')

        return random_template % { 'data' : output.name,
                                   'min_value' : min_limit,
                                   'max_value' : max_limit,
                                   'type' : type_map[output.type] }
    def evaluate(self, env, output):
        if len(self) == 2:
            min_limit, max_limit = self
            max_limit -= 1
        else:
            min_limit = 0
            max_limit = (2**32)/2-1


        for y in xrange(output.height):
            for x in xrange(output.width):
                output.setAt(x, y, random.randint(min_limit, max_limit))

        return output.value

reduce_template = """
// Reducing '%(input_data)s' to the single value '%(output_variable)s'
{
  %(output_variable)s = thrust::reduce(%(input_data)s.thrustPointer(), %(input_data)s.thrustEndPointer());
}
"""
class ParallelReduce(List):
    def to_cpp(self, env=defaultdict(bool)):
        function = None
        output = env['variable_to_assign']
        if not output:
            raise InternalException("The environment '%s' doesn't have a 'data_to_assign' variable set" % env)

        if len(self) == 1:
            input = self[0]
        elif len(self) == 2:
            input, function = self
        else:
            raise InternalException("Wrong list length to parallel reduce")

        check_is_symbol(input)
        check_is_symbol(output)

        input = symbolTable.lookup(input)
        output = symbolTable.lookup(output)

        check_type(input, Data)
        check_type(output, Variable)

        #TODO: Actually use function
        if function:
            print('Warning: functions in reduce() calls are not implemented yet')
            check_is_symbol(function)
            function = symbolTable.lookup(function)
            check_type(function, SequentialFunction)
            return ''

        else:
            return reduce_template % { 'input_data' : input.name,
                                       'output_variable' : output.name }

    def evaluate(self, env, output=None):
        function = None
        if len(self) == 1:
            input = self[0]
        elif len(self) == 2:
            input, function = self
        else:
            raise InternalException("Wrong list length to parallel reduce")

        input = env.lookup(input)
        return numpy.add.reduce(input.value.reshape(input.width*input.height))

sort_template = """
// Sorting '%(input_data)s' and placing it into '%(output_data)s'

// Thrust then performs the hard work, and we swap pointers at the end if needed
{
  %(input_data)s.copyTo(%(output_data)s); //TODO: Check if pointers are the same... and don't copy
  thrust::sort(%(output_data)s.thrustPointer(), %(output_data)s.thrustEndPointer());
}
"""
class ParallelSort(List):
    def to_cpp(self, env=defaultdict(bool)):
        function = None
        output = env['data_to_assign']
        if not output:
            raise InternalException("The environment '%s' doesn't have a 'data_to_assign' variable set" % env)

        if len(self) == 1:
            input = self[0]
        elif len(self) == 2:
            input, function = self
        else:
            raise InternalException("Wrong list length to parallel sort")

        check_is_symbol(input)
        check_is_symbol(output)

        input = symbolTable.lookup(input)
        output = symbolTable.lookup(output)

        check_type(input, Data)
        check_type(output, Data)

        #TODO: Actually use function
        if function:
            print('Warning: functions in reduce() calls are not implemented yet')
            check_is_symbol(function)
            function = symbolTable.lookup(function)
            check_type(function, SequentialFunction)
            return ''

        else:
            return sort_template % { 'input_data' : input.name,
                                     'output_data' : output.name }

    def evaluate(self, env, output=None):
        if len(self) == 1:
            input, function = self[0], None
        elif len(self) == 2:
            input, function = self
        else:
            raise InternalException("Wrong list length to parallel sort")

        input = env.lookup(input)

        #TODO: Actually use function
        if function:
            print('Warning: functions in reduce() calls are not implemented yet')
            return

        temp = input.value.copy().reshape(input.height*input.width)
        temp.sort()
        return temp.reshape(input.height, input.width)


map_template = """
{
    FunctionIterator startIterator = makeStartIterator(%(size_name)s.width, %(size_name)s.height);

    thrust::transform_iterator<%(function)s_functor<%(input_output_types)s>, FunctionIterator>
    iterator = thrust::make_transform_iterator(startIterator, %(function)s_functor<%(input_output_types)s>(%(variables)s));

    Array2d<%(output_type)s> temp_array = _allocator.arrayWithSize<%(output_type)s>(%(size_name)s.width, %(size_name)s.height);

    thrust::copy(iterator, iterator+%(size_name)s.length(), temp_array.thrustPointer());

    %(output_data)s.swapDataWith(temp_array);
    _allocator.releaseArray(temp_array);
}
"""
class ParallelFunctionCall(List):
    def to_cpp(self, env=defaultdict(bool)):
        output = env['data_to_assign']
        if not output:
            raise InternalException("The environment '%s' doesn't have a 'data_to_assign' variable set" % env)

        container, function, arguments = self

        container = symbolTable.lookup(container)
        if container.type in ['Size1', 'Size2', 'Size3']:
            if type(size) is not Size2:
                return InternalException("Sizes other than Size2 are not supported")
            size = container
        elif type(container) == Data:
            size = container.name + '.size()'

        check_is_symbol(function)
        function = symbolTable.lookup(function)
        check_type(function, ParallelFunction)

        if not len(arguments) == len(function.parameters):
            print arguments
            raise CompilerException("Error, parallel function ':%s' takes %s parameters but %s were given" % \
                    (function.name, len(function.parameters), len(arguments)))

        check_is_symbol(output)
        output = symbolTable.lookup(output)
        check_type(output, Data)

        variables = []
        input_output_types = [type_map[function.type]]

        for argument, parameter in zip(arguments, function.parameters):
            if parameter.type in data_types:
                input_output_types.append(type_map[symbolTable.lookup(argument.to_cpp(env)).type])

            variables.append(argument.to_cpp(env))


        return map_template % { 'output_data' : output.name,
                                'variables' : ', '.join(variables),
                                'input_output_types' : ', '.join(input_output_types),
                                'function' : function.name,
                                'size_name' : size,
                                'output_type' : type_map[function.type] }

    def evaluate(self, env, output):
        name = self[0]
        function = env.lookup(name)

        arguments = map(lambda arg: arg.evaluate(env), self[1])

        array = output.array.copy()

        for y in xrange(output.height):
            for x in xrange(output.width):
                args = map(lambda arg: RuntimeWindow(x, y, arg), arguments)

                try:
                    value = function.node.run(args, env)
                except InterpreterBreak:
                    raise InterpreterException('Error: caught break statement outside of a loop in function %s', function.name)
                except InterpreterReturn as return_value:
                    value = return_value[0]

                array[y, x] = value

        return array

