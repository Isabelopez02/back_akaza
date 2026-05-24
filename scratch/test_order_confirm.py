import requests
import uuid
import json

BASE_URL = "http://127.0.0.1:8000"

def test_order_confirmation():
    # 1. Registrar usuario
    email = f"user_{uuid.uuid4().hex[:6]}@akaza.com"
    password = "MySecurePassword123"
    print(f"--- Registering user: {email} ---")
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "nombre": "User Test Confirm",
        "correo": email,
        "contrasenia": password
    })
    
    # 2. Login
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "correo": email,
        "contrasenia": password
    })
    token = res.json().get("access_token")
    
    # 3. Get profile
    headers = {"Authorization": f"Bearer {token}"}
    res_me = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    user_id = res_me.json().get("id")
    print(f"User ID: {user_id}")
    
    # 4. Chatbot order message (using exact dish name)
    chat_payload = {
        "id_usuario": user_id,
        "nro_mesa": 5,
        "mensaje": "Quiero pedir 1 Ceviche de Pescado Clásico para mi mesa 5"
    }
    print("\n--- Sending Order Request ---")
    res_chat1 = requests.post(f"{BASE_URL}/api/chat/mensaje", json=chat_payload)
    print("AKAZA:", res_chat1.json().get("respuesta_ia"))
    
    # 5. Confirm Order message
    confirm_payload = {
        "id_usuario": user_id,
        "nro_mesa": 5,
        "mensaje": "Sí, deseo realizar otro pedido para esta misma mesa. Confirma el Ceviche de Pescado Clásico por favor."
    }
    print("\n--- Confirming Order ---")
    res_chat2 = requests.post(f"{BASE_URL}/api/chat/mensaje", json=confirm_payload)
    print("AKAZA:", res_chat2.json().get("respuesta_ia"))
    
    # 6. Verify order in DB
    print("\n--- Verifying Order in DB ---")
    res_pedidos = requests.get(f"{BASE_URL}/api/pedidos/")
    all_pedidos = res_pedidos.json()
    user_pedidos = [p for p in all_pedidos if p.get("id_usuario") == user_id]
    
    print(f"Total orders for User {user_id} in DB: {len(user_pedidos)}")
    for p in user_pedidos:
        print(f"Order Ticket: {p.get('ticket')}, Total: {p.get('total')}, Estado Cocina: {p.get('estado_cocina')}, Pago: {p.get('estado_pago')}")
        print("Detalles:")
        for d in p.get("detalles", []):
            print(f"  - Plato ID: {d.get('id_plato')}, Cantidad: {d.get('cantidad')}")

if __name__ == "__main__":
    test_order_confirmation()
