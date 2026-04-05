import asyncio
import re
import hashlib
import urllib.parse
import urllib.request
import os
import time

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

BOT_TOKEN = "SEU_BOT_TOKEN_AQUI"
CHAT_ID = SEU_CHAT_ID_AQUI

# ===== SESSION (CORRIGIDO PRO FLY) =====
SESSION = os.getenv("TG_SESSION")

print("SESSION:", SESSION)

if not SESSION:
    print("⚠️ TG_SESSION não encontrada... aguardando 5s...")
    time.sleep(5)
    SESSION = os.getenv("TG_SESSION")

    if not SESSION:
        raise Exception("❌ TG_SESSION não carregou no ambiente")

# ===== CLIENT =====
client = TelegramClient(
    StringSession(SESSION),
    api_id,
    api_hash,
    connection=ConnectionTcpAbridged,
    auto_reconnect=True,
    timeout=30
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
    ["panela", "polishop"],
    ["frigideira", "polishop"],
    ["confort", "sec"]
]

PRECOS_MAX = {
    "creatina": 40,
    "jordan": 400,
    "camiseta nike": 70,
    "pampers": 60
}

PALAVRAS_IGNORAR = [
    "iphone",
    "olympikus",
    "macbook",
    "celular",
    "smartphone",
    "galaxy",
]

mensagens_processadas = set()
promocoes_detectadas = set()

# ===== ALERTA =====
def enviar_alerta(msg):
    try:
        if len(msg) > 4000:
            msg = msg[:4000]

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": msg
        }).encode("utf-8")

        urllib.request.urlopen(url, data=data, timeout=10)

    except Exception as e:
        print("Erro ao enviar alerta:", e)

# ===== PREÇO =====
def extrair_preco(texto):
    texto = texto.lower()

    padroes = [
        r'por\s+r\$\s*(\d+[.,]?\d*)',
        r'apenas\s+r\$\s*(\d+[.,]?\d*)',
        r'r\$\s*(\d+[.,]?\d*)\s*(?:no pix|à vista)',
        r'de\s+r\$\s*\d+[.,]?\d*\s*por\s*r\$\s*(\d+[.,]?\d*)',
    ]

    precos = []

    for padrao in padroes:
        matches = re.findall(padrao, texto)
        for valor in matches:
            try:
                precos.append(float(valor.replace(",", ".")))
            except:
                pass

    return min(precos) if precos else None

# ===== TEXTO =====
def normalizar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s%$]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

# ===== PALAVRAS =====
def verificar_palavras(texto):
    texto = normalizar_texto(texto)

    # corre / correeeee
    if re.search(r'\bco+r{2,}e+\b', texto):
        return ["corre"]

    for conjunto in CONJUNTOS:
        if all(p in texto for p in conjunto):
            return conjunto

    return None

# ===== HASH =====
def gerar_hash_promocao(texto):
    texto = re.sub(r'\s+', ' ', texto.lower())
    return hashlib.md5(texto.encode()).hexdigest()

# ===== IGNORAR =====
def contem_palavra_ignorada(texto):
    texto = texto.lower()
    return any(p in texto for p in PALAVRAS_IGNORAR)

# ===== MONITOR =====
@client.on(events.NewMessage(incoming=True))
async def monitor(event):

    if not event.is_group and not event.is_channel:
        return

    if event.out or event.message.edit_date:
        return

    msg_uid = (event.chat_id, event.id)

    if msg_uid in mensagens_processadas:
        return

    mensagem = event.raw_text
    if not mensagem:
        return

    hash_promo = gerar_hash_promocao(mensagem)

    if hash_promo in promocoes_detectadas:
        return

    if contem_palavra_ignorada(mensagem):
        return

    conjunto = verificar_palavras(mensagem)
    if not conjunto:
        return

    preco = extrair_preco(mensagem)

    if USAR_FILTRO_PRECO and preco:
        texto = mensagem.lower()
        for produto in PRECOS_MAX:
            if produto in texto and preco > PRECOS_MAX[produto]:
                return

    nome_grupo = getattr(event.chat, "title", "Canal") if event.chat else "Canal"
    username = getattr(event.chat, "username", None)

    link = f"https://t.me/{username}/{event.id}" if username else ""

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
    mensagens_processadas.add(msg_uid)

# ===== MAIN =====
async def main():
    print("🤖 Bot iniciado...")
    await client.start()
    print("✅ Conectado ao Telegram")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
