with open("input.asm", "w") as f:
    f.write("""INCR MACRO X
MOV R 1
ADD X R
MEND

.CODE
MOV AX, 5
INCR AX
CLC
END
""")
print("input.asm created successfully!")





#code





# --- Macro Processor (Pass 1 and Pass 2) ---

import os

# Data Structures
class Macro:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.definition = []

# Global tables
MNT = {}   # Macro Name Table
MDT = []   # Macro Definition Table

# ---------------------------
# PASS 1: Macro Definition
# ---------------------------
def pass1(input_file):
    with open(input_file, "r") as f:
        lines = f.readlines()

    inside_macro = False
    current_macro = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        tokens = line.split()

        if "MACRO" in tokens:
            inside_macro = True
            continue

        elif "MEND" in tokens:
            inside_macro = False
            if current_macro:
                MNT[current_macro.name] = current_macro
                MDT.extend(current_macro.definition)
                current_macro = None
            continue

        if inside_macro:
            if current_macro is None:
                macro_name = tokens[0]
                args = [arg.strip(",") for arg in tokens[1:]]
                current_macro = Macro(macro_name, args)
            else:
                current_macro.definition.append(line)

    print("PASS 1 COMPLETE ✅")
    print("\nMNT (Macro Name Table):")
    for name, m in MNT.items():
        print(f"  {name} -> Args: {m.args}")

# ---------------------------
# PASS 2: Macro Expansion
# ---------------------------
def pass2(input_file, output_file="output.asm"):
    with open(input_file, "r") as f:
        lines = f.readlines()

    inside_macro = False
    output_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        tokens = stripped.split()

        if "MACRO" in tokens:
            inside_macro = True
            continue

        elif "MEND" in tokens:
            inside_macro = False
            continue

        if inside_macro:
            continue  # skip macro definitions during Pass 2

        macro_name = tokens[0]
        if macro_name in MNT:
            macro = MNT[macro_name]
            arg_values = tokens[1:]
            arg_map = dict(zip(macro.args, arg_values))

            for def_line in macro.definition:
                expanded = def_line
                for formal, actual in arg_map.items():
                    expanded = expanded.replace(formal, actual)
                output_lines.append(expanded)
        else:
            output_lines.append(stripped)

    with open(output_file, "w") as f:
        f.write("\n".join(output_lines))

    print("PASS 2 COMPLETE ✅")
    print(f"Output written to {output_file}")

# ---------------------------
# MAIN EXECUTION
# ---------------------------
def main():
    input_file = "input.asm"

    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found.")
        return

    print("Running Pass 1...")
    pass1(input_file)

    print("\nRunning Pass 2...")
    pass2(input_file)

# Run main
main()
