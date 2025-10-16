#!/usr/bin/env python3
"""
STAFF AI Meeting Room - Servidor Unificado
FastAPI servindo frontend (React) + backend (API + WebSocket)
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

# Configuração
STATIC_DIR = "/home/ubuntu/meeting_room_app/src/static"

app = FastAPI(title="STAFF AI Meeting Room", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente OpenAI
client = OpenAI()

# Configuração dos agentes
AGENTS_CONFIG = {
    "elara": {
        "name": "Elara Veyra",
        "role": "CEO & Chief of Staff",
        "personality": "Estratégica, decisiva, visionária.",
        "voice_id": "EXAVITQu4vr4xnSDxMaL"
    },
    "aurora": {
        "name": "Aurora Castellane",
        "role": "Chief Marketing Officer",
        "personality": "Criativa, analítica, orientada a resultados.",
        "voice_id": "ThT5KcBeYPX3keUQqHPh"
    },
    "helios": {
        "name": "Helios Vanterre",
        "role": "Chief Design Officer",
        "personality": "Visionário, perfeccionista, inovador.",
        "voice_id": "21m00Tcm4TlvDq8ikWAM"
    },
    "hephaestus": {
        "name": "Hephaestus Forge",
        "role": "Chief Technology Officer",
        "personality": "Pragmático, técnico, solucionador.",
        "voice_id": "pNInz6obpgDQGcFmaJgB"
    },
    "athena": {
        "name": "Athena Sophros",
        "role": "Chief Knowledge Officer",
        "personality": "Analítica, metódica, enciclopédica.",
        "voice_id": "onwK4e9ZLuTAKqWW03F9"
    }
}

# Gerenciador de conexões
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.meeting_sessions: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

# Modelos
class MeetingStart(BaseModel):
    user_name: str
    topic: str
    session_id: str

async def get_agent_response(agent_id: str, context: str, topic: str, user_name: str) -> str:
    """Gerar resposta do agente"""
    agent = AGENTS_CONFIG[agent_id]
    
    system_prompt = f"""Você é {agent['name']}, {agent['role']}.
Personalidade: {agent['personality']}

Reunião sobre: {topic}
Participante: {user_name}

Responda em português de Portugal, de forma profissional e concisa (máximo 100 palavras)."""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            max_tokens=200,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Desculpe, estou com dificuldades técnicas. ({agent['name']})"

# API Endpoints
@app.post("/meeting/start")
async def start_meeting(meeting: MeetingStart):
    """Iniciar reunião"""
    session_id = meeting.session_id
    user_name = meeting.user_name
    topic = meeting.topic
    
    manager.meeting_sessions[session_id] = {
        "user_name": user_name,
        "topic": topic,
        "conversation_history": [],
        "started_at": datetime.now().isoformat()
    }
    
    opening = await get_agent_response(
        "elara",
        f"Abra a reunião de forma profissional. Apresente-se e convide {user_name} a partilhar ideias sobre {topic}.",
        topic,
        user_name
    )
    
    manager.meeting_sessions[session_id]["conversation_history"].append({
        "from": "elara",
        "from_name": "Elara Veyra",
        "content": opening
    })
    
    return {
        "session_id": session_id,
        "opening_message": opening
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket para chat em tempo real"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            content = data.get("content", "")
            user_name = data.get("user_name", "Participante")
            
            session = manager.meeting_sessions.get(session_id)
            if not session:
                await websocket.send_json({"type": "error", "content": "Sessão inválida"})
                continue
            
            # Determinar agente
            responding_agent = "elara"
            content_lower = content.lower()
            
            if any(w in content_lower for w in ["marketing", "mercado"]):
                responding_agent = "aurora"
            elif any(w in content_lower for w in ["design", "visual"]):
                responding_agent = "helios"
            elif any(w in content_lower for w in ["técnico", "tecnologia"]):
                responding_agent = "hephaestus"
            elif any(w in content_lower for w in ["dados", "análise"]):
                responding_agent = "athena"
            
            # Gerar resposta
            agent_config = AGENTS_CONFIG[responding_agent]
            response = await get_agent_response(
                responding_agent,
                f"{user_name} disse: \"{content}\"\n\nResponda de forma relevante.",
                session["topic"],
                user_name
            )
            
            # Enviar resposta
            await manager.send_message(session_id, {
                "type": "agent_message",
                "from": responding_agent,
                "from_name": agent_config["name"],
                "role": agent_config["role"],
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "voice_id": agent_config["voice_id"]
            })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)

# Servir frontend
@app.get("/api/health")
async def health():
    return {"status": "operational", "agents": len(AGENTS_CONFIG)}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Servir frontend React"""
    file_path = os.path.join(STATIC_DIR, full_path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # SPA routing - retornar index.html
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)

