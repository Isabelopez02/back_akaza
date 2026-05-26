import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

try:
    res = requests.get(f"{BASE_URL}/api/pedidos/")
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        pedidos = res.json()
        print(f"Total pedidos: {len(pedidos)}")
        for p in pedidos[:3]:
            print(json.dumps(p, indent=2))
    else:
        print(res.text)
except Exception as e:
    print(f"Error fetching API: {e}")
