import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 1. CARGAR DATOS DEL JSON
def obtener_contexto():
    try:
        if os.path.exists('datos.json'):
            with open('datos.json', 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), ensure_ascii=False)
        return "No hay datos disponibles."
    except Exception as e:
        return f"Error al leer JSON: {str(e)}"

# 2. RUTA PRINCIPAL (CHAT)
@app.route('/preguntar', methods=['POST'])
def preguntar():
    api_key = os.environ.get("GEMINI_API_KEY")
    data = request.get_json()
    pregunta_usuario = data.get("pregunta", "")
    contexto = obtener_contexto()

    # Usamos Gemini 2.0 Flash (el más rápido y disponible según tu test)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Configuramos el prompt con tus reglas de oro
    prompt_sistema = (
        "Eres un experto en el CCT de Telmex. "
        "Responde de forma clara, corta y cita el texto exacto del JSON. "
        "Si no está en el JSON, di que no se encuentra en el contrato. No inventes nada. "
        f"CONTEXTO JSON: {contexto}"
    )

    payload = {
        "contents": [{
            "parts": [{
                "text": f"{prompt_sistema}\n\nPregunta del usuario: {pregunta_usuario}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 800
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()

        if response.status_code == 200:
            # Extraemos la respuesta de la estructura de Google
            texto_ia = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"respuesta": texto_ia, "status": "success"})
        else:
            return jsonify({"respuesta": "Error de la IA", "detalle": res_data}), response.status_code

    except Exception as e:
        return jsonify({"respuesta": "Error de conexión", "error": str(e)}), 500

@app.route('/')
def home():
    return "Servidor CCT Telmex con Gemini 2.0/2.5 Activo."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
