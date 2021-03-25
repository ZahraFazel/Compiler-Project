from utils import read

# except for = and ==
symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '<', '>']
keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'for']
spaces = [' ', '\n', '\t', '\v', '\r', '\f']


class Scanner:
    def __init__(self, path):
        self.line_num = 1
        self.file = read(path)
        self.unread_parts = self.file
        self.errors, self.tokens = {}, {}
        self.symbol_table = set()

    def get_next_token(self):
        pass
