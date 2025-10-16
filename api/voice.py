"""
Vercel Serverless Function - Voice Endpoint
Handles text-to-speech with ElevenLabs
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import base64

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for voice synthesis"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Extract data
            text = data.get('text', '')
            voice_id = data.get('voice_id', 'EXAVITQu4vr4xnSDxMaL')
            
            if not text:
                raise ValueError("No text provided")
            
            # Call ElevenLabs API
            url = f"{ELEVENLABS_API_URL}/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # Convert audio to base64
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'audio': audio_base64,
                    'format': 'mp3'
                }
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            else:
                raise Exception(f"ElevenLabs API error: {response.status_code}")
                
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = {'error': str(e)}
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

