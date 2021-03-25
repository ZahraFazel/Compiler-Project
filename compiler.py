from scanner import Scanner

scanner = Scanner('input_output/input1.txt')
while True:
    token_type = scanner.get_next_token()
    if token_type[0] == 'EOF':
        break

with open('input_output/tokens.txt', 'w') as file:
    for i in scanner.tokens.keys():
        if len(scanner.tokens[i]) > 0:
            file.write((str(i) + '.').ljust(4))
            for token in scanner.tokens[i]:
                file.write(token + ' ')
            file.write('\n')

with open('input_output/lexical_errors.txt', 'w') as file:
    for i in scanner.errors.keys():
        if len(scanner.errors[i]) > 0:
            for error in scanner.errors[i]:
                file.write((str(i) + '.').ljust(4) + error + '\n')

with open('input_output/symbol_table.txt', 'w') as file:
    i = 0
    for keyword in scanner.keywords:
        file.write((str(i) + '.').ljust(4) + keyword + '\n')
        i += 1
    for id in scanner.symbol_table:
        file.write((str(i) + '.').ljust(4) + id + '\n')
        i += 1
