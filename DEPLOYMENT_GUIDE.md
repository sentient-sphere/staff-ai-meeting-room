# 🚀 Guia de Deployment - STAFF AI Meeting Room

## Status Atual
✅ Código completo e funcional
✅ Frontend React construído (pasta static)
✅ Backend FastAPI pronto
✅ Git inicializado localmente
✅ render.yaml configurado

## Próximos Passos

### 1️⃣ Push para GitHub
```bash
# Adicionar remote (substitua pela URL real)
git remote add origin https://github.com/esfera-senciente/staff-ai-meeting-room.git

# Push do código
git push -u origin main
```

### 2️⃣ Configurar Render.com

1. **Acesse**: https://dashboard.render.com/
2. **Clique**: "New +" → "Web Service"
3. **Conecte**: Repositório GitHub `staff-ai-meeting-room`
4. **Configurações automáticas** (detectadas do render.yaml):
   - Name: `staff-ai-meeting-room`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/server.py`
   - Plan: `Free`

5. **Variáveis de Ambiente** (CRÍTICO):
   ```
   OPENAI_API_KEY=<sua_chave_openai>
   ELEVENLABS_API_KEY=<sua_chave_elevenlabs>
   PORT=5000
   ```

6. **Deploy**: Clique em "Create Web Service"

### 3️⃣ Aguardar Deploy
- Tempo estimado: 3-5 minutos
- Render irá:
  - Clonar repositório
  - Instalar dependências
  - Iniciar servidor
  - Gerar URL pública

### 4️⃣ Testar Aplicação
1. Acesse a URL fornecida pelo Render
2. Digite senha: `STAFF2025`
3. Inicie uma reunião
4. Teste chat com os 5 agentes

## 🔑 Credenciais Necessárias

### OpenAI API Key
- Console: https://platform.openai.com/api-keys
- Formato: `sk-...`

### ElevenLabs API Key
- Console: https://elevenlabs.io/app/settings/api-keys
- Formato: `...`

## 🎯 Agentes Configurados

1. **Elara Veyra** - CEO & Chief of Staff
2. **Aurora Castellane** - Chief Marketing Officer
3. **Helios Vanterre** - Chief Design Officer
4. **Hephaestus Forge** - Chief Technology Officer
5. **Athena Sophros** - Chief Knowledge Officer

## 📊 Arquitetura

```
Frontend (React) → Backend (FastAPI) → OpenAI GPT-4.1-mini
                                    → ElevenLabs Voice Synthesis
                                    → WebSocket (Real-time)
```

## 🔧 Troubleshooting

### Erro: "Application failed to start"
- Verificar variáveis de ambiente
- Verificar logs no Render dashboard

### Erro: "API key invalid"
- Verificar se as chaves estão corretas
- Verificar se as chaves têm créditos

### Erro: "WebSocket connection failed"
- Verificar se o servidor está rodando
- Verificar CORS settings

## 📝 Notas

- **Free tier** do Render: servidor hiberna após 15 min de inatividade
- **Cold start**: primeira requisição pode demorar 30-60s
- **Upgrade recomendado**: Plano Starter ($7/mês) para produção

---

© 2025 Sentient Sphere Technologies

