import asyncio
import re
from telethon import TelegramClient, events

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

USAR_FILTRO_PRECO = False

CONJUNTOS = [
    ["bug"],
    ["corre"],
    ["whey", "100%"],
    ["jordan"]
]

PRECOS_MAX = {
    "whey": 80,
    "creatina": 90,
    "pasta": 25
}

# memória de mensagens já enviadas
mensagens_processadas = set()

client = TelegramClient(
    "monitor",
    api_id,
    api_hash,
    connection_retries=10,
    retry_delay=5
)


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


def verificar_palavras(texto):

    texto = texto.lower()

    for conjunto in CONJUNTOS:

        if all(p.lower() in texto for p in conjunto):

            return conjunto

    return None


@client.on(events.NewMessage)
async def monitor(event):

    mensagem = event.raw_text

    if not mensagem:
        return

    # evita repetir mensagens
    msg_id = f"{event.chat_id}-{event.id}"

    if msg_id in mensagens_processadas:
        return

    texto = mensagem.lower()

    conjunto = verificar_palavras(texto)

    if not conjunto:
        return

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

    # envia alerta
    await client.send_message(27139211, alerta)

    # salva mensagem como já enviada
    mensagens_processadas.add(msg_id)


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

        asyncio.sleep(5)

