from repositories import group_repository, users_repository
from telegram.ext import ContextTypes
from zoneinfo import ZoneInfo
from handlers.admin import is_admin
from telegram.constants import MessageEntityType
from telegram import Update
import re
from datetime import timedelta


def get_target_user(update: Update):

    msg = update.message.reply_to_message

    if msg:
        return msg.from_user

    return update.effective_user

def get_reply_user(update: Update):
    if update.message.reply_to_message is None:
        return None

    return update.message.reply_to_message.from_user

def get_reply_member_data(update: Update):
    tel_user = get_reply_user(update)
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    user = users_repository.create_or_get_user(tel_user.id, tel_user.full_name, tel_user.username)
    return tel_user, group, user

def get_target_member_data(update: Update):
    tel_user = get_target_user(update)
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    user = users_repository.create_or_get_user(tel_user.id, tel_user.full_name, tel_user.username)
    return tel_user, group, user

def format_datetime(dt):
    if dt is None:
        return "دائمی"
    return dt.astimezone(ZoneInfo("Asia/Tehran")).strftime("%Y/%m/%d - %H:%M")

async def check_requirements(update: Update, context):
    if not await is_admin(update, context):
        return False

    tel_user = get_reply_user(update)


    if tel_user is None:
        msg = await update.message.reply_text("روی پیام کاربر ریپلای کن.")
        schedule_delete(context, msg)
        return False
    
    if tel_user.is_bot:
        await update.message.reply_text("نمیشه بات‌ها رو میوت کرد 🤖")
        return False
    
    if await is_admin(update, context, tel_user):
        msg = await update.message.reply_text("کاربر ادمین می‌باشد")
        schedule_delete(context, msg)
        return False
    
    return True

def has_link(message):
    if not message.entities:
        return False

    return any(
        entity.type in (
            MessageEntityType.URL,
            MessageEntityType.TEXT_LINK,
        )
        for entity in message.entities
    )

def parse_duration(text: str):
    m = re.fullmatch(r"(\d+)([mhd])", text.lower())

    if not m:
        return None

    value = int(m.group(1))
    unit = m.group(2)

    if unit == "m":
        return timedelta(minutes=value)

    if unit == "h":
        return timedelta(hours=value)

    if unit == "d":
        return timedelta(days=value)

def schedule_delete(context, message, seconds=30):
    context.job_queue.run_once(
        delete_message_job,
        when=seconds,
        data={
            "chat_id": message.chat.id,
            "message_id": message.message_id,
        },
    )

async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data

    try:
        await context.bot.delete_message(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
        )
    except Exception:
        pass

async def check_bot_permissions(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    return getattr(bot_member, "can_delete_messages", False)