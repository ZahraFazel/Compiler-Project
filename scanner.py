from utils import read

# except for = and ==
symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '<', '>']
keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'for']
whitespaces = [' ', '\n', '\t', '\v', '\r', '\f']


class Scanner:
    def __init__(self, path):
        self.line = 1
        self.file = read(path)
        self.unread = self.file
        self.errors, self.tokens = {}, {}
        self.symbol_table = set()

    def return_function(self, token_type, token_len):
        token = self.unread[:token_len]
        self.unread = self.unread[token_len:]
        return token_type, token

    def get_next_token(self):
        if len(self.unread) == 0:
            return 'EOF', 'EOF'
        # todo whitespace
        # todo comment
        # todo = and ==
        # todo symbols
        if self.unread[0].isalpha():
            length = len(self.unread)
            for i in range(len(self.unread)):
                if not self.unread[i].isalnum():
                    if self.unread[i] in symbols + whitespaces:
                        length = i
                        break
                    else:
                        return self.return_function('ERROR', i + 1)
            if self.return_function[:length] in keywords:
                return self.return_function('KEYWORD', length)
            else:
                return self.return_function('ID', length)
        if self.unread[0].isnumeric():
            for i in range(len(self.unread)):
                if not self.unread[i].isnumeric():
                    if self.unread[i] in symbols + whitespaces or self.unread[i].isalpha():
                        return self.return_function('NUM', i)
                    else:
                        return self.return_function('ERROR', i + 1)
        if self.unread[0] in whitespaces:
            return self.return_function('WHITESPACE', 1)
        return self.return_function('ERROR', 1)
