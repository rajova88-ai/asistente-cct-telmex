import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai  # Nueva librería

# 1. CONFIGURACIÓN INICIAL
# La SDK nueva toma automáticamente GEMINI_API_KEY del entorno
client = genai.Client()
MODEL_ID = "gemini-1.5-flash" # O "gemini-3-flash-preview" si ya tienes acceso total

instruction = (
    "Eres un asistente experto en el Contrato Colectivo de Trabajo (CCT) de Telmex. "
    "Tus respuestas deben ser claras, cortas y estrictamente basadas en el JSON proporcionado. "
    "REGLA DE ORO: No inventes nada. Si la información no está en el JSON, "
    "responde: 'Lo siento, esa información no se encuentra en el contrato actual'. "
    "Siempre que respondas algo sobre derechos, cita el texto tal cual aparece en el campo 'cita' o 'texto_exacto'."
)

# 2. INICIALIZAR FLASK
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# 3. FUNCIÓN PARA CARGAR EL JSON
def obtener_contexto():
    try:
        if os.path.exists('datos.json'):
            with open('datos.json', 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), ensure_ascii=False)
        return None
    except Exception as e:
        logging.error(f"Error al leer datos.json: {e}")
        return None

# 4. RUTAS
@app.route('/', methods=['GET'])
def index():
    return "Servidor Gemini 3 Activo."

@app.route('/preguntar', methods=['POST'])
def preguntar():
    try:
        data = request.get_json()
        pregunta_usuario = data.get("pregunta")
        contexto = obtener_contexto()

        if not pregunta_usuario or not contexto:
            return jsonify({"respuesta": "Error de configuración o pregunta vacía."}), 400

        # Nueva forma de generar contenido con la SDK 2.0
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"CONTEXTO CCT:\n{contexto}\n\nPREGUNTA:\n{pregunta_usuario}",
            config={'system_instruction': instruction}
        )
        
        return jsonify({
            "respuesta": response.text,
            "status": "success"
        })

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"respuesta": f"Error técnico: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
