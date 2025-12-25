from lexer import Token
import sys

class ASTNode:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []

    def __repr__(self):
        return self.label


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def expect(self, token_type, value=None):
        token = self.peek()
        if not token:
            raise SyntaxError("Unexpected EOF")
        if token.type != token_type or (value and token.value != value):
            raise SyntaxError(f"Expected {token_type} {value}, got {token.type} {token.value}")
        self.advance()
        return token

    def match(self, token_type, value=None):
        token = self.peek()
        if token and token.type == token_type and (value is None or token.value == value):
            self.advance()
            return token
        return None

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        functions = []
        while self.peek():
            functions.append(self.parse_function())
        return ASTNode("Program", functions)

    def parse_function(self):
        self.expect("KEYWORD")        
        name = self.expect("ID").value
        self.expect("LPAREN")
        self.expect("RPAREN")
        self.expect("LBRACE")

        body = []
        while self.peek() and self.peek().type != "RBRACE":
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        self.expect("RBRACE")
        return ASTNode(f"Function({name})", body)

    def parse_statement(self):
        token = self.peek()
        if token is None:
            return None
        if token.type == "KEYWORD" and token.value in {"int", "float", "char", "double", "long", "short", "unsigned", "signed"}:
            return self.parse_declaration()
        elif token.type == "ID":
            save_pos = self.pos
            try:
                return self.parse_assignment()
            except SyntaxError:
                self.pos = save_pos
                return self.parse_expression_statement()
        elif token.type == "KEYWORD" and token.value == "if":
            return self.parse_if_statement()
        elif token.type == "KEYWORD" and token.value == "while":
            return self.parse_while_statement()
        elif token.type == "KEYWORD" and token.value == "for":
            return self.parse_for_statement()
        elif token.type == "KEYWORD" and token.value == "break":
            self.advance()
            self.expect("SEMI")
            return ASTNode("Break")
        elif token.type == "KEYWORD" and token.value == "continue":
            self.advance()
            self.expect("SEMI")
            return ASTNode("Continue")
        elif token.type == "KEYWORD" and token.value == "return":
            return self.parse_return()
        else:
            self.advance()
            return None

    def parse_declaration(self):
        var_type = self.expect("KEYWORD").value
        names = []
        while True:
            id_token = self.peek()
            if not id_token or id_token.type != "ID":
                raise SyntaxError("Expected identifier in declaration")
            name = self.expect("ID").value
            # Support optional initialization
            next_token = self.peek()
            if next_token is not None and next_token.type == "OP" and next_token.value == "=":
                self.expect("OP", "=")
                expr = self.parse_expression()
                names.append(ASTNode("Init", [ASTNode(name), expr]))
            else:
                names.append(ASTNode(name))
            next_token = self.peek()
            if next_token is not None and next_token.type == "COMMA":
                self.advance()
            else:
                break
        self.expect("SEMI")
        return ASTNode("VarDecl", [ASTNode(var_type)] + names)

    def parse_assignment(self):
        id_token = self.peek()
        if not id_token or id_token.type != "ID":
            raise SyntaxError("Expected identifier in assignment")
        name = self.expect("ID").value
        self.expect("OP", "=")
        expr = self.parse_expression()
        self.expect("SEMI")
        return ASTNode("Assign", [ASTNode(name), expr])

    def parse_assignment_expr(self):
        id_token = self.peek()
        if not id_token or id_token.type != "ID":
            raise SyntaxError("Expected identifier in assignment expression")
        name = self.expect("ID").value
        self.expect("OP", "=")
        expr = self.parse_expression()
        return ASTNode("Assign", [ASTNode(name), expr])

    def parse_return(self):
        self.expect("KEYWORD", "return")
        expr = self.parse_expression()
        self.expect("SEMI")
        return ASTNode("Return", [expr])

    def parse_if_statement(self):
        self.expect("KEYWORD", "if")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        self.expect("LBRACE")
        then_body = []
        while True:
            next_token = self.peek()
            if next_token is not None and next_token.type != "RBRACE":
                then_body.append(self.parse_statement())
            else:
                break
        self.expect("RBRACE")

        else_body = []
        next_token = self.peek()
        if next_token is not None and next_token.type == "KEYWORD" and next_token.value == "else":
            self.expect("KEYWORD", "else")
            self.expect("LBRACE")
            while True:
                next_token = self.peek()
                if next_token is not None and next_token.type != "RBRACE":
                    else_body.append(self.parse_statement())
                else:
                    break
            self.expect("RBRACE")

        children = [ASTNode("Condition", [condition]), ASTNode("Then", then_body)]
        if else_body:
            children.append(ASTNode("Else", else_body))
        return ASTNode("If", children)

    def parse_while_statement(self):
        self.expect("KEYWORD", "while")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        self.expect("LBRACE")
        body = []
        while True:
            next_token = self.peek()
            if next_token is not None and next_token.type != "RBRACE":
                body.append(self.parse_statement())
            else:
                break
        self.expect("RBRACE")
        return ASTNode("While", [ASTNode("Condition", [condition]), ASTNode("Body", body)])

    def parse_for_statement(self):
        self.expect("KEYWORD", "for")
        self.expect("LPAREN")
        init = self.parse_assignment_expr()
        self.expect("SEMI")
        cond = self.parse_expression()
        self.expect("SEMI")
        update = self.parse_assignment_expr()
        self.expect("RPAREN")
        self.expect("LBRACE")
        body = []
        while True:
            next_token = self.peek()
            if next_token is not None and next_token.type != "RBRACE":
                body.append(self.parse_statement())
            else:
                break
        self.expect("RBRACE")
        return ASTNode("For", [init, ASTNode("Condition", [cond]), update, ASTNode("Body", body)])

    def parse_expression_statement(self):
        expr = self.parse_expression()
        self.expect("SEMI")
        return ASTNode("ExprStmt", [expr])

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while True:
            token = self.peek()
            if token is not None and token.type == "OP" and token.value == "||":
                op = self.expect("OP").value
                right = self.parse_and()
                left = ASTNode(f"Op({op})", [left, right])
            else:
                break
        return left

    def parse_and(self):
        left = self.parse_equality()
        while True:
            token = self.peek()
            if token is not None and token.type == "OP" and token.value == "&&":
                op = self.expect("OP").value
                right = self.parse_equality()
                left = ASTNode(f"Op({op})", [left, right])
            else:
                break
        return left

    def parse_equality(self):
        left = self.parse_relational()
        while True:
            token = self.peek()
            if token is not None and token.type == "OP" and token.value in {"==", "!="}:
                op = self.expect("OP").value
                right = self.parse_relational()
                left = ASTNode(f"Op({op})", [left, right])
            else:
                break
        return left

    def parse_relational(self):
        left = self.parse_additive()
        while True:
            token = self.peek()
            if token is not None and token.type == "OP" and token.value in {"<", ">", "<=", ">="}:
                op = self.expect("OP").value
                right = self.parse_additive()
                left = ASTNode(f"Op({op})", [left, right])
            else:
                break
        return left

    def parse_additive(self):
        left = self.parse_term()
        while True:
            token = self.peek()
            if token is not None and token.type == "OP" and token.value in {"+", "-"}:
                op = self.expect("OP").value
                right = self.parse_term()
                left = ASTNode(f"Op({op})", [left, right])
            else:
                break
        return left

    def parse_term(self):
        left = self.parse_factor()
        while True:
            token = self.peek()
            if token is not None and token.type == "OP" and token.value in {"*", "/", "%"}:
                op = self.expect("OP").value
                right = self.parse_factor()
                left = ASTNode(f"Op({op})", [left, right])
            else:
                break
        return left

    def parse_factor(self):
        token = self.peek()
        if not token:
            raise SyntaxError("Unexpected end of input in expression")
        if token.type == "OP" and token.value == "!":
            self.advance()
            expr = self.parse_factor()
            return ASTNode("Op(!)", [expr])
        elif token.type == "NUMBER":
            self.advance()
            return ASTNode(f"Number({token.value})")
        elif token.type == "ID":
            self.advance()
            return ASTNode(f"Var({token.value})")
        elif token.type == "LPAREN":
            self.expect("LPAREN")
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

def print_ast_tree(node, indent=""):
    print(indent + str(node.label))
    for child in node.children:
        print_ast_tree(child, indent + "  ")


if __name__ == "__main__":
    from lexer import Lexer

    code = """
    int main() {
        int x;
        x = 2 + 3;
        while (x < 5) {
            x = x + 1;
        }
        if (x == 5) {
            x = x + 5;
        } else {
            x = x - 1;
        }
        return x;
    }
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    print("==== AST TREE ====")
    print_ast_tree(ast)
