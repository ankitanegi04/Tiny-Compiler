import re

class Optimizer:
    def __init__(self, code_lines):
        self.code = code_lines
        self.optimized_code = []

    def constant_folding(self, line):
        match = re.match(r'(t\d+) = (\d+) ([+\-*/]) (\d+)', line)
        if match:
            target, lhs, op, rhs = match.groups()
            lhs, rhs = int(lhs), int(rhs)
            result = eval(f"{lhs} {op} {rhs}")
            return f"{target} = {result}  # constant folded"
        return line

    def dead_code_elimination(self):
        used_vars = set()
        for line in self.code:
            tokens = re.findall(r'\b\w+\b', line)
            if '=' in line:
                target = tokens[0]
                expr = tokens[2:]
                used_vars.update([tok for tok in expr if tok.startswith('t') or tok.isalpha()])
            elif 'RETURN' in line or 'IF' in line or 'GOTO' in line:
                used_vars.update([tok for tok in tokens[1:] if tok.startswith('t') or tok.isalpha()])

        new_code = []
        for line in self.code:
            if re.match(r'(t\d+) = .*', line):
                target = line.split('=')[0].strip()
                if target in used_vars:
                    new_code.append(line)
            else:
                new_code.append(line)
        self.code = new_code

    def optimize(self):

        self.code = [self.constant_folding(line) for line in self.code]


        self.dead_code_elimination()

        return self.code

if __name__ == "__main__":

    from intermediate import IntermediateCodeGenerator
    from parser import Parser
    from lexer import Lexer

    with open("test.c") as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()


    icg = IntermediateCodeGenerator()
    icg.generate(ast)
    tac = icg.get_code()

    print("Original TAC:")
    for line in tac:
        print(line)

    print("\nOptimized TAC:")
    optimizer = Optimizer(tac)
    optimized = optimizer.optimize()
    for line in optimized:
        print(line)
