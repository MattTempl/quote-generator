# Test Logic
import os
import csv
import sys
sys.path.append('execution')

# 1. Load Catalog
catalog_map = {}
with open('knowledge_base/sample_products.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        catalog_map[row['SKU']] = row

# 2. Simulate User Request
selection = {"sku": "DSK-004", "quantity": 1} # DSK-004 has Stock=0 now

# 3. Process
sku = selection["sku"]
qty = selection["quantity"]
item = catalog_map[sku]
stock = int(item['Stock'])

print(f"Item: {item['Name']}, Stock: {stock}, Requested: {qty}")
if qty > stock:
    print("SUCCESS: Inventory Check Failed (As Expected)")
else:
    print("FAILURE: Inventory Check Passed (Unexpected)")
