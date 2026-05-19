from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, ExportChatInviteRequest, EditPhotoRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights
import requests
from io import BytesIO
import traceback

api_id = 123456
api_hash = "YOUR_API_HASH"

client = TelegramClient("userbot", api_id, api_hash)

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

@client.on(events.NewMessage(pattern=r"\.mm (.+)"))
async def mm(event):
    try:
        amount = event.pattern_match.group(1)

        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Réponds à une personne avec .mm 50€")
            return

        target = reply.sender_id

        print("[DEBUG] Creating group...")

        result = await client(CreateChannelRequest(
            title=f"mm {amount}",
            about="deal group",
            megagroup=True
        ))

        chat = result.chats[0]

        print("[DEBUG] Group created:", chat.id)

        # READ ONLY
        await client(EditChatDefaultBannedRightsRequest(
            peer=chat,
            banned_rights=readonly
        ))

        print("[DEBUG] Read-only applied")

        # PHOTO
        img = requests.get("https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg").content
        file = BytesIO(img)
        file.name = "photo.jpg"

        await client(EditPhotoRequest(
            channel=chat,
            photo=await client.upload_file(file)
        ))

        print("[DEBUG] Photo set")

        # INVITE LINK
        invite = await client(ExportChatInviteRequest(chat))

        print("[DEBUG] Invite link created")

        # DM
        await client.send_message(
            target,
            f"""Merci de partager le lien du groupe seulement avec la personne concernée par le deal

{invite.link}"""
        )

        print("[DEBUG] DM sent")

        await event.delete()

    except Exception as e:
        print("[ERROR]", e)
        print(traceback.format_exc())
        await event.reply("❌ Erreur dans .mm (voir logs Replit)")
