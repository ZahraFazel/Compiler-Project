"""
Zahra Fazel 96102053
Fereshteh Forghani 96102104
"""
# import anytree

from prd_parser import Parser
from scanner import Scanner


def run(path=''):
    input_path = path + '/input.txt' if path != '' else 'input.txt'
    output_path = path + '/output/' if path != '' else ''
    # output_path = path
    scanner = Scanner(input_path)
    parser = Parser(scanner)
    parser.parse()

    with open(output_path + 'output.txt', 'w') as file:
        for idx, l in enumerate(parser.code_generator.pb):
            if l is not None:
                file.write('{}\t{}\n'.format(idx, l))
    # with open(output_path + 'parse_tree.txt', 'w') as file:
    #     if parser.parse_tree is not None:
    #         for pre, _, n in anytree.RenderTree(parser.parse_tree):
    #             file.write("%s%s\n" % (pre, n.name))
    #
    # with open(output_path + 'syntax_errors.txt', 'w') as file:
    #     if parser.errors == '':
    #         file.write('There is no syntax error.')
    #     else:
    #         file.write(parser.errors)
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
