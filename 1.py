import os
import sys

# --- Initialization of Global Data Structures ---
LC = 0
symindex = 0
symtab = {}  # {'Label': (Address, Index)}
pooltab = [] # [Pool Start Index]

# Mnemonic Table
mnemonics = {'STOP': ('00', 'IS', 1), 'ADD': ('01', 'IS', 1), 'SUB': ('02', 'IS', 1), 
             'MUL': ('03', 'IS', 1), 'MOVER': ('04', 'IS', 1), 'MOVEM': ('05', 'IS', 1),
             'DC': ('03', 'DL', 1), 'DS': ('04', 'DL', 1), 
             'START': ('01', 'AD', 0), 'END': ('02', 'AD', 0), 'ORIGIN': ('03', 'AD', 0), 
             'LTORG': ('05', 'AD', 0)}
REG = {'AREG': 1, 'BREG': 2, 'CREG': 3, 'DREG': 4}

# --- File Names ---
INPUT_FILENAME = "input.txt"
INTER_CODE_FILENAME = "inter_code.txt"
LITERALS_FILENAME = "literals.txt"
TMP_FILENAME = "tmp.txt"
SYMTAB_FILENAME = "SymTab.txt"
POOLTAB_FILENAME = "PoolTab.txt"

# --- Helper Display Functions (omitted for brevity, but contained in the full run) ---
# (Contains print_tables, END, LTORG, detect_mn definitions)

def print_tables(lit, current_line, current_words, LC_val):
    """Prints the current state of LC, tokenized words, and tables for tracing."""
    print(f"LC= {LC_val}")
    print(f"{current_line.strip()}")
    print(current_words)
    
    # Literal Table
    print("literal table:")
    lit.seek(0, 0)
    for x in lit:
        print(x.strip())
    
    # Pool Table
    print("Pool Table:")
    print(pooltab)
    
    # Symbol Table
    print("Symbol Table:")
    print(symtab)
    print("-" * 20)

def END(ifp, lit, tmp, line_content, words):
    global LC, pooltab 
    print(f"LC= {LC}")
    print(f"{line_content.strip()}")
    print(words)
    print("Mnemonic: END")
    pool = 0; z = 0; ifp.write("\t(AD,02)\n"); lit.seek(0, 0)
    lines = lit.readlines()
    for line in lines:
        if "**" in line:
            pool += 1
            if pool == 1: pooltab.append(z) 
            y = line.split(); tmp.write(f"{y[0]}\t{LC}\n"); LC += 1
        else: tmp.write(line)
        z += 1
    lit.truncate(0); tmp.seek(0, 0)
    for x in tmp: lit.write(x)
    tmp.truncate(0)
    print_tables(lit, line_content, words, LC)

def LTORG(ifp, lit, tmp, line_content, words):
    global LC, pooltab 
    print(f"LC= {LC}"); print(f"{line_content.strip()}"); print(words); print("Mnemonic: LTORG")
    ifp.write(f"{LC}\t({mnemonics['LTORG'][1]},{mnemonics['LTORG'][0].zfill(2)})\n")
    pool = 0; z = 0; lit.seek(0, 0); lines = lit.readlines()
    for line in lines:
        if "**" in line:
            pool += 1
            if pool == 1: pooltab.append(z) 
            y = line.split(); tmp.write(f"{y[0]}\t{LC}\n"); LC += 1
        else: tmp.write(line)
        z += 1
    lit.truncate(0); tmp.seek(0, 0); 
    for x in tmp: lit.write(x)
    tmp.truncate(0)
    print_tables(lit, line_content, words, LC)

def detect_mn(words, k, ifp, lit, line_content):
    global LC, symindex, symtab
    mnemonic = words[k]; val = mnemonics[mnemonic]
    print(f"LC= {LC}"); print(f"{line_content.strip()}"); print(words)
    if k == 0: print(f"Mnemonic: {mnemonic}")
    else: print(f"Label: {words[0]} Mnemonic: {mnemonic}")
    ifp.write(f"\t({val[1]},{val[0].zfill(2)})")
    for i in range(k + 1, len(words)):
        operand = words[i].replace(',', '')
        if operand in REG: ifp.write(f" {REG[operand]}")
        elif operand.startswith('='): lit.write(f"{operand} **\n"); ifp.write(f" (L,{symindex})") 
        elif operand.isdigit(): ifp.write(f" {operand}")
        elif operand not in symtab: symtab[operand] = ("**", symindex); ifp.write(f" (S,{symindex})"); symindex += 1
        else: ref_index = symtab[operand][1]; ifp.write(f" (S,{ref_index})")
    if mnemonic == "DS":
        LC += int(words[k+1]) - val[2]; print("yes")
    LC += val[2]
    print_tables(lit, line_content, words, LC)

# --- Main Pass I Execution Function ---

def run_pass_one():
    global LC, symindex, symtab, pooltab
    
    # Define the directory where input.txt is located
    INPUT_DIRECTORY = "/home/atharva-chopade/Downloads"
    FULL_INPUT_PATH = os.path.join(INPUT_DIRECTORY, INPUT_FILENAME)
    
    # 1. Create Input File Content (Ensuring the file exists for testing)
    input_file_content = [
        "START 100", "A DC 10", "MOVER AREG, B", "MOVEM BREG, ='1'", 
        "ADD AREG, ='2'", "SUB BREG, ='1'", "B DC 20", "ORIGIN 300", 
        "LTORG", "MOVER AREG, NUM", "MOVER CREG, LOOP", "ADD BREG, ='1'", 
        "NUM DS 5", "LOOP DC 10", "END"
    ]
    
    try:
        # We create the file at the specified path to prevent the FileNotFoundError
        with open(FULL_INPUT_PATH, 'w') as f:
            for line in input_file_content:
                f.write(line.strip() + '\n')
        print(f"Input file '{INPUT_FILENAME}' created successfully at {FULL_INPUT_PATH}.")
    except IOError as e:
        print(f"Fatal Error: Could not write to input file at '{FULL_INPUT_PATH}'. Check permissions. {e}")
        return

    # 2. Open Files using the specified path for input
    try:
        # *** KEY CHANGE HERE: Using the full, explicit path for the input file ***
        file = open(FULL_INPUT_PATH, "r")
        
        # Output files remain relative to the script execution directory
        ifp = open(INTER_CODE_FILENAME, "w")
        lit = open(LITERALS_FILENAME, "w+")
        tmp = open(TMP_FILENAME, "w+")
    except FileNotFoundError as e:
        # This block should now only catch errors if the output files can't be created.
        print(f"Error opening files: {e}")
        return

    # Reset globals
    LC, symindex = 0, 0
    symtab.clear()
    pooltab.clear()

    print("\n--- Starting Pass I Execution ---")

    for line_content in file:
        line = line_content.strip()
        if not line: continue
        
        words = line.split()
        k = 0
        
        # 1. Handle Label
        if words[0] not in mnemonics.keys() and words[0] not in REG and not words[0].isdigit():
            label = words[0]
            if label not in symtab.keys():
                symtab[label] = (LC, symindex)
                symindex += 1
            else:
                x = symtab[label]
                if x[0] == "**":
                    symtab[label] = (LC, x[1])
            k = 1
            
        # 2. Process Mnemonic/Directive
        mnemonic = words[k]
        
        if mnemonic == "START":
            # START is handled before LC is written to IC, as per your trace
            print(f"LC= {LC}")
            print(f"{line_content.strip()}")
            print(words)
            print("Mnemonic: START")
            ifp.write(f"\t({mnemonics['START'][1]},{mnemonics['START'][0].zfill(2)}) {words[1]}\n")
            LC = int(words[1])
            print_tables(lit, line_content, words, LC)
        elif mnemonic == "END":
            END(ifp, lit, tmp, line_content, words)
            break
        elif mnemonic == "LTORG":
            LTORG(ifp, lit, tmp, line_content, words)
        elif mnemonic == "ORIGIN":
            print(f"LC= {LC}")
            print(f"{line_content.strip()}")
            print(words)
            print("Mnemonic: ORIGIN")
            ifp.write(f"\t({mnemonics['ORIGIN'][1]},{mnemonics['ORIGIN'][0].zfill(2)}) {words[1]}\n")
            LC = int(words[1])
            print_tables(lit, line_content, words, LC)
        else:
            # Write current LC to Intermediate Code file
            ifp.write(f"{LC}")
            detect_mn(words, k, ifp, lit, line_content)
            ifp.write("\n")

    # 3. Final Cleanup and Table Saving
    file.close()
    ifp.close()
    lit.close()
    tmp.close()

    sym = open(SYMTAB_FILENAME, "w")
    for label, (addr, index) in symtab.items():
        sym.write(f"{label}\t{addr}\t{index}\n")
    sym.close()

    pool = open(POOLTAB_FILENAME, "w")
    for start_index in pooltab:
        pool.write(f"{start_index}\n")
    pool.close()

    if os.path.exists(TMP_FILENAME):
        os.remove(TMP_FILENAME)

    print("\n--- Pass I Complete ---")
    print(f"Final Symbol Table saved to {SYMTAB_FILENAME}")
    print(f"Intermediate Code saved to {INTER_CODE_FILENAME}")

if __name__ == "__main__":
    run_pass_one()
