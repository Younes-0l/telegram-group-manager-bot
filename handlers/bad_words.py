from telegram import Update
from telegram.ext import ContextTypes
from .settings import *
from .admin import is_admin
from repositories import bad_words_repository, group_repository
from services.helpers import schedule_delete


async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    group_id = group.id
    word = None

    if context.args:
        word = context.args[0].lower().strip() if context.args else None

    if word is not None:
        saved = bad_words_repository.save_bad_word(group_id, word)

        if saved:
            await update.message.reply_text("ثبت شد.")
        else:
            await update.message.reply_text("این کلمه قبلاً ثبت شده است.")

async def get_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    group_id = group.id
    bad_words = bad_words_repository.get_bad_words(group_id)

    if not bad_words:
        msg = await update.message.reply_text(
            "هیچ کلمه ممنوعه‌ای ثبت نشده است."
        )
        schedule_delete(context, msg)
        return

    text = "\n".join(word.word for word in bad_words)

    await update.message.reply_text(
        f"لیست کلمات ممنوعه:\n\n{text}"
    )

async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    if group is None:
        return
    
    group_id = group.id
    word = None

    if context.args:
        word = context.args[0].lower().strip() if context.args else None

    if word is not None:
        deleted = bad_words_repository.delete_bad_word(group_id, word)

        if deleted:
            msg = await update.message.reply_text("حذف شد.")
        else:
            msg = await update.message.reply_text("این کلمه وجود ندارد.")

        schedule_delete(context, msg)