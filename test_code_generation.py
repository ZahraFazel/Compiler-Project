from glob import glob
from compiler import run
from os import mkdir, chdir, path
import subprocess

for file in glob('D:/University/Compiler Design/Project/CodeGeneration_Tests/*/input.txt'):
    # for file in glob('/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/CodeGeneration_Tests/*/input.txt'):
    file = file.replace('\\', '/')
    folder = file.split('/')[-2]
    if folder[0] == 'T' and int(folder[1:]) <= 25:
        input_path = 'D:/University/Compiler Design/Project/CodeGeneration_Tests/' + folder
        # input_path = '/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/CodeGeneration_Tests/' + folder
        chdir(input_path)
        if not path.exists(input_path + '/output'):
            mkdir('output')
        run(input_path)
        chdir(input_path + '/output')
        result = subprocess.Popen(['tester_Windows'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = result.communicate()
        out = stdout.decode('utf-8')
        result = ''
        while out.find('\nPRINT') > 0:
            line = out[out.find('\nPRINT'):]
            line = line[1:line.find('\r')]
            out = out[out.find('\nPRINT') + 1:]
            result += line + '\n'
        result = result.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '').lower()
        with open(input_path + '/expected.txt', 'r') as f:
            expected_result = f.read().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '').lower()
        if expected_result == result:
            print('Test ' + folder + ': PASS\n')
        else:
            print('Test ' + folder + ': FAIL\n')
            print(result)
