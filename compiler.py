"""
Zahra Fazel 96102053
Fereshteh Forghani 96102104
"""
from prd_parser import Parser
from scanner import Scanner


def run(path=''):
    input_path = path + '/input.txt' if path != '' else 'input.txt'
    output_path = path + '/output/' if path != '' else ''
    scanner = Scanner(input_path)
    parser = Parser(scanner)
    parser.parse()

    with open(output_path + 'output.txt', 'w') as file:
        if parser.code_generator.semantic_checker.errors == '':
            for idx, l in enumerate(parser.code_generator.pb):
                if l != '':
                    file.write('{}\t{}\n'.format(idx, l))
        else:
            file.write('The output code has not been generated.')

    with open(output_path + 'semantic_errors.txt', 'w') as file:
        if parser.code_generator.semantic_checker.errors == '':
            file.write('The input program is semantically correct.')
        else:
            file.write(parser.code_generator.semantic_checker.errors)


run()
