import asyncio
from telethon import TelegramClient, events

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

palavras = [
"bug",
"corre",
"whey"
]

client = TelegramClient(
    "monitor",
    api_id,
    api_hash,
    connection_retries=None,
    retry_delay=5
)

@client.on(events.NewMessage)
async def monitor(event):

    if not event.raw_text:
        return

    texto = event.raw_text.lower()

    for palavra in palavras:

        if palavra in texto:

            chat = await event.get_chat()

            nome_grupo = getattr(chat, "title", "Chat privado")

            mensagem_original = event.raw_text

            link = ""

            if hasattr(chat, "username") and chat.username:
                link = f"https://t.me/{chat.username}/{event.id}"

            alerta = f"""
🚨 Palavra encontrada: {palavra}

📢 Grupo: {nome_grupo}

💬 Mensagem:
{mensagem_original}

🔗 Link:
{link}
"""

            await client.send_message("me", alerta)

            break


async def main():

    await client.start()
    await client.connect()

    print("✅ Monitorando mensagens...")

    while True:
        try:
            await client.run_until_disconnected()
        except Exception:
            print("⚠ Conexão perdida. Tentando reconectar...")
            await asyncio.sleep(5)


asyncio.run(main())
