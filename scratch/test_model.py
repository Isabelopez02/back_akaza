import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview"]:
    print(f"Testing model: {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Hola, responde con la palabra 'OK'."
        )
        print(f"  Result: {response.text.strip()}")
    except Exception as e:
        print(f"  Error: {e}")
