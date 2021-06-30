"""
Zahra Fazel 96102053
Fereshteh Forghani 96102104
"""
# import anytree

from prd_parser import Parser
from scanner import Scanner
from os import mkdir, chdir, path
import subprocess


def run(path=''):
    input_path = path + '/input.txt' if path != '' else 'input.txt'
    output_path = path + '/output/' if path != '' else 'CodeGeneration_Tests/Tester/'
    # output_path = path
    scanner = Scanner(input_path)
    parser = Parser(scanner)
    parser.parse()

    with open(output_path + 'output.txt', 'w') as file:
        for idx, l in enumerate(parser.code_generator.pb):
            if l is not None:
                file.write('{}\t{}\n'.format(idx, l))


# run()
# chdir('D:/University/Compiler Design/Project/CodeGeneration_Tests/Tester')
# # chdir('/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/CodeGeneration_Tests/Tester')
# result = subprocess.Popen(['tester_Windows'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# stdout, stderr = result.communicate()
# out = stdout.decode('utf-8')
# result = ''
# while out.find('\nPRINT') > 0:
#     line = out[out.find('\nPRINT'):]
#     line = line[1:line.find('\r')]
#     out = out[out.find('\nPRINT') + 1:]
#     result += line + '\n'
# print(result)
# print(out)
