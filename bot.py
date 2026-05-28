import os
import telebot
import schedule
import time
import threading
import requests
import random
from groq import Groq

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
MEU_ID = 6688691337

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# DNA da Marca centralizado - Princípio DRY para manter o código limpo
PROMPT_SISTEMA = """Você é a copywriter oficial da marca 'Linne Indica'.
Seu tom de voz é de uma criadora de conteúdo de beleza e estética sofisticada, falando de forma informal, mas muito elegante com suas seguidoras.
O seu nicho é 'Achadinhos que parecem caros'.

REGRAS ABSOLUTAS:
1. NUNCA use termos bregas como 'OFERTA IMPERDÍVEL', 'Economize grande', 'Compre agora mesmo' ou excesso de caixa alta.
2. A copy deve ser natural, parecendo uma mensagem de WhatsApp de uma amiga que encontrou algo incrível.
3. Não use listas genéricas de características técnicas. Venda o DESEJO e o resultado.
4. O texto deve ser curto (máximo de 3 parágrafos pequenos).
5. Posicione o link do produto de forma clara no final da mensagem."""

# Variações para evitar banner blindness no seu canal
ANGULOS_DE_VENDA = [
    "Foco em estética premium. Use um tom de 'segredo entre amigas' sobre um produto que parece caro, mas é super acessível.",
    "Foco na escassez inteligente. Comente de forma elegante que o estoque na Shopee costuma esgotar rápido para produtos desse nível.",
    "Foco no custo-benefício. Destaque como essa é uma compra inteligente para quem gosta de se cuidar sem rasgar dinheiro.",
    "Foco em resenha rápida. Haja como se tivesse testado (ou visto muita gente testar) e aprovado a qualidade do produto."
]

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
    angulo_escolhido = random.choice(ANGULOS_DE_VENDA)
    prompt_usuario = f"Escreva a copy para este produto. {angulo_escolhido}\n\nProduto: {produto['nome']}\nLink: {produto['link']}"
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.7 # Temperatura ajustada para maior criatividade
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na API Groq: {e}")
        # Fallback elegante caso a IA falhe
        return f"✨ Achadinho de luxo detectado! Olha que perfeito que eu encontrei para vocês. O custo-benefício tá surreal.\n\n🔗 Link direto: {produto['link']}"

def postar_automatico():
    produtos = buscar_produtos()
    if produtos:
        produto = produtos[0]
        legenda = gerar_legenda(produto)
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
    bot.reply_to(message, "Bot ativo! Me manda o link do produto Shopee ou aguarde os posts automáticos!")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    link = message.text
    if 'shopee' in link.lower():
        bot.reply_to(message, "⏳ Analisando produto e gerando legenda premium...")
        
        angulo_escolhido = random.choice(ANGULOS_DE_VENDA)
        prompt_usuario = f"Escreva a copy para este link de produto. {angulo_escolhido}\n\nLink: {link}"
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.7
            )
            legenda = response.choices[0].message.content
            bot.send_message(CHANNEL_ID, legenda)
            bot.reply_to(message, "✅ Postado no canal com a copy atualizada!")
        except Exception as e:
            bot.reply_to(message, f"❌ Falha de conexão com a IA: {e}")
    else:
        bot.reply_to(message, "Por favor, mande um link válido da Shopee.")

agendador = threading.Thread(target=agendar_posts)
agendador.daemon = True
agendador.start()

bot.polling()
