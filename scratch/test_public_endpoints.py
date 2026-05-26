import os
from dotenv import load_dotenv
import requests

load_dotenv()
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

try:
    print("Testing GET /api/admin/platos/ ...")
    res_platos = requests.get(f"{BASE_URL}/api/admin/platos/")
    print(f"Status: {res_platos.status_code}")
    if res_platos.status_code == 200:
        print(f"Success! Loaded {len(res_platos.json())} platos.")
    else:
        print(res_platos.text)

    print("\nTesting GET /api/admin/combos/ ...")
    res_combos = requests.get(f"{BASE_URL}/api/admin/combos/")
    print(f"Status: {res_combos.status_code}")
    if res_combos.status_code == 200:
        print(f"Success! Loaded {len(res_combos.json())} combos.")
    else:
        print(res_combos.text)

except Exception as e:
    print(f"Error testing endpoints: {e}")
