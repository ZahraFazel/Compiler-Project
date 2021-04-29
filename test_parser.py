from glob import glob
from compiler import run
from os import mkdir, chdir, path


for file in glob('D:/University/Compiler Design/Project/Parser_Tests/*/input.txt'):
    # for file in glob('/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/Scanner_Tests/*/input.txt'):
    file = file.replace('\\', '/')
    folder = file.split('/')[-2]
    input_path = 'D:/University/Compiler Design/Project/Parser_Tests/' + folder
    # input_path = '/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/Scanner_Tests/' + folder
    chdir(input_path)
    if not path.exists(input_path + '/output'):
        mkdir('output')
    run(input_path)
    print('Test ' + folder + ':')

    with open(input_path + '/parse_tree.txt', 'r') as f:
        test_tokens = f.read().replace(' ', '').replace('\t', '').replace('\n', '').lower()
    with open(input_path + '/output/parse_tree.txt', 'r') as f:
        our_tokens = f.read().replace(' ', '').replace('\t', '').replace('\n', '').lower()
    if test_tokens == our_tokens:
        print('Test Parse Tree: PASS')
    else:
        print('Test Parse Tree: FAIL')

    with open(input_path + '/syntax_errors.txt', 'r') as f:
        test_symbol_table = f.read().replace(' ', '').replace('\t', '').replace('\n', '').lower()
    with open(input_path + '/output/syntax_errors.txt', 'r') as f:
        our_symbol_table = f.read().replace(' ', '').replace('\t', '').replace('\n', '').lower()
    if test_symbol_table == our_symbol_table:
        print('Test Syntax Errors: PASS')
    else:
        print('Test Syntax Errors: FAIL')

    print()
