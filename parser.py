class Parser:

    def __init__(self, scanner):
        self.lookahead_type = None
        self.lookahead_token = None
        self.scanner = scanner
        self.errors = ''

    def parse(self):
        program = self.program()
        return program

    def match(self, expected_token):
        if self.lookahead_token == expected_token:
            self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        else:
            print("Error")
            # TODO -> Error handling
        return

    # program -> declaration declaration-list
    def program(self):
        if self.lookahead_token in {'int', 'void'}:
            return self.declaration_list([self.declaration()])

    # declaration-list -> declaration declaration-list | ϵ
    def declaration_list(self, declarations):
        if self.lookahead_token in {'int', 'void'}:
            return self.declaration_list(declarations + [self.declaration()])

    # declaration -> type-specifier ID var-declaration ; | type-specifier ID ( params ) compound-stmt
    def declaration(self):
        kind = self.lookahead_token
        self.lookahead_type, self.lookahead_token = self.scanner.get_next_token()
        name = self.lookahead_token
        if self.lookahead_token in {'[', ';'}:
            array = self.var_declaration()
            self.match(';')
            # return VarDeclaration(kind, name, array)
        else:
            self.match('(')
            params = self.params()
            self.match(')')
            body = self.compound_stmt()
            # return FunDeclaration(kind, name, params, body)

    # params -> int ID param_prime param-list | void ID param_prime param-list | void
    def params(self):
        # if self.lookahead_token in ['int', 'float']:
        #     return self.param_list([self.param()])
        # else:
        #     self.accept_val('void')
        #     if self.next().type == 'ID':
        #         # param = ParamFormal(Type.VOID, self.id(), self.param_())
        #         # return self.param_list([param])
             return []

    def var_declaration(self):
        return 1

    def compound_stmt(self):
        return 1







# from enum import Enum
#
#
# class Type(Enum):
#     INTEGER = 1
#     VOID = 2
#
#     @staticmethod
#     def from_string(kind):
#         return {
#             'int': Type.INTEGER,
#             'void': Type.VOID,
#         }[kind]
#
#     def to_string(self):
#         return {
#             'INTEGER': 'int',
#             'VOID': 'void',
#         }[self.name]
