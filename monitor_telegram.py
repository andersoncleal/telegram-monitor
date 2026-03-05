import asyncio
import re
from telethon import TelegramClient, events

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

# ===== CONFIGURAÇÕES =====

USAR_FILTRO_PRECO = False

CONJUNTOS = [
    ["bug"],
    ["corre"],
    ["whey", "100%"]
]

PRECOS_MAX = {
    "whey": 80,
    "creatina": 90,
    "pasta": 25
}

links_enviados = set()

# ===== CLIENT =====

client = TelegramClient(
    "monitor",
    api_id,
    api_hash,
    connection_retries=None,
    retry_delay=5
)

# ===== FUNÇÃO PREÇO =====

def extrair_preco(texto):

    padrao = r"\d+[.,]?\d*"
    numeros = re.findall(padrao, texto)

    for n in numeros:
        valor = n.replace(",", ".")

        try:
            return float(valor)
        except:
            pass

    return None


# ===== MONITOR =====

@client.on(events.NewMessage(incoming=True))
async def monitor(event):

    texto_original = event.raw_text or ""
    texto = texto_original.lower()

    if not texto:
        return

    chat = await event.get_chat()

    nome_grupo = getattr(chat, "title", None)

    if not nome_grupo:
        nome_grupo = getattr(chat, "first_name", "Chat privado")

    link = ""

    if hasattr(chat, "username") and chat.username:
        link = f"https://t.me/{chat.username}/{event.id}"

    if link in links_enviados:
        return

    for grupo in CONJUNTOS:

        if all(p in texto for p in grupo):

            preco = extrair_preco(texto)

            if USAR_FILTRO_PRECO:

                palavra_principal = grupo[0]

                if preco and palavra_principal in PRECOS_MAX:

                    if preco > PRECOS_MAX[palavra_principal]:
                        return

            links_enviados.add(link)

            alerta = f"""
🔥 POSSÍVEL PROMOÇÃO

🛒 Produto detectado: {' + '.join(grupo)}

💰 Preço detectado: {preco}

📢 Grupo: {nome_grupo}

💬 Mensagem:
{texto_original}

🔗 Link:
{link}
"""

            print(alerta)

            await client.send_message("me", alerta)

            break


# ===== LOOP =====

async def main():

    await client.start()

    print("✅ Bot monitorando promoções...")

    while True:
        try:
            await client.run_until_disconnected()

        except Exception as e:

            print("⚠ Reconectando...")
            print(e)

            await asyncio.sleep(5)


asyncio.run(main())

