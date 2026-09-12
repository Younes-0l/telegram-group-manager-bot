from telegram import Update
from telegram.ext import ContextTypes


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user=None):
    if user is None:
        user = update.effective_user
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    return any(admin.user.id == user.id for admin in admins)