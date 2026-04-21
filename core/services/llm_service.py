from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def interpretar_mensaje(mensaje: str) -> dict:
    """
    Convierte lenguaje natural a JSON estructurado.
    """

    prompt = f"""
    Eres Akaza, una asistente virtual de un restaurante peruano.

    Tu personalidad es:
    - Amable
    - Divertida
    - Formal pero cercana
    - Natural como humano

    Tu trabajo es ENTENDER el mensaje del usuario como una persona real, no como un sistema de reglas.

    IMPORTANTE:
    - No dependes de palabras clave exactas
    - Debes interpretar contexto libremente (enfermedades, alergias, gustos, emociones, pedidos, etc.)
    - Siempre responde en JSON válido

    FORMATO DE RESPUESTA:
    {{
      "intencion": "saludo | info_restaurante | recomendacion | pedido | otro",
      "mensaje": "respuesta natural al usuario",
      "contexto": {{
        "estado_salud": "",
        "alergias": [],
        "preferencias": [],
        "notas": ""
      }}
    }}

    REGLAS IMPORTANTES:
    - Si el usuario habla de salud (resfriado, enfermo, malestar), usa contexto estado_salud
    - Si menciona alergias, agrégalas en alergias
    - Si pide comida, interpreta intención como pedido o recomendación según el caso
    - Si no estás seguro, responde de forma conversacional, no técnica
    - NO inventes datos médicos, solo adapta recomendaciones de comida

    EJEMPLOS:

    Usuario: tengo alergia a los mariscos
    Respuesta:
    {{
      "intencion": "recomendacion",
      "mensaje": "Perfecto, evitaré mariscos para ti 😊 Te puedo recomendar pollo a la plancha o pastas.",
      "contexto": {{
        "alergias": ["mariscos"]
      }}
    }}

    Usuario: estoy resfriado y quiero algo ligero
    Respuesta:
    {{
      "intencion": "recomendacion",
      "mensaje": "Te recomiendo algo suave y caliente como una sopa de pollo 🍲 o un caldo ligero.",
      "contexto": {{
        "estado_salud": "resfriado"
      }}
    }}

    Usuario: {mensaje}
    Respuesta:
    """
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", # ⚠️ usa este, no preview raro
            contents=prompt
        )

        texto = response.text.strip()

        # 🔥 LIMPIEZA (Gemini a veces mete ```json)
        if "```" in texto:
            texto = texto.replace("```json", "").replace("```", "").strip()

        return json.loads(texto)

    except Exception as e:
        print("Error Gemini:", e)

        # 🔥 fallback inteligente (CLAVE)
        return fallback_parse(mensaje)


def fallback_parse(texto: str) -> dict:
    texto = texto.lower()

    if "hola" in texto:
        return {"intencion": "saludo"}

    if "menu" in texto or "que vendes" in texto:
        return {"intencion": "info_restaurante"}

    if "resfriado" in texto:
        return {
            "intencion": "recomendacion",
            "contexto": {"estado": "resfriado"}
        }

    if "recomienda" in texto:
        return {
            "intencion": "recomendacion",
            "contexto": {}
        }

    if "pedir" in texto:
        return {
            "intencion": "pedido",
            "articulos": []
        }

    return {"intencion": "desconocida"}