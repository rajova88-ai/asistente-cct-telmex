import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# 1. CONFIGURACIÓN INICIAL
# Reemplaza con tu llave real obtenida en Google AI Studio
API_KEY = "TU_API_KEY_AQUI"
genai.configure(api_key=API_KEY)

# Configuración del modelo Gemini 1.5 Flash (económico y rápido)
# Usamos 'system_instruction' para darle la personalidad y reglas que pediste
instruction = (
    "Eres un asistente experto en el Contrato Colectivo de Trabajo (CCT) de Telmex. "
    "Tus respuestas deben ser claras, cortas y estrictamente basadas en el JSON proporcionado. "
    "REGLA DE ORO: No inventes nada. Si la información no está en el JSON, "
    "responde: 'Lo siento, esa información no se encuentra en el contrato actual'. "
    "Siempre que respondas algo sobre derechos, cita el texto tal cual aparece en el campo 'cita' o 'texto_exacto'."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruction
)

# 2. INICIALIZAR FLASK
app = Flask(__name__)
CORS(app)  # Esto permite que tu HTML consulte al servidor sin bloqueos

# Configurar logs para ver errores en la consola del servidor
logging.basicConfig(level=logging.INFO)

# 3. FUNCIÓN PARA CARGAR EL JSON
def obtener_contexto():
    try:
        # Buscamos el archivo en la misma ruta que este script
        ruta_json = os.path.join(os.path.dirname(__file__), 'datos.json')
        with open(ruta_json, 'r', encoding='utf-8') as f:
            return json.dumps(json.load(f), ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error al leer datos.json: {e}")
        return None

# 4. RUTAS DEL SERVIDOR
@app.route('/', methods=['GET'])
def index():
    return "Servidor de IA Telmex Activo y Corriendo."

@app.route('/preguntar', methods=['POST'])
def preguntar():
    try:
        # Obtener la pregunta del HTML
        data = request.get_json()
        pregunta_usuario = data.get("pregunta")

        if not pregunta_usuario:
            return jsonify({"respuesta": "No enviaste ninguna pregunta."}), 400

        # Obtener la base de conocimientos del JSON
        contexto = obtener_contexto()
        if not contexto:
            return jsonify({"respuesta": "Error: El servidor no pudo cargar la base de datos JSON."}), 500

        # Construir el mensaje para la IA
        # Le pasamos el JSON entero como contexto previo
        prompt_final = f"BASE DE DATOS (JSON):\n{contexto}\n\nPREGUNTA DEL USUARIO: {pregunta_usuario}"

        # Generar respuesta
        response = model.generate_content(prompt_final)
        
        logging.info(f"Consulta procesada: {pregunta_usuario}")
        
        return jsonify({
            "respuesta": response.text,
            "status": "success"
        })

    except Exception as e:
        logging.error(f"Error en el endpoint /preguntar: {e}")
        return jsonify({"respuesta": "Hubo un error interno en el servidor.", "error": str(e)}), 500

# 5. EJECUCIÓN (Para Hostinger/Local)
if __name__ == '__main__':
    # Usamos el puerto 5000 por defecto
    app.run(host='0.0.0.0', port=5000, debug=True)
