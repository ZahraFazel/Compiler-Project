from scanner import Scanner

scanner = Scanner('input_output/input1.txt')
while True:
    token_type = scanner.get_next_token()
    if token_type[0] == 'EOF':
        break
print(scanner.symbol_table)
print(scanner.tokens)
print(scanner.errors)
