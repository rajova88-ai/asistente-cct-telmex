import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

# 1. CONFIGURACIÓN DE LOGS (Para ver qué pasa en Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. INICIALIZAR CLIENTE
# Render leerá GEMINI_API_KEY de las Environment Variables automáticamente
try:
    client = genai.Client()
    # Usamos una versión específica y estable para evitar el error 404
    MODEL_ID = "gemini-1.5-flash-002" 
    logger.info(f"Cliente Gemini configurado con el modelo: {MODEL_ID}")
except Exception as e:
    logger.error(f"Error al inicializar el cliente de Google: {e}")

# 3. INSTRUCCIONES DEL SISTEMA (Reglas de Oro)
SYSTEM_INSTRUCTION = (
    "Eres un asistente experto en el Contrato Colectivo de Trabajo (CCT) de Telmex. "
    "Tus respuestas deben ser claras, cortas y estrictamente basadas en el JSON proporcionado. "
    "REGLA DE ORO: No inventes nada. Si la información no está en el JSON, "
    "responde: 'Lo siento, esa información no se encuentra en el contrato actual'. "
    "Siempre que respondas algo sobre derechos, cita el texto tal cual aparece en el campo 'cita' o 'texto_exacto'."
)

# 4. INICIALIZAR FLASK
app = Flask(__name__)
CORS(app) # Permite que tu Hostinger hable con Render

# 5. FUNCIÓN PARA CARGAR EL CONTRATO
def obtener_contexto():
    ruta = os.path.join(os.path.dirname(__file__), 'datos.json')
    try:
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False)
        else:
            logger.error("ARCHIVO NO ENCONTRADO: datos.json no está en la raíz.")
            return None
    except Exception as e:
        logger.error(f"Error leyendo el JSON: {e}")
        return None

# 6. RUTAS
@app.route('/', methods=['GET'])
def home():
    return "Servidor del Asistente CCT funcionando correctamente."

@app.route('/preguntar', methods=['POST'])
def preguntar():
    try:
        # Validar entrada
        data = request.get_json()
        if not data or 'pregunta' not in data:
            return jsonify({"respuesta": "Error: No se recibió ninguna pregunta."}), 400
        
        pregunta_usuario = data.get("pregunta")
        
        # Obtener datos del contrato
        contexto = obtener_contexto()
        if not contexto:
            return jsonify({"respuesta": "Error técnico: No se pudo cargar la base de datos del contrato."}), 500

        # Llamada a la IA
        logger.info(f"Procesando pregunta: {pregunta_usuario}")
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"CONTEXTO DEL CONTRATO:\n{contexto}\n\nPREGUNTA DEL TRABAJADOR:\n{pregunta_usuario}",
            config={
                'system_instruction': SYSTEM_INSTRUCTION,
                'temperature': 0.1 # Muy baja para que no invente nada
            }
        )

        if not response.text:
            return jsonify({"respuesta": "La IA no generó una respuesta válida."}), 500

        return jsonify({
            "respuesta": response.text,
            "status": "success"
        })

    except Exception as e:
        error_msg = str(e)
        logger.error(f"ERROR CRÍTICO: {error_msg}")
        # Enviamos el error detallado para saber si es 404, 401, etc.
        return jsonify({
            "respuesta": f"Lo siento, ocurrió un error en el servidor de IA.",
            "detalle_tecnico": error_msg
        }), 500

if __name__ == '__main__':
    # Puerto para pruebas locales
    app.run(host='0.0.0.0', port=5000)
