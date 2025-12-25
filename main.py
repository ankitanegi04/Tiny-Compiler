from lexer import Lexer
from parser import Parser, print_ast_tree
from semantic_analyzer import SemanticAnalyzer
from intermediate import TACGenerator
from optimizer import Optimizer
from codegen import CodeGenerator
from simulator import simulate_return  

def print_section(title):
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))

try:
    with open("test.c", "r") as f:
        source_code = f.read()
except FileNotFoundError:
    print(" test.c file not found.")
    exit()


print_section("PHASE 1: Lexical Analysis")
lexer = Lexer(source_code)
tokens = lexer.tokenize()
for token in tokens:
    print(f"{token.type}: {token.value}")

print_section("PHASE 2: Syntax Analysis / AST Construction")
parser = Parser(tokens)
ast = parser.parse()
print_ast_tree(ast)


print_section("PHASE 3: Semantic Analysis")
analyzer = SemanticAnalyzer()
try:
    analyzer.analyze(ast)
    print("Semantic Analysis: PASSED ")
except Exception as e:
    print("Semantic Analysis: FAILED ")
    print("Error:", str(e))
    exit()

print_section("PHASE 4: Intermediate Code Generation (Three Address Code)")
tacgen = TACGenerator()
tac_code = tacgen.generate(ast)
for line in tac_code:
    print(line)

print_section("PHASE 5: Optimization")
optimizer = Optimizer(tac_code)
optimized_code = optimizer.optimize()
for line in optimized_code:
    print(line)

print_section("PHASE 6: Target Code Generation")
codegen = CodeGenerator(optimized_code)
assembly = codegen.generate()
for line in assembly:
    print(line)

simulate_return(tac_code) 
