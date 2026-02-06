import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. Configuración de API Key desde las variables de entorno de Render
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. Cargar tu archivo JSON (Contrato)
def cargar_contexto_json(ruta_archivo):
    try:
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "Archivo no encontrado"}
    except Exception as e:
        return {"error": str(e)}

contexto_datos = cargar_contexto_json('datos.json')

# 3. Configuración del Agente con tus REGLAS ESTRICTAS
instrucciones_sistema = (
    "Eres un asistente experto en el Contrato Colectivo de Trabajo (CCT) de Telmex. "
    f"Tu base de conocimiento es estrictamente este JSON: {json.dumps(contexto_datos, ensure_ascii=False)}. "
    "REGLAS OBLIGATORIAS: "
    "1. No inventes nada. Si la información no está en el JSON, responde que no se encuentra en el contrato. "
    "2. Si el usuario pregunta por vacaciones con 8 años de antigüedad (o cualquier otra), "
    "debes decir que el contrato proporciona esos días, mencionar que la ley federal establece los mínimos, "
    "y citar el texto exacto que aparezca en el documento."
)

# 4. Inicializar el modelo verificado en tu lista (gemini-flash-latest)
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=instrucciones_sistema
)

# Iniciamos el chat (sesión persistente por cada ejecución del servidor)
chat_session = model.start_chat(history=[])

@app.route('/preguntar', methods=['POST'])
def preguntar():
    try:
        data = request.get_json()
        pregunta_usuario = data.get("pregunta", "")
        
        # Enviamos la pregunta usando la sesión de chat
        response = chat_session.send_message(pregunta_usuario)
        
        return jsonify({
            "respuesta": response.text,
            "status": "success"
        })
    except Exception as e:
        # Si ocurre el error 429, el mensaje será claro
        error_msg = str(e)
        if "429" in error_msg:
            return jsonify({"respuesta": "Límite de mensajes alcanzado. Espera un minuto."}), 429
        return jsonify({"respuesta": "Error en el servidor", "detalle": error_msg}), 500

@app.route('/')
def home():
    return "Servidor CCT Telmex (Gemini-Flash) Activo"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
