from utils import read


class Scanner:

    symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '>', '*', '=']
    keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'for']
    whitespaces = [' ', '\n', '\t', '\v', '\r', '\f']

    def __init__(self, path):
        self.line = 1
        self.file = read(path)
        self.unread = self.file
        self.errors, self.tokens, self.symbol_table = {k: [] for k in range(1, self.file.count('\n') + 2)},\
                                                      {k: [] for k in range(1, self.file.count('\n') + 2)}, []

    def return_function(self, token_type, token_len):
        token = self.unread[:token_len]
        self.unread = self.unread[token_len:]
        self.fill_tokens(token_type, token)
        self.fill_errors(token_type, token)
        self.fill_symbol_table(token_type, token)
        return token_type, token

    def get_next_token(self):
        if len(self.unread) == 0:
            return 'EOF', 'EOF'

        if self.unread[0] in self.whitespaces:
            if self.unread[0] == '\n':
                self.line += 1
                return self.return_function('WHITESPACE', 1)
            else:
                for i in range(len(self.unread)):
                    if not self.unread[i].isspace():
                        return self.return_function('WHITESPACE', i)

        if self.unread[0] == '/':
            if len(self.unread) == 1:
                return self.return_function('ERROR: Invalid input', 1)
            elif self.unread[1] == '/':
                for i in range(len(self.unread)):
                    if self.unread[i] == '\n':
                        return self.return_function('COMMENT', i)
            elif self.unread[1] == '*':
                for i in range(len(self.unread)):
                    if self.unread[i] == '*' and i + 1 < len(self.unread) and self.unread[i + 1] == '/':
                        return self.return_function('COMMENT', i + 2)
                return self.return_function('ERROR: Unclosed comment', len(self.unread))

        if self.unread[0] in Scanner.symbols:
            if len(self.unread) == 1:
                return self.return_function('ERROR: Invalid input', 1)
            else:
                if self.unread[0:2] == '==':
                    return self.return_function('SYMBOL', 2)
                elif self.unread[0:2] == '*/':
                    return self.return_function('ERROR: Unmatched comment', 2)
                return self.return_function('SYMBOL', 1)

        if self.unread[0].isalpha():
            length = len(self.unread)
            for i in range(len(self.unread)):
                if not self.unread[i].isalnum():
                    if self.unread[i] in Scanner.symbols + Scanner.whitespaces:
                        length = i
                        break
                    else:
                        return self.return_function('ERROR: Invalid input', i + 1)
            if self.unread[:length] in Scanner.keywords:
                return self.return_function('KEYWORD', length)
            else:
                return self.return_function('ID', length)

        if self.unread[0].isnumeric():
            for i in range(len(self.unread)):
                if not self.unread[i].isnumeric():
                    if self.unread[i] in Scanner.symbols + Scanner.whitespaces or self.unread[i].isalpha():
                        return self.return_function('NUM', i)
                    else:
                        return self.return_function('ERROR: Invalid number', i + 1)

        return self.return_function('ERROR: Invalid input', 1)

    def fill_symbol_table(self, token_type, token):
        if token_type == 'ID' and not token in self.symbol_table:
            self.symbol_table.append(token)

    def fill_errors(self, token_type, token):
        if token_type.startswith('ERROR'):
            if token_type.endswith('Unclosed comment'):
                token = token[:7]
            self.errors[self.line].append('(' + token + ', ' + token_type[7:] + ')')

    def fill_tokens(self, token_type, token):
        if not token_type.startswith('ERROR') and (token_type == 'ID' or token_type == 'KEYWORD'
                                                   or token_type == 'NUM' or token_type == 'SYMBOL'):
            self.tokens[self.line].append('(' + token_type + ', ' + token + ')')
