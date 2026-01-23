import re
import sys

def parse_capes_txt(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return

    processed_lines = []
    
    # Define indentation thresholds based on analysis of output.txt
    # Lvl 0: 0 spaces (Grande Área)
    # Lvl 1: ~3 spaces (Área)
    # Lvl 2: ~9 spaces (Subárea)
    # Lvl 3: ~13 spaces (Especialidade)
    
    for line in lines:
        # Regex to find lines starting with optional spaces, then digits, then text
        match = re.match(r'^(\s*)(\d+)\s+(.+)$', line)
        if match:
            indent_str = match.group(1)
            code = match.group(2)
            term = match.group(3).strip()
            
            indent_len = len(indent_str)
            
            # Determine hierarchy level
            if indent_len < 2:
                level = 0
            elif indent_len < 6:
                level = 1
            elif indent_len < 12:
                level = 2
            else:
                level = 3
                
            # Create tab indentation string
            tabs = '\t' * level
            
            # Format: Termo (Código)
            formatted_line = f"{tabs}{term} ({code})"
            processed_lines.append(formatted_line)
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed_lines))
        
    print(f"Successfully processed {len(processed_lines)} entries. Output saved to {output_file}")

if __name__ == "__main__":
    input_path = '/home/francis/laravel/labvoc/tabela_capes/output.txt'
    output_path = '/home/francis/laravel/labvoc/tabela_capes/tabela_capes_tematres.txt'
    
    parse_capes_txt(input_path, output_path)
