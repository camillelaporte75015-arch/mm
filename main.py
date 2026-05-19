from telethon import TelegramClient, events
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    ExportChatInviteRequest,
    EditPhotoRequest,
    EditAdminRequest,
    EditBannedRequest
)
from telethon.tl.types import ChatAdminRights, ChatBannedRights
import requests
from io import BytesIO

# ======================
# CONFIG
# ======================
api_id = 123456
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

# ======================
# STORAGE (2 first joiners)
# ======================
first_two = {}

# ======================
# READ ONLY FOR MEMBERS
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
# LIMITED ADMIN (write + photos only)
# ======================
admin_rights = ChatAdminRights(
    change_info=False,
    post_messages=True,
    edit_messages=False,
    delete_messages=False,
    ban_users=False,
    invite_users=False,
    pin_messages=False,
    add_admins=False,
    anonymous=False,
    manage_call=False
)

# ======================
# CREATE DEAL GROUP (.mm)
# ======================
@client.on(events.NewMessage(pattern=r"\.mm (.+)"))
async def create_group(event):
    amount = event.pattern_match.group(1)

    reply = await event.get_reply_message()
    if not reply:
        await event.reply("Réponds à quelqu’un avec .mm 50€")
        return

    target = reply.sender_id
    me = await client.get_me()

    # ✅ CREATE MEGAGROUP (IMPORTANT FIX)
    result = await client(CreateChannelRequest(
        title=f"mm {amount}",
        about="deal group",
        megagroup=True
    ))

    chat = result.chats[0]

    # init tracking
    first_two[chat.id] = []

    # set read-only default for members
    await client(EditBannedRequest(
        channel=chat,
        participant="everyone",
        banned_rights=readonly
    ))

    # set group photo
    img = requests.get(
        "https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg"
    ).content

    file = BytesIO(img)
    file.name = "photo.jpg"

    await client(EditPhotoRequest(
        channel=chat,
        photo=await client.upload_file(file)
    ))

    # invite link
    invite = await client(ExportChatInviteRequest(chat))

    # DM message
    await client.send_message(
        target,
        f"""Merci de partager le lien du groupe seulement avec la personne concernée par le deal

{invite.link}"""
    )

    await event.reply("Groupe créé + lien envoyé.")

# ======================
# AUTO HANDLE JOINERS
# ======================
@client.on(events.ChatAction)
async def on_join(event):

    if not (event.user_joined or event.user_added):
        return

    chat_id = event.chat_id
    user = await event.get_user()
    uid = user.id

    if chat_id not in first_two:
        return

    # stop after 2 admins
    if len(first_two[chat_id]) >= 2:
        return

    if uid in first_two[chat_id]:
        return

    first_two[chat_id].append(uid)

    # promote to admin (write + photos only)
    await client(EditAdminRequest(
        channel=chat_id,
        user_id=uid,
        admin_rights=admin_rights,
        rank="deal"
    ))

client.start()
client.run_until_disconnected()
