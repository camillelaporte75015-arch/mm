from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, ExportChatInviteRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights
import requests
from io import BytesIO
import traceback

# ======================
# CONFIG
# ======================
api_id = 123456
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

# ======================
# FULL MEMBER RESTRICTION (LOCK MODE)
# ======================
lock_rights = ChatBannedRights(
    until_date=None,

    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,

    send_polls=True,
    change_info=True,
    invite_users=True,
    pin_messages=True
)

# ======================
# CREATE DEAL (.mm)
# ======================
@client.on(events.NewMessage(pattern=r"\.mm (.+)"))
async def mm(event):
    try:
        amount = event.pattern_match.group(1)

        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Réponds à une personne avec .mm 50€")
            return

        target = reply.sender_id

        # create group (megagroup = stable)
        result = await client(CreateChannelRequest(
            title=f"mm {amount}",
            about="deal group",
            megagroup=True
        ))

        chat = result.chats[0]

        # photo
        img = requests.get("https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg").content
        file = BytesIO(img)
        file.name = "photo.jpg"

        await client.send_file(chat, file)

        # invite link
        invite = await client(ExportChatInviteRequest(chat))

        # DM only
        await client.send_message(
            target,
            f"""Merci de partager le lien du groupe seulement avec la personne concernée par le deal

{invite.link}"""
        )

        # delete command
        await event.delete()

    except Exception as e:
        print("[MM ERROR]", e)
        print(traceback.format_exc())


# ======================
# LOCK GROUP (.lock)
# ======================
@client.on(events.NewMessage(pattern=r"\.lock"))
async def lock(event):
    try:
        chat = await event.get_chat()

        await client(EditChatDefaultBannedRightsRequest(
            peer=chat,
            banned_rights=lock_rights
        ))

        await event.delete()

    except Exception as e:
        print("[LOCK ERROR]", e)
        print(traceback.format_exc())


# ======================
# FINISH (.finish)
# ======================
@client.on(events.NewMessage(pattern=r"\.finish"))
async def finish(event):
    try:
        chat = await event.get_chat()

        msg = """Merci d’avoir utilisé incultes pour votre deal,

N’oubliez pas de mettre un vouch de cet manière : Vouch @incultes mm xxx€ . ( merci de mettre la valeur du deal ) il sera automatiquement transmis dans le canal @incultesvouches .

⚠️ : Je vous rappelle que je ne vous contacterai jamais en premier, si quelqu’un vous contacte avec le même profil que moi, ce n’est pas moi !"""

        await client.send_message(chat, msg)

        await event.delete()

    except Exception as e:
        print("[FINISH ERROR]", e)
        print(traceback.format_exc())


# ======================
# START BOT
# ======================
client.start()
client.run_until_disconnected()
