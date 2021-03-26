from glob import glob
from compiler import run
from os import mkdir, chdir


# for file in glob('D:/University/Compiler Design/Project/Tests/*/input.txt'):
for file in glob('/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/Tests/*/input.txt'):
    file = file.replace('\\', '/')
    folder = file.split('/')[-2]
    # path = 'D:/University/Compiler Design/Project/Tests/' + folder
    path = '/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/Tests/' + folder
    chdir(path)
    mkdir('output')
    run(path)
    print('Test ' + folder + ':')

    with open(path + '/tokens.txt', 'r') as f:
        test_tokens = f.read().replace(' ', '').replace('\t', '').replace('\n', '')
    with open(path + '/output/tokens.txt', 'r') as f:
        our_tokens = f.read().replace(' ', '').replace('\t', '').replace('\n', '')
    if test_tokens == our_tokens:
        print('Test tokens: PASS')
    else:
        print('Test tokens: FAIL')

    with open(path + '/symbol_table.txt', 'r') as f:
        test_symbol_table = f.read().replace(' ', '').replace('\t', '').replace('\n', '')
    with open(path + '/output/symbol_table.txt', 'r') as f:
        our_symbol_table = f.read().replace(' ', '').replace('\t', '').replace('\n', '')
    if test_symbol_table == our_symbol_table:
        print('Test symbol_table: PASS')
    else:
        print('Test symbol_table: FAIL')

    with open(path + '/lexical_errors.txt', 'r') as f:
        test_lexical_errors = f.read().replace(' ', '').replace('\t', '').replace('\n', '')
    with open(path + '/output/lexical_errors.txt', 'r') as f:
        our_lexical_errors = f.read().replace(' ', '').replace('\t', '').replace('\n', '')
    if test_lexical_errors == our_lexical_errors:
        print('Test lexical_errors: PASS')
    else:
        print('Test lexical_errors: FAIL')

    print()
