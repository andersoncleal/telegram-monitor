import asyncio
import re
import hashlib
import urllib.parse
import urllib.request
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

BOT_TOKEN = "8785139630:AAGeXw7AQDa0TgH9ce1wSFeVcSTfXICjuc8"
CHAT_ID = 8604120421

SESSION = os.getenv("TG_SESSION")

if not SESSION:
    raise Exception("TG_SESSION não encontrada nas variáveis do Railway")

client = TelegramClient(
    StringSession(SESSION),
    api_id,
    api_hash,
    connection=ConnectionTcpAbridged,
    connection_retries=None,
    retry_delay=5,
    auto_reconnect=True,
    timeout=30,
    receive_updates=True,
    device_model="Samsung Galaxy S23",
    system_version="Android 14",
    app_version="10.5"
)

USAR_FILTRO_PRECO = True

CONJUNTOS = [
    ["bug"],
    ["whey", "100%"],
    ["jordan"],
    ["dux"],
    ["camiseta", "nike"],
    ["folha", "tripla"],
    ["preco", "absurdo"],
    ["panela","polishop"],
    ["frigideira","polishop"]
]

PRECOS_MAX = {
    "creatina": 40,
    "jordan": 400,
    "camiseta": 80
}

# -------- NOVO BLOCO ADICIONADO --------
PALAVRAS_IGNORAR = [
    "iphone",
    "olympikus",
    "olimpikys",
    "macbook",
    "dark lab",
    "celular",
    "smartphone",
    "galaxy","S24",
    "galaxy","S25",
    "galaxy","S26"
]
# --------------------------------------

mensagens_processadas = set()
promocoes_detectadas = set()


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

    texto = texto.lower()

    padroes = [
        r'por\s+r\$\s*(\d+[.,]?\d*)',
        r'apenas\s+r\$\s*(\d+[.,]?\d*)',
        r'r\$\s*(\d+[.,]?\d*)\s*(?:no pix|à vista)',
        r'de\s+r\$\s*\d+[.,]?\d*\s*por\s*r\$\s*(\d+[.,]?\d*)',
        r'🔥\s*r\$\s*(\d+[.,]?\d*)'
    ]

    precos = []

    for padrao in padroes:

        matches = re.findall(padrao, texto)

        for valor in matches:

            valor = valor.replace(",", ".")

            try:
                precos.append(float(valor))
            except:
                pass

    if not precos:
        return None

    return min(precos)


def normalizar_texto(texto):

    texto = texto.lower()

    texto = re.sub(r"[^\w\s%$]", " ", texto)

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def verificar_palavras(texto):

    texto = normalizar_texto(texto)

    # 🔥 Detecta qualquer variação de "corre"
    if re.search(r'\bco+r{2,}e+\b', texto):
        return ["corre"]

    for conjunto in CONJUNTOS:

        encontrou = True

        for palavra in conjunto:

            # ✅ agora busca no texto inteiro, não só palavra isolada
            if palavra.lower() not in texto:
                encontrou = False
                break

        if encontrou:
            return conjunto

    return None


def gerar_hash_promocao(texto):

    texto = texto.lower()

    texto = re.sub(r'\s+', ' ', texto)

    return hashlib.md5(texto.encode()).hexdigest()


# -------- NOVA FUNÇÃO ADICIONADA --------
def contem_palavra_ignorada(texto):

    texto = texto.lower()

    for palavra in PALAVRAS_IGNORAR:
        if palavra in texto:
            return True

    return False
# ----------------------------------------


@client.on(events.NewMessage(incoming=True))
async def monitor(event):

    # apenas grupos e canais
    if not event.is_group and not event.is_channel:
        return

    # ignora mensagens enviadas por você
    if event.out:
        return

    # ignora mensagens editadas
    if event.message.edit_date:
        return

    # ID único da mensagem
    msg_uid = (event.chat_id, event.id)

    if msg_uid in mensagens_processadas:
        return

    mensagem = event.raw_text

    if not mensagem:
        return

    if not mensagem:
        return

    hash_promo = gerar_hash_promocao(mensagem)

    if hash_promo in promocoes_detectadas:
        return

    # -------- NOVA VERIFICAÇÃO ADICIONADA --------
    if contem_palavra_ignorada(mensagem):
        return
    # --------------------------------------------

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
        nome_grupo = getattr(event.chat, "title", "Canal")
        username = getattr(event.chat, "username", None)
    else:
        nome_grupo = "Canal"
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

    promocoes_detectadas.add(hash_promo)

    if len(promocoes_detectadas) > 5000:
        promocoes_detectadas.clear()

    mensagens_processadas.add(msg_uid)

    # limpa memória
    if len(mensagens_processadas) > 5000:
        mensagens_processadas.clear()


async def main():

    print("🤖 Bot iniciado e monitorando...")

    while True:

        try:

            await client.start()

            print("✅ Conectado ao Telegram")

            await client.run_until_disconnected()

        except Exception as e:

            print("⚠️ Conexão perdida:", e)

            print("🔄 Tentando reconectar em 10 segundos...")

            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())























