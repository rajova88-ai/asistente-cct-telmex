import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- EL CAMBIO ESTÁ AQUÍ ---
# Forzamos explícitamente la versión 'v1' para saltarnos el error de la beta
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never" 
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY, transport='rest') # Usamos transporte REST para mayor estabilidad en Render

# Intentamos cargar el modelo con el nombre que la API v1 reconoce
model = genai.GenerativeModel('gemini-1.5-flash')
# ---------------------------

app = Flask(__name__)
CORS(app)

def obtener_contexto():
    try:
        if os.path.exists('datos.json'):
            with open('datos.json', 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), ensure_ascii=False)
        return None
    except Exception as e:
        logger.error(f"Error JSON: {e}")
        return None

@app.route('/', methods=['GET'])
def home():
    return "Servidor en v1 Estable Activo."

@app.route('/preguntar', methods=['POST'])
def preguntar():
    try:
        data = request.get_json()
        pregunta = data.get("pregunta")
        contexto = obtener_contexto()

        if not pregunta or not contexto:
            return jsonify({"respuesta": "Faltan datos."}), 400

        # Instrucciones del sistema pegadas al prompt (método más compatible)
        prompt_instrucciones = (
            "Eres un asistente experto en el CCT de Telmex. "
            "Responde corto, claro y cita el texto del JSON. No inventes nada. "
            f"Base de datos: {contexto}\n\nPregunta: {pregunta}"
        )
        
        response = model.generate_content(prompt_instrucciones)

        return jsonify({
            "respuesta": response.text,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Error detectado: {e}")
        return jsonify({"respuesta": "Error de comunicación.", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
