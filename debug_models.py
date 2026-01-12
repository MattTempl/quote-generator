import google.generativeai as genai
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

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API KEY found")
    exit(1)

genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        print(f"Model: {m.name}")
        print(f"Supported methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
