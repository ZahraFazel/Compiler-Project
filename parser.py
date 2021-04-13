import scanner


class Parser:

    def __init__(self, scanner):
        self.lookahead_type = None
        self.lookahead_token = None
        self.scanner = scanner
        self.errors = ''

    def match(self, expected_token):
        if self.lookahead_token == expected_token:
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        else:
            print("Error")
            # TODO Error handling

    def program(self):
        if self.lookahead_token in {'$', 'int', 'void'}:
            self.match(self.lookahead_token)
        elif self.lookahead_token == "$":
            self.errors += "#" + self.scanner.line.tostring() + " : syntax error, missing int or void\n"
        else:
            self.errors += "#" + self.scanner.line.tostring() + " : syntax error, illegal lookahead\n"
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
            self.program()

    def declaration_list(self):
        if self.lookahead_token in {"int", "void", ""}:
            self.match(self.lookahead_token)
        # elif self.lookahead_token in {}:

