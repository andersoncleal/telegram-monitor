import asyncio
from telethon import TelegramClient, events

api_id = 39830316
api_hash = "801694a8767bb74ce2998044ccf111f7"

palavras = [
"bug",
"corre",
"corree",
"correee",
"correeee",
"correeeee",
"correeeeee",
"correeeeeee",
"correeeeeeee",
"correeeeeeeee",
"correeeeeeeeee",
"correeeeeeeeeee",
"correeeeeeeeeeee",
"whey"
]

client = TelegramClient(
    "monitor",
    api_id,
    api_hash,
    connection_retries=None,
    retry_delay=5
)


@client.on(events.NewMessage(incoming=True))
async def monitor(event):

    texto = (event.raw_text or "").lower()

    if not texto:
        return

    for palavra in palavras:

        if palavra.lower() in texto:

            chat = await event.get_chat()

            nome_grupo = getattr(chat, "title", None)

            if not nome_grupo:
                nome_grupo = getattr(chat, "first_name", "Chat privado")

            mensagem_original = event.raw_text or "(mensagem sem texto)"

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

            print(alerta)

            await client.send_message("me", alerta)

            break


async def main():

    await client.start()

    print("✅ Monitorando mensagens...")

    while True:
        try:
            await client.run_until_disconnected()

        except Exception as e:

            print("⚠ Conexão perdida. Tentando reconectar...")
            print(e)

            await asyncio.sleep(5)


asyncio.run(main())
