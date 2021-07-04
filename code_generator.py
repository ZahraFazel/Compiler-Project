from utils import Stack
from symbol_table import *
from semantic_checker import *


class CodeGeneration:
    def __init__(self):
        self.index = 1
        self.semantic_stack = Stack()
        self.symbol_table = SymbolTable()
        self.symbol_table.new_symbol('output', 500, None, 1, 0, 'void')
        self.symbol_table.new_symbol('dummydummydummydummydummydummydummydummy', 504, None, 1, 0, 'int')
        self.loop_scope_stack = Stack()
        self.current_scope = None
        self.pb = [''] * 500
        self.pb[0] = '(ASSIGN, #0, 500, )'
        self.data_index = 508
        self.temp_index = 1000
        self.main = 1
        self.semantic_checker = SemanticChecker()
        self.semantic_routines = {'#pid': self.pid, '#pop': self.pop, '#pnum': self.pnum, '#save_array': self.save_array,
                                  '#save': self.save, '#jpf': self.jpf, '#jp': self.jp, '#label': self.label,
                                  '#while_stmt': self.while_stmt, '#assign': self.assign, '#address_array': self.address_array,
                                  '#relop': self.relop, '#operator': self.operator, '#add_or_sub': self.add_or_sub,
                                  '#mult': self.mult, '#signed_num': self.signed_num, '#output': self.output,
                                  '#loop_size': self.loop_size, '#assign_for': self.assign_for, '#count': self.count,
                                  '#for_stmt': self.for_stmt, '#push_zero': self.push_zero, '#initial': self.initial,
                                  '#step': self.step, '#jp_main': self.jp_main, '#start_function': self.start_function,
                                  '#end_function': self.end_function, '#start_function_call': self.start_function_call,
                                  '#function_call': self.function_call, '#add_param': self.add_param,
                                  '#define_function': self.define_function, '#return': self._return,
                                  '#return_value': self.return_value, '#break': self._break, '#loop': self.loop,
                                  '#type': self.type, '#array_input': self.array_input, '#define_id': self.define_id,
                                  '#check_type': self.check_type}

    def code_gen(self, action_symbol, token=None, line_num=None):
        if action_symbol in ['#pid']:
            self.semantic_routines[action_symbol](token, line_num)
        elif action_symbol in ['#pnum', '#operator', '#type', '#define_id']:
            self.semantic_routines[action_symbol](token)
        elif action_symbol in ['#function_call', '#break', '#check_type', '#assign', '#relop', '#add_or_sub', '#mult',
                               '#signed_num']:
            self.semantic_routines[action_symbol](line_num)
        else:
            self.semantic_routines[action_symbol]()

    def get_temp(self):
        res = self.temp_index
        self.temp_index += 4
        return res

    def find_temp(self):
        temp = self.temp_index
        self.temp_index += 1
        return temp

    def jp_main(self):
        line_num = self.symbol_table.find_symbol_by_name('main', None).starts_at
        t = self.pb[self.main - 1]
        self.pb[self.main - 1] = '(JP, {}, , )'.format(line_num - 2)
        self.pb[self.main] = t

    def start_function(self):
        function = self.symbol_table.symbols[-1]
        function.type = function.type + '_function'
        if self.symbol_table.is_first_function(function.name):
            self.main = self.index
            self.index += 1
        self.current_scope = function.name
        self.symbol_table.new_symbol('return_' + function.name, function.address + 4, None, 0, self.index, function.type)
        self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(self.data_index)
        self.data_index += 4
        self.index += 1

    def define_function(self):
        function = self.symbol_table.find_symbol_by_name(self.current_scope, None)
        function.starts_at = self.index

    def loop(self):
        self.loop_scope_stack.push(self.index)
        self.index += 2

    def end_function(self):
        if self.current_scope == 'main':
            function_return = self.symbol_table.find_symbol_by_name('return_' + self.current_scope, None)
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(self.index + 2, function_return.address)
            self.index += 1
        function_return = self.symbol_table.find_symbol_by_name('return_' + self.current_scope, None)
        self.pb[self.index] = '(JP, @{}, , )'.format(function_return.address)
        self.index += 1
        self.current_scope = None
        self.semantic_stack.empty()

    def add_param(self):
        function = self.symbol_table.find_symbol_by_name(self.current_scope, None)
        function.length += 1

    def array_input(self):
        self.symbol_table.symbols[-1].type = self.symbol_table.symbols[-1].type + '_array_input'

    def _break(self, line_num):
        if self.loop_scope_stack.size > 0:
            self.pb[self.index] = '(JP, {}, , )'.format(self.loop_scope_stack.top() + 1)
            self.index += 1
        else:
            self.semantic_checker.error('break_statement', line_num)

    def _return(self):
        function_return = self.symbol_table.find_symbol_by_name('return_' + self.current_scope, None)
        self.pb[self.index] = '(JP, @{}, , )'.format(function_return.address)
        self.index += 1

    def return_value(self):
        function = self.symbol_table.find_symbol_by_name(self.current_scope, None)
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.semantic_stack.top(), function.address)
        self.semantic_stack.pop(1)
        self.index += 1
        function_return = self.symbol_table.find_symbol_by_name('return_' + self.current_scope, None)
        self.pb[self.index] = '(JP, @{}, , )'.format(function_return.address)
        self.index += 1

    def start_function_call(self):
        function = self.symbol_table.find_symbol_by_address(self.semantic_stack.top(), None)
        self.semantic_stack.pop(1)
        if function.name != 'output':
            self.semantic_stack.push(function.name)
        else:
            self.semantic_stack.push('output')

    def function_call(self, line_num):
        n_params = 0
        while not isinstance(self.semantic_stack.get_from_top(n_params), str) or \
                (isinstance(self.semantic_stack.get_from_top(n_params), str) and
                 self.semantic_stack.get_from_top(n_params).startswith('#')) or \
                (isinstance(self.semantic_stack.get_from_top(n_params), str) and
                 self.semantic_stack.get_from_top(n_params).startswith('@')):
            n_params += 1
        function = self.symbol_table.find_symbol_by_name(self.semantic_stack.get_from_top(n_params), None)
        if function.length != n_params:
            self.semantic_checker.error('actual_and_formal_parameters_number_matching', line_num, function.name)
            self.semantic_stack.pop(n_params + 1)
            self.semantic_stack.push(function.address)
            return
        else:
            if function.name != 'output':
                params = self.symbol_table.find_function_parameters(function.name, function.length)
                params.reverse()
                for param in params:
                    if param.type.endswith('_array_input'):
                        if isinstance(self.semantic_stack.top(), str):
                            self.semantic_checker.error('actual_and_formal_parameters_type_matching', line_num,
                                                        function.length - params.index(param), function.name, 'array',
                                                        'int')
                            self.semantic_stack.pop(n_params - params.index(param) + 1)
                            self.semantic_stack.push(function.address)
                            return
                        else:
                            array = self.symbol_table.find_symbol_by_address(self.semantic_stack.top(), self.current_scope)
                            if array.type.endswith('_array') or array.type.endswith('_array_input'):
                                start = 4 * array.length + self.semantic_stack.top()
                                self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(start, param.address)
                            else:
                                self.semantic_checker.error('actual_and_formal_parameters_type_matching', line_num,
                                                            function.length - params.index(param), function.name, 'array',
                                                            'int')
                                self.semantic_stack.pop(n_params - params.index(param) + 1)
                                self.semantic_stack.push(function.address)
                                return
                    else:
                        if not isinstance(self.semantic_stack.top(), str) and self.semantic_stack.top() < 1000:
                            var = self.symbol_table.find_symbol_by_address(self.semantic_stack.top(), self.current_scope)
                        elif (not isinstance(self.semantic_stack.top(), str) and self.semantic_stack.top() >= 1000) \
                                or isinstance(self.semantic_stack.top(), str):
                            var = self.semantic_stack.top()
                        else:
                            var = None
                        if (isinstance(var, SymbolTableEntry) and var.type == 'int') or (isinstance(var, int)) or \
                                (isinstance(var, str) and var[1:].isdigit()):
                            self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.semantic_stack.top(), param.address)
                        else:
                            self.semantic_checker.error('actual_and_formal_parameters_type_matching', line_num,
                                                        function.length - params.index(param), function.name, 'int',
                                                        'array')
                            self.semantic_stack.pop(n_params - params.index(param) + 1)
                            self.semantic_stack.push(function.address)
                            return
                    self.index += 1
                    self.semantic_stack.pop(1)
                self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(self.index + 2, function.address + 4)
                self.index += 1
                self.pb[self.index] = '(JP, {}, , )'.format(function.starts_at)
                self.index += 1
                self.semantic_stack.pop(1)
                if function.type == 'int_function':
                    t = self.get_temp()
                    self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(function.address, t)
                    self.index += 1
                    self.semantic_stack.push(t)
                else:
                    self.semantic_stack.push(function.address)
            else:
                self.output()

    def type(self, token):
        self.semantic_stack.push(token)

    def define_id(self, token):
        t = self.semantic_stack.top()
        self.semantic_stack.pop(1)
        self.symbol_table.new_symbol(token, self.data_index, self.current_scope, 0, self.index, t)
        self.data_index += 4
        self.semantic_stack.push(self.symbol_table.symbols[-1].address)
        self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(self.semantic_stack.top())
        self.index += 1

    def check_type(self, line_num):
        symbol = self.symbol_table.symbols[-1]
        if symbol.type == 'void':
            self.semantic_checker.error('void_type', line_num, symbol.name)
            symbol.type = 'int'

    def pid(self, token, line_num):
        p = self.symbol_table.find_symbol_by_name(token, self.current_scope)
        if p != 'first':
            self.semantic_stack.push(p.address)
        else:
            self.semantic_checker.error('scoping', line_num, token)
            self.semantic_stack.push(self.symbol_table.symbols[1].address)

    def pop(self):
        self.semantic_stack.pop()

    def pnum(self, token):
        self.semantic_stack.push('#{}'.format(token))

    def save_array(self):
        array_size = self.semantic_stack.get_from_top(0)
        array_size = int(array_size.replace('#', ''))
        symbol = self.symbol_table.symbols[-1]
        symbol.length = array_size
        symbol.type = symbol.type + '_array'
        for i in range(array_size - 1):
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(0, self.data_index)
            self.index += 1
            self.data_index += 4
        self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(symbol.address, self.data_index)
        self.data_index += 4
        self.index += 1
        self.semantic_stack.pop(2)

    def save(self):
        self.semantic_stack.push(self.index)
        self.index += 1

    def jpf(self):
        self.pb[self.semantic_stack.top()] = '(JPF, {}, {}, )'.format(self.semantic_stack.get_from_top(1), self.index + 1)
        self.semantic_stack.pop(2)
        self.semantic_stack.push(self.index)
        self.index += 1

    def jp(self):
        self.pb[self.semantic_stack.top()] = '(JP, {}, , )'.format(self.index)
        self.semantic_stack.pop()

    def label(self):
        self.semantic_stack.push(self.index)

    def while_stmt(self):
        self.pb[self.semantic_stack.top()] = '(JPF, {}, {}, )'.format(self.semantic_stack.get_from_top(1), self.index + 1)
        self.pb[self.index] = '(JP, {}, , )'.format(self.semantic_stack.get_from_top(2))
        self.index += 1
        self.semantic_stack.pop(3)
        start = self.loop_scope_stack.top()
        self.loop_scope_stack.pop(1)
        self.pb[start] = '(JP, {}, , )'.format(start + 2)
        self.pb[start + 1] = '(JP, {}, , )'.format(self.index)

    def assign(self, line_num):
        par1_type = self.get_type(self.semantic_stack.top())
        par2_type = self.get_type(self.semantic_stack.get_from_top(1))
        if par1_type == 'array' or par2_type == 'array':
            self.semantic_checker.error('type_mismatch', line_num, 'array', 'int')
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(1))
        temp = self.semantic_stack.top()
        self.index += 1
        self.semantic_stack.pop(2)
        self.semantic_stack.push(temp)

    def address_array(self):
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, #4, {})'.format(self.semantic_stack.top(), t)
        self.semantic_stack.pop()
        self.index += 1
        symbol = self.symbol_table.find_symbol_by_address(self.semantic_stack.top(), self.current_scope)
        if symbol.type.endswith('_array_input'):
            self.pb[self.index] = '(ADD, {}, {}, {})'.format(self.semantic_stack.top(), t, t)
        else:
            self.pb[self.index] = '(ADD, #{}, {}, {})'.format(self.semantic_stack.top(), t, t)
        self.semantic_stack.pop()
        self.index += 1
        self.semantic_stack.push('@' + str(t))

    def relop(self, line_num):
        par1_type = self.get_type(self.semantic_stack.top())
        par2_type = self.get_type(self.semantic_stack.get_from_top(2))
        if par1_type == 'array' or par2_type == 'array':
            self.semantic_checker.error('type_mismatch', line_num, 'array', 'int')
        addr = self.get_temp()
        if self.semantic_stack.get_from_top(1) == '<':
            self.pb[self.index] = '(LT, {}, {}, {})'.format(self.semantic_stack.get_from_top(2), self.semantic_stack.top(), addr)
        elif self.semantic_stack.get_from_top(1) == '==':
            self.pb[self.index] = '(EQ, {}, {}, {})'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(2), addr)
        self.index += 1
        self.semantic_stack.pop(3)
        self.semantic_stack.push(addr)

    def operator(self, token):
        self.semantic_stack.push(token)

    def add_or_sub(self, line_num):
        par1_type = self.get_type(self.semantic_stack.top())
        par2_type = self.get_type(self.semantic_stack.get_from_top(2))
        if par1_type == 'array' or par2_type == 'array':
            self.semantic_checker.error('type_mismatch', line_num, 'array', 'int')
        t = self.get_temp()
        if self.semantic_stack.get_from_top(1) == '+':
            self.pb[self.index] = '(ADD, {}, {}, {})'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(2), t)
        if self.semantic_stack.get_from_top(1) == '-':
            self.pb[self.index] = '(SUB, {}, {}, {})'.format(self.semantic_stack.get_from_top(2), self.semantic_stack.top(), t)
        self.index += 1
        self.semantic_stack.pop(3)
        self.semantic_stack.push(t)

    def mult(self, line_num):
        par1_type = self.get_type(self.semantic_stack.top())
        par2_type = self.get_type(self.semantic_stack.get_from_top(1))
        if par1_type == 'array' or par2_type == 'array':
            self.semantic_checker.error('type_mismatch', line_num, 'array', 'int')
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, {}, {})'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(1), t)
        self.index += 1
        self.semantic_stack.pop(2)
        self.semantic_stack.push(t)

    def signed_num(self, line_num):
        par1_type = self.get_type(self.semantic_stack.top())
        if par1_type == 'array':
            self.semantic_checker.error('type_mismatch', line_num, 'array', 'int')
        addr = self.get_temp()
        self.pb[self.index] = '(SUB, #0, {}, {})'.format(self.semantic_stack.top(), addr)
        self.semantic_stack.pop()
        self.index += 1
        self.semantic_stack.push(addr)

    def loop_size(self):
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(t)
        self.index += 1
        self.semantic_stack.push(t)

    def push_zero(self):
        self.semantic_stack.push('#0')

    def count(self):
        i = int(self.semantic_stack.get_from_top(1).replace('#', ''))
        self.semantic_stack.push('#{}'.format(i + 1))
        t = self.get_temp()
        self.pb[self.index] = '(ADD, #1, {}, {})'.format(self.semantic_stack.get_from_top(2 * i + 4), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(t, self.semantic_stack.get_from_top(2 * i + 4))
        self.index += 1

    def assign_for(self):
        array_size = int(self.semantic_stack.top().replace('#', ''))
        start = -1
        for i in range(array_size):
            t = self.get_temp()
            loop_var = self.semantic_stack.get_from_top(1)
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(loop_var, t)
            self.index += 1
            self.semantic_stack.pop(2)
            if i == array_size - 1:
                start = t
        self.semantic_stack.pop()
        self.semantic_stack.push(start)

    def initial(self):
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(self.semantic_stack.top(), t)
        self.index += 1
        self.semantic_stack.pop()
        self.semantic_stack.push(t)
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(t)
        self.index += 1
        self.semantic_stack.push(t)
        t = self.get_temp()
        self.pb[self.index] = '(LT, {}, {}, {})'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(3), t)
        self.index += 1
        self.semantic_stack.push(t)

    def step(self):
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, @{}, {}, )'.format(self.semantic_stack.get_from_top(3), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, @{}, {}, )'.format(t, self.semantic_stack.get_from_top(4))
        self.index += 1
        t = self.get_temp()
        self.pb[self.index] = '(SUB, {}, #4, {})'.format(self.semantic_stack.get_from_top(3), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(t, self.semantic_stack.get_from_top(3))
        self.index += 1
        t = self.get_temp()
        self.pb[self.index] = '(ADD, {}, #1, {})'.format(self.semantic_stack.get_from_top(2), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(t, self.semantic_stack.get_from_top(2))
        self.index += 1

    def for_stmt(self):
        self.pb[self.semantic_stack.top()] = '(JPF, {}, {}, )'.format(self.semantic_stack.get_from_top(1), self.index + 1)
        self.pb[self.index] = '(JP, {}, , )'.format(self.semantic_stack.top() - 1)
        self.index += 1
        self.semantic_stack.pop(6)
        start = self.loop_scope_stack.top()
        self.loop_scope_stack.pop(1)
        self.pb[start] = '(JP, {}, , )'.format(start + 2)
        self.pb[start + 1] = '(JP, {}, , )'.format(self.index)

    def output(self):
        self.pb[self.index] = '(PRINT, {}, , )'.format(self.semantic_stack.top())
        self.index += 1
        self.semantic_stack.pop(1)

    def get_type(self, par):
        if isinstance(par, str):
            return 'int'
        else:
            if par >= 1000:
                return 'int'
            else:
                par_symbol = self.symbol_table.find_symbol_by_address(par, self.current_scope)
                if par_symbol.type == 'int' or par_symbol.type == 'int_function':
                    return 'int'
                else:
                    return 'array'
