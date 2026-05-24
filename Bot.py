import os, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality, VideoQuality
from pytgcalls.types.input_stream import InputVideoStream, InputAudioStream
from pytgcalls.types.input_stream.video import VideoParameters

API_ID = os.environ.get("38278928")
API_HASH = os.environ.get("172472dcd05e016637e13d137708209e")
BOT_TOKEN = os.environ.get("8623984588:AAH7TtNf1V1vAOwaM33Gu7wv7Pf0jrY55mQ")

app = Client("film_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

downloading = {}
playing = {}

@app.on_message(filters.command("oynat") & filters.group & filters.reply)
async def oynat(client, message: Message):
    reply = message.reply_to_message
    chat_id = message.chat.id

    if not reply.video and not (reply.document and reply.document.mime_type and "video" in reply.document.mime_type):
        await message.reply("❌ Bir video mesajına reply ver!")
        return

    if chat_id in downloading:
        await message.reply("⏳ Zaten bir film indiriliyor, bekle.")
        return

    downloading[chat_id] = True
    status = await message.reply("⏬ Film indiriliyor...")

    try:
        file_path = await reply.download(progress=lambda c, t: None)
    except Exception as e:
        await status.edit(f"❌ İndirme hatası: {e}")
        downloading.pop(chat_id, None)
        return

    downloading.pop(chat_id, None)
    await status.edit("🎬 Video call başlatılıyor...")

    try:
        if chat_id in playing:
            await pytgcalls.leave_group_call(chat_id)

        await pytgcalls.join_group_call(
            chat_id,
            InputVideoStream(
                source=file_path,
                parameters=VideoParameters(
                    width=1280,
                    height=720,
                    frame_rate=30,
                ),
            ),
            InputAudioStream(
                source=file_path,
            ),
        )
        playing[chat_id] = file_path
        await status.edit("▶️ Film oynuyor! Video call'a katılın.")

    except Exception as e:
        await status.edit(f"❌ Hata: {e}")

@app.on_message(filters.command("durdur") & filters.group)
async def durdur(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing:
        await message.reply("❌ Şu an bir şey oynatılmıyor.")
        return
    await pytgcalls.leave_group_call(chat_id)
    playing.pop(chat_id, None)
    await message.reply("⏹ Film durduruldu.")

pytgcalls.run()
