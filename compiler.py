from scanner import Scanner


def run(path):
    scanner = Scanner(path + '/input.txt')
    while True:
        token_type = scanner.get_next_token()
        if token_type[0] == 'EOF':
            break

    with open(path + '/output/tokens.txt', 'w') as file:
        for i in scanner.tokens.keys():
            if len(scanner.tokens[i]) > 0:
                file.write((str(i) + '.').ljust(8))
                for token in scanner.tokens[i]:
                    file.write(token + ' ')
                file.write('\n')

    with open(path + '/output/lexical_errors.txt', 'w') as file:
        no_errors = True
        for i in scanner.errors.keys():
            if len(scanner.errors[i]) > 0:
                no_errors = False
                write_str = (str(i) + '.').ljust(8)
                for error in scanner.errors[i]:
                    write_str += error + ' '
                write_str += '\n'
                file.write(write_str)
        if no_errors:
            file.write('There is no lexical error.')

    with open(path + '/output/symbol_table.txt', 'w') as file:
        i = 1
        for keyword in scanner.keywords:
            file.write((str(i) + '.').ljust(8) + keyword + '\n')
            i += 1
        for id in scanner.symbol_table:
            file.write((str(i) + '.').ljust(8) + id + '\n')
            i += 1

