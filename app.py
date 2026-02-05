import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def test_comunicacion():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: No encontré la GEMINI_API_KEY en las variables de Render.", 500
    
    # Intentamos la ruta más básica y ESTABLE de Google (v1, no v1beta)
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    
    try:
        response = requests.get(url)
        datos = response.json()
        
        if response.status_code == 200:
            # Si entramos aquí, la API Key está perfecta y la comunicación existe
            modelos = [m['name'] for m in datos.get('models', [])]
            return jsonify({
                "mensaje": "¡CONEXIÓN EXITOSA!",
                "tu_api_key": "Configurada correctamente",
                "modelos_disponibles": modelos
            })
        else:
            return jsonify({
                "mensaje": "Google rechazó la conexión",
                "error_google": datos
            }), response.status_code
            
    except Exception as e:
        return f"Error al intentar conectar: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
