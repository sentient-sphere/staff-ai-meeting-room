#!/usr/bin/env python3
"""
Voice Service - ElevenLabs Integration
Síntese de voz para os agentes do STAFF AI
"""

import os
import requests
import base64
from typing import Optional

# API Key do ElevenLabs (configurar via env var)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

class VoiceService:
    """Serviço de síntese de voz usando ElevenLabs"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> Optional[bytes]:
        """
        Converter texto em áudio usando ElevenLabs
        
        Args:
            text: Texto para converter
            voice_id: ID da voz do ElevenLabs
            model_id: Modelo a usar (eleven_multilingual_v2 suporta português)
            stability: Estabilidade da voz (0-1)
            similarity_boost: Similaridade com voz original (0-1)
            style: Estilo/expressividade (0-1)
            use_speaker_boost: Melhorar clareza
            
        Returns:
            Bytes do áudio MP3 ou None se falhar
        """
        
        if not self.api_key:
            print("⚠️  ELEVENLABS_API_KEY não configurada")
            return None
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ Erro ElevenLabs: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao chamar ElevenLabs: {e}")
            return None
    
    def text_to_speech_base64(
        self,
        text: str,
        voice_id: str,
        **kwargs
    ) -> Optional[str]:
        """
        Converter texto em áudio e retornar como base64
        Útil para enviar via WebSocket/JSON
        """
        
        audio_bytes = self.text_to_speech(text, voice_id, **kwargs)
        
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode('utf-8')
        return None
    
    def get_available_voices(self) -> list:
        """Listar vozes disponíveis"""
        
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("voices", [])
            return []
        except Exception as e:
            print(f"Erro ao listar vozes: {e}")
            return []

# Configuração das vozes dos agentes
AGENT_VOICES = {
    "elara": {
        "voice_id": "XrExE9yKIg1WjnnlVkGX",  # Matilda
        "name": "Matilda",
        "settings": {
            "stability": 0.6,
            "similarity_boost": 0.8,
            "style": 0.3,  # Leve expressividade
            "use_speaker_boost": True
        }
    },
    "aurora": {
        "voice_id": "FGY2WhTYpPnrIDTdsKH5",  # Laura
        "name": "Laura",
        "settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,  # Mais expressiva
            "use_speaker_boost": True
        }
    },
    "helios": {
        "voice_id": "2EiwWnXFnvU5JabPnv8n",  # Clyde
        "name": "Clyde",
        "settings": {
            "stability": 0.7,
            "similarity_boost": 0.7,
            "style": 0.2,  # Mais estável
            "use_speaker_boost": True
        }
    },
    "hephaestus": {
        "voice_id": "CwhRBWXzGAHq8TQ4Fs17",  # Roger
        "name": "Roger",
        "settings": {
            "stability": 0.8,
            "similarity_boost": 0.6,
            "style": 0.1,  # Muito estável (técnico)
            "use_speaker_boost": True
        }
    },
    "athena": {
        "voice_id": "Xb7hH8MSUJpSbSDYk0k2",  # Alice
        "name": "Alice",
        "settings": {
            "stability": 0.7,
            "similarity_boost": 0.75,
            "style": 0.2,  # Clara e objetiva
            "use_speaker_boost": True
        }
    }
}

def generate_agent_audio(agent_id: str, text: str, api_key: str = None) -> Optional[str]:
    """
    Gerar áudio para um agente específico
    
    Args:
        agent_id: ID do agente (elara, aurora, helios, hephaestus, athena)
        text: Texto para sintetizar
        api_key: API key do ElevenLabs (opcional)
        
    Returns:
        Áudio em base64 ou None
    """
    
    voice_config = AGENT_VOICES.get(agent_id)
    if not voice_config:
        print(f"⚠️  Agente {agent_id} não tem voz configurada")
        return None
    
    service = VoiceService(api_key)
    
    return service.text_to_speech_base64(
        text=text,
        voice_id=voice_config["voice_id"],
        **voice_config["settings"]
    )

# Teste
if __name__ == "__main__":
    print("🎤 Teste de Voice Service")
    print("=" * 50)
    
    # Verificar API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("⚠️  ELEVENLABS_API_KEY não configurada")
        print("   Configure com: export ELEVENLABS_API_KEY='sua_chave'")
        exit(1)
    
    service = VoiceService(api_key)
    
    # Testar com Elara
    print("\n🗣️  Testando voz de Elara...")
    text = "Olá! Sou Elara Veyra, CEO da Sentient Sphere Technologies. É um prazer conhecê-lo!"
    
    audio_base64 = generate_agent_audio("elara", text, api_key)
    
    if audio_base64:
        print(f"✅ Áudio gerado com sucesso!")
        print(f"   Tamanho: {len(audio_base64)} caracteres (base64)")
        
        # Salvar para teste
        audio_bytes = base64.b64decode(audio_base64)
        with open("/tmp/elara_test.mp3", "wb") as f:
            f.write(audio_bytes)
        print(f"   Salvo em: /tmp/elara_test.mp3")
    else:
        print("❌ Falha ao gerar áudio")

