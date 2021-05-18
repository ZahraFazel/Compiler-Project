from utils import Stack


class CodeGeneration:
    def __init__(self):
        self.index = 1
        self.ss = Stack()
        self.symbol_table = Stack()
        self.scope_stack = Stack().push((0, None))
        self.pb = [0] * 10000
        self.data_index = 2000
        self.temp_index = 8000
        self.jmp_position_index = 7000
        # self.arg_index = 8000
        # self.return_values_index = 9000
        self.current_arg = 0
        self.in_rhs = False
        # self.semantic_errors = []
        self.global_variables = []

    def get_address_by_token(self, label):
        for symcell in self.symbol_table.stack:
            if symcell['token'] == label:
                if self.in_rhs and symcell['type'] == 'void':
                    raise Exception('using return value of void function: {}.'.format(label))
                return symcell['addr']
        raise Exception("\'{}\' is not defined.".format(label))

    def get_arg_address_by_token_and_num(self, func, num):
        for symcell in self.symbol_table.stack:
            if symcell['token'] == func and symcell.get('is_func', False):
                if num < len(symcell['args']):
                    return symcell['args'][num]
                else:
                    raise Exception('Mismatch in numbers of arguments of \'{}\'.'.format(func))
        raise Exception("\'{}\' is not defined.".format(func))

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

    def print_pb(self):
        for ind, x in enumerate(self.pb):
            if x != 0:
                print(ind, x, sep='\t')

    print()

    def get_dict_by_address(self, address):
        for x in self.symbol_table.stack:
            addr = x.get('addr', None)
            if not addr:
                continue
            if addr == address or addr == int(address):
                return x

    def get_dict_by_token(self, token):
        for x in self.symbol_table.stack:
            if x['token'] == token:
                return x
        raise Exception("\'{}\' is not defined.".format(token))

    def output_pb(self):
        with open('in_out/' + 'output.txt', 'w+') as f:
            for ind, x in enumerate(self.pb):
                if x != 0:
                    l = '{}\t{}\n'.format((str(ind)), x)
                    f.write(l)

    def find_temp(self):
        temp = self.temp_index
        self.temp_index += 1
        return temp

    def find_address(self, token):
        addr = None
        for x in self.symbol_table.stack:
            if x[0] == token:
                addr = x[1]
        if not addr:
            addr = self.data_index
            print('symbol table')
            self.symbol_table.push((token, self.data_index))
            self.data_index += 4
        return addr

    def pid(self, token):
        p = self.find_address(token)
        self.ss.push(p)
        # print(p)
        # print(self.ss.stack)
        # print(self.symbol_table.stack)

    def pop(self):
        self.ss.pop(1)

    def pnum(self, token):
        self.ss.push(int(token))

    def save_array(self):
        array_size = self.ss.get_from_top(0)
        name = self.symbol_table.get_from_top(0)
        self.symbol_table.pop(1)
        self.symbol_table.push((name[0], name[1], array_size))
        self.data_index += (array_size - 1) * 4
        self.ss.pop(2)

    def save(self):
        pass

    def jpf(self):
        pass

    def jp(self):
        pass

    def label(self):
        pass

    def while_stmt(self):
        pass

    def assign(self):
        pass

    def address_array(self):
        pass

    def relop(self):
        pass

    def relop_sign(self):
        pass

    def add(self):
        pass

    def sign(self):
        pass

    def mult(self):
        pass

    def signed_num(self):
        pass

    def output(self):
        pass
