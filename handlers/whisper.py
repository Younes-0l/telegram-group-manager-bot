from telegram import Update, MessageEntity
from telegram.ext import ContextTypes
from .settings import *
from repositories import users_repository, whisper_repository
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Forbidden
from telegram.constants import ParseMode


async def handle_whisper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    sender_id = update.effective_user.id

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        whisper_text = " ".join(context.args) if context.args else None

        if not whisper_text:
            await _reply_and_self_destruct(message, "لطفاً متن نجوا رو بعد از دستور بنویس.")
            return

        if target_user.is_bot:
            await _reply_and_self_destruct(message, "نمیشه به بات‌ها نجوا فرستاد 🤖")
            return

        if target_user.id == sender_id:
            await _reply_and_self_destruct(message, "نمیشه به خودت نجوا بفرستی 😄")
            return

        await _send_whisper(update, context, target_user.id, target_user.first_name, whisper_text)
        return

    if not context.args:
        await _reply_and_self_destruct(
            message,
            "استفاده صحیح:\n"
            "/whisper @username متن پیام\n"
            "یا: روی پیام شخص ریپلای کن و بنویس /whisper متن پیام"
        )
        return

    target_user_id = None

    for entity in message.entities or []:
        if entity.type == MessageEntity.TEXT_MENTION:
            target_user_id = entity.user.id
            break
        elif entity.type == MessageEntity.MENTION:
            mention_text = message.text[entity.offset: entity.offset + entity.length]
            username_clean = mention_text.lstrip("@")
            db_user = users_repository.get_user_by_username(username_clean)
            if db_user:
                target_user_id = db_user.telegram_id
            break

    if target_user_id is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ نتونستم این کاربر رو پیدا کنم.\n"
                 "بهتره روی پیام همون شخص ریپلای کنی و دستور /whisper رو بزنی."
        )
        await _try_delete_message(context, message.chat_id, message.message_id)
        return

    if target_user_id == sender_id:
        await _reply_and_self_destruct(message, "نمیشه به خودت نجوا بفرستی 😄")
        return

    whisper_text = " ".join(context.args[1:]) if len(context.args) > 1 else None
    if not whisper_text:
        await _reply_and_self_destruct(message, "لطفاً متن نجوا رو بعد از یوزرنیم بنویس.")
        return

    db_user = users_repository.get_user(target_user_id)
    display_name = db_user.full_name if db_user else "کاربر"
    await _send_whisper(update, context, target_user_id, display_name, whisper_text)


async def _reply_and_self_destruct(message, text: str):
    await message.reply_text(text)


async def _try_delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> bool:
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True
    except Forbidden:
        return False
    except BadRequest:
        return False


async def _send_whisper(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         target_id: int, target_display_name: str, whisper_text: str):
    sender = update.effective_user
    chat_id = update.effective_chat.id
    original_message_id = update.message.message_id

    deleted = await _try_delete_message(context, chat_id, original_message_id)

    if not deleted:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "⚠️ نتونستم پیام قبلی رو حذف کنم چون دسترسی ادمین ندارم.\n"
                "برای امنیت نجواها، لطفاً من رو با مجوز «حذف پیام‌ها» ادمین گروه کن "
                "و دوباره امتحان کن."
            ),
            reply_to_message_id=original_message_id
        )
        return
    
    sent_message = await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f'🤫 یک پیام نجوا از {sender.first_name} برای <a href="tg://user?id={target_id}">{target_display_name}</a>\n'
            f"فقط گیرنده می‌تونه محتوا رو ببینه."
        ),
        parse_mode=ParseMode.HTML
    )

    whisper = whisper_repository.create_whisper(
        sender_id=sender.id,
        target_id=target_id,
        text=whisper_text,
        chat_id=chat_id,
        message_id=sent_message.message_id
    )

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("نمایش پیام", callback_data=f"whisper_{whisper.id}")
    ]])
    await sent_message.edit_reply_markup(reply_markup=keyboard)

async def cleanup_job(context: ContextTypes.DEFAULT_TYPE):
    whisper_repository.delete_old_whispers(hours=24)

async def whisper_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    whisper_id = int(query.data.split("_", 1)[1])

    whisper = whisper_repository.get_whisper(whisper_id)

    if whisper is None:
        await query.answer("این پیام دیگر در دسترس نیست.", show_alert=True)
        return

    clicker_id = query.from_user.id

    if clicker_id not in (whisper.sender_id, whisper.target_id):
        await query.answer("این پیام برای شما نیست! 🙈", show_alert=True)
        return

    await query.answer(whisper.text, show_alert=True)

    if clicker_id == whisper.target_id and not whisper.is_read:
        whisper_repository.mark_whisper_read(whisper_id)