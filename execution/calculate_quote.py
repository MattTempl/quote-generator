import argparse
import json
import sys

def calculate_quote(items_input):
    """
    items_input structure: List of dicts OR JSON string
    [
        {"name": "Item Name", "price": 100.00, "quantity": 2},
        ...
    ]
    """
    if isinstance(items_input, list):
        items = items_input
    else:
        try:
            items = json.loads(items_input)
        except json.JSONDecodeError:
            print("Error: Invalid JSON input")
            sys.exit(1)

    subtotal = 0.0
    detailed_lines = []

    for item in items:
        price = float(item.get('price', 0))
        qty = int(item.get('quantity', 1))
        line_total = price * qty
        subtotal += line_total
        detailed_lines.append({
            "name": item.get('name'),
            "quantity": qty,
            "unit_price": price,
            "line_total": line_total
        })
    
    # Simple hardcoded tax for demo
    tax_rate = 0.08
    tax = subtotal * tax_rate
    total = subtotal + tax

    return {
        "line_items": detailed_lines,
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('items_json', help='JSON string of items list')
    args = parser.parse_args()
    
    result = calculate_quote(args.items_json)
    
    print("--- QUOTE BREAKDOWN ---")
    for line in result['line_items']:
        print(f"{line['name']} (x{line['quantity']}) @ ${line['unit_price']:,.2f} = ${line['line_total']:,.2f}")
    print("-----------------------")
    print(f"Subtotal: ${result['subtotal']:,.2f}")
    print(f"Tax (8%): ${result['tax']:,.2f}")
    print(f"TOTAL:    ${result['total']:,.2f}")
    print("-----------------------")
