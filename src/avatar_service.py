#!/usr/bin/env python3
"""
Avatar Service - D-ID Integration
Geração de vídeos com avatares animados para os agentes
"""

import os
import requests
import time
from typing import Optional, Dict

# API Key do D-ID (configurar via env var)
DID_API_KEY = os.getenv("DID_API_KEY", "")

class AvatarService:
    """Serviço de geração de avatares animados usando D-ID"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DID_API_KEY
        self.base_url = "https://api.d-id.com"
        
    def create_talk(
        self,
        source_url: str,
        script_text: str = None,
        audio_url: str = None,
        voice_id: str = None,
        provider: str = "elevenlabs"
    ) -> Optional[Dict]:
        """
        Criar vídeo de avatar falando
        
        Args:
            source_url: URL da imagem do avatar
            script_text: Texto para o avatar falar (se não usar audio_url)
            audio_url: URL do áudio pré-gerado (alternativa a script_text)
            voice_id: ID da voz (ElevenLabs ou Microsoft)
            provider: Provedor de voz (elevenlabs, microsoft, amazon)
            
        Returns:
            Dict com id do vídeo e status
        """
        
        if not self.api_key:
            print("⚠️  DID_API_KEY não configurada")
            return None
        
        url = f"{self.base_url}/talks"
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configurar input de áudio
        if audio_url:
            script = {
                "type": "audio",
                "audio_url": audio_url
            }
        elif script_text and voice_id:
            script = {
                "type": "text",
                "input": script_text,
                "provider": {
                    "type": provider,
                    "voice_id": voice_id
                }
            }
        else:
            print("❌ Precisa fornecer audio_url OU (script_text + voice_id)")
            return None
        
        data = {
            "source_url": source_url,
            "script": script,
            "config": {
                "fluent": True,
                "pad_audio": 0.0,
                "stitch": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"❌ Erro D-ID: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao chamar D-ID: {e}")
            return None
    
    def get_talk_status(self, talk_id: str) -> Optional[Dict]:
        """Verificar status de um vídeo"""
        
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/talks/{talk_id}"
        headers = {"Authorization": f"Basic {self.api_key}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erro ao verificar status: {e}")
            return None
    
    def wait_for_video(self, talk_id: str, max_wait: int = 60) -> Optional[str]:
        """
        Aguardar vídeo ficar pronto e retornar URL
        
        Args:
            talk_id: ID do vídeo
            max_wait: Tempo máximo de espera em segundos
            
        Returns:
            URL do vídeo ou None
        """
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_talk_status(talk_id)
            
            if not status:
                return None
            
            if status.get("status") == "done":
                return status.get("result_url")
            elif status.get("status") == "error":
                print(f"❌ Erro na geração: {status.get('error')}")
                return None
            
            time.sleep(2)  # Aguardar 2 segundos antes de verificar novamente
        
        print("⏱️  Timeout aguardando vídeo")
        return None

# Configuração dos avatares dos agentes
AGENT_AVATARS = {
    "elara": {
        "image_url": "https://create-images-results.d-id.com/google-oauth2%7C117862926490962374265/upl_YMhbDRIYTNPbhOLcTCvqT/image.jpeg",
        "name": "Elara Veyra",
        "description": "CEO executiva, elegante, confiante"
    },
    "aurora": {
        "image_url": "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg",
        "name": "Aurora Castellane",
        "description": "CMO criativa, energética, carismática"
    },
    "helios": {
        "image_url": "https://create-images-results.d-id.com/DefaultPresenters/Eric_f/image.jpeg",
        "name": "Helios Vanterre",
        "description": "CDO visionário, moderno, artístico"
    },
    "hephaestus": {
        "image_url": "https://create-images-results.d-id.com/DefaultPresenters/James_f/image.jpeg",
        "name": "Hephaestus Forge",
        "description": "CTO técnico, focado, analítico"
    },
    "athena": {
        "image_url": "https://create-images-results.d-id.com/DefaultPresenters/Amy_f/image.jpeg",
        "name": "Athena Sophros",
        "description": "CKO inteligente, precisa, objetiva"
    }
}

def generate_agent_video(
    agent_id: str,
    text: str,
    audio_url: str = None,
    voice_id: str = None,
    api_key: str = None
) -> Optional[str]:
    """
    Gerar vídeo de avatar para um agente
    
    Args:
        agent_id: ID do agente (elara, aurora, helios, hephaestus, athena)
        text: Texto para o avatar falar
        audio_url: URL do áudio (opcional, se já tiver gerado)
        voice_id: ID da voz ElevenLabs (opcional)
        api_key: API key do D-ID
        
    Returns:
        URL do vídeo ou None
    """
    
    avatar_config = AGENT_AVATARS.get(agent_id)
    if not avatar_config:
        print(f"⚠️  Agente {agent_id} não tem avatar configurado")
        return None
    
    service = AvatarService(api_key)
    
    # Criar vídeo
    result = service.create_talk(
        source_url=avatar_config["image_url"],
        script_text=text if not audio_url else None,
        audio_url=audio_url,
        voice_id=voice_id,
        provider="elevenlabs"
    )
    
    if not result:
        return None
    
    talk_id = result.get("id")
    if not talk_id:
        return None
    
    print(f"🎬 Vídeo criado: {talk_id}")
    print(f"   Aguardando processamento...")
    
    # Aguardar vídeo ficar pronto
    video_url = service.wait_for_video(talk_id, max_wait=120)
    
    if video_url:
        print(f"✅ Vídeo pronto: {video_url}")
    
    return video_url

# Teste
if __name__ == "__main__":
    print("🎬 Teste de Avatar Service")
    print("=" * 50)
    
    # Verificar API key
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print("⚠️  DID_API_KEY não configurada")
        print("   Configure com: export DID_API_KEY='sua_chave'")
        exit(1)
    
    service = AvatarService(api_key)
    
    # Testar com Elara
    print("\n🎬 Testando avatar de Elara...")
    text = "Olá! Sou Elara Veyra, CEO da Sentient Sphere Technologies."
    
    video_url = generate_agent_video(
        "elara",
        text,
        voice_id="XrExE9yKIg1WjnnlVkGX",  # Voz da Elara no ElevenLabs
        api_key=api_key
    )
    
    if video_url:
        print(f"\n✅ Vídeo gerado com sucesso!")
        print(f"   URL: {video_url}")
    else:
        print("\n❌ Falha ao gerar vídeo")

