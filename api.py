from flask import Flask, request, jsonify
from flask_cors import CORS
from lexer import Lexer
from parser import Parser, print_ast_tree
from semantic_analyzer import SemanticAnalyzer
from intermediate import TACGenerator
from optimizer import Optimizer
from codegen import CodeGenerator 
from simulator import simulate_return

import io
import sys
import traceback

app = Flask(__name__)
CORS(app)  

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    code = data.get('code', '')
    try:
        output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output

        print("PHASE 1: Lexical Analysis")
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print("TOKENS:")
        for token in tokens:
            print(f"{token.type}: {token.value}")

        print("PHASE 2: Syntax Analysis / AST Construction")
        parser = Parser(tokens)
        ast = parser.parse()
        print_ast_tree(ast)

        print("PHASE 3: Semantic Analysis")
        analyzer = SemanticAnalyzer()
        try:
            analyzer.analyze(ast)
            print("Semantic Analysis: PASSED ")
        except Exception as e:
            print("Semantic Analysis: FAILED ")
            print("Error:", str(e))
            sys.stdout = old_stdout
            return jsonify({'output': output.getvalue()}), 400

        print("PHASE 4: Intermediate Code Generation")
        tacgen = TACGenerator()
        tac_code = tacgen.generate(ast)
        for line in tac_code:
            print(line)

        print("PHASE 5: Optimization")
        optimizer = Optimizer(tac_code)
        optimized_code = optimizer.optimize()
        for line in optimized_code:
            print(line)

        print("PHASE 6: Code Generation (Assembly)")
        codegen = CodeGenerator(optimized_code)
        asm_code = codegen.generate()
        for line in asm_code:
            print(line)

        print("PHASE 7: Simulation")
        simulate_return(tac_code)

        sys.stdout = old_stdout
        result = output.getvalue()
        return jsonify({'output': result})

    except Exception as e:
        sys.stdout = old_stdout
        print("Backend error:", e)
        traceback.print_exc()
        return jsonify({'output': '', 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
