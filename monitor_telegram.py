import asyncio
import re
import requests
import hashlib
import time
from telethon import TelegramClient, events

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

BOT_TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = 27139211

USAR_FILTRO_PRECO = False

CONJUNTOS = [
    ["bug"],
    ["corre"],
    ["corree"],
    ["correee"],
    ["correeee"],
    ["correeeee"],
    ["correeeeee"],
    ["correeeeeee"],
    ["correeeeeeee"],
    ["correeeeeeeee"],
    ["correeeeeeeeee"],
    ["correeeeeeeeeee"],
    ["correeeeeeeeeeee"],
    ["whey", "100%"],
    ["jordan"]
]

PRECOS_MAX = {
    "whey": 80,
    "creatina": 90,
    "pasta": 25
}

mensagens_processadas = set()

client = TelegramClient(
    "monitor",
    api_id,
    api_hash,
    connection_retries=10,
    retry_delay=5
)


def enviar_alerta(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Erro ao enviar alerta:", e)


def extrair_preco(texto):

    regex = r'(?:R\$|r\$)\s?\d+[.,]?\d*'

    match = re.search(regex, texto)

    if match:

        valor = match.group()

        valor = valor.replace("R$", "").replace("r$", "").strip()

        valor = valor.replace(",", ".")

        try:
            return float(valor)
        except:
            return None

    return None


# NORMALIZA TEXTO
def normalizar_texto(texto):

    texto = texto.lower()

    # remove emojis e pontuação
    texto = re.sub(r"[^\w\s%$]", " ", texto)

    # remove múltiplos espaços
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


# VERIFICA PALAVRAS EXATAS
def verificar_palavras(texto):

    texto = normalizar_texto(texto)

    palavras_texto = texto.split()

    for conjunto in CONJUNTOS:

        encontrou_todas = True

        for palavra in conjunto:

            palavra = palavra.lower()

            if palavra not in palavras_texto:
                encontrou_todas = False
                break

        if encontrou_todas:
            return conjunto

    return None


def gerar_hash_promocao(texto):

    texto = texto.lower().strip()

    texto = re.sub(r"\s+", " ", texto)

    return hashlib.md5(texto.encode()).hexdigest()


@client.on(events.NewMessage)
async def monitor(event):

    mensagem = event.raw_text

    if not mensagem:
        return

    promo_hash = gerar_hash_promocao(mensagem)

    if promo_hash in mensagens_processadas:
        return

    conjunto = verificar_palavras(mensagem)

    if not conjunto:
        return

    texto = mensagem.lower()

    preco = None

    if USAR_FILTRO_PRECO:

        preco = extrair_preco(mensagem)

        for produto in PRECOS_MAX:

            if produto in texto:

                if preco and preco > PRECOS_MAX[produto]:
                    return

    chat = await event.get_chat()

    nome_grupo = getattr(chat, "title", "Chat privado")

    link = ""

    if getattr(chat, "username", None):
        link = f"https://t.me/{chat.username}/{event.id}"

    alerta = f"""
🚨 Promoção encontrada

📢 Grupo: {nome_grupo}

🔎 Palavras detectadas: {' + '.join(conjunto)}

💬 Mensagem:
{mensagem}
"""

    if preco:
        alerta += f"\n💰 Preço detectado: {preco}"

    if link:
        alerta += f"\n🔗 Link:\n{link}"

    enviar_alerta(alerta)

    mensagens_processadas.add(promo_hash)


async def iniciar():

    print("🤖 Bot iniciado e monitorando...")

    await client.start()

    await client.run_until_disconnected()


while True:

    try:

        asyncio.run(iniciar())

    except Exception as erro:

        print("⚠ Erro detectado:", erro)

        print("🔄 Reconectando em 5 segundos...")

        time.sleep(5)

