import os
import anthropic

key = os.getenv("CLAUDE_API_KEY")
if not key:
    print("No key provided")
    exit()

client = anthropic.Anthropic(api_key=key)

models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
]

print(f"Testing key: {key[:15]}...")

for m in models:
    try:
        print(f"Trying {m}...")
        client.messages.create(
            model=m,
            max_tokens=5,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"SUCCESS: {m}")
        # Build a file to save the winner
        with open("winner.txt", "w") as f:
            f.write(m)
        break
    except Exception as e:
        print(f"FAILED {m}: {e}")
