from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from .settings import *
from .admin import is_admin
from repositories import message_repository, group_repository


async def delete_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    to_message_id = update.message.reply_to_message.id
    
    await context.bot.delete_message(chat_id, to_message_id)
    message_repository.mark_as_deleted(
        group.id,
        to_message_id,
    )

async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int):
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    messages = message_repository.get_last_messages(group.id, count)
    for message in messages:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=message.message_id,
            )

            message_repository.mark_as_deleted(
                group.id,
                message.message_id,
            )

        except TelegramError:
            pass

async def handle_delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    
    message_id = update.message.id
    chat_id = update.effective_chat.id
    count = None

    if context.args:
        try:
            count = min(int(context.args[0]), MAX_PURGE)
        except ValueError:
            pass

    if update.message.reply_to_message:
        await delete_reply_message(update, context)

    elif count is not None:
        await purge_messages(update, context, count)
    
    await context.bot.delete_message(chat_id, message_id)