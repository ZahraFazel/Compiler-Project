from utils import Stack


class CodeGeneration:
    def __init__(self):
        self.index = 0
        self.ss = Stack()
        self.symbol_table = Stack()
        self.scope_stack = Stack().push((0, None))
        self.pb = [None] * 200
        self.data_index = 500
        self.temp_index = 1000
        self.jmp_position_index = 7000
        self.current_arg = 0
        self.in_rhs = False
        self.global_variables = []
        self.semantic_routines = {'#pid': self.pid, '#pop': self.pop, '#pnum': self.pnum, '#save_array': self.save_array,
                                  '#save': self.save, '#jpf': self.jpf, '#jp': self.jp, '#label': self.label,
                                  '#while_stmt': self.while_stmt, '#assign': self.assign, '#address_array': self.address_array,
                                  '#relop': self.relop, '#operator': self.operator, '#add_or_sub': self.add_or_sub,
                                  '#mult': self.mult, '#signed_num': self.signed_num, '#output': self.output,
                                  '#loop_size': self.loop_size, '#assign_for': self.assign_for, '#count': self.count,
                                  '#for_stmt': self.for_stmt, '#push_zero': self.push_zero, '#initial': self.initial,
                                  '#step': self.step}

    def code_gen(self, action_symbol, token=None):
        if action_symbol in ['#pnum', '#pid', '#operator']:
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

    def find_address(self, token):
        addr = None
        temp = None
        for x in self.symbol_table.stack:
            if x[0] == token:
                addr = x[1]
                temp = 'second'
        if not addr:
            addr = self.data_index
            # print('symbol table')
            self.symbol_table.push((token, self.data_index))
            self.data_index += 4
            temp = 'first'
        return addr, temp

    def pid(self, token):
        # print("############ pid")
        if token == 'output':
            return
        p, temp = self.find_address(token)
        self.ss.push(p)
        if temp == 'first':
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(0, self.ss.top())
            self.index += 1
        # print(token, self.pb)

    def pop(self):
        # print("############ pop")
        self.ss.pop()

    def pnum(self, token):
        # print("############ pnum")
        self.ss.push('#{}'.format(token))

    def save_array(self):
        # print("############ save array")
        array_size = self.ss.get_from_top(0)
        name = self.symbol_table.get_from_top(0)
        self.symbol_table.pop(1)
        self.symbol_table.push((name[0], name[1], array_size))
        for i in range(int(array_size.replace('#', '')) - 1):
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(0, self.data_index)
            self.index += 1
            self.data_index += 4
        self.ss.pop(2)

    def save(self):
        # print("############ save")
        # print("hel", self.index)
        self.ss.push(self.index)
        self.index += 1

    def jpf(self):
        # print("############ jpf")
        # print(self.ss.stack)
        self.pb[self.ss.top()] = '(JPF, {}, {}, )'.format(self.ss.get_from_top(1), self.index + 1)
        # print(self.pb)
        self.ss.pop(2)
        self.ss.push(self.index)
        self.index += 1

    def jp(self):
        # print("############ jp")
        self.pb[self.ss.top()] = '(JP, {}, , )'.format(self.index)
        # print(self.pb)
        self.ss.pop()

    def label(self):
        # print("############ label")
        self.ss.push(self.index)

    def while_stmt(self):
        # print("############ while")
        self.pb[self.ss.top()] = '(JPF, {}, {}, )'.format(self.ss.get_from_top(1), self.index + 1)
        self.pb[self.index] = '(JP, {}, , )'.format(self.ss.get_from_top(2))
        # print(self.pb)
        self.index += 1
        self.ss.pop(3)

    def assign(self):
        # print("############ assign")
        # print("hello", self.ss.top())
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.ss.top(), self.ss.get_from_top(1))
        temp = self.ss.top()
        # print(self.pb)
        self.index += 1
        self.ss.pop(2)
        self.ss.push(temp)

    def address_array(self):
        # print("############ address array")
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, #4, {})'.format(self.ss.top(), t)
        self.ss.pop()
        self.index += 1
        self.pb[self.index] = '(ADD, #{}, {}, {}'.format(self.ss.top(), t, t)
        self.ss.pop()
        self.index += 1
        self.ss.push('@' + str(t))

    def relop(self):
        # print("############ relop")
        addr = self.get_temp()
        if self.ss.get_from_top(1) == '<':
            self.pb[self.index] = '(LT, {}, {}, {})'.format(self.ss.get_from_top(2), self.ss.top(), addr)
        elif self.ss.get_from_top(1) == '==':
            self.pb[self.index] = '(EQ, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(2), addr)
        # print(self.pb)
        self.index += 1
        self.ss.pop(3)
        self.ss.push(addr)

    def operator(self, token):
        # print("############ operator")
        self.ss.push(token)

    def add_or_sub(self):
        # print("############ add")
        t = self.get_temp()
        if self.ss.get_from_top(1) == '+':
            self.pb[self.index] = '(ADD, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(2), t)
        if self.ss.get_from_top(1) == '-':
            self.pb[self.index] = '(SUB, {}, {}, {})'.format(self.ss.get_from_top(2), self.ss.top(), t)
        # print(self.pb)
        self.index += 1
        self.ss.pop(3)
        self.ss.push(t)

    def mult(self):
        # print("############ mult")
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(1), t)
        # print(self.pb)
        self.index += 1
        self.ss.pop(2)
        self.ss.push(t)

    def signed_num(self):
        # print("############ signed num")
        addr = self.get_temp()
        self.pb[self.index] = '(SUB, #0, {}, {})'.format(self.ss.top(), addr)
        self.ss.pop()
        self.index += 1
        self.ss.push(addr)

    def loop_size(self):
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(t)
        self.index += 1
        self.ss.push(t)

    def push_zero(self):
        self.ss.push('#0')

    def count(self):
        i = int(self.ss.get_from_top(1).replace('#', ''))
        self.ss.push('#{}'.format(i + 1))
        t = self.get_temp()
        self.pb[self.index] = '(ADD, #1, {}, {})'.format(self.ss.get_from_top(2 * i + 4), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(t, self.ss.get_from_top(2 * i + 4))
        self.index += 1

    def assign_for(self):
        array_size = int(self.ss.top().replace('#', ''))
        start = -1
        for i in range(array_size):
            t = self.get_temp()
            loop_var = self.ss.get_from_top(1)
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(loop_var, t)
            self.index += 1
            self.ss.pop(2)
            if i == array_size - 1:
                start = t
        self.ss.pop()
        self.ss.push(start)

    def initial(self):
        # self.pb[self.index] = '(ASSIGN, @{}, {}, )'.format(self.ss.top(), self.ss.get_from_top(1))
        # self.index += 1
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(self.ss.top(), t)
        self.index += 1
        self.ss.pop()
        self.ss.push(t)
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, #0, {}, )'.format(t)
        self.index += 1
        self.ss.push(t)
        t = self.get_temp()
        self.pb[self.index] = '(LT, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(3), t)
        self.index += 1
        self.ss.push(t)

    def step(self):
        t = self.get_temp()
        self.pb[self.index] = '(ASSIGN, @{}, {}, )'.format(self.ss.get_from_top(3), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, @{}, {}, )'.format(t, self.ss.get_from_top(4))
        self.index += 1
        t = self.get_temp()
        self.pb[self.index] = '(SUB, {}, #4, {})'.format(self.ss.get_from_top(3), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(t, self.ss.get_from_top(3))
        self.index += 1
        t = self.get_temp()
        self.pb[self.index] = '(ADD, {}, #1, {})'.format(self.ss.get_from_top(2), t)
        self.index += 1
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(t, self.ss.get_from_top(2))
        self.index += 1

    def for_stmt(self):

        self.pb[self.ss.top()] = '(JPF, {}, {}, )'.format(self.ss.get_from_top(1), self.index + 1)
        self.pb[self.index] = '(JP, {}, , )'.format(self.ss.top() - 1)
        # print(self.pb)
        self.index += 1
        self.ss.pop(6)

    def output(self):
        # print("############ output")
        self.pb[self.index] = '(PRINT, {}, , )'.format(self.ss.top())
        self.index += 1
        # print(self.pb)
