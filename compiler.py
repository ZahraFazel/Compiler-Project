"""
Zahra Fazel 96102053
Fereshteh Forghani 96102104
"""
import anytree

from prd_parser import Parser
from scanner import Scanner


def run(path=''):
    scanner = Scanner("Parser_Tests/T6/input.txt")
    parser = Parser(scanner)
    p_tree = parser.parse()
    for pre, _, n in anytree.RenderTree(p_tree):
        print("%s%s" % (pre, n.name))
    if parser.errors == '':
        print('There is no syntax error.')
    print(parser.errors)
    # input_path = path + '/input.txt' if path != '' else 'input.txt'
    # # output_path = path + '/output/'
    # output_path = ''
    # scanner = Scanner(input_path)
    # while True:
    #     token_type = scanner.get_next_token()
    #     if token_type[0] == 'EOF':
    #         break
    #
    # with open(output_path + 'tokens.txt', 'w') as file:
    #     for i in scanner.tokens.keys():
    #         if len(scanner.tokens[i]) > 0:
    #             file.write((str(i) + '.').ljust(8))
    #             for token in scanner.tokens[i]:
    #                 file.write(token + ' ')
    #             file.write('\n')
    #
    # with open(output_path + 'lexical_errors.txt', 'w') as file:
    #     no_errors = True
    #     for i in scanner.errors.keys():
    #         if len(scanner.errors[i]) > 0:
    #             no_errors = False
    #             write_str = (str(i) + '.').ljust(8)
    #             for error in scanner.errors[i]:
    #                 write_str += error + ' '
    #             write_str += '\n'
    #             file.write(write_str)
    #     if no_errors:
    #         file.write('There is no lexical error.')
    #
    # with open(output_path + 'symbol_table.txt', 'w') as file:
    #     i = 1
    #     for keyword in scanner.keywords:
    #         file.write((str(i) + '.').ljust(8) + keyword + '\n')
    #         i += 1
    #     for id in scanner.symbol_table:
    #         file.write((str(i) + '.').ljust(8) + id + '\n')
    #         i += 1


run()
