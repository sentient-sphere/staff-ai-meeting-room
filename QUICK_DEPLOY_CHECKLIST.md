# ⚡ Quick Deploy Checklist - STAFF AI

## ✅ Pré-requisitos (COMPLETO)
- [x] Código desenvolvido e testado
- [x] Frontend React construído
- [x] Backend FastAPI funcional
- [x] Git inicializado
- [x] .gitignore configurado
- [x] README.md criado
- [x] render.yaml configurado

## 🔄 Aguardando

### 1. Criar Repositório GitHub
- [ ] Acesse: https://github.com/new
- [ ] Nome: `staff-ai-meeting-room`
- [ ] Visibilidade: Public
- [ ] NÃO inicializar com arquivos
- [ ] Copiar URL do repositório

### 2. Push para GitHub (Automático)
```bash
# Será executado automaticamente após fornecer a URL
./push_to_github.sh <URL_DO_REPO>
```

### 3. Deploy no Render.com
- [ ] Acesse: https://dashboard.render.com/
- [ ] New + → Web Service
- [ ] Conectar repositório GitHub
- [ ] Configurar variáveis de ambiente:
  - `OPENAI_API_KEY`
  - `ELEVENLABS_API_KEY`
- [ ] Create Web Service

### 4. Teste Final
- [ ] Acessar URL pública
- [ ] Login com senha: `STAFF2025`
- [ ] Iniciar reunião
- [ ] Testar chat com agentes
- [ ] Verificar síntese de voz

## 🎯 Tempo Estimado
- Push GitHub: < 1 minuto
- Deploy Render: 3-5 minutos
- **TOTAL: ~5 minutos** ⚡

## 🔑 Credenciais Necessárias
- OpenAI API Key (já disponível)
- ElevenLabs API Key (já disponível)

---

**PRONTO PARA DEPLOYMENT!** 🚀

