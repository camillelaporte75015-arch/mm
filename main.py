from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, ExportChatInviteRequest, EditPhotoRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights
import requests
from io import BytesIO

# ======================
# CONFIG
# ======================
api_id = 123456
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

# ======================
# READ ONLY MODE
# ======================
readonly = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

# ======================
# CREATE GROUP (.mm)
# ======================
@client.on(events.NewMessage(pattern=r"\.mm (.+)"))
async def mm(event):

    amount = event.pattern_match.group(1)

    reply = await event.get_reply_message()
    if not reply:
        await event.reply("Réponds à une personne avec .mm 50€")
        return

    target = reply.sender_id

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

    await client(EditPhotoRequest(
        channel=chat,
        photo=await client.upload_file(file)
    ))

    # invite link
    invite = await client(ExportChatInviteRequest(chat))

    # send DM
    await client.send_message(
        target,
        f"""Merci de partager le lien du groupe seulement avec la personne concernée par le deal

{invite.link}"""
    )

    await event.delete()


# ======================
# LOCK GROUP
# ======================
@client.on(events.NewMessage(pattern=r"\.lock"))
async def lock(event):

    chat = await event.get_chat()

    await client(EditChatDefaultBannedRightsRequest(
        peer=chat,
        banned_rights=readonly
    ))

    invite = await client(ExportChatInviteRequest(chat))

    await client.send_message(
        "incultesvouches",
        f"🔒 Groupe lock : {invite.link}"
    )

    await event.delete()


# ======================
# FINISH
# ======================
@client.on(events.NewMessage(pattern=r"\.finish"))
async def finish(event):

    chat = await event.get_chat()

    msg = """Merci d’avoir utilisé incultes pour votre deal,

N’oubliez pas de mettre un vouch de cet manière : Vouch @incultes mm xxx€ . ( merci de mettre la valeur du deal ) il sera automatiquement transmis dans le canal @incultesvouches .

⚠️ : Je vous rappelle que je ne vous contacterai jamais en premier, si quelqu’un vous contacte avec le même profil que moi, ce n’est pas moi !"""

    await client.send_message(chat, msg)
    await event.delete()


# ======================
# START
# ======================
client.start()
client.run_until_disconnected()
