import subprocess
import re
import sys
import os

GRANDES_AREAS = {
    '10000003': 'CIÊNCIAS EXATAS E DA TERRA',
    '20000006': 'CIÊNCIAS BIOLÓGICAS',
    '30000009': 'ENGENHARIAS',
    '40000001': 'CIÊNCIAS DA SAÚDE',
    '50000004': 'CIÊNCIAS AGRÁRIAS',
    '60000007': 'CIÊNCIAS SOCIAIS APLICADAS',
    '70000000': 'CIÊNCIAS HUMANAS',
    '80000002': 'LINGUÍSTICA, LETRAS E ARTES',
    '90000005': 'MULTIDISCIPLINAR'
}

AREAS_AVALIACAO_CODIGOS = {
    '10100008', '10200002', '10300007', '10400001', '10500006', '10600000', '10700005', '10800000',
    '20100000', '20200005', '20600003', '20700008', '20800002', '20900007', '21000000', '21100004',
    '21200009', '21300003', '20500009', '10801006', '20300000', '20400004',
    '30100003', '30700000', '31000002', '30200008', '30300002', '30600006', '30900000',
    '30500001', '30800005', '31100007', '31200001', '30400007', '31300006',
    '40100006', '40101002', '40101037', '40101150', '40102009', '40500004', '40200000', '40300005',
    '40400000', '40600009', '40900002', '40700003', '40800008',
    '50100009', '50200003', '50300008', '50400002', '50600001', '50500007', '50700006',
    '60100001', '60200006', '61300004', '60300000', '60400005', '61200000', '60500000', '60600004',
    '60700009', '60800003', '60900008', '61000000', '61100005',
    '70100004', '71000003', '70200009', '70300003', '70400008', '70500002', '70600007', '70700001',
    '70800006', '70900000',
    '80100007', '80200001', '80300006',
    '90100000', '90200000', '90300009', '90400003', '90500008',
}

def analyze_pdf_dump(dump_path):
    print(f"[PDF-TXT] Analisando texto extraído do PDF: {dump_path}")
    
    counts = {'Grande Área': 0, 'Área': 0, 'Subárea': 0, 'Especialidade': 0, 'Total': 0}
    
    grande_area_atual = None
    area_atual = None
    subarea_atual = None
    
    if not os.path.exists(dump_path):
        print("Arquivo de dump não encontrado.")
        return None

    with open(dump_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Regex to find Code (8 digits)
            match = re.search(r'(\d{8})', line)
            if match:
                codigo = match.group(1)
                tipo = None
                
                if codigo in GRANDES_AREAS:
                    tipo = 'Grande Área'
                    grande_area_atual = codigo
                    area_atual = None
                    subarea_atual = None
                    
                elif (codigo in AREAS_AVALIACAO_CODIGOS or codigo.endswith('000')):
                    tipo = 'Área'
                    area_atual = codigo
                    subarea_atual = None
                    
                elif area_atual and not codigo[-3:] in ['000', '001', '002', '003', '004']:
                    tipo = 'Subárea'
                    subarea_atual = codigo
                    
                elif subarea_atual:
                    tipo = 'Especialidade'
                
                if tipo:
                    counts[tipo] += 1
                    counts['Total'] += 1
                    
    return counts

def analyze_txt(txt_path):
    print(f"[TXT] Analisando arquivo original: {txt_path}")
    counts = {'Grande Área': 0, 'Área': 0, 'Subárea': 0, 'Especialidade': 0, 'Total': 0}
    
    if not os.path.exists(txt_path):
        print("Arquivo TXT não encontrado.")
        return None
        
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            
            tabs = 0
            for char in line:
                if char == '\t': tabs += 1
                else: break
            
            if tabs == 0: counts['Grande Área'] += 1
            elif tabs == 1: counts['Área'] += 1
            elif tabs == 2: counts['Subárea'] += 1
            elif tabs >= 3: counts['Especialidade'] += 1
            
            counts['Total'] += 1
            
    return counts

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the temporary dump file created separately
    dump_path = "temp_pdf_dump.txt" 
    # Relative to CWD (verificação_tabela_capes_scripts/)
    
    possible_txt_paths = [
        "../tabelacapes/olds/areas_hierarquicas.txt",
        "../../tabelacapes/olds/areas_hierarquicas.txt",
        "/home/francis/laravel/tematres/tabelacapes/olds/areas_hierarquicas.txt" 
    ]
    
    txt_path = None
    for p in possible_txt_paths:
        full_p = os.path.join(script_dir, p)
        if os.path.exists(full_p):
            txt_path = full_p
            break
            
    if not txt_path:
        print("Erro: Arquivo TXT original não encontrado.")
        sys.exit(1)
        
    if not os.path.exists(dump_path):
        # Fallback: try full path relative to script
        dump_path = os.path.join(script_dir, "temp_pdf_dump.txt")
        if not os.path.exists(dump_path):
             print(f"Erro: Arquivo de dump {dump_path} não encontrado. Execute pdftotext primeiro.")
             sys.exit(1)
    
    pdf_counts = analyze_pdf_dump(dump_path)
    txt_counts = analyze_txt(txt_path)
    
    if pdf_counts is None or txt_counts is None:
        print("Erro na análise. Abortando.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("RELATÓRIO COMPARATIVO: PDF (Dump) vs TXT (Original)")
    print("="*60)
    print(f"{'Nível':<20} | {'PDF (Códigos)':<15} | {'TXT (Indentação)':<15} | {'Status'}")
    print("-" * 60)
    
    levels = ['Grande Área', 'Área', 'Subárea', 'Especialidade', 'Total']
    
    all_match = True
    for level in levels:
        pdf_val = pdf_counts.get(level, 0)
        txt_val = txt_counts.get(level, 0)
        
        match_symbol = "✓ OK"
        if pdf_val != txt_val:
             match_symbol = "⚠️ DIFERENÇA"
             all_match = False
             
        print(f"{level:<20} | {pdf_val:<15} | {txt_val:<15} | {match_symbol}")
    
    print("="*60)
    if all_match:
        print("\nCONCLUSÃO: A extração foi BEM SUCEDIDA. As quantidades batem exatamente.")
    else:
        print("\nCONCLUSÃO: Houve divergências na extração. Verifique os níveis acima.")
        
    # Cleanup
    # if os.path.exists(dump_path):
    #     os.remove(dump_path)
    #     print("\nInfo: Arquivo temporário removido.")
