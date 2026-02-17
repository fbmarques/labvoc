import re
import sys
import os

def count_terms(file_path):
    # Resolve relative path if needed, assuming run from script dir or provided full path
    if not os.path.exists(file_path):
        # Try finding it relative to script directory just in case
        script_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.join(script_dir, file_path)
        if os.path.exists(potential_path):
            file_path = potential_path
            
    print(f"Lendo arquivo: {file_path}")
    
    counts = {
        'Grande Área': 0,
        'Área': 0,
        'Subárea': 0,
        'Especialidade': 0,
        'Total': 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line_content = line.strip()
            if not line_content:
                continue
                
            # Detect indentation (tabs or spaces)
            # Assuming the file uses tabs for hierarchy as seen in previous steps
            
            # Count leading tabs
            tabs = 0
            for char in line:
                if char == '\t':
                    tabs += 1
                else:
                    break
            
            # If no tabs, it is a Grande Área (Root term)
            if tabs == 0:
                counts['Grande Área'] += 1
            elif tabs == 1:
                counts['Área'] += 1
            elif tabs == 2:
                counts['Subárea'] += 1
            elif tabs >= 3:
                counts['Especialidade'] += 1
                
            counts['Total'] += 1
            
        print("\n=== Relatório de Contagem (Estimativa baseada em indentação) ===")
        print(f"Grandes Áreas: {counts['Grande Área']}")
        print(f"Áreas: {counts['Área']}")
        print(f"Subáreas: {counts['Subárea']}")
        print(f"Especialidades: {counts['Especialidade']}")
        print(f"--------------------------------------------------")
        print(f"Total de Termos: {counts['Total']}")
        print("==================================================")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {file_path}")
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")

if __name__ == "__main__":
    # Default path relative to where script is located (verificação_tabela_capes_scripts/)
    # The file areas_hierarquicas.txt is in ../tabelacapes/olds/
    default_file = "../tabelacapes/olds/areas_hierarquicas.txt"
    
    file_to_check = sys.argv[1] if len(sys.argv) > 1 else default_file
    count_terms(file_to_check)
