import os
import json
import random
import telebot
from groq import Groq
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
client = Groq(api_key=GROQ_API_KEY)

def carregar_produtos():
    try:
        with open('produtos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar produtos: {e}")
        return []

PRODUTOS = carregar_produtos()

PROMPT_SISTEMA = """Você é a copywriter oficial da marca 'Linne Indica'.

Tom: sofisticado, informal, elegante. Como uma amiga que faz curadoria de achados.

REGRAS OBRIGATÓRIAS:
1. Máximo 4 linhas no total
2. Máximo 300 caracteres (sem contar o link)
3. Máximo 2 emojis por post
4. NUNCA comece duas legendas com a mesma frase
5. NUNCA use: imperdível, corre, últimas unidades, oferta
6. Link sempre na última linha, precedido de 🛍️ Confira aqui:
7. Formato: abertura + 1 linha de benefício + link
"""

ANGULOS = [
    "Curiosidade — comece gerando surpresa sobre o produto",
    "Sensação — descreva como ele transforma o ambiente ou a rotina",
    "Problema — mencione uma dor comum que esse produto resolve",
    "Estética — foque no visual e no aspecto sofisticado",
    "Rotina — mostre como ele torna o dia a dia mais prático"
]

def gerar_legenda(nome_produto, link_produto):
    angulo = random.choice(ANGULOS)

    prompt = (
        f"Escreva a copy para: {angulo}\n\n"
        f"Produto: {nome_produto}\n"
        f"Link: {link_produto}\n\n"
        f"Fale SOMENTE sobre este produto."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return f"✨ Olha esse achado! {nome_produto}\n\n🔗 {link_produto}"

def postar_automatico():
    try:
        print("🚀 Iniciando post automático...")

        produto = random.choice(PRODUTOS)

        print(f"📦 Produto escolhido: {produto['nome']}")

        legenda = gerar_legenda(
            produto['nome'],
            produto['link']
        )

        bot.send_message(CHANNEL_ID, legenda)

        print("✅ Post realizado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao postar automaticamente: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Bot ativo! Me manda:\n\nNome do produto\nhttps://link-shopee.com.br"
    )

@bot.message_handler(commands=['postar'])
def postar_agora(message):
    bot.reply_to(message, "⏳ Postando agora...")
    postar_automatico()

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    texto = message.text
    linhas = texto.strip().split('\n')

    if len(linhas) >= 2 and 'shopee' in linhas[-1].lower():

        nome = linhas[0].strip()
        link = linhas[-1].strip()

        bot.reply_to(
            message,
            "⏳ Gerando legenda premium..."
        )

        legenda = gerar_legenda(nome, link)

        bot.send_message(CHANNEL_ID, legenda)

        bot.reply_to(
            message,
            f"✅ Postado!\n\nProduto: {nome}"
        )

    else:
        bot.reply_to(
            message,
            "Mande assim:\n\nNome do produto\nhttps://link-shopee.com.br"
        )

scheduler = BackgroundScheduler()

scheduler.add_job(postar_automatico, 'cron', hour=9, minute=0)
scheduler.add_job(postar_automatico, 'cron', hour=12, minute=0)
scheduler.add_job(postar_automatico, 'cron', hour=18, minute=0)
scheduler.add_job(postar_automatico, 'cron', hour=21, minute=0)

scheduler.start()

print("✅ Bot iniciado com agendamento automático!")
print("⏰ Posts agendados: 09:00, 12:00, 18:00 e 21:00")

while True:
    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60,
            skip_pending=True
        )
    except Exception as e:
        print(f"❌ Erro no polling, reconectando em 5s: {e}")
        import time
        time.sleep(5)
