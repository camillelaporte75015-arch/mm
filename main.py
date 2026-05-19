from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, ExportChatInviteRequest, EditChatDefaultBannedRightsRequest, EditPhotoRequest
from telethon.tl.types import ChatBannedRights
import requests
from io import BytesIO
import traceback

api_id = 123456
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

# 🔒 permissions bloquées (read-only total)
READONLY_ALL = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)


# =========================
# 📌 .mm COMMAND
# =========================
@client.on(events.NewMessage(pattern=r"\.mm (.+)"))
async def mm(event):
    try:
        amount = event.pattern_match.group(1)

        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Réponds à une personne avec .mm 50€")
            return

        target = reply.sender_id

        # 🏗️ création du groupe
        result = await client(CreateChannelRequest(
            title=f"mm {amount}",
            about="deal group",
            megagroup=True
        ))

        chat = result.chats[0]

        # 🔒 read-only global
        await client(EditChatDefaultBannedRightsRequest(
            peer=chat,
            banned_rights=READONLY_ALL
        ))

        # 🖼️ photo groupe
        img = requests.get("https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg").content
        file = BytesIO(img)
        file.name = "photo.jpg"

        await client(EditPhotoRequest(
            channel=chat,
            photo=await client.upload_file(file)
        ))

        # 🔗 invite link
        invite = await client(ExportChatInviteRequest(chat))

        # 📩 DM cible
        await client.send_message(
            target,
            f"""Merci de partager le lien du groupe seulement avec la personne concernée par le deal

{invite.link}"""
        )

        await event.delete()

    except Exception as e:
        print("[ERROR .mm]", e)
        print(traceback.format_exc())
        await event.reply("❌ Erreur dans .mm")


# =========================
# 📌 .finish COMMAND
# =========================
@client.on(events.NewMessage(pattern=r"\.finish"))
async def finish(event):
    try:
        chat = await event.get_chat()

        message = """Merci d'avoir utilisé incultes pour votre deal,

N'oubliez pas de mettre un vouch de cet manière : Vouch @incultes mm xxx€ . ( merci de mettre la valeur du deal ) il sera automatiquement transmis dans le canal @incultesvouches .

⚠️ : Je vous rappelle que je ne vous contacterai jamais en premier, si quelqu'un vous contacte avec le même profil que moi, ce n'est pas moi !"""

        await client.send_message(chat, message)

        await event.delete()

    except Exception as e:
        print("[ERROR .finish]", e)
        await event.reply("❌ Erreur dans .finish")


# =========================
# 📌 .lock COMMAND
# =========================
@client.on(events.NewMessage(pattern=r"\.lock"))
async def lock(event):
    try:
        chat = await event.get_chat()

        # 🔒 lock complet du groupe
        await client(EditChatDefaultBannedRightsRequest(
            peer=chat,
            banned_rights=READONLY_ALL
        ))

        # 🔗 lien du groupe
        invite = await client(ExportChatInviteRequest(chat))

        # 📢 envoi dans le canal vouches
        await client.send_message(
            "incultesvouches",
            f"un deal a été terminé : {invite.link}"
        )

        await event.delete()

    except Exception as e:
        print("[ERROR .lock]", e)
        await event.reply("❌ Erreur dans .lock")


# =========================
# 🚀 START
# =========================
client.start()
print("Userbot running...")
client.run_until_disconnected()
