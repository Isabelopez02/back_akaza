# Importa el SDJ de Google Gemini
from google import genai
# Acceder a variables de entorno
import os
#Carga las variables desde el archivo .env
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Función del chatbot (Aún estoy validando porque esta fallando pero si hace la conexión)
def responder_chat(mensaje: str):
    response = client.models.generate_content(
        #Modelo  de IA para mensajes
        model="gemini-1.5-flash",
        contents=[
            #Comportamiento del chatbot(He puesto algo básico lo podemos mejorar)
            "Eres un chatbot de restaurante, responde corto y conciso.",
            mensaje
        ]
    )

#Devuelve la respuesta del chatbot
    return response.text