from glob import glob
from compiler import run
from os import mkdir, chdir, path
import subprocess

for file in glob('D:/University/Compiler Design/Project/CodeGeneration_Tests/*/input.txt'):
    # for file in glob('/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/Scanner_Tests/*/input.txt'):
    file = file.replace('\\', '/')
    folder = file.split('/')[-2]
    input_path = 'D:/University/Compiler Design/Project/CodeGeneration_Tests/' + folder
    # input_path = '/Users/fereshtah/Desktop/term 8/compiler/Project/Compiler-Project/Scanner_Tests/' + folder
    chdir(input_path)
    if not path.exists(input_path + '/output'):
        mkdir('output')
    run(input_path)
    chdir(input_path + '/output')
    result = subprocess.Popen(['tester_Windows'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = result.communicate()
    out = stdout.decode('utf-8')
    print('Test ' + folder + ':')
    while out.find('\nPRINT') > 0:
        line = out[out.find('\nPRINT'):]
        line = line[1:line.find('\r')]
        out = out[out.find('\nPRINT') + 1:]
        print(line)
    print()
