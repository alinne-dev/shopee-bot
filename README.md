# 🤖 Bot de Curadoria Inteligente (Telegram)

Sistema de curadoria automatizada para o nicho de beleza e afiliados. O bot gerencia uma base de dados de produtos e realiza postagens agendadas de forma orgânica no Telegram, utilizando Inteligência Artificial para gerar conteúdo natural e focado em conversão.

> **Status:** 🟢 Em produção (Deploy ativo) | **[Clique aqui para ver o Bot em ação no Canal](https://t.me/ofertasinteligentesag)**

## 📸 Demonstração

<div align="center">
  <img width="373" height="606" alt="Chat com o Bot" src="https://github.com/user-attachments/assets/71e23b3d-4ddf-462d-9ff6-7c42b9c0c0ce" />
  <img width="379" height="658" alt="Post no Canal" src="https://github.com/user-attachments/assets/a4fffbfb-d18c-4f76-9f32-eaf877a4c6fd" />
</div>

## 🚀 O que este projeto faz
- **Gestão de Curadoria:** Processa uma lista de produtos estruturada em `produtos.json`, garantindo que o feed esteja sempre atualizado.
- **Automação Estratégica:** Realiza postagens agendadas em horários de pico, maximizando o engajamento.
- **IA de Conteúdo:** Utiliza a API da Groq para gerar legendas coloquiais e naturais, focadas em "indicação de amiga" em vez de vendas agressivas.
- **Infraestrutura Resiliente:** Sistema executado em container com lógica de reconexão automática e tratamento robusto de erros de API.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python
- **Integrações:** API do Bot do Telegram, API de IA (Groq)
- **Infraestrutura:** Deploy em nuvem (Railway)
- **Formato de dados:** JSON

## ⚙️ Como executar o projeto localmente
Para rodar este projeto na sua máquina, siga os passos abaixo:

1. Clone o repositório:
   ```bash
   git clone https://github.com/alInne-dev/shopee-bot.git
   
