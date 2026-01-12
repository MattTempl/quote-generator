import os
import csv
import argparse

def search_products(query, kb_path):
    results = []
    # Search all CSVs for product/SKU matches
    for root, _, files in os.walk(kb_path):
        for file in files:
            if file.endswith('.csv'):
                with open(os.path.join(root, file), 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Simple case-insensitive contains search
                        # Keyword-based search (ALL keywords must be present in ANY field combination)
                        # This simulates "understanding" natural language like "lamp floor"
                        fields_combined = " ".join([
                            row.get('Name', ''), 
                            row.get('SKU', ''), 
                            row.get('Category', ''), 
                            row.get('Tags', '')
                        ]).lower()
                        
                        stop_words = {'that', 'goes', 'on', 'the', 'for', 'with', 'a', 'an', 'is', 'of', 'in', 'to', 'and'}
                        
                        # Simple stemming (remove trailing 's')
                        query_words = []
                        for w in query.lower().split():
                            if w in stop_words: continue
                            if w.endswith('s') and len(w) > 3: w = w[:-1]
                            query_words.append(w)
                        
                        match = True
                        if not query_words: match = False
                        
                        for word in query_words:
                            if word not in fields_combined:
                                match = False
                                break
                        
                        if match:
                             results.append(row)
    return results

def search_specs(query, kb_path):
    results = []
    # Search all TXT/MD files for content matches
    for root, _, files in os.walk(kb_path):
        for file in files:
            if file.endswith('.txt') or file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        # Return snippet around match
                        idx = content.lower().find(query.lower())
                        start = max(0, idx - 50)
                        end = min(len(content), idx + 150)
                        snippet = content[start:end].replace('\n', ' ')
                        results.append(f"File: {file} | Match: ...{snippet}...")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search Knowledge Base')
    parser.add_argument('query', help='Search query (product name or SKU)')
    parser.add_argument('--type', choices=['product', 'spec'], default='product')
    parser.add_argument('--kb_path', default='./knowledge_base')
    
    args = parser.parse_args()
    
    if args.type == 'product':
        hits = search_products(args.query, args.kb_path)
        for hit in hits:
            print(f"FOUND_PRODUCT: {hit}")
    else:
        hits = search_specs(args.query, args.kb_path)
        for hit in hits:
            print(f"FOUND_SPEC: {hit}")
