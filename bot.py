import os
import telebot
import schedule
import time
import threading
import requests
import random
import re
from urllib.parse import urlparse, urlunparse
from groq import Groq

# Configurações
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
MEU_ID = 6688691337

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

def limpar_link(url):
    """Limpa o link de afiliados para evitar bloqueios e ajudar no preview"""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def gerar_legenda(link):
    """Gera a copy sofisticada mesmo sem o nome técnico, focada na estética"""
    prompt = f"Escreva uma legenda curta (máx 3 parágrafos) para um achadinho na Shopee. Tom: Linne Indica (sofisticada, elegante, segredo entre amigas). O link é: {link}"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Você é uma curadora de estilo."}, {"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except:
        return f"✨ Achei este achadinho maravilhoso! Perfeito e acessível: {link}"

@bot.message_handler(func=lambda message: 'shopee' in message.text.lower())
def handle_link(message):
    # O bot processa tudo sozinho
    link_limpo = limpar_link(message.text)
    legenda = gerar_legenda(link_limpo)
    
    # Envia a legenda com o link limpo no final para forçar o preview da imagem
    bot.send_message(CHANNEL_ID, f"{legenda}\n\n{link_limpo}")
    bot.reply_to(message, "✅ Postado automaticamente!")

# Mantém o polling
if __name__ == "__main__":
    bot.polling()
