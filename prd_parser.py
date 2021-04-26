import anytree


class Parser:

    def __init__(self, scr):
        self.lookahead_type = None
        self.lookahead_token = None
        self.scanner = scr
        self.parse_tree = None
        self.errors = ''

    def parse(self):
        self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        while self.lookahead_type is None:
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        self.program()
        return self.parse_tree

    def next(self):
        self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        while self.lookahead_type is None:
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()

    def match_value(self, parent, expected_token):
        if self.lookahead_token == expected_token:
            anytree.Node('(' + self.lookahead_type + ', ' + str(self.lookahead_token) + ')', parent=parent)
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
            while self.lookahead_type is None:
                self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        else:
            print("Error")
            # TODO -> Error handling
        return

    def match_type(self, parent, expected_type):
        if self.lookahead_type == expected_type:
            anytree.Node('(' + self.lookahead_type + ', ' + str(self.lookahead_token) + ')', parent=parent)
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
            while self.lookahead_type is None:
                self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        else:
            print("Error")
            # TODO -> Error handling
        return

    # program ->  declaration-list $
    def program(self):
        if self.lookahead_token in {'int', 'void'}:
            self.parse_tree = anytree.Node('Program', parent=None)
            self.declaration_list(self.parse_tree)
        elif self.lookahead_token == '$':
            self.parse_tree = anytree.Node('Program', parent=None)
            node = anytree.Node('Declaration list', parent=self.parse_tree)
            anytree.Node('epsilon', parent=node)
            anytree.Node('$', parent=self.parse_tree)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.program()

    # declaration-list -> declaration declaration-list | EPSILON
    def declaration_list(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Declaration list', parent=parent)
            self.declaration(node)
            self.declaration_list(node)
        elif self.lookahead_type in {'ID', 'NUM', ';', '(', '{', '}', 'break', 'if', 'while', 'return', 'for', '+', '-', '$'}:
            node = anytree.Node('Declaration list', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.declaration(parent)

    # declaration -> Declaration-initial Declaration-prime
    def declaration(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Declaration', parent=parent)
            self.declaration_initial(node)
            self.declaration_prime(node)
        elif self.lookahead_type in {'ID', 'NUM', ';', '(', '{', '}', 'int', 'void', 'break', 'if', 'while', 'return',
                                     'for', '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing declaration'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.declaration(parent)

    # declaration_initial ->  type-specifier ID
    def declaration_initial(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Declaration initial', parent=parent)
            self.type_specifier(node)
            self.match_type(node, 'ID')
        elif self.lookahead_token in {';', '[', '(', ')', ','}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing declaration_initial'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.declaration_initial(parent)

    # Declaration-prime -> Fun-declaration-prime | Var-declaration-prime
    def declaration_prime(self, parent):
        if self.lookahead_token in {';', '['}:
            node = anytree.Node('Declaration prime', parent=parent)
            self.var_declaration_prime(node)
        elif self.lookahead_token == '(':
            node = anytree.Node('Declaration prime', parent=parent)
            self.fun_declaration_prime(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'int', 'void',
                                                                              'break', 'if', 'while', 'return', 'for',
                                                                              '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing declaration_prime'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.declaration_prime(parent)

    # Fun-declaration-prime -> ( Params ) Compound-stmt
    def fun_declaration_prime(self, parent):
        if self.lookahead_token == '(':
            node = anytree.Node('Fun declaration prime', parent=parent)
            self.match_value(node, '(')
            self.params(node)
            self.match_value(node, ')')
            self.compound_stmt(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'int', 'void', 'break',
                                                                              'if', 'while', 'return', 'for', '+', '-',
                                                                              '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing Fun_declaration_prime'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.fun_declaration_prime(parent)

    # Var-declaration-prime -> ; | [ NUM ] ;
    def var_declaration_prime(self, parent):
        if self.lookahead_token == ';':
            node = anytree.Node('Var declaration prime', parent=parent)
            self.match_value(node, ';')
        elif self.lookahead_token == '[':
            node = anytree.Node('Var declaration prime', parent=parent)
            self.match_value(node, '[')
            self.match_type(node, 'NUM')
            self.match_value(node, ']')
            self.match_value(node, ';')
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'int', 'void', 'break',
                                                                              'if', 'while', 'return', 'for', '+', '-',
                                                                              '$'}:
            if self.lookahead_type == 'NUM':
                self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing ['
            else:
                self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing ;'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.var_declaration_prime(parent)

    # Type-specifier -> int | void
    def type_specifier(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Type specifier', parent=parent)
            self.match_type(node, 'KEYWORD')
        elif self.lookahead_type == 'ID':
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing int or void'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.type_specifier(parent)

    # TODO: Zahra
    # Params -> int ID Param-prime Param-list | void Param-list-void-abtar
    def params(self, parent):
        if self.lookahead_token == 'int':
            node = anytree.Node('Params', parent=parent)
            self.match_type(node, 'KEYWORD')
            self.match_type(node, 'ID')
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead_token == 'void':
            node = anytree.Node('Params', parent=parent)
            self.match_type(node, 'KEYWORD')
            self.param_list_void_abtar(node)
        elif self.lookahead_type == ')':
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing params'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.params(parent)

    # Param-list-void-abtar -> ID Param-prime Param-list | EPSILON
    def param_list_void_abtar(self, parent):
        if self.lookahead_type == 'ID':
            node = anytree.Node('Param list void abtar', parent=parent)
            self.match_type(node, 'ID')
            self.param_prime(node)
            self.param_list(node)
        elif self.lookahead_token == ')':
            node = anytree.Node('Param list void abtar', paren=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.param_list_void_abtar(parent)

    # TODO: Zahra
    # Param-list -> , Param Param-list | EPSILON
    # First: , EPSILON  Follow: )
    def param_list(self, parent):
        pass

    # Param -> Declaration-initial Param-prime
    def param(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Param', parent=parent)
            self.declaration_initial(node)
            self.param_prime(node)
        elif self.lookahead_token in {')', ','}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing int or void'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.param(parent)

    # TODO: Zahra
    # Param-prime -> [ ] | EPSILON
    def param_prime(self, parent):
        pass

    # Compound-stmt -> { Declaration-list Statement-list }
    def compound_stmt(self, parent):
        if self.lookahead_token == '{':
            node = anytree.Node('Compound stmt', parent=parent)
            self.match_value(node, '{')
            self.declaration_list(node)
            self.statement_list(node)
            self.match_value(node, '}')
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'int', 'void', 'break',
                                                                              'if', 'else', 'while', 'return', 'for',
                                                                              '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing {'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.compound_stmt(parent)

    # TODO: Zahra
    # Statement-list -> Statement Statement-list | EPSILON
    def statement_list(self, parent):
        pass

    # Statement -> Expression-stmt | Compound-stmt | Selection-stmt | Iteration-stmt | Return-stmt | For-stmt
    def statement(self, parent):
        if self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', 'break', '+', '-'}:
            node = anytree.Node('Statement', parent=parent)
            self.expression_stmt(node)
        elif self.lookahead_token == '{':
            node = anytree.Node('Statement', parent=parent)
            self.compound_stmt(node)
        elif self.lookahead_token == 'if':
            node = anytree.Node('Statement', parent=parent)
            self.selection_stmt(node)
        elif self.lookahead_token == 'while':
            node = anytree.Node('Statement', parent=parent)
            self.selection_stmt(node)
        elif self.lookahead_token == 'return':
            node = anytree.Node('Statement', parent=parent)
            self.return_stmt(node)
        elif self.lookahead_token == 'for':
            node = anytree.Node('Statement', parent=parent)
            self.for_stmt(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'break', 'else', 'if',
                                                                              'while', 'return', 'for', '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing statement'
            self.next()

    # TODO: Zahra
    # Expression-stmt -> Expression ; | break ; | ;
    def expression_stmt(self, parent):
        pass

    # Selection-stmt -> if ( Expression ) Statement else Statement
    def selection_stmt(self, parent):
        if self.lookahead_token == 'if':
            node = anytree.Node('Selection stmt', parent=parent)
            self.match_value(node, 'if')
            self.match_value(node, '(')
            self.expression(node)
            self.match_value(node, ')')
            self.match_value(node, 'else')
            self.statement(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'break', 'else', 'if',
                                                                              'while', 'return', 'for', '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing selection stmt'
            # self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.selection_stmt(parent)

    # TODO: Zahra
    # Iteration-stmt -> while ( Expression ) Statement
    def iteration_stmt(self, parent):
        pass

    # Return-stmt -> return Return-stmt-prime
    def return_stmt(self, parent):
        if self.lookahead_token == 'return':
            node = anytree.Node('Return stmt', parent=parent)
            self.match_value(node, 'return')
            self.return_stmt_prime(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'break', 'else', 'if',
                                                                              'while', 'return', 'for', '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing return stmt'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.return_stmt(parent)

    # TODO: Zahra
    # Return-stmt-prime -> ; | Expression ;
    def return_stmt_prime(self, parent):
        pass

    # For-stmt -> for ID = Vars Statement
    def for_stmt(self, parent):
        if self.lookahead_token == 'for':
            node = anytree.Node('For stmt', parent=parent)
            self.match_value(node, 'for')
            self.match_type(node, 'ID')
            self.match_value(node, '=')
            self.vars(node)
            self.statement(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', '}', 'break', 'else', 'if',
                                                                              'while', 'return', 'for', '+', '-', '$'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing for stmt'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.for_stmt(parent)

    # TODO: Zahra
    # Vars -> Var Var-zegond
    def vars(self, parent):
        pass

    # Var-zegond -> , Var Var-zegond | EPSILON
    def var_zegond(self, parent):
        if self.lookahead_token == ',':
            node = anytree.Node('Var zegond', parent=parent)
            self.match_value(node, ',')
            self.var(node)
            self.var_zegond(node)
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {';', '(', '{', 'break', 'if', 'while',
                                                                              'return', 'for', '+', '-'}:
            node = anytree.Node('Var zegond', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.var_zegond(parent)

    # TODO: Zahra
    # Var -> ID Var-prime
    def var(self, parent):
        pass

    # Expression -> Simple-expression-zegond | ID B
    def expression(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_token in {'(', '+', '-'}:
            node = anytree.Node('Expression', parent=parent)
            self.simple_expression_zegond(node)
        elif self.lookahead_type == 'ID':
            node = anytree.Node('Expression', parent=parent)
            self.match_type(node, 'ID')
            self.b(node)
        elif self.lookahead_token in {';', ']', ')', ','}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing Expression'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.expression(parent)

    # TODO: Zahra
    # B -> = Expression | [ Expression ] H | Simple-expression-prime
    def b(self, parent):
        pass

    # H -> = Expression | G D C
    def h(self, parent):
        if self.lookahead_token == '=':
            node = anytree.Node('H', parent=parent)
            self.match_value(node, '=')
            self.expression(node)
        elif self.lookahead_token in {'<', '==', '+', '-', '*'}:
            node = anytree.Node('H', parent=parent)
            self.g(node)
            self.d(node)
            self.c(node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.h(parent)

    # TODO: Zahra
    # Simple-expression-zegond -> Additive-expression-zegond C
    def simple_expression_zegond(self, parent):
        pass

    # Simple-expression-prime -> Additive-expression-prime C
    def simple_expression_prime(self, parent):
        if self.lookahead_token in {'(', '<', '==', '+', '-', '*'}:
            node = anytree.Node('Simple expression prime', parent=parent)
            self.additive_expression_prime(node)
            self.c(node)
        elif self.lookahead_token in {';', ']', ')', ','}:
            node = anytree.Node('Simple expression prime', parent=parent)
            node_1 = anytree.Node('Additive expression prime', parent=node)
            anytree.Node('epsilon', parent=node_1)
            node_2 = anytree.Node('C', parent=node)
            anytree.Node('epsilon', parent=node_2)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.signed_factor_prime(parent)

    # TODO: Zahra
    # C -> Relop Additive-expression | EPSILON
    def c(self, parent):
        pass

    # Relop -> < | ==
    def relop(self, parent):
        if self.lookahead_token == '==':
            node = anytree.Node('Relop', parent=parent)
            self.match_value(node, '==')
        elif self.lookahead_token == '<':
            node = anytree.Node('Relop', parent=parent)
            self.match_value(node, '<')
        elif self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {'(', '+', '-'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing == or <'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.relop(parent)

    # TODO: Zahra
    # Additive-expression -> Term D
    def additive_expression(self, parent):
        pass

    # Additive-expression-prime -> Term-prime D
    def additive_expression_prime(self, parent):
        if self.lookahead_token in {'(', '+', '-', '*'}:
            node = anytree.Node('Additive expression prime', parent=parent)
            self.term_prime(node)
            self.d(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '=='}:
            node = anytree.Node('Simple expression prime', parent=parent)
            node_1 = anytree.Node('Term prime', parent=node)
            anytree.Node('epsilon', parent=node_1)
            node_2 = anytree.Node('D', parent=node)
            anytree.Node('epsilon', parent=node_2)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.additive_expression_prime(parent)

    # TODO: Zahra
    # Additive-expression-zegond -> Term-zegond D
    def additive_expression_zegond(self, parent):
        pass

    # D -> Addop Term D | EPSILON
    def d(self, parent):
        if self.lookahead_token in {'+', '-'}:
            node = anytree.Node('D', parent=parent)
            self.addop(node)
            self.term(node)
            self.d(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '=='}:
            node = anytree.Node('D', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.d(parent)

    # TODO: Zahra
    # Addop -> + | -
    def addop(self, parent):
        pass

    # Term -> Signed-factor G
    def term(self, parent):
        if self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token in {'(', '+', '-'}:
            node = anytree.Node('Term', parent=parent)
            self.signed_factor(node)
            self.g(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '==', '+', '-'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing ID or NUM'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.term(parent)

    # TODO: Zahra
    # Term-prime -> Signed-factor-prime G
    def term_prime(self, parent):
        pass

    # Term-zegond -> Signed-factor-zegond G
    def term_zegond(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_token in {'(', '+', '-'}:
            node = anytree.Node('Term Zegond', parent=parent)
            self.signed_factor_zegond(node)
            self.g(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '==', '+', '-'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing NUM'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.term_zegond(parent)

    # TODO: Zahra
    # G -> * Signed-factor G | EPSILON
    def g(self, parent):
        pass

    # Signed-factor -> + Factor | - Factor | Factor
    def signed_factor(self, parent):
        if self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token == '(':
            node = anytree.Node('Signed factor', parent=parent)
            self.factor(node)
        elif self.lookahead_token == '+':
            node = anytree.Node('Signed factor', parent=parent)
            self.match_value(node, '+')
            self.factor(node)
        elif self.lookahead_token == '-':
            node = anytree.Node('Signed factor', parent=parent)
            self.match_value(node, '-')
            self.factor(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '==', '+', '-', '*'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing ID or NUM'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.signed_factor(parent)

    # TODO: Zahra
    # Signed-factor-prime -> Factor-prime
    def signed_factor_prime(self, parent):
        pass

    # Signed-factor-zegond -> + Factor | - Factor | Factor-zegond
    def signed_factor_zegond(self, parent):
        if self.lookahead_type == 'NUM' or self.lookahead_token == '(':
            node = anytree.Node('Signed factor zegond', parent=parent)
            self.factor_zegond(node)
        elif self.lookahead_token == '+':
            node = anytree.Node('Signed factor zegond', parent=parent)
            self.match_value(node, '+')
            self.factor(node)
        elif self.lookahead_token == '-':
            node = anytree.Node('Signed factor zegond', parent=parent)
            self.match_value(node, '-')
            self.factor(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '==', '+', '-', '*'}:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, missing ID or NUM'
            self.next()
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.signed_factor_zegond(parent)

    # TODO: Zahra
    # Factor -> ( Expression ) | ID Var-call-prime | NUM
    def factor(self, parent):
        pass

    # Var-call-prime -> ( Args ) | Var-prime
    def var_call_prime(self, parent):
        if self.lookahead_token == '(':
            node = anytree.Node('Var call prime', parent=parent)
            self.match_value(node, '(')
            self.args(node)
            self.match_value(node, ')')
        elif self.lookahead_token == '[':
            node = anytree.Node('Var call prime', parent=parent)
            self.var_prime(node)
        elif self.lookahead_token in {';', ']', ')', ',', '<', '==', '+', '-', '*'}:
            node = anytree.Node('Var call prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.var_call_prime(parent)

    # TODO: Zahra
    # Var-prime -> [ Expression ] | EPSILON
    def var_prime(self, parent):
        pass

    # Factor-prime -> ( Args ) | EPSILON
    def factor_prime(self, parent):
        if self.lookahead_token == '(':
            node = anytree.Node('Factor prime', parent=parent)
            self.match_value(node, '(')
            self.args(node)
            self.match_value(node, ')')
        elif self.lookahead_token in {';', ']', ')', ',', '<', '==', '+', '-', '*'}:
            node = anytree.Node('Factor prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.factor_prime(parent)

    # TODO: Zahra
    # Factor-zegond -> ( Expression ) | NUM
    def factor_zegond(self, parent):
        pass

    # Args -> Arg-list | EPSILON
    def args(self, parent):
        if self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token == '(':
            node = anytree.Node('Args', parent=parent)
            self.arg_list(node)
        elif self.lookahead_token == ')':
            node = anytree.Node('Args', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.args(parent)

    # TODO: Zahra
    # Arg-list -> Expression Arg-list-prime
    def arg_list(self, parent):
        pass

    # Arg-list-prime -> , Expression Arg-list-prime | EPSILON
    def arg_list_prime(self, parent):
        if self.lookahead_type in {'ID', 'NUM'} or self.lookahead_token == '(':
            node = anytree.Node('Args list prime', parent=parent)
            self.match_value(node, ',')
            self.expression(node)
            self.arg_list_prime(node)
        elif self.lookahead_token == ')':
            node = anytree.Node('Args list prime', parent=parent)
            anytree.Node('epsilon', parent=node)
        else:
            self.errors += '#' + str(self.scanner.line) + ' : syntax error, illegal ' + self.lookahead_token
            self.next()
            self.arg_list_prime(parent)
