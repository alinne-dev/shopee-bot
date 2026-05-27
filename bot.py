import os
import telebot
from groq import Groq

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ativo! Me manda o link do produto Shopee!")

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

bot.polling()
