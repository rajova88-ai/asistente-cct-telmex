import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# 1. CONFIGURACIÓN
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar la API Key
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. REGLAS Y MODELO
instruction = (
    "Eres un asistente experto en el Contrato Colectivo de Trabajo (CCT) de Telmex. "
    "Tus respuestas deben ser claras, cortas y estrictamente basadas en el JSON proporcionado. "
    "REGLA DE ORO: No inventes nada. Si la información no está en el JSON, "
    "responde: 'Lo siento, esa información no se encuentra en el contrato actual'. "
    "Cita el texto tal cual aparece en el campo 'cita' o 'texto_exacto'."
)

# Usamos el nombre base que nunca falla
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruction
)

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
    return "Servidor Estable Activo."

@app.route('/preguntar', methods=['POST'])
def preguntar():
    try:
        data = request.get_json()
        pregunta = data.get("pregunta")
        contexto = obtener_contexto()

        if not pregunta or not contexto:
            return jsonify({"respuesta": "Faltan datos o pregunta."}), 400

        # En esta versión, el prompt incluye el contexto directamente
        prompt_completo = f"Usa este JSON para responder: {contexto}\n\nPregunta: {pregunta}"
        
        response = model.generate_content(prompt_completo)

        return jsonify({
            "respuesta": response.text,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"respuesta": "Error de conexión con la IA.", "detalle": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
