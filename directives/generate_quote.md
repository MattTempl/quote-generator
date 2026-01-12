# Directive: Generate Quote

## Goal
Generate a mathematically accurate price quote for a customer based on their natural language request, using internal product data and pricing rules.

## Inputs
- Customer Request (e.g., "I need 3 heat pumps and installation for a 2500 sq ft house")
- Knowledge Base: `knowledge_base/*.csv` (Pricing/Stock) and `knowledge_base/*.txt` (Specs)

## Tools
1. `execution/read_docs.py`: To search for product SKUs, prices, and specs.
2. `execution/calculate_quote.py`: To perform the final calculation.

## Process
1. **Analyze Request (LLM Step)**: 
   - Run `python3 execution/parse_intent.py "User Query"` to extract structured search terms.
   - Example: "Lamp for floor" -> `["floor lamp", "standing light"]`.

2. **Search Knowledge Base**:
   - Use `read_docs.py` with the *extracted keywords* from Step 1.
   - Retrieve the unit price and stock status.
   - Check specs in `.txt` files if the user provided constraints (e.g., "2500 sq ft" -> confirms HVAC-001 is appropriate).
3. **Calculate**:
   - Call `calculate_quote.py` with the list of SKUs and quantities.
   - The script will handle total summation and tax/discounts if hardcoded.
4. **Responsd**:
   - Present the final quote clearly to the user.
   - Include a breakdown of items.
   - Mention any potential issues (e.g., Low Stock).

## Edge Cases
- **Product Not Found**: Inform the user and ask for clarification.
- **Ambiguous Request**: If "AC" matches 2 products, ask the user to clarify (e.g., "Do you want the Premium (22 SEER) or Standard (16 SEER)?").
- **Stock Low**: Warn the user if requested quantity > stock.
