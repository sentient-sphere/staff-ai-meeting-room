#!/usr/bin/env python3
"""
STAFF AI Meeting Room - Flask Wrapper
Serve o frontend React e faz proxy para o backend FastAPI
"""

import os
import subprocess
import time
from flask import Flask, send_from_directory, request, Response
from flask_cors import CORS
import requests

# Inicializar Flask
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# URL do backend FastAPI (local)
FASTAPI_URL = "http://localhost:8002"

# Iniciar FastAPI em background
def start_fastapi():
    """Iniciar servidor FastAPI em background"""
    subprocess.Popen([
        "python3", "/home/ubuntu/meeting_room_app/src/main.py"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)  # Aguardar inicialização

# Iniciar FastAPI ao carregar
start_fastapi()

@app.route('/')
def index():
    """Servir frontend React"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Servir arquivos estáticos ou frontend"""
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    # Se não for arquivo, servir index.html (SPA routing)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_api(path):
    """Proxy para API FastAPI"""
    url = f"{FASTAPI_URL}/{path}"
    
    # Preparar request
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    
    try:
        if request.method == 'GET':
            resp = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            resp = requests.post(url, headers=headers, json=request.json)
        elif request.method == 'PUT':
            resp = requests.put(url, headers=headers, json=request.json)
        elif request.method == 'DELETE':
            resp = requests.delete(url, headers=headers)
        elif request.method == 'OPTIONS':
            return Response(status=200)
        
        # Retornar resposta
        return Response(
            resp.content,
            status=resp.status_code,
            headers=dict(resp.headers)
        )
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

