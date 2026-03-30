import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
ACCESS_KEY = os.environ["ACCESS_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]
IDENTIFIER = os.environ["IDENTIFIER"]

os.makedirs("downloads", exist_ok=True)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    file = msg.document or msg.video or msg.audio
    if not file:
        return

    tg_file = await context.bot.get_file(file.file_id)
    path = f"downloads/{file.file_name or file.file_id}"

    await tg_file.download_to_drive(path)

    with open(path, "rb") as f:
        requests.put(
            f"https://s3.us.archive.org/{IDENTIFIER}/{os.path.basename(path)}",
            data=f,
            headers={
                "authorization": f"LOW {ACCESS_KEY}:{SECRET_KEY}"
            }
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_file))

app.run_polling()
