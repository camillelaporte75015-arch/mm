from telethon import TelegramClient, events
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    ExportChatInviteRequest,
    EditChatDefaultBannedRightsRequest,
    EditPhotoRequest
)
from telethon.tl.types import ChatBannedRights
import requests
from io import BytesIO
import traceback

api_id = 123456
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

# 🔒 LOCK GLOBAL
LOCK_RIGHTS = ChatBannedRights(
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
# 📌 .mm
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

        # 🏗️ création groupe
        result = await client(CreateChannelRequest(
            title=f"mm {amount}",
            about="deal group",
            megagroup=True
        ))

        chat = result.chats[0]
        chat_entity = await client.get_entity(chat)

        # 🔒 LOCK DIRECT
        await client(EditChatDefaultBannedRightsRequest(
            peer=chat_entity,
            banned_rights=LOCK_RIGHTS
        ))

        # 🖼️ PHOTO FIXÉE (TA URL)
        try:
            url = "https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg"
            r = requests.get(url, timeout=10)
            r.raise_for_status()

            file = BytesIO(r.content)
            file.name = "photo.jpg"

            uploaded = await client.upload_file(file)

            await client(EditPhotoRequest(
                channel=chat_entity,
                photo=uploaded
            ))

        except Exception:
            print("[PHOTO ERROR]")
            print(traceback.format_exc())

        # 🔗 invite link
        invite = await client(ExportChatInviteRequest(chat_entity))

        # 📩 DM
        await client.send_message(
            target,
            f"Merci de partager le lien du groupe seulement avec la personne concernée par le deal\n\n{invite.link}"
        )

        await event.delete()

    except Exception:
        print("[ERROR .mm]")
        print(traceback.format_exc())
        await event.reply("❌ Erreur dans .mm")


# =========================
# 📌 .finish
# =========================
@client.on(events.NewMessage(pattern=r"\.finish"))
async def finish(event):
    try:
        chat = await event.get_chat()

        msg = """Merci d'avoir utilisé incultes pour votre deal,

N'oubliez pas de mettre un vouch de cet manière : Vouch @incultes mm xxx€ . ( merci de mettre la valeur du deal ) il sera automatiquement transmis dans le canal @incultesvouches .

⚠️ : Je vous rappelle que je ne vous contacterai jamais en premier, si quelqu'un vous contacte avec le même profil que moi, ce n'est pas moi !"""

        await client.send_message(chat, msg)
        await event.delete()

    except Exception:
        print("[ERROR .finish]")
        print(traceback.format_exc())
        await event.reply("❌ Erreur dans .finish")


# =========================
# 📌 .lock
# =========================
@client.on(events.NewMessage(pattern=r"\.lock"))
async def lock(event):
    try:
        chat = await event.get_chat()
        chat_entity = await client.get_entity(chat)

        # 🔒 LOCK GLOBAL
        await client(EditChatDefaultBannedRightsRequest(
            peer=chat_entity,
            banned_rights=LOCK_RIGHTS
        ))

        # 🔗 lien groupe
        invite = await client(ExportChatInviteRequest(chat_entity))

        # 📢 canal vouches
        await client.send_message(
            "incultesvouches",
            f"un deal a été terminé : {invite.link}"
        )

        await event.delete()

    except Exception:
        print("[ERROR .lock]")
        print(traceback.format_exc())
        await event.reply("❌ Erreur dans .lock")


# =========================
# 🚀 START
# =========================
client.start()
print("Userbot running...")
client.run_until_disconnected()
