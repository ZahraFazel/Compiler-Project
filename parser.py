import anytree
from scanner import Scanner


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

    # declaration-list -> declaration declaration-list | ϵ
    def declaration_list(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Declaration list', parent=parent)
            self.declaration(node)
            self.declaration_list(node)
        elif self.lookahead_token == '$':
            anytree.Node('$', parent=parent)

    # declaration -> Declaration-initial Declaration-prime
    def declaration(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Declaration', parent=parent)
            self.declaration_initial(node)
            self.declaration_prime(node)
        else:
            pass

    # declaration_initial ->  type-specifier ID
    def declaration_initial(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Declaration initial', parent=parent)
            self.type_specifier(node)
            self.match_type(node, 'ID')
        else:
            pass

    # Declaration-prime -> Fun-declaration-prime | Var-declaration-prime
    def declaration_prime(self, parent):
        if self.lookahead_token in {';', '['}:
            node = anytree.Node('Declaration prime', parent=parent)
            self.var_declaration_prime(node)
        elif self.lookahead_token == '(':
            node = anytree.Node('Declaration prime', parent=parent)
            self.fun_declaration_prime(node)
        else:
            pass

    # Fun-declaration-prime -> ( Params ) Compound-stmt
    def fun_declaration_prime(self, parent):
        if self.lookahead_token == '(':
            node = anytree.Node('Fun declaration prime', parent=parent)
            self.match_value(node, '(')
            self.params(node)
            self.match_value(node, ')')
            self.compound_stmt(node)
        else:
            pass

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

    # Type-specifier -> int | void
    def type_specifier(self, parent):
        if self.lookahead_token in {'int', 'void'}:
            node = anytree.Node('Type specifier', parent=parent)
            self.match_type(node, 'KEYWORD')
        else:
            pass

    # TODO: Zahra
    # Params -> int ID Param-prime Param-list | void Param-list-void-abtar
    def params(self, parent):
        pass

    # TODO: Fereshteh
    # Param-list-void-abtar -> ID Param-prime Param-list | EPSILON
    def param_list_void_abtar(self, parent):
        pass

    # TODO: Zahra
    # Param-list -> , Param Param-list | EPSILON
    def param_list(self, parent):
        pass

    # TODO: Fereshteh
    # Param -> Declaration-initial Param-prime
    def param(self, parent):
        pass

    # TODO: Zahra
    # Param-prime -> [ ] | EPSILON
    def param_prime(self, parent):
        pass

    # TODO: Fereshteh
    # Compound-stmt -> { Declaration-list Statement-list }
    def compound_stmt(self, parent):
        pass

    # TODO: Zahra
    # Statement-list -> Statement Statement-list | EPSILON
    def statement_list(self, parent):
        pass

    # TODO: Fereshteh
    # Statement -> Expression-stmt | Compound-stmt | Selection-stmt | Iteration-stmt | Return-stmt | For-stmt
    def statement(self, parent):
        pass

    # TODO: Zahra
    # Expression-stmt -> Expression ; | break ; | ;
    def expression_stmt(self, parent):
        pass

    # TODO: Fereshteh
    # Selection-stmt -> if ( Expression ) Statement else Statement
    def selection_stmt(self, parent):
        pass

    # TODO: Zahra
    # Iteration-stmt -> while ( Expression ) Statement
    def iteration_stmt(self, parent):
        pass

    # TODO: Fereshteh
    # Return-stmt -> return Return-stmt-prime
    def return_stmt(self, parent):
        pass

    # TODO: Zahra
    # Return-stmt-prime -> ; | Expression ;
    def return_stmt_prime(self, parent):
        pass

    # TODO: Fereshteh
    # For-stmt -> for ID = Vars Statement
    def for_stmt(self, parent):
        pass

    # TODO: Zahra
    # Vars -> Var Var-zegond
    def vars(self, parent):
        pass

    # TODO: Fereshteh
    # Var-zegond -> , Var Var-zegond | EPSILON
    def var_zegond(self, parent):
        pass

    # TODO: Zahra
    # Var -> ID Var-prime
    def var(self, parent):
        pass

    # TODO: Fereshteh
    # Expression -> Simple-expression-zegond | ID B
    def expression(self, parent):
        pass

    # TODO: Zahra
    # B -> = Expression | [ Expression ] H | Simple-expression-prime
    def b(self, parent):
        pass

    # TODO: Fereshteh
    # H -> = Expression | G D C
    def h(self, parent):
        pass

    # TODO: Zahra
    # Simple-expression-zegond -> Additive-expression-zegond C
    def simple_expression_zegond(self, parent):
        pass

    # TODO: Fereshteh
    # Simple-expression-prime -> Additive-expression-prime C
    def simple_expression_prime(self, parent):
        pass

    # TODO: Zahra
    # C -> Relop Additive-expression | EPSILON
    def c(self, parent):
        pass

    # TODO: Fereshteh
    # Relop -> < | ==
    def relop(self, parent):
        pass

    # TODO: Zahra
    # Additive-expression -> Term D
    def additive_expression(self, parent):
        pass

    # TODO: Fereshteh
    # Additive-expression-prime -> Term-prime D
    def additive_expression_prime(self, parent):
        pass

    # TODO: Zahra
    # Additive-expression-zegond -> Term-zegond D
    def additive_expression_zegond(self, parent):
        pass

    # TODO: Fereshteh
    # D -> Addop Term D | EPSILON
    def d(self, parent):
        pass

    # TODO: Zahra
    # Addop -> + | -
    def addop(self, parent):
        pass

    # TODO: Fereshteh
    # Term -> Signed-factor G
    def term(self, parent):
        pass

    # TODO: Zahra
    # Term-prime -> Signed-factor-prime G
    def term_prime(self, parent):
        pass

    # TODO: Fereshteh
    # Term-zegond -> Signed-factor-zegond G
    def term_zegond(self, parent):
        pass

    # TODO: Zahra
    # G -> * Signed-factor G | EPSILON
    def g(self, parent):
        pass

    # TODO: Fereshteh
    # Signed-factor -> + Factor | - Factor | Factor
    def signed_factor(self, parent):
        pass

    # TODO: Zahra
    # Signed-factor-prime -> Factor-prime
    def signed_factor_prime(self, parent):
        pass

    # TODO: Fereshteh
    # Signed-factor-zegond -> + Factor | - Factor | Factor-zegond
    def signed_factor_zegond(self, parent):
        pass

    # TODO: Zahra
    # Factor -> ( Expression ) | ID Var-call-prime | NUM
    def factor(self, parent):
        pass

    # TODO: Fereshteh
    # Var-call-prime -> ( Args ) | Var-prime
    def var_call_prime(self, parent):
        pass

    # TODO: Zahra
    # Var-prime -> [ Expression ] | EPSILON
    def var_call(self, parent):
        pass

    # TODO: Fereshteh
    # Factor-prime -> ( Args ) | EPSILON
    def factor_prime(self, parent):
        pass

    # TODO: Zahra
    # Factor-zegond -> ( Expression ) | NUM
    def factor_zegond(self, parent):
        pass

    # TODO: Fereshteh
    # Args -> Arg-list | EPSILON
    def args(self, parent):
        pass

    # TODO: Zahra
    # Arg-list -> Expression Arg-list-prime
    def arg_list(self, parent):
        pass

    # TODO: Fereshteh
    # Arg-list-prime -> , Expression Arg-list-prime | EPSILON
    def arg_list_prime(self, parent):
        pass


scanner = Scanner("Parser_Tests/T1/input.txt")
parser = Parser(scanner)
p_tree = parser.parse()
for pre, _, n in anytree.RenderTree(p_tree):
    print("%s%s" % (pre, n.name))
