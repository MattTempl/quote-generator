import csv
import random
import os

file_path = 'knowledge_base/sample_products.csv'
temp_path = 'knowledge_base/sample_products_temp.csv'

with open(file_path, 'r') as infile, open(temp_path, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    # The header names might have whitespace
    fieldnames = [f.strip() for f in reader.fieldnames]
    
    # Ensure Inventory_Limit is in fieldnames
    if 'Inventory_Limit' not in fieldnames:
        fieldnames.append('Inventory_Limit')
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        # Generate random inventory
        # 20% chance of being 0 (Out of Stock)
        if random.random() < 0.2:
            inv = 0
        else:
            inv = random.randint(1, 50)
            
        # Clean up row keys (remove whitespace from keys if present)
        clean_row = {k.strip(): v for k, v in row.items() if k}
        
        # Add new value
        clean_row['Inventory_Limit'] = inv
        
        writer.writerow(clean_row)

os.replace(temp_path, file_path)
print("CSV Updated successfully with random inventory limits.")
