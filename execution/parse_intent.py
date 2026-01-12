import json
import argparse
import os

# NOTE: In a real production environment, you would use:
# import google.generativeai as genai
# or
# import openai

def mock_llm_response(prompt):
    """
    Simulates an LLM response for demonstration purposes without an API key.
    In production, this function would call the actual API.
    """
    prompt_lower = prompt.lower()
    intent = "search_product"
    products = []
    
    # Logic to simulate "Understanding" MULTIPLE items
    
    # 1. Check for Lamps
    if "lamp" in prompt_lower and "floor" in prompt_lower:
        products.append({"search_terms": ["floor lamp", "standing light"], "category": "Lighting"})

    # 2. Check for Sofas
    if "sofa" in prompt_lower or "couch" in prompt_lower:
        terms = ["sofa"]
        if "leather" in prompt_lower: terms.append("leather")
        if "fabric" in prompt_lower: terms.append("fabric")
        products.append({"search_terms": terms, "category": "Seating"})
        
    # 3. Check for Desks
    if "desk" in prompt_lower:
        terms = ["desk"]
        if "standing" in prompt_lower: terms.append("standing")
        products.append({"search_terms": terms, "category": "Desks"})
    
    if products:
        return json.dumps({
            "intent": intent,
            "products": products
        })
    
    # Fallback
    return json.dumps({
        "intent": "unknown",
        "products": []
    })

def call_real_llm(prompt):
    """
    Tries to call Google Gemini or OpenAI if keys are present.
    Falls back to mock logic if no keys found.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("CLAUDE_API_KEY")
    
    if claude_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=claude_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API Error: {e}")
            return json.dumps({
                "intent": "chat", 
                "conversational_reply": f"Claude API Error: {str(e)}", 
                "selected_products": []
            })
            
    elif gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            
            # DEBUG: List models
            # for m in genai.list_models():
            #     print(m.name)
                
            # DEBUG: List models
            # for m in genai.list_models():
            #     print(m.name)
                
            model = genai.GenerativeModel('gemini-flash-latest') 
            response = model.generate_content(prompt)
            # Cleanup JSON markdown if present
            text = response.text.replace('```json', '').replace('```', '')
            return text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            # return mock_llm_response(prompt) # DON'T FALLBACK SILENTLY
            # return mock_llm_response(prompt) # DON'T FALLBACK SILENTLY
            return json.dumps({
                "intent": "chat", 
                "conversational_reply": f"System Error: {str(e)}", 
                "selected_products": []
            })
            
    elif openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return mock_llm_response(prompt)
            
    return mock_llm_response(prompt)

def load_catalog_summary():
    # Helper to create a text summary of the catalog for the LLM
    catalog_path = os.path.join(os.path.dirname(__file__), '../knowledge_base/sample_products.csv')
    try:
        import csv
        summary_lines = []
        with open(catalog_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                line = f"SKU: {row['SKU']} | Name: {row['Name']} | Price: ${row['Price']} | Tags: {row['Tags']} | Category: {row['Category']}"
                summary_lines.append(line)
        return "\n".join(summary_lines)
    except Exception as e:
        return f"Error loading catalog: {e}"

def parse_intent(user_query):
    catalog_text = load_catalog_summary()
    
    system_prompt = f"""
    You are an intelligent Sales Engineer for a furniture company. 
    You have the following Product Catalog available:
    
    --- CATALOG START ---
    {catalog_text}
    --- CATALOG END ---
    
    USER QUERY: "{user_query}"
    
    INSTRUCTIONS:
    1. You are "QuoteBot", a helpful, professional, slightly witty Sales Engineer.
    2. Analyze the user's request.
    3. If they are chatting (e.g. "hello", "who are you"), be friendly but pivot back to selling furniture.
    4. If they want products, select the BEST matching products from the catalog.
    5. Return a JSON object.
    
    JSON FORMAT:
    {{
        "intent": "product_selection" (OR "chat" if no products needed),
        "conversational_reply": "Your friendly text response here...",
        "selected_products": [
            {{ "sku": "SKU-001", "quantity": 2 }}
        ]
    }}
    
    EXAMPLES:
    User: "Who are you?"
    Response: {{ "intent": "chat", "conversational_reply": "I'm QuoteBot, your digital sales engineer. I can't feel emotions, but I love a good spreadsheet. Looking for some office furniture today?", "selected_products": [] }}
    
    User: "I need a desk"
    Response: {{ "intent": "product_selection", "conversational_reply": "Excellent choice. Here is a solid option from our catalog.", "selected_products": [...] }}
    """
    
    # Call the LLM with the full context
    response_json = call_real_llm(system_prompt)
    
    try:
        parsed = json.loads(response_json)
        return parsed
    except:
        # Fallback for parsing errors
        return {
            "intent": "chat", 
            "conversational_reply": "I'm having a bit of trouble connecting to my brain right now. Could you try asking about furniture again?",
            "selected_products": []
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='User natural language query')
    args = parser.parse_args()
    
    result = parse_intent(args.query)
    print(json.dumps(result, indent=2))
