import anytree
from scanner import Scanner


class Parser:

    def __init__(self, scanner):
        self.lookahead_type = None
        self.lookahead_token = None
        self.scanner = scanner
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

    def params(self, parent):
        pass

    def compound_stmt(self, parent):
        pass


scanner = Scanner("Parser_Tests/T1/input.txt")
parser = Parser(scanner)
p_tree = parser.parse()
for pre, _, node in anytree.RenderTree(p_tree):
    print("%s%s" % (pre, node.name))
