import re

def parse_tesauro(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    terms = {}
    current_term = None
    last_field = None
    
    # Flags to detect start of content
    start_parsing = False
    
    # Regex patterns
    # Page breaks often have form feed character or header/footer lines
    header_pattern = re.compile(r'^\s*TESAURO BRASILEIRO', re.IGNORECASE)
    
    # Patterns
    header_pattern = re.compile(r'^\s*TESAURO BRASILEIRO', re.IGNORECASE)
    classification_start = "PLANO GERAL DE CLASSIFICAÇÃO"
    alphabetical_start = "ORDEM ALFABÉTICO- ESTRUTURADA"
    
    in_classification = False
    in_alphabetical = False
    previous_line_was_empty = True
    
    # Store category terms separately to ensure they are added
    category_terms = {} # id -> {text, bt}
    
    for line in lines:
        # Pre-cleaning
        has_form_feed = '\x0c' in line
        line_clean_start = line.lstrip('\x0c')
        line_stripped = line_clean_start.rstrip()
        
        # Form feed acts as a separator/blank line
        if has_form_feed:
            previous_line_was_empty = True
        
        # Skip totally empty lines but flag
        if not line_stripped.strip():
            previous_line_was_empty = True
            continue
            
        # Detect sections
        if classification_start in line:
            in_classification = True
            continue
            
        if alphabetical_start in line:
            in_classification = False
            in_alphabetical = True
            previous_line_was_empty = True
            continue

        # Skip headers
        if header_pattern.match(line_stripped) or line_stripped.strip().isdigit():
            continue

        # ---------------------------
        # PARSING CLASSIFICATION PLAN
        # ---------------------------
        if in_classification:
            # Lines look like: "1 Epistemologia...", "  1.1 História..."
            # Regex to capture ID and Name
            match = re.search(r'^\s*(\d+(?:\.\d+)*)\s+(.+)', line_stripped)
            if match:
                cat_id = match.group(1)
                cat_name = match.group(2).strip()
                
                # Sanitize colons to avoid splitting/qualifier issues
                cat_name = cat_name.replace(':', ' -')
                
                full_term = f"{cat_id} {cat_name}"
                
                # Determine parent
                # If 1.4.1 -> Parent is 1.4
                # If 1.4 -> Parent is 1
                # If 1 -> No parent (Top Term)
                
                parts = cat_id.split('.')
                parent_id = None
                if len(parts) > 1:
                    parent_id = '.'.join(parts[:-1])
                
                # We need to look up the full name of the parent to use as BT
                # This requires that parents appear before children (which they do in the file)
                
                bt = None
                if parent_id:
                    # Find extracted parent
                    # We store just the ID mapping?
                    # Let's iterate found categories
                    for existing_id in category_terms:
                        if existing_id == parent_id:
                            bt = category_terms[existing_id]['text']
                            break
                
                term_obj = {
                    'text': full_term,
                    'fields': []
                }
                
                if bt:
                    term_obj['fields'].append(('BT', bt))
                # Else: it's a root term, no fields needed (implies Top Term)
                    
                category_terms[cat_id] = term_obj
                terms[full_term] = term_obj
            continue

        # ---------------------------
        # PARSING ALPHABETICAL TERMS
        # ---------------------------
        if in_alphabetical:
            # DEBUG: One time print
            if not getattr(parse_tesauro, 'printed_cats', False):
                # print(f"DEBUG: Parsed Category IDs: {sorted(category_terms.keys())}")
                parse_tesauro.printed_cats = True

            # Determine if it is a New Term
            is_indented = line_clean_start.startswith(' ') or line_clean_start.startswith('\t')
            
            if not is_indented and previous_line_was_empty:
                # New term
                term_name = line_stripped.strip()
                
                # NORMALIZATION AT SOURCE:
                # Check if this term starts with a known ID (e.g. "1.4 ...", "8 -reas...")
                # If so, force the name to be the canonical one from the Classification Plan
                match_id = re.match(r'^(\d+(?:\.\d+)*)', term_name)
                canonical_name = None
                if match_id:
                     found_id = match_id.group(1)
                     # Only if it's in our known categories (Top Terms or Classification items)
                     if found_id in category_terms:
                         canonical_name = category_terms[found_id]['text']
                
                if canonical_name:
                    current_term = canonical_name
                else:
                    current_term = term_name
                
                if current_term not in terms:
                    terms[current_term] = {
                        'text': current_term,
                        'fields': [] 
                    }
                # Else: term already exists (e.g. from Classification Plan), we just append key fields to it.
                # This correctly merges "8 -reas..." fields into "8 Áreas..." object.
                
                last_field = None
                previous_line_was_empty = False
                
            else:
                # Field or continuation
                if current_term is None:
                    continue
                    
                stripped = line_stripped.strip()
                parts = stripped.split(None, 1)
                first_token = parts[0] if parts else ""
                rest = parts[1] if len(parts) > 1 else ""
                
                field_map = {
                    'USE': 'USE',
                    'UP': 'UF',
                    'TG': 'BT',
                    'TE': 'NT',
                    'TR': 'RT',
                    'NE:': 'NA',
                    'CAT:': 'BT', # CHANGED: Link category as Broader Term
                    'ING:': 'ING',
                    'ESP:': 'ESP'
                }
                
                field_type = field_map.get(first_token)
                
                if field_type:
                    value = rest
                    
                    # Logic: If field is BT (was CAT), we need to ensure the value matches the full Category Name
                    # The alphabetical list usually gives "CAT: 2.1 Organização..."
                    # Check if "2.1 Organização..." exists in our extracted categories.
                    # Usually the text matches exactly.
                    
                    if field_type == 'BT' and first_token == 'CAT:':
                        # Try to extract ID from value to normalize
                        # Value might be "1.5 Ensino ... -reas ..."
                        # Extract "1.5"
                        match_id = re.match(r'^(\d+(?:\.\d+)*)', value)
                        if match_id:
                             found_id = match_id.group(1)
                             if found_id in category_terms:
                                 # Use the canonical text from the classification plan
                                 value = category_terms[found_id]['text']

                    terms[current_term]['fields'].append((field_type, value))
                    last_field = field_type
                else:
                    # Continuation
                    if last_field:
                        last_type, last_val = terms[current_term]['fields'][-1]
                        if last_type == 'NA': 
                            new_val = last_val + " " + stripped
                            terms[current_term]['fields'][-1] = (last_type, new_val)
                        else:
                            val_to_add = stripped
                            # NORMALIZATION FOR CONTINUATION LINES (e.g. multiple CATs)
                            if last_type == 'BT':
                                match_id = re.match(r'^(\d+(?:\.\d+)*)', val_to_add)
                                if match_id:
                                     found_id = match_id.group(1)
                                     if found_id in category_terms:
                                         val_to_add = category_terms[found_id]['text']

                            terms[current_term]['fields'].append((last_type, val_to_add))
                
                previous_line_was_empty = False

    # Output generation
    with open(output_file, 'w', encoding='utf-8') as out:
        # Sort terms: maybe categories first, then alphabetical?
        # Or just alphabetical sort of everything?
        # Tematres import shouldn't care about order, but strict checking might.
        # Let's write categories first for clarity, then others.
        
        # Actually, let's just sort everything alphabetically by term text
        sorted_keys = sorted(terms.keys())
        
        for key in sorted_keys:
            term = terms[key]
            out.write(f"{term['text']}\n")
            for f_type, f_val in term['fields']:
                cleaned_val = f_val.strip()
                if not cleaned_val: continue
                out.write(f"{f_type}: {cleaned_val}\n")
            out.write("\n")

if __name__ == "__main__":
    parse_tesauro("full_tesauro.txt", "tesauro_final.txt")
