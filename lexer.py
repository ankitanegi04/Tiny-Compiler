import re

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []

    def tokenize(self):
        token_specification = [
            ('NUMBER',   r'\d+(\.\d+)?'),
            ('ID',       r'[A-Za-z_]\w*'),
            ('STRING',   r'"([^"\\]|\\.)*"'),
            ('OP',       r'\+\+|--|==|!=|>=|<=|&&|\|\||[+\-*/%!=<>]'),
            ('SEMI',     r';'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('LBRACE',   r'\{'),
            ('RBRACE',   r'\}'),
            ('COMMA',    r','),
            ('WHITESPACE', r'[ \t]+'),
            ('NEWLINE',  r'\n'),
            ('MISMATCH', r'.')
        ]

        token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        keywords = {
            'int', 'float', 'char', 'double', 'long', 'short', 'unsigned', 'signed', 'void',
            'return', 'if', 'else', 'while', 'for', 'break', 'continue', 'do', 'switch', 'case', 'default',
            'struct', 'union', 'enum', 'typedef', 'const', 'volatile', 'static', 'extern', 'auto', 'register',
            'sizeof', 'goto'
        }

        for match in re.finditer(token_regex, self.source):
            kind = match.lastgroup
            value = match.group()

            if kind == 'WHITESPACE' or kind == 'NEWLINE':
                continue
            elif kind == 'ID' and value in keywords:
                self.tokens.append(Token("KEYWORD", value))
            elif kind == 'ID':
                self.tokens.append(Token("ID", value))
            elif kind == 'NUMBER':
                self.tokens.append(Token("NUMBER", value))
            elif kind == 'STRING':
                self.tokens.append(Token("STRING", value))
            elif kind == 'OP':
                self.tokens.append(Token("OP", value))
            elif kind in {'SEMI', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA'}:
                self.tokens.append(Token(kind, value))
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character: {value}")

        return self.tokens

