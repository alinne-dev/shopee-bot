import os
import json
import random
import telebot
from groq import Groq
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
MEU_ID = 6688691337

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

PROMPT_SISTEMA = """Você é a copywriter oficial da marca 'Linne Indica'.
Seu tom é sofisticado, informal e elegante.
Nicho: Achadinhos que parecem caros mas são acessíveis.

REGRAS:
1. NUNCA use 'OFERTA IMPERDÍVEL' ou termos bregas
2. Cite o nome exato do produto no primeiro parágrafo
3. Escreva como uma amiga recomendando algo incrível
4. Foque no desejo e resultado, não em especificações
5. Máximo 3 parágrafos curtos
6. Link sempre no final"""

ANGULOS = [
    "Foco em estética premium — 'segredo entre amigas'",
    "Foco em escassez — estoque costuma esgotar rápido",
    "Foco em custo-benefício — compra inteligente",
    "Foco em resenha — como se tivesse testado",
]

def carregar_produtos():
    try:
        with open("produtos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        return []

def gerar_legenda(nome_produto, link_produto):
    angulo = random.choice(ANGULOS)
    prompt = (f"Escreva a copy para: {angulo}\n\n"
              f"Produto: {nome_produto}\nLink: {link_produto}\n\n"
              f"Fale SOMENTE sobre este produto.")
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
        print(f"Erro na IA: {e}")
        return f"✨ Olha esse achado! {nome_produto}\n\n🔗 {link_produto}"

def postar_automatico():
    print("Iniciando post automático...")
    produtos = carregar_produtos()
    if produtos:
        produto = random.choice(produtos)
        print(f"Produto escolhido: {produto['nome']}")
        legenda = gerar_legenda(produto['nome'], produto['link'])
        bot.send_message(CHANNEL_ID, legenda)
        bot.send_message(MEU_ID, f"✅ Post automático feito!\n\n{legenda}")
        print("Post realizado com sucesso!")
    else:
        print("Nenhum produto encontrado no JSON!")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ativo! Me manda:\n\nNome do produto\nhttps://link-shopee.com.br")

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
        bot.reply_to(message, "⏳ Gerando legenda premium...")
        legenda = gerar_legenda(nome, link)
        bot.send_message(CHANNEL_ID, legenda)
        bot.reply_to(message, f"✅ Postado!\n\nProduto: {nome}")
    else:
        bot.reply_to(message, "Mande assim:\n\nNome do produto\nhttps://link-shopee.com.br")

scheduler = BackgroundScheduler()
scheduler.add_job(postar_automatico, 'cron', hour=9, minute=0)
scheduler.add_job(postar_automatico, 'cron', hour=12, minute=0)
scheduler.add_job(postar_automatico, 'cron', hour=18, minute=0)
scheduler.add_job(postar_automatico, 'cron', hour=21, minute=0)
scheduler.start()

print("✅ Bot iniciado com agendamento automático!")
print("⏰ Posts agendados: 9h, 12h, 18h e 21h")

bot.infinity_polling()
