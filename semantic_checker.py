class SemanticChecker:
    def __init__(self):
        self.errors = ''

    def error(self, error_type, line_number, *args):
        if error_type == 'scoping':
            self.errors += '#{} : Semantic Error! \'{}\' is not defined.\n'.format(line_number, args[0])
        elif error_type == 'void_type':
            self.errors += '#{} : Semantic Error! Illegal type of void for \'{}\'.\n'.format(line_number, args[0])
        elif error_type == 'actual_and_formal_parameters_number_matching':
            self.errors += '#{} : Semantic Error! Mismatch in numbers of arguments of \'{}\'.\n'.format(line_number,
                                                                                                        args[0])
        elif error_type == 'break_statement':
            self.errors += '#{} : Semantic Error! No \'while\' or \'for\' found for \'break\'.\n'.format(line_number)
        elif error_type == 'type_mismatch':
            self.errors += '#{} : Semantic Error! Type mismatch in operands, Got {} instead of {}.\n'.format(line_number,
                                                                                                             args[0],
                                                                                                             args[1])
        elif error_type == 'actual_and_formal_parameters_type_matching':
            self.errors += '#{} : Semantic Error! Mismatch in type of argument {} for \'{}\'. Expected \'{}\' but got ' \
                           '\'{}\' instead.\n'.format(line_number, args[0], args[1], args[2], args[3])
