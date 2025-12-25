class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = set()

    def analyze(self, node):
        if node.label == "Program":
            for child in node.children:
                self.analyze(child)

        elif node.label.startswith("Function"):
            self.symbol_table = set()
            for stmt in node.children:
                self.analyze(stmt)

        elif node.label == "VarDecl":
            var_type = node.children[0].label
            for child in node.children[1:]:
                if child.label == "Init":
                    var_name = child.children[0].label
                else:
                    var_name = child.label
                if var_name in self.symbol_table:
                    raise Exception(f"Semantic Error: Variable '{var_name}' already declared.")
                self.symbol_table.add(var_name)

        elif node.label == "Assign":
            var_name = node.children[0].label
            if var_name not in self.symbol_table:
                raise Exception(f"Semantic Error: Variable '{var_name}' not declared before assignment.")
            self.analyze(node.children[1]) 

        elif node.label == "Return":
            self.analyze(node.children[0])

        elif node.label == "If":
            for child in node.children:
                self.analyze(child)

        elif node.label == "While":
            for child in node.children:
                self.analyze(child)

        elif node.label == "Then" or node.label == "Else" or node.label == "Body" or node.label == "Condition":
            for stmt in node.children:
                self.analyze(stmt)

        elif node.label.startswith("Op("):
            self.analyze(node.children[0])
            self.analyze(node.children[1])

        elif node.label.startswith("Var("):
            var_name = node.label[4:-1]
            if var_name not in self.symbol_table:
                raise Exception(f"Semantic Error: Variable '{var_name}' used before declaration.")

        elif node.label.startswith("Number("):
            pass  # constants are okay

        else:
        
            for child in node.children:
                self.analyze(child)
