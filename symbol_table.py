class SymbolTableEntry:
    def __init__(self, name, address, scope, length, starts_at, type):
        self.name = name
        self.address = address
        self.scope = scope
        self.length = length
        self.starts_at = starts_at
        self.type = type

    def __str__(self):
        output = '{}\t{}\t{}\t{}\t{}\t{}\n'.format(self.name, self.address, self.scope, self.length, self.starts_at, self.type)
        return output


class SymbolTable:
    def __init__(self):
        self.symbols = []

    def new_symbol(self, name, address, scope, length, starts_at, type):
        self.symbols.append(SymbolTableEntry(name, address, scope, length, starts_at, type))

    def find_symbol_by_name(self, name, scope):
        for symbol in self.symbols:
            if symbol.name == name and symbol.scope == scope:
                return symbol
        for symbol in self.symbols:
            if symbol.name == name and symbol.scope is None:
                return symbol
        return 'first'

    def find_symbol_by_address(self, address, scope):
        for symbol in self.symbols:
            if symbol.address == address and (symbol.scope == scope or symbol.scope is None):
                return symbol

    def find_function_parameters(self, function_name, number_of_parameter):
        output = []
        for i in range(len(self.symbols)):
            if self.symbols[i].scope == function_name and len(output) < number_of_parameter:
                output.append(self.symbols[i])
        return output

    def is_first_function(self, function_name):
        first_function = ''
        for i in range(len(self.symbols)):
            if self.symbols[i].type.endswith('function'):
                first_function = self.symbols[i].name
                break
        return first_function == function_name

    def get_first_int(self, scope):
        for i in range(len(self.symbols) - 1, -1, -1):
            if self.symbols[i].type == 'int' and self.symbols[i].scope == scope:
                return self.symbols[i]
        for i in range(len(self.symbols) - 1, -1, -1):
            if self.symbols[i].type == 'int' and self.symbols[i].scope is None:
                return self.symbols[i]


    def __str__(self):
        output = ''
        for symbol in self.symbols:
            output += str(symbol)
        return output
