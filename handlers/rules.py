from telegram.ext import ContextTypes
from telegram import Update
from .admin import is_admin
from handlers.settings import *
from repositories import group_repository
from services.helpers import schedule_delete


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    title = update.effective_chat.title
    rules = group_repository.get_rules(chat_id, title)

    if rules is not None:
        await update.message.reply_text(f"قوانین گروه:\n{rules}")
    else:
        msg = await update.message.reply_text(f'قانونی برای گروه تنظیم نشده، برای تنظیم\n/setrules "متن قوانین"')
        schedule_delete(context, msg)

async def set_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    chat_id = update.effective_chat.id
    title = update.effective_chat.title
    rules = None

    if context.args:
        try:
            rules = " ".join(context.args)
            group_repository.set_rules(chat_id, title, rules)
            await update.message.reply_text("متن قوانین گروه تنظیم شد.")
        except ValueError:
            pass
    else:
        msg = await update.message.reply_text('برای تنظیم قوانین متن خود را بنویسید، مثال:\n/setrules "متن قوانین"')
        schedule_delete(context, msg)

async def delete_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    
    chat_id = update.effective_chat.id
    title = update.effective_chat.title
    status = group_repository.delete_rules(chat_id, title)
    if status:
        msg = await update.message.reply_text(f'متن قوانین گروه پاک شد. برای تنظیم\n/setrules "متن قوانین"')
        schedule_delete(context, msg)
        