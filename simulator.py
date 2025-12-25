def resolve(variables, val):

    if isinstance(val, int):
        return val
    if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
        return int(val)
    if val in variables:
        if variables[val] == val:
            return 0
        return resolve(variables, variables[val])
    return 0

def simulate_return(tac_code):
    print("\n" + "=" * 31)
    print("FINAL OUTPUT (Simulated Return)")
    print("=" * 31)

    variables = {}
    labels = {}
    lines = []

    for idx, line in enumerate(tac_code):
        line = line.strip()
        if line.endswith(":"):
            labels[line[:-1]] = len(lines)
        else:
            lines.append(line)

    pc = 0
    while pc < len(lines):
        line = lines[pc]
        if line.startswith("IF NOT"):
  
            parts = line.split()
            cond = parts[2]
            label = parts[4]
            cond_val = resolve(variables, cond)
            if not cond_val:
                pc = labels[label]
                continue
        elif line.startswith("GOTO"):
            label = line.split()[1]
            pc = labels[label]
            continue
        elif line.startswith("RETURN"):
            ret_var = line.split()[1]
            value = resolve(variables, ret_var)
            print(f"Return Value: {value}")
            return
        elif "=" in line:
            left, right = map(str.strip, line.split("=", 1))
            tokens = right.split()
            if len(tokens) == 3:
                a, op, b = tokens
                a_val = resolve(variables, a)
                b_val = resolve(variables, b)
                try:
                    if op == '+':
                        variables[left] = a_val + b_val
                    elif op == '-':
                        variables[left] = a_val - b_val
                    elif op == '*':
                        variables[left] = a_val * b_val
                    elif op == '/':
                        variables[left] = a_val // b_val if b_val != 0 else 0
                    elif op == '%':
                        variables[left] = a_val % b_val if b_val != 0 else 0
                    elif op == '&&':
                        variables[left] = int(bool(a_val) and bool(b_val))
                    elif op == '||':
                        variables[left] = int(bool(a_val) or bool(b_val))
                    elif op == '==':
                        variables[left] = int(a_val == b_val)
                    elif op == '!=':
                        variables[left] = int(a_val != b_val)
                    elif op == '<':
                        variables[left] = int(a_val < b_val)
                    elif op == '>':
                        variables[left] = int(a_val > b_val)
                    elif op == '<=':
                        variables[left] = int(a_val <= b_val)
                    elif op == '>=':
                        variables[left] = int(a_val >= b_val)
                    else:
                        variables[left] = 0
                except Exception as e:
                    variables[left] = 0
            elif len(tokens) == 2 and tokens[0] == '!':
                # Unary not
                val = resolve(variables, tokens[1])
                variables[left] = int(not bool(val))
            elif len(tokens) == 1:
                val = tokens[0]
                variables[left] = resolve(variables, val)
        pc += 1
