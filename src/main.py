#!/usr/bin/env python3
"""
Backend API - STAFF AI Meeting Room
FastAPI + WebSocket para reuniões em tempo real
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from voice_service import generate_agent_audio

# Adicionar path do projeto principal
sys.path.append('/home/ubuntu/elara_production')
from agent_communication import AgentCommunicationHub

# Configuração
app = FastAPI(title="STAFF AI Meeting Room API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente OpenAI
client = OpenAI()

# Hub de comunicação
hub = AgentCommunicationHub()

# Gerenciador de conexões WebSocket
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
        if session_id in self.meeting_sessions:
            del self.meeting_sessions[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast(self, session_id: str, message: dict):
        await self.send_message(session_id, message)

manager = ConnectionManager()

# Modelos
class MeetingStart(BaseModel):
    user_name: str
    topic: str
    session_id: str

class ChatMessage(BaseModel):
    session_id: str
    from_user: str
    content: str

# Configuração dos agentes
AGENTS_CONFIG = {
    "elara": {
        "name": "Elara Veyra",
        "role": "CEO & Chief of Staff",
        "personality": "Estratégica, decisiva, visionária. Lidera com empatia e dados. Tom executivo e inspirador.",
        "voice_id": "XrExE9yKIg1WjnnlVkGX"
    },
    "aurora": {
        "name": "Aurora Castellane",
        "role": "Chief Marketing Officer",
        "personality": "Criativa, analítica, orientada a resultados. Domina storytelling e growth hacking. Tom envolvente e persuasivo.",
        "voice_id": "FGY2WhTYpPnrIDTdsKH5"
    },
    "helios": {
        "name": "Helios Vanterre",
        "role": "Chief Design Officer",
        "personality": "Visionário, perfeccionista, inovador. Obsessivo por detalhes e estética. Tom inspirador e criativo.",
        "voice_id": "2EiwWnXFnvU5JabPnv8n"
    },
    "hephaestus": {
        "name": "Hephaestus Forge",
        "role": "Chief Technology Officer",
        "personality": "Pragmático, técnico, solucionador. Arquitecta sistemas robustos e escaláveis. Tom analítico e preciso.",
        "voice_id": "CwhRBWXzGAHq8TQ4Fs17"
    },
    "athena": {
        "name": "Athena Sophros",
        "role": "Chief Knowledge Officer",
        "personality": "Analítica, metódica, enciclopédica. Transforma dados em insights accionáveis. Tom claro e objetivo.",
        "voice_id": "Xb7hH8MSUJpSbSDYk0k2"
    }
}

async def get_agent_response(
    agent_id: str,
    context: str,
    topic: str,
    conversation_history: List[dict],
    user_name: str
) -> str:
    """Gerar resposta de um agente usando IA"""
    
    agent = AGENTS_CONFIG.get(agent_id)
    if not agent:
        return f"Erro: Agente {agent_id} não encontrado"
    
    # Construir histórico
    history_text = ""
    if conversation_history:
        history_text = "\n\nCONTEXTO DA CONVERSA:\n"
        for msg in conversation_history[-6:]:
            speaker = msg.get('from_name', msg.get('from', 'Desconhecido'))
            content = msg.get('content', '')[:150]
            history_text += f"- {speaker}: {content}...\n"
    
    # Prompt do sistema
    system_prompt = f"""Você é {agent['name']}, {agent['role']} da Sentient Sphere Technologies.

PERSONALIDADE E TOM: {agent['personality']}

CONTEXTO DA REUNIÃO:
- Tópico: {topic}
- Participante: {user_name}
- Você está numa reunião executiva profissional

INSTRUÇÕES CRÍTICAS:
- Responda em português de Portugal
- Máximo 120 palavras (seja conciso e direto)
- Mantenha tom profissional mas acessível
- Contribua com insights específicos da sua área de expertise
- Seja colaborativo e construtivo
- Use dados e exemplos quando relevante
- Evite repetir o que outros já disseram

{history_text}

{context}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            max_tokens=250,
            temperature=0.8,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return f"Desculpe, {user_name}, estou a ter dificuldades técnicas. Pode repetir?"

# Endpoints HTTP
@app.get("/")
async def root():
    return {
        "service": "STAFF AI Meeting Room API",
        "version": "1.0.0",
        "status": "operational",
        "agents": len(AGENTS_CONFIG)
    }

@app.get("/agents")
async def get_agents():
    """Listar agentes disponíveis"""
    return {
        "agents": [
            {
                "id": agent_id,
                "name": config["name"],
                "role": config["role"],
                "voice_id": config["voice_id"]
            }
            for agent_id, config in AGENTS_CONFIG.items()
        ]
    }

@app.post("/meeting/start")
async def start_meeting(meeting: MeetingStart):
    """Iniciar nova reunião"""
    
    session_id = meeting.session_id
    user_name = meeting.user_name
    topic = meeting.topic
    
    # Criar sessão
    thread_id = f"meeting_{session_id}"
    manager.meeting_sessions[session_id] = {
        "thread_id": thread_id,
        "user_name": user_name,
        "topic": topic,
        "started_at": datetime.now().isoformat(),
        "conversation_history": []
    }
    
    # Mensagem de abertura da Elara
    opening = await get_agent_response(
        agent_id="elara",
        context=f"Abra a reunião de forma profissional e calorosa. Apresente-se brevemente e convide {user_name} a partilhar suas ideias sobre {topic}.",
        topic=topic,
        conversation_history=[],
        user_name=user_name
    )
    
    # Guardar na memória
    hub.send_message(
        from_agent="Elara Veyra",
        to_agent="all",
        content=opening,
        message_type="opening",
        thread_id=thread_id
    )
    
    manager.meeting_sessions[session_id]["conversation_history"].append({
        "from": "elara",
        "from_name": "Elara Veyra",
        "content": opening,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "session_id": session_id,
        "thread_id": thread_id,
        "opening_message": opening,
        "agents": list(AGENTS_CONFIG.keys())
    }

# WebSocket para chat em tempo real
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            content = data.get("content", "")
            user_name = data.get("user_name", "Participante")
            
            # Obter sessão
            session = manager.meeting_sessions.get(session_id)
            if not session:
                await websocket.send_json({
                    "type": "error",
                    "content": "Sessão não encontrada"
                })
                continue
            
            topic = session["topic"]
            conversation_history = session["conversation_history"]
            
            # Adicionar mensagem do utilizador ao histórico
            conversation_history.append({
                "from": "user",
                "from_name": user_name,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            # Guardar na memória
            hub.send_message(
                from_agent=user_name,
                to_agent="all",
                content=content,
                message_type="user_message",
                thread_id=session["thread_id"]
            )
            
            # Determinar qual agente deve responder
            # Por padrão, Elara responde e pode convocar outros
            responding_agent = "elara"
            
            # Lógica simples: se mencionar área específica, agente relevante responde
            content_lower = content.lower()
            if any(word in content_lower for word in ["marketing", "mercado", "campanha", "clientes"]):
                responding_agent = "aurora"
            elif any(word in content_lower for word in ["design", "visual", "interface", "ux", "ui"]):
                responding_agent = "helios"
            elif any(word in content_lower for word in ["técnico", "tecnologia", "sistema", "código", "arquitetura"]):
                responding_agent = "hephaestus"
            elif any(word in content_lower for word in ["dados", "análise", "métricas", "números", "estatística"]):
                responding_agent = "athena"
            
            # Gerar resposta
            agent_config = AGENTS_CONFIG[responding_agent]
            
            response = await get_agent_response(
                agent_id=responding_agent,
                context=f"{user_name} disse: \"{content}\"\n\nResponda de forma relevante e acrescente valor à discussão.",
                topic=topic,
                conversation_history=conversation_history,
                user_name=user_name
            )
            
            # Adicionar resposta ao histórico
            conversation_history.append({
                "from": responding_agent,
                "from_name": agent_config["name"],
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Guardar na memória
            hub.send_message(
                from_agent=agent_config["name"],
                to_agent=user_name,
                content=response,
                message_type="agent_response",
                thread_id=session["thread_id"]
            )
            
            # Gerar áudio da resposta
            audio_base64 = generate_agent_audio(
                responding_agent,
                response,
                os.getenv("ELEVENLABS_API_KEY")
            )
            
            # Enviar resposta ao cliente
            await manager.send_message(session_id, {
                "type": "agent_message",
                "from": responding_agent,
                "from_name": agent_config["name"],
                "role": agent_config["role"],
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "voice_id": agent_config["voice_id"],
                "audio": audio_base64
            })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Cliente {session_id} desconectado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

