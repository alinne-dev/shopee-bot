import os
import telebot
import schedule
import time
import threading
import requests
import random
from urllib.parse import unquote
from groq import Groq

# Configurações do Ambiente
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
MEU_ID = 6688691337

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# DNA da Marca
PROMPT_SISTEMA = """Você é a copywriter oficial da marca 'Linne Indica'.
Seu tom de voz é de uma criadora de conteúdo de beleza e estética sofisticada, informal e elegante.
O seu nicho é 'Achadinhos que parecem caros'.

REGRAS ABSOLUTAS:
1. NUNCA use termos bregas como 'OFERTA IMPERDÍVEL', 'Compre agora' ou excesso de caixa alta.
2. Você DEVE citar o nome do produto no início do texto. O cliente precisa saber o que é.
3. A copy deve parecer uma mensagem de WhatsApp de uma amiga.
4. Venda o DESEJO e o resultado do produto.
5. Máximo de 3 parágrafos pequenos.
6. Link no final da mensagem."""

ANGULOS_DE_VENDA = [
    "Foco em estética premium e segredo entre amigas.",
    "Foco na escassez elegante (estoque costuma esgotar).",
    "Foco no custo-benefício inteligente.",
    "Foco em resenha rápida de qualidade."
]

def decodificar_link_shopee(url_curta):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url_curta, headers=headers, allow_redirects=True, timeout=10)
        url_real = response.url
        if "-i." in url_real:
            slug = url_real.split("/")[-1].split("-i.")[0]
            nome_produto = unquote(slug).replace("-", " ")
            return nome_produto, url_real
        return "Achadinho de beleza", url_real
    except:
        return "Achadinho de beleza", url_curta

def buscar_produtos():
    url = "https://shopee.com.br/api/v4/search/search_items/?by=sales&limit=5&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://shopee.com.br/"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        produtos = []
        for item in data.get("items", [])[:5]:
            info = item.get("item_basic", {})
            link = f"https://shopee.com.br/product/{info.get('shopid')}/{info.get('itemid')}"
            produtos.append({"nome": info.get("name", "Produto"), "link": link})
        return produtos
    except:
        return []

def gerar_legenda(nome_produto, link_produto):
    angulo_escolhido = random.choice(ANGULOS_DE_VENDA)
    prompt_usuario = (
        f"PRODUTO: {nome_produto}\n"
        f"LINK: {link_produto}\n"
        f"ANGULO: {angulo_escolhido}\n\n"
        f"REGRA OBRIGATÓRIA: Comece citando o NOME DO PRODUTO de forma natural. Não faça suspense."
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": PROMPT_SISTEMA}, {"role": "user", "content": prompt_usuario}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except:
        return f"✨ Achei esse {nome_produto} perfeito! Dá uma olhada: {link_produto}"

def postar_automatico():
    produtos = buscar_produtos()
    if produtos:
        prod = produtos[0]
        legenda = gerar_legenda(prod['nome'], prod['link'])
        bot.send_message(CHANNEL_ID, legenda)
        bot.send_message(MEU_ID, f"✅ Post automático feito!\n\n{legenda}")

def agendar_posts():
    schedule.every().day.at("09:00").do(postar_automatico)
    schedule.every().day.at("12:00").do(postar_automatico)
    schedule.every().day.at("18:00").do(postar_automatico)
    schedule.every().day.at("21:00").do(postar_automatico)
    while True:
        schedule.run_pending()
        time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ativo!")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    if 'shopee' in message.text.lower():
        bot.reply_to(message, "⏳ Processando...")
        nome, url = decodificar_link_shopee(message.text)
        legenda = gerar_legenda(nome, url)
        bot.send_message(CHANNEL_ID, legenda)
        bot.reply_to(message, f"✅ Postado! Identificado como: {nome}")

if __name__ == "__main__":
    threading.Thread(target=agendar_posts, daemon=True).start()
    bot.polling()
