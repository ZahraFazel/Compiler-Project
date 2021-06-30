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
            if symbol.name == name and (symbol.scope == scope or symbol.scope is None):
                return symbol
        return 'first'

    def find_symbol_by_address(self, address, scope):
        for symbol in self.symbols:
            if symbol.address == address and (symbol.scope == scope or symbol.scope is None):
                return symbol

    def __str__(self):
        output = ''
        for symbol in self.symbols:
            output += str(symbol)
        return output
