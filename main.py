from telethon import TelegramClient, events
from telethon.tl.functions.messages import CreateChatRequest, ExportChatInviteRequest
from telethon.tl.functions.channels import EditPhotoRequest, EditChatDefaultBannedRightsRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights
import requests
from io import BytesIO

# ======================
# CONFIG
# ======================
api_id = 123456  # <-- ton api_id
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

# ======================
# GLOBAL DATA
# ======================
first_two = {}

# ======================
# READ ONLY RULES (members)
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
# ADMIN LIMITED (only text + photos)
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
# CREATE DEAL GROUP
# ======================
@client.on(events.NewMessage(pattern=r"\.mm (.+)"))
async def create_group(event):
    amount = event.pattern_match.group(1)

    reply = await event.get_reply_message()
    if not reply:
        await event.reply("Réponds à une personne avec .mm 50€")
        return

    target = reply.sender_id
    me = await client.get_me()

    # create group with only you
    result = await client(CreateChatRequest(
        users=[me.id],
        title=f"mm {amount}"
    ))

    chat = result.chats[0]

    # store chat state
    first_two[chat.id] = []

    # set read-only globally
    await client(EditChatDefaultBannedRightsRequest(
        peer=chat.id,
        banned_rights=readonly
    ))

    # set photo
    img = requests.get("https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg").content
    file = BytesIO(img)
    file.name = "photo.jpg"

    await client(EditPhotoRequest(
        chat_id=chat.id,
        photo=await client.upload_file(file)
    ))

    # invite link
    invite = await client(ExportChatInviteRequest(chat.id))

    # send DM to target
    await client.send_message(
        target,
        f"""Merci de partager le lien du groupe seulement avec la personne concernée par le deal

{invite.link}"""
    )

    await event.reply("Groupe créé + lien envoyé.")

# ======================
# AUTO PROMOTE FIRST 2 JOINERS
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

    # already 2 admins max
    if len(first_two[chat_id]) >= 2:
        return

    if uid in first_two[chat_id]:
        return

    first_two[chat_id].append(uid)

    await client(EditAdminRequest(
        chat_id,
        uid,
        admin_rights,
        rank="deal"
    ))

# ======================
# START BOT
# ======================
client.start()
client.run_until_disconnected()
