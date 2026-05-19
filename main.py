from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest, EditBannedRequest
from telethon.tl.types import ChatBannedRights
from io import BytesIO
import requests
import logging

logging.basicConfig(level=logging.INFO)

# ======================
# CONFIG
# ======================

api_id = 123456
api_hash = "YOUR_API_HASH"
session_name = "userbot"

client = TelegramClient(session_name, api_id, api_hash)

OWNER_ID = 123456789

# ======================
# MEMORY
# ======================

deals = {}
locked = set()

# ======================
# IMAGES
# ======================

PRIMARY_IMAGE = "https://front-silver-5dgokcoizr.edgeone.app/IMG_0081.jpeg"
FALLBACK_IMAGE = "https://img.sanishtech.com/u/a1a6ed8453945f7a1c55e68d6ec96cd5.jpeg"


def download_image(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    file = BytesIO(r.content)
    file.name = "group.jpg"
    return file


# ======================
# BOT
# ======================

@client.on(events.NewMessage)
async def handler(event):

    if event.sender_id != OWNER_ID:
        return

    text = event.raw_text

    # ======================
    # .mm CREATE DEAL
    # ======================
    if text.startswith(".mm "):
        try:
            amount = text.split(" ", 1)[1]

            result = await client(CreateChannelRequest(
                title=f"mm {amount}",
                about="deal avec @incultes , merci de consulter @incultescrow",
                megagroup=True
            ))

            chat = result.chats[0]
            chat_id = chat.id

            # ======================
            # PHOTO + FALLBACK
            # ======================
            try:
                try:
                    img = download_image(PRIMARY_IMAGE)
                except:
                    img = download_image(FALLBACK_IMAGE)

                await client(EditPhotoRequest(
                    channel=chat,
                    photo=await client.upload_file(img)
                ))
            except Exception as e:
                print("Photo error:", e)

            # ======================
            # SAVE DEAL
            # ======================
            link = f"https://t.me/c/{str(chat_id)[4:]}"

            deals[chat_id] = {
                "amount": amount,
                "link": link,
                "locked": False
            }

            # ======================
            # DM MESSAGE (GRAS)
            # ======================
            await event.reply(
                "**Merci de partager le lien du groupe seulement avec la personne concernée par le deal**\n\n"
                f"**{link}**",
                parse_mode="md"
            )

            # ======================
            # MESSAGE GROUPE
            # ======================
            await client.send_message(chat_id,
                "Merci de nous renseigner les informations suivantes:\n\n"
                "**1 • Qui est l’acheteur ? qui est le vendeur ?**\n"
                "**2 • Quel est le deal ? (détails complets)**\n"
                "**3 • Quel est le montant du deal ?**\n"
                "**4 • Quelle monnaie est utilisée ?**"
            )

            await event.delete()

        except Exception as e:
            await event.reply(f"Erreur .mm: {e}")

    # ======================
    # .fini
    # ======================
    elif text == ".fini":
        try:
            chat_id = event.chat_id
            deal = deals.get(chat_id)

            await event.delete()

            amount = deal["amount"] if deal else "xxx€"

            await client.send_message(chat_id,
                "Merci d’avoir utilisé incultes pour votre deal,\n\n"
                f"**N’oubliez pas de mettre un vouch de cet manière : Vouch @incultes mm {amount} . ( merci de mettre la valeur du deal ) il sera automatiquement transmis dans le canal @incultesvouches .**\n\n"
                "**⚠️ : Je vous rappelle que je ne vous contacterai jamais en premier, si quelqu’un vous contacte avec le même profil que moi, ce n’est pas moi !**"
            )

        except Exception as e:
            await event.reply(f"Erreur .fini: {e}")

    # ======================
    # .lock
    # ======================
    elif text == ".lock":
        try:
            chat_id = event.chat_id

            await event.delete()

            if chat_id in locked:
                return

            if chat_id not in deals:
                await event.reply("❌ Aucun deal enregistré.")
                return

            locked.add(chat_id)
            deals[chat_id]["locked"] = True

            rights = ChatBannedRights(
                until_date=None,
                send_messages=True
            )

            participants = await client.get_participants(chat_id)

            for user in participants:
                try:
                    await client(EditBannedRequest(chat_id, user, rights))
                except:
                    continue

            link = deals[chat_id]["link"]

            await client.send_message(
                "incultesvouches",
                f"un deal a été fini vous pouvez allez voir l’aperçu ici : {link}"
            )

        except Exception as e:
            await event.reply(f"Erreur .lock: {e}")


# ======================
# START
# ======================

print("Userbot lancé...")
client.start()
client.run_until_disconnected()
