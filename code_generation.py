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

    # def get_address_by_token(self, label):
    #     for symcell in self.symbol_table.stack:
    #         if symcell['token'] == label:
    #             if self.in_rhs and symcell['type'] == 'void':
    #                 raise Exception('using return value of void function: {}.'.format(label))
    #             return symcell['addr']
    #     raise Exception("\'{}\' is not defined.".format(label))

    # def get_arg_address_by_token_and_num(self, func, num):
    #     for symcell in self.symbol_table.stack:
    #         if symcell['token'] == func and symcell.get('is_func', False):
    #             if num < len(symcell['args']):
    #                 return symcell['args'][num]
    #             else:
    #                 raise Exception('Mismatch in numbers of arguments of \'{}\'.'.format(func))
    #     raise Exception("\'{}\' is not defined.".format(func))

    def get_temp(self):
        res = self.temp_index
        self.temp_index += 4
        return res

    # def execute(self, func, token):
    #     key = token[2] if (token[0] == 'id' or token[0] == 'num') else token[0]
    #     try:
    #         func(self, key)
    #     except Exception as e:
    #         # self.semantic_errors += ['#{}:\t{}\n'.format(str(token[1]), str(e))]
    #         pass
    #     self.print_pb()

    # def print_pb(self):
    #     for ind, x in enumerate(self.pb):
    #         if not x:
    #             print(ind, x, sep='\t')

    # def get_dict_by_address(self, address):
    #     for x in self.symbol_table.stack:
    #         addr = x.get('addr', None)
    #         if not addr:
    #             continue
    #         if addr == address or addr == int(address):
    #             return x

    # def get_dict_by_token(self, token):
    #     for x in self.symbol_table.stack:
    #         if x['token'] == token:
    #             return x
    #     raise Exception("\'{}\' is not defined.".format(token))

    # def output_pb(self):
    #     with open('in_out/' + 'output.txt', 'w+') as f:
    #         for ind, x in enumerate(self.pb):
    #             if x != 0:
    #                 l = '{}\t{}\n'.format((str(ind)), x)
    #                 f.write(l)

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
            print('symbol table')
            self.symbol_table.push((token, self.data_index))
            self.data_index += 4
            temp = 'first'
        return addr, temp

    def pid(self, token):
        print("############ pid")
        if token == 'output':
            return
        p, temp = self.find_address(token)
        self.ss.push(p)
        if temp == 'first':
            self.pb[self.index] = '(ASSIGN, #{}, {}, )'.format(0, self.ss.top())
            self.index += 1
        print(token, self.pb)
        # print(self.ss.stack)
        # print(self.symbol_table.stack)

    def pop(self):
        print("############ pop")
        self.ss.pop()

    def pnum(self, token):
        print("############ pnum")
        self.ss.push('#{}'.format(token))

    def save_array(self):
        print("############ save array")
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
        print("############ save")
        # print("hel", self.index)
        self.ss.push(self.index)
        self.index += 1

    def jpf(self):
        print("############ jpf")
        print(self.ss.stack)
        self.pb[self.ss.top()] = '(JPF, {}, {}, )'.format(self.ss.get_from_top(1), self.index + 1)
        print(self.pb)
        self.ss.pop(2)
        self.ss.push(self.index)
        self.index += 1

    def jp(self):
        print("############ jp")
        self.pb[self.ss.top()] = '(JP, {}, , )'.format(self.index)
        print(self.pb)
        self.ss.pop()

    def label(self):
        print("############ label")
        self.ss.push(self.index)

    def while_stmt(self):
        print("############ while")
        self.pb[self.ss.top()] = '(JPF, {}, {}, )'.format(self.ss.get_from_top(1), self.index + 1)
        self.pb[self.index] = '(JP, {}, , )'.format(self.ss.get_from_top(2))
        print(self.pb)
        self.index += 1
        self.ss.pop(3)

    def assign(self):
        print("############ assign")
        # print("hello", self.ss.top())
        self.pb[self.index] = '(ASSIGN, {}, {}, )'.format(self.ss.top(), self.ss.get_from_top(1))
        temp = self.ss.top()
        print(self.pb)
        self.index += 1
        self.ss.pop(2)
        self.ss.push(temp)

    def address_array(self):
        print("############ address array")
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, #4, {})'.format(self.ss.top(), t)
        self.ss.pop()
        self.index += 1
        self.pb[self.index] = '(ADD, #{}, {}, {}'.format(self.ss.top(), t, t)
        self.ss.pop()
        self.index += 1
        self.ss.push('@' + str(t))

    def relop(self):
        print("############ relop")
        addr = self.get_temp()
        if self.ss.get_from_top(1) == '<':
            self.pb[self.index] = '(LT, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(2), addr)
        elif self.ss.get_from_top(1) == '==':
            self.pb[self.index] = '(EQ, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(2), addr)
        print(self.pb)
        self.index += 1
        self.ss.pop(3)
        self.ss.push(addr)

    def operator(self, token):
        print("############ operator")
        self.ss.push(token)

    def add_or_sub(self):
        print("############ add")
        t = self.get_temp()
        if self.ss.get_from_top(1) == '+':
            self.pb[self.index] = '(ADD, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(2), t)
        if self.ss.get_from_top(1) == '-':
            self.pb[self.index] = '(SUB, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(2), t)
        print(self.pb)
        self.index += 1
        self.ss.pop(3)
        self.ss.push(t)

    def mult(self):
        print("############ mult")
        t = self.get_temp()
        self.pb[self.index] = '(MULT, {}, {}, {})'.format(self.ss.top(), self.ss.get_from_top(1), t)
        print(self.pb)
        self.index += 1
        self.ss.pop(2)
        self.ss.push(t)

    def signed_num(self):
        print("############ signed num")
        addr = self.get_temp()
        self.pb[self.index] = '(SUB, #0, {}, {})'.format(self.ss.pop(), addr)
        self.index += 1
        self.ss.push(addr)

    def output(self):
        print("############ output")
        self.pb[self.index] = '(PRINT, {}, , )'.format(self.ss.top())
        self.index += 1
        print(self.pb)
