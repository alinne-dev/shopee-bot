import os
import telebot
import schedule
import time
import threading
import requests
from groq import Groq

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

def buscar_produtos():
    url = "https://shopee.com.br/api/v4/search/search_items/?by=sales&limit=5&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://shopee.com.br/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        items = data.get("items", [])
        produtos = []
        for item in items[:5]:
            info = item.get("item_basic", {})
            nome = info.get("name", "Produto")
            itemid = info.get("itemid")
            shopid = info.get("shopid")
            link = f"https://shopee.com.br/product/{shopid}/{itemid}"
            produtos.append({"nome": nome, "link": link})
        return produtos
    except:
        return []

def gerar_legenda(produto):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"Crie uma legenda curta e atrativa para divulgar esse produto da Shopee como afiliado. Use emojis, destaque o desconto e coloque o link no final. Produto: {produto['nome']}. Link: {produto['link']}"
        }]
    )
    return response.choices[0].message.content

def postar_automatico():
    produtos = buscar_produtos()
    if produtos:
        produto = produtos[0]
        legenda = gerar_legenda(produto)
        bot.send_message(CHANNEL_ID, legenda)

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
    bot.reply_to(message, "Bot ativo! Me manda o link do produto Shopee ou aguarde os posts automáticos!")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    link = message.text
    if 'shopee' in link.lower():
        bot.reply_to(message, "⏳ Gerando legenda...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Crie uma legenda curta e atrativa para divulgar esse produto da Shopee como afiliado. Use emojis, destaque o desconto e coloque o link no final. Link: {link}"
            }]
        )
        legenda = response.choices[0].message.content
        bot.send_message(CHANNEL_ID, legenda)
        bot.reply_to(message, "✅ Postado no canal!")
    else:
        bot.reply_to(message, "Por favor, manda um link da Shopee!")

agendador = threading.Thread(target=agendar_posts)
agendador.daemon = True
agendador.start()

bot.polling()
