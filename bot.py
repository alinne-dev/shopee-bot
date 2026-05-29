import os
import telebot
import schedule
import time
import threading
import requests
import random
from urllib.parse import unquote
from groq import Groq

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
MEU_ID = 6688691337

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

PROMPT_SISTEMA = """Você é a copywriter oficial da marca 'Linne Indica'.
Seu tom de voz é de uma criadora de conteúdo de beleza e estética sofisticada, falando de forma informal, mas muito elegante com suas seguidoras.
O seu nicho é 'Achadinhos que parecem caros'.

REGRAS ABSOLUTAS:
1. NUNCA use termos bregas como 'OFERTA IMPERDÍVEL', 'Economize grande', 'Compre agora mesmo' ou excesso de caixa alta.
2. Você DEVE citar o nome exato do produto recebido no primeiro parágrafo. NUNCA invente ou substitua o produto por outro.
3. A copy deve ser natural, parecendo uma mensagem de WhatsApp de uma amiga que encontrou algo incrível.
4. Não use listas genéricas de características técnicas. Venda o DESEJO, a estética e o resultado do produto.
5. O texto deve ser curto (máximo de 3 parágrafos pequenos).
6. Posicione o link do produto de forma clara no final da mensagem."""

ANGULOS_DE_VENDA = [
    "Foco em estética premium. Use um tom de 'segredo entre amigas' sobre um produto que parece caro, mas é super acessível.",
    "Foco na escassez inteligente. Comente de forma elegante que o estoque na Shopee costuma esgotar rápido para produtos desse nível.",
    "Foco no custo-benefício. Destaque como essa é uma compra inteligente para quem gosta de se cuidar sem rasgar dinheiro.",
    "Foco em resenha rápida. Haja como se tivesse testado e aprovado a qualidade do produto."
]

def decodificar_link_shopee(url_curta):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url_curta, headers=headers, allow_redirects=True, timeout=10)
        url_real = response.url
        if "-i." in url_real:
            slug = url_real.split("/")[-1].split("-i.")[0]
            nome_produto = unquote(slug).replace("-", " ")
            return nome_produto, url_real
        elif "product/" in url_real:
            return "Achadinho especial", url_real
        return "Produto especial", url_real
    except Exception as e:
        print(f"Erro ao decodificar link: {e}")
        return "Produto", url_curta

def buscar_produtos():
    url = "https://shopee.com.br/api/v4/search/search_items/?by=sales&limit=5&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
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
            
            # Puxa o ID da imagem direto do banco de dados da Shopee
            imagem_id = info.get("image")
            url_foto = f"https://down-br.img.sstd.com/photo/{imagem_id}" if imagem_id else None
            
            produtos.append({"nome": nome, "link": link, "foto": url_foto})
        return produtos
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        return []

def gerar_legenda(nome_produto, link_produto):
    angulo_escolhido = random.choice(ANGULOS_DE_VENDA)
    prompt_usuario = f"Escreva a copy para este produto específico. {angulo_escolhido}\n\nProduto: {nome_produto}\nLink: {link_produto}\n\nLembre-se: fale SOMENTE sobre o produto acima, nunca substitua por outro."
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na API Groq: {e}")
        return f"✨ Olha que achado incrível! {nome_produto} por um preço que você não vai acreditar.\n\n🔗 {link_produto}"

def postar_automatico():
    produtos = buscar_produtos()
    if produtos:
        produto = produtos[0]
        legenda = gerar_legenda(produto['nome'], produto['link'])
        
        # Posta a foto real com a legenda fina da Groq acoplada. Se falhar, manda texto.
        if produto.get('foto'):
            bot.send_photo(CHANNEL_ID, produto['foto'], caption=legenda)
        else:
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
    bot.reply_to(message, "Bot ativo! Me manda o nome e link do produto Shopee ou aguarde os posts automáticos!")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    texto = message.text
    linhas = texto.strip().split('\n')
    
    if len(linhas) >= 2 and 'shopee' in linhas[-1].lower():
        nome_produto = linhas[0].strip()
        link = linhas[-1].strip()
        bot.reply_to(message, "⏳ Gerando legenda premium...")
        legenda = gerar_legenda(nome_produto, link)
        bot.send_message(CHANNEL_ID, legenda)
        bot.reply_to(message, f"✅ Postado no canal!\n\nProduto: {nome_produto}")
        
    elif 'shopee' in texto.lower():
        bot.reply_to(message, "⏳ Identificando produto e gerando legenda premium...")
        nome_produto, url_real = decodificar_link_shopee(texto)
        legenda = gerar_legenda(nome_produto, texto)
        bot.send_message(CHANNEL_ID, legenda)
        bot.reply_to(message, f"✅ Postado no canal!\n\nProduto identificado: {nome_produto}")
        
    else:
        bot.reply_to(message, "Por favor, mande assim:\n\nNome do produto\nhttps://link-shopee.com.br")

agendador = threading.Thread(target=agendar_posts)
agendador.daemon = True
agendador.start()

bot.polling()
