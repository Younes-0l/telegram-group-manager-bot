from telegram import Update
from telegram.ext import ContextTypes


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = update.message.new_chat_members
    for m in members:
        await update.message.reply_text(f"{m.full_name} عزیز خوش اومدی")