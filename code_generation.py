from utils import Stack
from symbol_table import *


class CodeGeneration:
    def __init__(self):
        self.index = 1
        self.semantic_stack = Stack()
        self.symbol_table = SymbolTable()
        self.symbol_table.new_symbol('output', 500, None, 1, 0, 'void')
        self.loop_scope_stack = Stack()
        self.current_scope = None
        self.pb = [None] * 500
        self.pb[0] = '(ASSIGN, #0, 500, )'
        self.data_index = 504
        self.temp_index = 2000
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
                                  '#type': self.type}

    def code_gen(self, action_symbol, token=None):
        if action_symbol in ['#pnum', '#pid', '#operator', '#type']:
            self.semantic_routines[action_symbol](token)
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
        self.pb[1] = '(JP, {}, , )'.format(line_num - 2)

    def start_function(self):
        function = self.symbol_table.symbols[-1]
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

    def end_scope(self):
        pass

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
        pass

    def var_input(self):
        pass

    def _break(self):
        self.pb[self.index] = '(JP, {}, , )'.format(self.loop_scope_stack.top() + 1)
        self.index += 1

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
        # print("start func call")
        # print(self.semantic_stack.stack)

    def function_call(self):
        n_params = 0
        while not isinstance(self.semantic_stack.get_from_top(n_params), str) or \
                (isinstance(self.semantic_stack.get_from_top(n_params), str) and
                 self.semantic_stack.get_from_top(n_params).startswith('#')) or \
                (isinstance(self.semantic_stack.get_from_top(n_params), str) and
                 self.semantic_stack.get_from_top(n_params).startswith('@')):
            n_params += 1
        function = self.symbol_table.find_symbol_by_name(self.semantic_stack.get_from_top(n_params), None)
        # print("function call")
        # print(self.semantic_stack.stack)
        if function.name != 'output':
            params_addresses = [function.address + (i + 2) * 4 for i in range(function.length)]
            params_addresses.reverse()
            for address in params_addresses:
                self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.semantic_stack.top(), address)
                self.index += 1
                self.semantic_stack.pop(1)
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(self.index + 2, function.address + 4)
            self.index += 1
            self.pb[self.index] = '(JP, {}, , )'.format(function.starts_at)
            self.index += 1
            self.semantic_stack.pop(1)
            if function.type == 'int':
                t = self.get_temp()
                self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(function.address, t)
                self.index += 1
                self.semantic_stack.push(t)
            else:
                self.semantic_stack.push(function.address)
        else:
            self.output()
        # print(self.semantic_stack.stack)

    def type(self, token):
        self.semantic_stack.push(token)

    def pid(self, token):
        p = self.symbol_table.find_symbol_by_name(token, self.current_scope)
        if p == 'first':
            t = self.semantic_stack.top()
            self.semantic_stack.pop(1)
            self.symbol_table.new_symbol(token, self.data_index, self.current_scope, 0, self.index, t)
            self.data_index += 4
            self.semantic_stack.push(self.symbol_table.symbols[-1].address)
            self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(self.semantic_stack.top())
            self.index += 1
        else:
            self.semantic_stack.push(p.address)
        # print("pid")
        # print(self.semantic_stack.stack)

    def pop(self):
        self.semantic_stack.pop()
        # print("pop")
        # print(self.semantic_stack.stack)

    def pnum(self, token):
        self.semantic_stack.push('#{}'.format(token))
        # print("pnum")
        # print(self.semantic_stack.stack)

    def save_array(self):
        array_size = self.semantic_stack.get_from_top(0)
        symbol = self.symbol_table.symbols[-1]
        symbol.length = array_size
        for i in range(int(array_size.replace('#', '')) - 1):
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(0, self.data_index)
            self.index += 1
            self.data_index += 4
        self.semantic_stack.pop(2)
        # print("save_arr")
        # print(self.semantic_stack.stack)

    def save(self):
        self.semantic_stack.push(self.index)
        self.index += 1
        # print("save")
        # print(self.semantic_stack.stack)

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

    def assign(self):
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(1))
        temp = self.semantic_stack.top()
        self.index += 1
        self.semantic_stack.pop(2)
        self.semantic_stack.push(temp)
        # print("assign")
        # print(self.semantic_stack.stack)

    def address_array(self):
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, #4, {})'.format(self.semantic_stack.top(), t)
        self.semantic_stack.pop()
        self.index += 1
        self.pb[self.index] = '(ADD, #{}, {}, {}'.format(self.semantic_stack.top(), t, t)
        self.semantic_stack.pop()
        self.index += 1
        self.semantic_stack.push('@' + str(t))

    def relop(self):
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

    def add_or_sub(self):
        t = self.get_temp()
        if self.semantic_stack.get_from_top(1) == '+':
            self.pb[self.index] = '(ADD, {}, {}, {})'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(2), t)
        if self.semantic_stack.get_from_top(1) == '-':
            self.pb[self.index] = '(SUB, {}, {}, {})'.format(self.semantic_stack.get_from_top(2), self.semantic_stack.top(), t)
        self.index += 1
        self.semantic_stack.pop(3)
        self.semantic_stack.push(t)

    def mult(self):
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, {}, {})'.format(self.semantic_stack.top(), self.semantic_stack.get_from_top(1), t)
        self.index += 1
        self.semantic_stack.pop(2)
        self.semantic_stack.push(t)

    def signed_num(self):
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
