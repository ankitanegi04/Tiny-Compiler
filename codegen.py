import re

class CodeGenerator:
    def __init__(self, tac_lines):
        self.tac = tac_lines
        self.asm = []

    def generate(self):
        for line in self.tac:
            line = line.strip()

            if line.startswith("#"):
                self.asm.append(f"; {line[1:].strip()}")
                continue


            if line.endswith(":"):
                self.asm.append(f"{line}")
                continue

 
            match = re.match(r"IF NOT (\w+) GOTO (L\d+)", line)
            if match:
                cond, label = match.groups()
                self.asm.append(f"CMP {cond}, 0")
                self.asm.append(f"JE {label}")
                continue

            match = re.match(r"GOTO (L\d+)", line)
            if match:
                self.asm.append(f"JMP {match.group(1)}")
                continue

 
            match = re.match(r"RETURN (\w+)", line)
            if match:
                self.asm.append(f"MOV R0, {match.group(1)}")
                self.asm.append("RET")
                continue

    
            match = re.match(r"(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(\w+)", line)
            if match:
                dest, src1, op, src2 = match.groups()
                self.asm.append(f"MOV R1, {src1}")
                asm_op = {"+" : "ADD", "-" : "SUB", "*" : "MUL", "/" : "DIV"}[op]
                self.asm.append(f"{asm_op} R1, {src2}")
                self.asm.append(f"MOV {dest}, R1")
                continue

            # x = y
            match = re.match(r"(\w+)\s*=\s*(\w+)", line)
            if match:
                dest, src = match.groups()
                self.asm.append(f"MOV {dest}, {src}")
                continue

            self.asm.append(f"; Unrecognized TAC: {line}")

        return self.asm
