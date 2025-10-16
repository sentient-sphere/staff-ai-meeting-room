"""
Vercel Serverless Function - Chat Endpoint
Handles chat messages with AI agents
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Agent configurations
AGENTS = {
    'elara': {
        'name': 'Elara Veyra',
        'role': 'CEO & Chief of Staff',
        'voice_id': 'EXAVITQu4vr4xnSDxMaL',
        'personality': 'Strategic, decisive, visionary leader'
    },
    'aurora': {
        'name': 'Aurora Castellane',
        'role': 'Chief Marketing Officer',
        'voice_id': 'ThT5KcBeYPX3keUQqHPh',
        'personality': 'Creative, analytical, results-oriented'
    },
    'helios': {
        'name': 'Helios Vanterre',
        'role': 'Chief Design Officer',
        'voice_id': '21m00Tcm4TlvDq8ikWAM',
        'personality': 'Visionary, perfectionist, innovative'
    },
    'hephaestus': {
        'name': 'Hephaestus Forge',
        'role': 'Chief Technology Officer',
        'voice_id': 'pNInz6obpgDQGcFmaJgB',
        'personality': 'Pragmatic, technical, problem-solver'
    },
    'athena': {
        'name': 'Athena Sophros',
        'role': 'Chief Knowledge Officer',
        'voice_id': 'onwK4e9ZLuTAKqWW03F9',
        'personality': 'Analytical, methodical, encyclopedic'
    }
}

def route_to_agent(message, topic):
    """Route message to appropriate agent based on content"""
    message_lower = message.lower()
    
    # Simple keyword-based routing
    if any(word in message_lower for word in ['marketing', 'brand', 'campaign', 'audience']):
        return 'aurora'
    elif any(word in message_lower for word in ['design', 'ui', 'ux', 'interface', 'visual']):
        return 'helios'
    elif any(word in message_lower for word in ['tech', 'code', 'api', 'backend', 'infrastructure']):
        return 'hephaestus'
    elif any(word in message_lower for word in ['data', 'analysis', 'research', 'knowledge']):
        return 'athena'
    else:
        return 'elara'  # Default to CEO

def generate_response(agent_id, message, topic):
    """Generate AI response for agent"""
    agent = AGENTS[agent_id]
    
    system_prompt = f"""You are {agent['name']}, {agent['role']} at Sentient Sphere Technologies.
Your personality: {agent['personality']}

The meeting topic is: {topic}

Respond professionally and concisely (2-3 sentences max) from your role's perspective.
Be helpful, insightful, and stay in character."""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Extract data
            message = data.get('message', '')
            topic = data.get('topic', 'General Discussion')
            
            # Route to agent
            agent_id = route_to_agent(message, topic)
            agent = AGENTS[agent_id]
            
            # Generate response
            response_text = generate_response(agent_id, message, topic)
            
            # Prepare response
            response_data = {
                'agent': {
                    'id': agent_id,
                    'name': agent['name'],
                    'role': agent['role'],
                    'voice_id': agent['voice_id']
                },
                'message': response_text,
                'timestamp': None  # Will be set by frontend
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
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

