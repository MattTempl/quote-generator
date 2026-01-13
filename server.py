from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Manual .env loader
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                key, value = line.split('=', 1)
                os.environ[key] = value

load_env()

# Ensure we can import from execution/
sys.path.append(os.path.join(os.path.dirname(__file__), 'execution'))

from parse_intent import parse_intent
from read_docs import search_products
from calculate_quote import calculate_quote

app = FastAPI()

# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root
@app.get("/")
async def read_root():
    return FileResponse('frontend/index.html')

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Step 1: Parse Intent
        intent_data = parse_intent(request.message)
        
        # If it's just chat (or an error/confusion), return the LLM's reply
        if intent_data.get("intent") == "chat" or not intent_data.get("selected_products"):
            reply = intent_data.get("conversational_reply")
            if not reply:
                reply = "I'm here to help with furniture quotes. What do you need?"
                
            return {
                "message": reply,
                "quote": None
            }

        # Step 2: Lookup Selected Products
        found_items = []
        kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base')
        
        # Helper to load full catalog for lookup
        import csv
        catalog_map = {}
        for root, _, files in os.walk(kb_path):
             for file in files:
                if file.endswith('.csv'):
                    with open(os.path.join(root, file), 'r') as f:
                        reader = csv.DictReader(f)
                        # Clean fieldnames (strip whitespace) if needed
                        if reader.fieldnames:
                            reader.fieldnames = [name.strip() for name in reader.fieldnames]
                            
                        for row in reader:
                            catalog_map[row['SKU']] = row

        missing_stock = []
        
        for selection in intent_data.get("selected_products", []):
            sku = selection.get("sku")
            qty = selection.get("quantity", 1)
            
            if sku in catalog_map:
                item = catalog_map[sku].copy()
                # Use the new Inventory_Limit column (fallback to Stock if missing, or 0)
                limit_val = item.get('Inventory_Limit') or item.get('Stock', 0)
                stock_available = int(limit_val)
                
                if qty > stock_available:
                    missing_stock.append(f"{item['Name']} (Requested: {qty}, Available: {stock_available})")
                else:
                    item['quantity'] = qty
                    found_items.append(item)

        if missing_stock:
            return {
                "message": f"I cannot complete that quote due to inventory limits. The following items are low on stock: {', '.join(missing_stock)}. Please adjust your quantity.",
                "quote": None
            }

        if not found_items:
            return {
                "message": "I couldn't find those specific items in the catalog. Try describing them differently.",
                "quote": None
            }

        # Step 3: Calculate Quote
        # Prepare data for calculator
        calc_input = []
        for item in found_items:
            calc_input.append({
                "sku": item['SKU'],
                "name": item['Name'],
                "price": float(item['Price']),
                "quantity": item['quantity']
            })
            
        quote_data = calculate_quote(calc_input)
        
        return {
            "message": intent_data.get("conversational_reply", f"I found {len(found_items)} items for you."),
            "data": quote_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
