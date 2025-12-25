class TACGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        self.break_stack = []
        self.continue_stack = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, node):
        if node.label == "Program":
            for fn in node.children:
                self.generate(fn)
            return self.code

        elif node.label.startswith("Function"):
            self.code.append(f"\n# Function {node.label}")
            for stmt in node.children:
                self.generate(stmt)

        elif node.label == "VarDecl":
         
            for child in node.children[1:]:
                if child.label == "Init":
                    var_name = child.children[0].label
                    expr_temp = self.generate(child.children[1])
                    self.code.append(f"{var_name} = {expr_temp}")
            return  

        elif node.label == "Assign":
            var_name = node.children[0].label
            expr_temp = self.generate(node.children[1])
            self.code.append(f"{var_name} = {expr_temp}")

        elif node.label == "Return":
            expr_temp = self.generate(node.children[0])
            self.code.append(f"RETURN {expr_temp}")

        elif node.label == "If":
            cond = self.generate(node.children[0].children[0]) 
            else_label = self.new_label()
            end_label = self.new_label()

            self.code.append(f"IF NOT {cond} GOTO {else_label}")
            for stmt in node.children[1].children:  
                self.generate(stmt)
            self.code.append(f"GOTO {end_label}")
            self.code.append(f"{else_label}:")
            if len(node.children) == 3: 
                for stmt in node.children[2].children:
                    self.generate(stmt)
            self.code.append(f"{end_label}:")

        elif node.label == "While":
            start_label = self.new_label()
            end_label = self.new_label()
            self.continue_stack.append(start_label)
            self.break_stack.append(end_label)
            self.code.append(f"{start_label}:")
            cond = self.generate(node.children[0].children[0]) 
            self.code.append(f"IF NOT {cond} GOTO {end_label}")
            for stmt in node.children[1].children:  
                self.generate(stmt)
            self.code.append(f"GOTO {start_label}")
            self.code.append(f"{end_label}:")
            self.continue_stack.pop()
            self.break_stack.pop()

        elif node.label == "For":
            init = node.children[0]
            cond = node.children[1].children[0]
            update = node.children[2]
            body = node.children[3].children
            start_label = self.new_label()
            end_label = self.new_label()
            update_label = self.new_label()
            self.generate(init)
            self.code.append(f"{start_label}:")
            cond_temp = self.generate(cond)
            self.code.append(f"IF NOT {cond_temp} GOTO {end_label}")
            self.continue_stack.append(update_label)
            self.break_stack.append(end_label)
            for stmt in body:
                self.generate(stmt)
            self.code.append(f"{update_label}:")
            self.generate(update)
            self.code.append(f"GOTO {start_label}")
            self.code.append(f"{end_label}:")
            self.continue_stack.pop()
            self.break_stack.pop()

        elif node.label == "Break":
            if self.break_stack:
                self.code.append(f"GOTO {self.break_stack[-1]}")

        elif node.label == "Continue":
            if self.continue_stack:
                self.code.append(f"GOTO {self.continue_stack[-1]}")

        elif node.label.startswith("Op("):
            op = node.label[3:-1]
            if op == "!": 
                expr = self.generate(node.children[0])
                temp = self.new_temp()
                self.code.append(f"{temp} = ! {expr}")
                return temp
            elif len(node.children) == 2:
                left = self.generate(node.children[0])
                right = self.generate(node.children[1])
                temp = self.new_temp()
                self.code.append(f"{temp} = {left} {op} {right}")
                return temp
            else:
                return self.generate(node.children[0])

        elif node.label.startswith("Number("):
            return node.label[7:-1]

        elif node.label.startswith("Var("):
            return node.label[4:-1]

        else:
            for child in node.children:
                self.generate(child)
