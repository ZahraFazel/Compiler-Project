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
        self.errors, self.tokens, self.symbol_table = {}, {}, {}

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
                        return self.return_function('INPUT ERROR', i + 1)
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
                        return self.return_function('NUM ERROR', i + 1)
        if self.unread[0] in whitespaces:
            return self.return_function('WHITESPACE', 1)
        # return self.return_function('ERROR', 1)

    def fill_symbol_table(self, token_type, token):
        if token_type == 'KEYWORD':
            if 'KEYWORD' in self.symbol_table.keys():
                self.symbol_table['KEYWORD'].add(token)
            else:
                self.symbol_table['KEYWORD'] = set(token)
        if token_type == 'ID':
            if 'ID' in self.symbol_table.keys():
                self.symbol_table['ID'].add(token)
            else:
                self.symbol_table['ID'] = set(token)

    def fill_errors(self, token_type, token):
        if token_type.endswith('ERROR'):
            if self.line in self.errors.keys():
                if token_type.startswith('NUM'):
                    self.errors[self.line] += ' (' + token + ', Invalid number)'
                elif token_type.startswith('INPUT'):
                    self.errors[self.line] += ' (' + token + ', Invalid input)'
                elif token_type.startswith('UNMATCHED'):
                    self.errors[self.line] += ' (' + token + ', Unmatched comment)'
                elif token_type.startswith('UNCLOSED'):
                    self.errors[self.line] += ' (' + token + ', Unclosed comment)'
            else:
                if token_type.startswith('NUM'):
                    self.errors[self.line] = ' (' + token + ', Invalid number)'
                elif token_type.startswith('INPUT'):
                    self.errors[self.line] = ' (' + token + ', Invalid input)'
                elif token_type.startswith('UNMATCHED'):
                    self.errors[self.line] = ' (' + token + ', Unmatched comment)'
                elif token_type.startswith('UNCLOSED'):
                    self.errors[self.line] = ' (' + token + ', Unclosed comment)'

    def fill_tokens(self, token_type, token):
        if not token_type.endswith('ERROR'):
            if token_type == 'WHITESPACE' or token_type == 'COMMENT' or token_type == 'EOF':
                return
            if self.line in self.tokens.keys():
                self.tokens[self.line] += ' (' + token_type + ', ' + token + ')'
            else:
                self.tokens[self.line] = ' (' + token_type + ', ' + token + ')'

    def scan(self):
        while True:
            token_type, token = self.get_next_token()
            if token_type == 'EOF':
                break
        # todo write to files
