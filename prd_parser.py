import anytree
from code_generation import CodeGeneration


class Parser:

    def __init__(self, scr):
        self.lookahead_type = None
        self.lookahead_lexeme = None
        self.scanner = scr
        self.parse_tree = None
        self.errors = ''
        self.code_generator = CodeGeneration()

    def parse(self):
        self.next()
        self.program()

    def next(self):
        if self.lookahead_lexeme == '$':
            self.lookahead_lexeme, self.lookahead_type = None, None
        else:
            self.lookahead_type, self.lookahead_lexeme = self.scanner.get_next_token()
            while self.lookahead_type is None:
                self.lookahead_type, self.lookahead_lexeme = self.scanner.get_next_token()

    def match(self, parent, expected_token):
        if expected_token[0] == self.lookahead_type and ((expected_token[0] in ['ID', 'NUM']) or
                                                         (expected_token[0] in ['KEYWORD', 'SYMBOL'] and
                                                          self.lookahead_lexeme) in expected_token[1]):
            anytree.Node('(' + self.lookahead_type + ', ' + str(self.lookahead_lexeme) + ') ', parent=parent)
            self.next()
        elif self.lookahead_lexeme is not None:
            expected = ''
            if len(expected_token[1]) == 1:
                expected = expected_token[1][0]
            else:
                for i in range(len(expected_token[1]) - 1):
                    expected += expected_token[1][i] + ' or '
                expected += expected_token[1][-1]
            self.errors += '#{0} : syntax error, missing {1}\n'.format(self.scanner.line, expected)

    # program ->  declaration-list $
    def program(self):
        if self.lookahead_lexeme in ['int', 'void']:
            self.parse_tree = anytree.Node('Program', parent=None)
            self.declaration_list(self.parse_tree)
            if self.lookahead_lexeme == '$':
                anytree.Node('$', parent=self.parse_tree)
                self.code_generator.code_gen('#jp_main')
            elif self.lookahead_lexeme is not None:
                self.errors += '#{0} : syntax error, missing $'.format(self.scanner.line)
        elif self.lookahead_lexeme == '$':
            self.parse_tree = anytree.Node('Program', parent=None)
            node = anytree.Node('Declaration-list', parent=self.parse_tree)
            anytree.Node('epsilon', parent=node)
            anytree.Node('$', parent=self.parse_tree)
        elif self.lookahead_lexeme is not None:
            expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
            self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.program()

    # declaration-list -> declaration declaration-list | EPSILON
    def declaration_list(self, parent):
        if self.lookahead_lexeme in ['int', 'void']:
            node = anytree.Node('Declaration-list', parent=parent)
            self.declaration(node)
            self.declaration_list(node)
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'break', 'if',
                                                                               'while', 'return', 'for', '+', '-', '$']:
            node = anytree.Node('Declaration-list', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.declaration_list(parent)

    # declaration -> Declaration-initial Declaration-prime
    def declaration(self, parent):
        if self.lookahead_lexeme in ['int', 'void']:
            node = anytree.Node('Declaration', parent=parent)
            self.declaration_initial(node)
            self.declaration_prime(node)
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'int', 'void',
                                                                               'break', 'if', 'while', 'return', 'for',
                                                                               '+', '-', '$']:
            self.errors += '#{0} : syntax error, missing declaration\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.declaration(parent)

    # declaration_initial ->  type-specifier ID
    def declaration_initial(self, parent):
        if self.lookahead_lexeme in ['int', 'void']:
            node = anytree.Node('Declaration-initial', parent=parent)
            self.code_generator.code_gen('#type', self.lookahead_lexeme)
            self.type_specifier(node)
            self.code_generator.code_gen('#define_id', self.lookahead_lexeme)
            self.match(node, ('ID', ['ID']))
        elif self.lookahead_lexeme in [';', '[', '(', ')', ',']:
            self.errors += '#{0} : syntax error, missing declaration-initial\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.declaration_initial(parent)

    # Declaration-prime -> Fun-declaration-prime | Var-declaration-prime
    def declaration_prime(self, parent):
        if self.lookahead_lexeme in [';', '[']:
            node = anytree.Node('Declaration-prime', parent=parent)
            self.var_declaration_prime(node)
        elif self.lookahead_lexeme == '(':
            self.code_generator.code_gen('#start_function')
            node = anytree.Node('Declaration-prime', parent=parent)
            self.fun_declaration_prime(node)
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'int', 'void',
                                                                               'break', 'if', 'while', 'return', 'for',
                                                                               '+', '-', '$']:
            self.errors += '#{0} : syntax error, missing declaration-prime\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.declaration_prime(parent)

    # Fun-declaration-prime -> ( Params ) Compound-stmt
    def fun_declaration_prime(self, parent):
        if self.lookahead_lexeme == '(':
            node = anytree.Node('Fun-declaration-prime', parent=parent)
            self.match(node, ('SYMBOL', ['(']))
            self.params(node)
            self.code_generator.code_gen('#define_function')
            self.match(node, ('SYMBOL', [')']))
            self.compound_stmt(node)
            self.code_generator.code_gen('#end_function')
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'int', 'void',
                                                                               'break', 'if', 'while', 'return', 'for',
                                                                               '+', '-', '$']:
            self.errors += '#{0} : syntax error, missing fun-declaration-prime\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.fun_declaration_prime(parent)

    # Var-declaration-prime -> ; | [ NUM ] ;
    def var_declaration_prime(self, parent):
        if self.lookahead_lexeme == ';':
            node = anytree.Node('Var-declaration-prime', parent=parent)
            self.code_generator.code_gen('#pop')
            self.match(node, ('SYMBOL', [';']))
        elif self.lookahead_lexeme == '[':
            node = anytree.Node('Var-declaration-prime', parent=parent)
            self.match(node, ('SYMBOL', ['[']))
            self.code_generator.code_gen('#pnum', self.lookahead_lexeme)
            self.match(node, ('NUM', 'NUM'))
            self.match(node, ('SYMBOL', [']']))
            self.code_generator.code_gen('#save_array')
            self.match(node, ('SYMBOL', [';']))
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '{', '}', 'int', 'void', 'break',
                                                                               'if', 'while', 'return', 'for', '+', '-',
                                                                               '$']:
            if self.lookahead_type == 'NUM':
                self.errors += '#{0} : syntax error, missing [\n'.format(self.scanner.line)
            else:
                self.errors += '#{0} : syntax error, missing ;\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.var_declaration_prime(parent)

    # Type-specifier -> int | void
    def type_specifier(self, parent):
        if self.lookahead_lexeme in ['int', 'void']:
            node = anytree.Node('Type-specifier', parent=parent)
            self.match(node, ('KEYWORD', ['int', 'void']))
        elif self.lookahead_type == 'ID':
            self.errors += '#{0} : syntax error, missing type-specifier\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.type_specifier(parent)

    # Params -> int ID Param-prime Param-list | void Param-list-void-abtar
    def params(self, parent):
        if self.lookahead_lexeme == 'int':
            node = anytree.Node('Params', parent=parent)
            self.code_generator.code_gen('#type', self.lookahead_lexeme)
            self.match(node, ('KEYWORD', ['int']))
            self.code_generator.code_gen('#define_id', self.lookahead_lexeme)
            self.match(node, ('ID', ['ID']))
            self.code_generator.code_gen('#add_param')
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead_lexeme == 'void':
            node = anytree.Node('Params', parent=parent)
            self.match(node, ('KEYWORD', ['void']))
            self.param_list_void_abtar(node)
        elif self.lookahead_lexeme == ')':
            self.errors += '#{0} : syntax error, missing params\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.params(parent)

    # Param-list-void-abtar -> ID Param-prime Param-list | EPSILON
    def param_list_void_abtar(self, parent):
        if self.lookahead_type == 'ID':
            node = anytree.Node('Param-list-void-abtar', parent=parent)
            self.code_generator.code_gen('#pid', self.lookahead_lexeme)
            self.match(node, ('ID', ['ID']))
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead_lexeme == ')':
            node = anytree.Node('Param-list-void-abtar', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.param_list_void_abtar(parent)

    # Param-list -> , Param Param-list | EPSILON
    def param_list(self, parent):
        if self.lookahead_lexeme == ',':
            node = anytree.Node('Param-list', parent=parent)
            self.match(node, ('SYMBOL', [',']))
            self.param(node)
            self.code_generator.code_gen('#add_param')
            self.param_list(node)
        elif self.lookahead_lexeme == ')':
            node = anytree.Node('Param-list', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.param_list(parent)

    # Param -> Declaration-initial Param-prime
    def param(self, parent):
        if self.lookahead_lexeme in ['int', 'void']:
            node = anytree.Node('Param', parent=parent)
            self.declaration_initial(node)
            self.param_prime(node)
        elif self.lookahead_lexeme in {')', ','}:
            self.errors += '#{0} : syntax error, missing param\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.param(parent)

    # Param-prime -> [ ] | EPSILON
    def param_prime(self, parent):
        if self.lookahead_lexeme == '[':
            node = anytree.Node('Param-prime', parent=parent)
            self.match(node, ('SYMBOL', ['[']))
            self.match(node, ('SYMBOL', [']']))
            self.code_generator.code_gen('#array_input')
        elif self.lookahead_lexeme in [')', ',']:
            node = anytree.Node('Param-prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.param_prime(parent)

    # Compound-stmt -> { Declaration-list Statement-list }
    def compound_stmt(self, parent):
        if self.lookahead_lexeme == '{':
            node = anytree.Node('Compound-stmt', parent=parent)
            self.match(node, ('SYMBOL', ['{']))
            self.declaration_list(node)
            self.statement_list(node)
            self.match(node, ('SYMBOL', ['}']))
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '}', 'int', 'void', 'break',
                                                                               'if', 'else', 'while', 'return', 'for',
                                                                               '+', '-', '$']:
            self.errors += '#{0} : syntax error, missing {\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.compound_stmt(parent)

    # Statement-list -> Statement Statement-list | EPSILON
    def statement_list(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', 'break', 'if', 'while',
                                                                             'return', 'for', '+', '-']:
            node = anytree.Node('Statement-list', parent=parent)
            self.statement(node)
            self.statement_list(node)
        elif self.lookahead_lexeme == '}':
            node = anytree.Node('Statement-list', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.statement_list(parent)

    # Statement -> Expression-stmt | Compound-stmt | Selection-stmt | Iteration-stmt | Return-stmt | For-stmt
    def statement(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', 'break', '+', '-']:
            node = anytree.Node('Statement', parent=parent)
            self.expression_stmt(node)
        elif self.lookahead_lexeme == '{':
            node = anytree.Node('Statement', parent=parent)
            self.compound_stmt(node)
        elif self.lookahead_lexeme == 'if':
            node = anytree.Node('Statement', parent=parent)
            self.selection_stmt(node)
        elif self.lookahead_lexeme == 'while':
            node = anytree.Node('Statement', parent=parent)
            self.iteration_stmt(node)
        elif self.lookahead_lexeme == 'return':
            node = anytree.Node('Statement', parent=parent)
            self.return_stmt(node)
        elif self.lookahead_lexeme == 'for':
            node = anytree.Node('Statement', parent=parent)
            self.for_stmt(node)
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['}', 'break', 'else', '+', '-']:
            self.errors += '#{0} : syntax error, missing statement\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.statement(parent)

    # Expression-stmt -> Expression ; | break ; | ;
    def expression_stmt(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Expression-stmt', parent=parent)
            self.expression(node)
            self.match(node, ('SYMBOL', [';']))
            self.code_generator.code_gen('#pop')
        elif self.lookahead_lexeme == 'break':
            node = anytree.Node('Expression-stmt', parent=parent)
            self.match(node, ('KEYWORD', ['break']))
            self.code_generator.code_gen('#break')
            self.match(node, ('SYMBOL', [';']))
        elif self.lookahead_lexeme == ';':
            node = anytree.Node('Expression-stmt', parent=parent)
            self.match(node, ('SYMBOL', [';']))
        elif self.lookahead_lexeme in ['{', '}', 'else', 'if', 'while', 'return', 'for']:
            self.errors += '#{0} : syntax error, missing expression-stmt\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.expression_stmt(parent)

    # Selection-stmt -> if ( Expression ) Statement else Statement
    def selection_stmt(self, parent):
        if self.lookahead_lexeme == 'if':
            node = anytree.Node('Selection-stmt', parent=parent)
            self.match(node, ('KEYWORD', ['if']))
            self.match(node, ('SYMBOL', ['(']))
            self.expression(node)
            self.match(node, ('SYMBOL', [')']))
            self.code_generator.code_gen('#save')
            self.statement(node)
            self.match(node, ('KEYWORD', ['else']))
            self.code_generator.code_gen('#jpf')
            self.statement(node)
            self.code_generator.code_gen('#jp')
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'break', 'else',
                                                                               'while', 'return', 'for', '+', '-']:
            self.errors += '#{0} : syntax error, missing selection-stmt\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.selection_stmt(parent)

    # Iteration-stmt -> while ( Expression ) Statement
    def iteration_stmt(self, parent):
        if self.lookahead_lexeme == 'while':
            node = anytree.Node('Iteration-stmt', parent=parent)
            self.code_generator.code_gen('#loop')
            self.match(node, ('KEYWORD', ['while']))
            self.match(node, ('SYMBOL', ['(']))
            self.code_generator.code_gen('#label')
            self.expression(node)
            self.match(node, ('SYMBOL', [')']))
            self.code_generator.code_gen('#save')
            self.statement(node)
            self.code_generator.code_gen('#while_stmt')
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'break', 'else',
                                                                               'if', 'return', 'for', '+', '-']:
            self.errors += '#{0} : syntax error, missing iteration-stmt\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.iteration_stmt(parent)

    # Return-stmt -> return Return-stmt-prime
    def return_stmt(self, parent):
        if self.lookahead_lexeme == 'return':
            node = anytree.Node('Return-stmt', parent=parent)
            self.match(node, ('KEYWORD', ['return']))
            self.return_stmt_prime(node)
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'break', 'else',
                                                                               'if', 'while', 'for', '+', '-']:
            self.errors += '#{0} : syntax error, missing return-stmt\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.return_stmt(parent)

    # Return-stmt-prime -> ; | Expression ;
    def return_stmt_prime(self, parent):
        if self.lookahead_lexeme == ';':
            node = anytree.Node('Return-stmt-prime', parent=parent)
            self.code_generator.code_gen('#return')
            self.match(node, ('SYMBOL', [';']))
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Return-stmt-prime', parent=parent)
            self.expression(node)
            self.code_generator.code_gen('#return_value')
            self.match(node, ('SYMBOL', [';']))
        elif self.lookahead_lexeme in ['{', '}', 'break', 'else', 'if', 'while', 'return', 'for']:
            self.errors += '#{0} : syntax error, missing return-stmt-prime\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.return_stmt_prime(parent)

    # For-stmt -> for ID = Vars Statement
    def for_stmt(self, parent):
        if self.lookahead_lexeme == 'for':
            node = anytree.Node('For-stmt', parent=parent)
            self.code_generator.code_gen('#loop')
            self.match(node, ('KEYWORD', ['for']))
            self.code_generator.code_gen('#loop_size')
            self.code_generator.code_gen('#pid', self.lookahead_lexeme)
            self.code_generator.code_gen('#push_zero')
            self.match(node, ('ID', ['ID']))
            self.match(node, ('SYMBOL', ['=']))
            self.vars(node)
            # self.code_generator.code_gen('#label')
            self.code_generator.code_gen('#assign_for')
            self.code_generator.code_gen('#initial')
            self.code_generator.code_gen('#save')
            self.code_generator.code_gen('#step')
            self.statement(node)
            self.code_generator.code_gen('#for_stmt')
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', '}', 'break', 'else',
                                                                               'if', 'while', 'return', '+', '-']:
            self.errors += '#{0} : syntax error, missing for-stmt\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.for_stmt(parent)

    # Vars -> Var Var-zegond
    def vars(self, parent):
        if self.lookahead_type == 'ID':
            node = anytree.Node('Vars', parent=parent)
            self.var(node)
            self.code_generator.code_gen('#count')
            self.var_zegond(node)
        elif self.lookahead_type == 'NUM' or self.lookahead_lexeme in [';', '(', '{', 'break', 'if', 'while', 'return',
                                                                       'for', '+', '-']:
            self.errors += '#{0} : syntax error, missing vars\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.vars(parent)

    # Var-zegond -> , Var Var-zegond | EPSILON
    def var_zegond(self, parent):
        if self.lookahead_lexeme == ',':
            node = anytree.Node('Var-zegond', parent=parent)
            self.match(node, ('SYMBOL', [',']))
            self.var(node)
            self.code_generator.code_gen('#count')
            self.var_zegond(node)
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', '(', '{', 'break', 'if', 'while',
                                                                               'return', 'for', '+', '-']:
            node = anytree.Node('Var-zegond', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.var_zegond(parent)

    # Var -> ID Var-prime
    def var(self, parent):
        if self.lookahead_type == 'ID':
            node = anytree.Node('Var', parent=parent)
            self.code_generator.code_gen('#pid', self.lookahead_lexeme)
            self.match(node, ('ID', ['ID']))
            self.var_prime(node)
        elif self.lookahead_type == 'NUM' or self.lookahead_lexeme in [';', '(', '{', ',', 'break', 'if', 'while',
                                                                       'return', 'for', '+', '-']:
            self.errors += '#{0} : syntax error, missing var\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.var(parent)

    # Expression -> Simple-expression-zegond | ID B
    def expression(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Expression', parent=parent)
            self.simple_expression_zegond(node)
        elif self.lookahead_type == 'ID':
            node = anytree.Node('Expression', parent=parent)
            self.code_generator.code_gen('#pid', self.lookahead_lexeme)
            self.match(node, ('ID', ['ID']))
            self.b(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            self.errors += '#{0} : syntax error, missing expression\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.expression(parent)

    # B -> = Expression | [ Expression ] H | Simple-expression-prime
    def b(self, parent):
        if self.lookahead_lexeme == '=':
            node = anytree.Node('B', parent=parent)
            self.match(node, ('SYMBOL', ['=']))
            self.expression(node)
            self.code_generator.code_gen('#assign')
        elif self.lookahead_lexeme == '[':
            node = anytree.Node('B', parent=parent)
            self.match(node, ('SYMBOL', ['[']))
            self.expression(node)
            self.match(node, ('SYMBOL', [']']))
            self.code_generator.code_gen('#address_array')
            self.h(node)
        elif self.lookahead_lexeme in ['(', '<', '==', '+', '-', '*']:
            node = anytree.Node('B', parent=parent)
            self.simple_expression_prime(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            node = anytree.Node('B', parent=parent)
            node_1 = anytree.Node('Simple-expression-prime', parent=node)
            node_2 = anytree.Node('Additive-expression-prime', parent=node_1)
            node_4 = anytree.Node('Term-prime', parent=node_2)
            node_6 = anytree.Node('Signed-factor-prime', parent=node_4)
            node_8 = anytree.Node('Factor-prime', parent=node_6)
            anytree.Node('epsilon', parent=node_8)
            node_7 = anytree.Node('G', parent=node_4)
            anytree.Node('epsilon', parent=node_7)
            node_5 = anytree.Node('D', parent=node_2)
            anytree.Node('epsilon', parent=node_5)
            node_3 = anytree.Node('C', parent=node_1)
            anytree.Node('epsilon', parent=node_3)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.b(parent)

    # H -> = Expression | G D C
    def h(self, parent):
        if self.lookahead_lexeme == '=':
            node = anytree.Node('H', parent=parent)
            self.match(node, ('SYMBOL', ['=']))
            self.expression(node)
            self.code_generator.code_gen('#assign')
        elif self.lookahead_lexeme in ['<', '==', '+', '-', '*']:
            node = anytree.Node('H', parent=parent)
            self.g(node)
            self.d(node)
            self.c(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            node = anytree.Node('H', parent=parent)
            node_1 = anytree.Node('G', parent=node)
            anytree.Node('epsilon', parent=node_1)
            node_2 = anytree.Node('D', parent=node)
            anytree.Node('epsilon', parent=node_2)
            node_3 = anytree.Node('C', parent=node)
            anytree.Node('epsilon', parent=node_3)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.h(parent)

    # Simple-expression-zegond -> Additive-expression-zegond C
    def simple_expression_zegond(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Simple-expression-zegond', parent=parent)
            self.additive_expression_zegond(node)
            self.c(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            self.errors += '#{0} : syntax error, missing simple-expression-zegond\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.simple_expression_zegond(parent)

    # Simple-expression-prime -> Additive-expression-prime C
    def simple_expression_prime(self, parent):
        if self.lookahead_lexeme in ['(', '<', '==', '+', '-', '*']:
            node = anytree.Node('Simple-expression-prime', parent=parent)
            self.additive_expression_prime(node)
            self.c(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            node = anytree.Node('Simple-expression-prime', parent=parent)
            node_2 = anytree.Node('Additive-expression-prime', parent=node)
            node_4 = anytree.Node('Term-prime', parent=node_2)
            node_6 = anytree.Node('Signed-factor-prime', parent=node_4)
            node_8 = anytree.Node('Factor-prime', parent=node_6)
            anytree.Node('epsilon', parent=node_8)
            node_7 = anytree.Node('G', parent=node_4)
            anytree.Node('epsilon', parent=node_7)
            node_5 = anytree.Node('D', parent=node_2)
            anytree.Node('epsilon', parent=node_5)
            node_3 = anytree.Node('C', parent=node)
            anytree.Node('epsilon', parent=node_3)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.signed_factor_prime(parent)

    # C -> Relop Additive-expression | EPSILON
    def c(self, parent):
        if self.lookahead_lexeme in ['<', '==']:
            node = anytree.Node('C', parent=parent)
            self.code_generator.code_gen('#operator', self.lookahead_lexeme)
            self.relop(node)
            self.additive_expression(node)
            self.code_generator.code_gen('#relop')
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            node = anytree.Node('C', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.c(parent)

    # Relop -> < | ==
    def relop(self, parent):
        if self.lookahead_lexeme == '==':
            node = anytree.Node('Relop', parent=parent)
            # self.code_generator.relop_sign()
            self.match(node, ('SYMBOL', ['==']))
        elif self.lookahead_lexeme == '<':
            node = anytree.Node('Relop', parent=parent)
            # self.code_generator.relop_sign()
            self.match(node, ('SYMBOL', ['<']))
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            self.errors += '#{0} : syntax error, missing relop\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.relop(parent)

    # Additive-expression -> Term D
    def additive_expression(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Additive-expression', parent=parent)
            self.term(node)
            self.d(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',']:
            self.errors += '#{0} : syntax error, missing additive-expression\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.additive_expression(parent)

    # Additive-expression-prime -> Term-prime D
    def additive_expression_prime(self, parent):
        if self.lookahead_lexeme in ['(', '+', '-', '*']:
            node = anytree.Node('Additive-expression-prime', parent=parent)
            self.term_prime(node)
            self.d(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==']:
            node = anytree.Node('Additive-expression-prime', parent=parent)
            node_4 = anytree.Node('Term-prime', parent=node)
            node_6 = anytree.Node('Signed-factor-prime', parent=node_4)
            node_8 = anytree.Node('Factor-prime', parent=node_6)
            anytree.Node('epsilon', parent=node_8)
            node_7 = anytree.Node('G', parent=node_4)
            anytree.Node('epsilon', parent=node_7)
            node_5 = anytree.Node('D', parent=node)
            anytree.Node('epsilon', parent=node_5)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.additive_expression_prime(parent)

    # Additive-expression-zegond -> Term-zegond D
    def additive_expression_zegond(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Additive-expression-zegond', parent=parent)
            self.term_zegond(node)
            self.d(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==']:
            self.errors += '#{0} : syntax error, missing additive-expression-zegond\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.additive_expression_zegond(parent)

    # D -> Addop Term D | EPSILON
    def d(self, parent):
        if self.lookahead_lexeme in ['+', '-']:
            node = anytree.Node('D', parent=parent)
            self.code_generator.code_gen('#operator', self.lookahead_lexeme)
            self.addop(node)
            self.term(node)
            self.code_generator.code_gen('#add_or_sub')
            self.d(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==']:
            node = anytree.Node('D', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.d(parent)

    # Addop -> + | -
    def addop(self, parent):
        if self.lookahead_lexeme in ['+', '-']:
            node = anytree.Node('Addop', parent=parent)
            self.match(node, ('SYMBOL', ['+', '-']))
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            self.errors += '#{0} : syntax error, missing addop\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.addop(parent)

    # Term -> Signed-factor G
    def term(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Term', parent=parent)
            self.signed_factor(node)
            self.g(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-']:
            self.errors += '#{0} : syntax error, missing term\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.term(parent)

    # Term-prime -> Signed-factor-prime G
    def term_prime(self, parent):
        if self.lookahead_lexeme in ['(', '*']:
            node = anytree.Node('Term-prime', parent=parent)
            self.signed_factor_prime(node)
            self.g(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-']:
            node = anytree.Node('Term-prime', parent=parent)
            node_1 = anytree.Node('Signed-factor-prime', parent=node)
            node_3 = anytree.Node('Factor-prime', parent=node_1)
            anytree.Node('epsilon', parent=node_3)
            node_2 = anytree.Node('G', parent=node)
            anytree.Node('epsilon', parent=node_2)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.term_prime(parent)

    # Term-zegond -> Signed-factor-zegond G
    def term_zegond(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Term-zegond', parent=parent)
            self.signed_factor_zegond(node)
            self.g(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-']:
            self.errors += '#{0} : syntax error, missing term-zegond\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.term_zegond(parent)

    # G -> * Signed-factor G | EPSILON
    def g(self, parent):
        if self.lookahead_lexeme == '*':
            node = anytree.Node('G', parent=parent)
            self.match(node, ('SYMBOL', ['*']))
            self.signed_factor(node)
            self.code_generator.code_gen('#mult')
            self.g(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-']:
            node = anytree.Node('G', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.g(parent)

    # Signed-factor -> + Factor | - Factor | Factor
    def signed_factor(self, parent):
        flag = self.lookahead_lexeme == '-'
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme == '(':
            node = anytree.Node('Signed-factor', parent=parent)
            self.factor(node)
        elif self.lookahead_lexeme in ['+', '-']:
            node = anytree.Node('Signed-factor', parent=parent)
            # self.code_generator.sign()
            self.match(node, ('SYMBOL', ['+', '-']))
            self.factor(node)
            if flag:
                self.code_generator.code_gen('#signed_num')
        elif self.lookahead_lexeme in {';', ']', ')', ',', '<', '==', '+', '-', '*'}:
            self.errors += '#{0} : syntax error, missing signed-factor\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.signed_factor(parent)

    # Signed-factor-prime -> Factor-prime
    def signed_factor_prime(self, parent):
        if self.lookahead_lexeme == '(':
            node = anytree.Node('Signed-factor-prime', parent=parent)
            self.factor_prime(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-', '*']:
            node = anytree.Node('Signed-factor-prime', parent=parent)
            node_1 = anytree.Node('Factor-prime', parent=node)
            anytree.Node('epsilon', parent=node_1)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.signed_factor_prime(parent)

    # Signed-factor-zegond -> + Factor | - Factor | Factor-zegond
    def signed_factor_zegond(self, parent):
        flag = self.lookahead_lexeme == '-'
        if self.lookahead_type == 'NUM' or self.lookahead_lexeme == '(':
            node = anytree.Node('Signed-factor-zegond', parent=parent)
            self.factor_zegond(node)
        elif self.lookahead_lexeme in ['+', '-']:
            node = anytree.Node('Signed-factor-zegond', parent=parent)
            # self.code_generator.sign()
            self.match(node, ('SYMBOL', ['+', '-']))
            self.factor(node)
            if flag:
                self.code_generator.code_gen('#signed_num')
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-', '*']:
            self.errors += '#{0} : syntax error, missing signed-factor-zegond\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.signed_factor_zegond(parent)

    # Factor -> ( Expression ) | ID Var-call-prime | NUM
    def factor(self, parent):
        if self.lookahead_lexeme == '(':
            node = anytree.Node('Factor', parent=parent)
            self.match(node, ('SYMBOL', ['(']))
            self.expression(node)
            self.match(node, ('SYMBOL', [')']))
        elif self.lookahead_type == 'ID':
            node = anytree.Node('Factor', parent=parent)
            self.code_generator.code_gen('#pid', self.lookahead_lexeme)
            self.match(node, ('ID', ['ID']))
            self.var_call_prime(node)
        elif self.lookahead_type == 'NUM':
            node = anytree.Node('Factor', parent=parent)
            self.code_generator.code_gen('#pnum', self.lookahead_lexeme)
            self.match(node, ('NUM', ['NUM']))
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-', '*']:
            self.errors += '#{0} : syntax error, missing factor\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.factor(parent)

    # Var-call-prime -> ( Args ) | Var-prime
    def var_call_prime(self, parent):
        if self.lookahead_lexeme == '(':
            self.code_generator.code_gen('#start_function_call')
            node = anytree.Node('Var-call-prime', parent=parent)
            self.match(node, ('SYMBOL', ['(']))
            self.args(node)
            self.match(node, ('SYMBOL', [')']))
            self.code_generator.code_gen('#function_call')
        elif self.lookahead_lexeme == '[':
            node = anytree.Node('Var-call-prime', parent=parent)
            self.var_prime(node)
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-', '*']:
            node = anytree.Node('Var-call-prime', parent=parent)
            node_1 = anytree.Node('Var-prime', parent=node)
            anytree.Node('epsilon', parent=node_1)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.var_call_prime(parent)

    # Var-prime -> [ Expression ] | EPSILON
    def var_prime(self, parent):
        if self.lookahead_lexeme == '[':
            node = anytree.Node('Var-prime', parent=parent)
            self.match(node, ('SYMBOL', ['[']))
            self.expression(node)
            self.match(node, ('SYMBOL', [']']))
            self.code_generator.code_gen('#address_array')
        elif self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in [';', ']', '(', ')', ',', '{', 'break',
                                                                               'if', 'while', 'return', 'for', '<',
                                                                               '==', '+', '-', '*']:
            node = anytree.Node('Var-prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.var_prime(parent)

    # Factor-prime -> ( Args ) | EPSILON
    def factor_prime(self, parent):
        if self.lookahead_lexeme == '(':
            self.code_generator.code_gen('#start_function_call')
            node = anytree.Node('Factor-prime', parent=parent)
            self.match(node, ('SYMBOL', ['(']))
            self.args(node)
            self.match(node, ('SYMBOL', [')']))
            self.code_generator.code_gen('#function_call')
        elif self.lookahead_lexeme in {';', ']', ')', ',', '<', '==', '+', '-', '*'}:
            node = anytree.Node('Factor-prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.factor_prime(parent)

    # Factor-zegond -> ( Expression ) | NUM
    def factor_zegond(self, parent):
        if self.lookahead_lexeme == '(':
            node = anytree.Node('Factor-zegond', parent=parent)
            self.match(node, ('SYMBOL', ['(']))
            self.expression(node)
            self.match(node, ('SYMBOL', [')']))
        elif self.lookahead_type == 'NUM':
            node = anytree.Node('Factor-zegond', parent=parent)
            self.code_generator.code_gen('#pnum', self.lookahead_lexeme)
            self.match(node, ('NUM', ['NUM']))
        elif self.lookahead_lexeme in [';', ']', ')', ',', '<', '==', '+', '-', '*']:
            self.errors += '#{0} : syntax error, missing factor-zegond\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.factor_zegond(parent)

    # Args -> Arg-list | EPSILON
    def args(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Args', parent=parent)
            self.arg_list(node)
        elif self.lookahead_lexeme == ')':
            node = anytree.Node('Args', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.args(parent)

    # Arg-list -> Expression Arg-list-prime
    def arg_list(self, parent):
        if self.lookahead_type in ['ID', 'NUM'] or self.lookahead_lexeme in ['(', '+', '-']:
            node = anytree.Node('Arg-list', parent=parent)
            self.expression(node)
            self.arg_list_prime(node)
        elif self.lookahead_lexeme == ')':
            self.errors += '#{0} : syntax error, missing arg-list\n'.format(self.scanner.line)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.arg_list(parent)

    # Arg-list-prime -> , Expression Arg-list-prime | EPSILON
    def arg_list_prime(self, parent):
        if self.lookahead_lexeme == ',':
            node = anytree.Node('Arg-list-prime', parent=parent)
            self.match(node, ('SYMBOL', [',']))
            self.expression(node)
            self.arg_list_prime(node)
        elif self.lookahead_lexeme == ')':
            node = anytree.Node('Arg-list-prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        elif self.lookahead_lexeme is not None:
            if self.lookahead_lexeme == '$':
                self.errors += '#{0} : syntax error, unexpected EOF\n'.format(self.scanner.line)
            else:
                expected = self.lookahead_type if self.lookahead_type in ['ID', 'NUM'] else self.lookahead_lexeme
                self.errors += '#{0} : syntax error, illegal {1}\n'.format(self.scanner.line, expected)
            self.next()
            self.arg_list_prime(parent)
