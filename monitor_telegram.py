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
    ["jordan"],
    ["historico"]
]

PRECOS_MAX = {
    "whey": 80,
    "creatina": 90,
    "pasta": 25
}

client = TelegramClient(
    "monitor",
    api_id,
    api_hash,
    connection_retries=None,
    retry_delay=5
)

def extrair_preco(texto):

    padrao = r'(\d{1,4}[,.]\d{2})'

    numeros = re.findall(padrao, texto)

    if numeros:
        valor = numeros[0].replace(",", ".")
        return float(valor)

    return None


@client.on(events.NewMessage)
async def monitor(event):

    if not event.raw_text:
        return

    texto = event.raw_text.lower()

    for conjunto in CONJUNTOS:

        if all(p.lower() in texto for p in conjunto):

            preco = extrair_preco(texto)

            if USAR_FILTRO_PRECO:
                preco = extrair_preco(texto)

                for produto in PRECOS_MAX:

                    if produto in texto:

                        if preco > PRECOS_MAX[produto]:
                            return

            chat = await event.get_chat()

            nome_grupo = getattr(chat, "title", "Chat privado")

            link = ""

            if hasattr(chat, "username") and chat.username:
                link = f"https://t.me/{chat.username}/{event.id}"

            alerta = f"""
🚨 Promoção encontrada

📢 Grupo: {nome_grupo}

💬 Mensagem:
{event.raw_text}

if preco:
    mensagem_alerta += f"\n💰 Preço detectado: {preco}"

🔗 Link:
{link}
"""

            await client.send_message("me", alerta)

            break


async def main():

    await client.start()

    print("✅ Bot monitorando promoções...")

    while True:
        try:
            await client.run_until_disconnected()
        except Exception:
            print("⚠ Reconectando...")
            await asyncio.sleep(5)


asyncio.run(main())


