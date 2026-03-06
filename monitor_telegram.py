import asyncio
import re
import hashlib
import urllib.parse
import urllib.request
import os

from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

BOT_TOKEN = "8614974695:AAEYfpkXzmIN-_qgPovELdO8aX8E01TpvGY"
CHAT_ID = 27139211

SESSION = os.getenv("TG_SESSION")

if not SESSION:
    raise Exception("TG_SESSION não encontrada nas variáveis do Railway")

client = TelegramClient(
    StringSession(SESSION),
    api_id,
    api_hash,
    connection_retries=None,
    retry_delay=5,
    auto_reconnect=True
)

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


def enviar_alerta(msg):

    try:

        # limite máximo telegram
        if len(msg) > 4000:
            msg = msg[:4000]

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": msg
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data)

        urllib.request.urlopen(req, timeout=10)

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


def normalizar_texto(texto):

    texto = texto.lower()

    texto = re.sub(r"[^\w\s%$]", " ", texto)

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def verificar_palavras(texto):

    texto = normalizar_texto(texto)

    palavras_texto = texto.split()

    for conjunto in CONJUNTOS:

        encontrou = True

        for palavra in conjunto:

            if palavra.lower() not in palavras_texto:
                encontrou = False
                break

        if encontrou:
            return conjunto

    return None


@client.on(events.NewMessage)
async def monitor(event):

    # 1️⃣ ignora mensagens do próprio chat do bot
    if event.chat_id == CHAT_ID:
        return

    # 2️⃣ ignora mensagens editadas
    if event.message.edit_date:
        return

    # evita loop com mensagens enviadas pelo próprio cliente
    if event.out:
        return

    msg_id = f"{event.chat_id}-{event.id}"

    if msg_id in mensagens_processadas:
        return

    mensagem = event.raw_text

    if not mensagem:
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

    if event.chat:
        nome_grupo = getattr(event.chat, "title", "Chat privado")
        username = getattr(event.chat, "username", None)
    else:
        nome_grupo = "Chat privado"
        username = None

    link = ""

    if username:
        link = f"https://t.me/{username}/{event.id}"

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

    mensagens_processadas.add(msg_id)


async def main():

    print("🤖 Bot iniciado e monitorando...")

    await client.start()

    await client.run_until_disconnected()


if __name__ == "__main__":

    asyncio.run(main())
