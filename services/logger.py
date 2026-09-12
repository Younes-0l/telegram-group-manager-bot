from telegram.ext import ContextTypes
from repositories.logs_repository import add_log
from database.models.logs import LogAction
import html
from handlers.settings import LOG_CHANNEL_ID, MAX_WARN
from database.models import Group, User
from repositories import warning_repository


_ACTION_LABELS = {
    LogAction.WARN: "⚠️ اخطار",
    LogAction.UNWARN: "✅ حذف اخطار",
    LogAction.MUTE: "🔇 میوت",
    LogAction.UNMUTE: "🔊 آنمیوت",
    LogAction.BAN: "🚫 بن",
    LogAction.UNBAN: "✅ آنبن",
    LogAction.DELETE_MESSAGE: "🗑 حذف پیام",
    LogAction.BAD_WORD_DETECTED: "🤬 کلمه‌ی نامناسب",
    LogAction.WHISPER_SENT: "🤫 نجوا",
}


async def log_action(
    context: ContextTypes.DEFAULT_TYPE,
    action: LogAction,
    group_id: int | None = None,
    group_title: str | None = None,
    actor_id: int | None = None,
    actor_name: str | None = None,
    target_id: int | None = None,
    target_name: str | None = None,
    details: str | None = None,
):
    add_log(
        action=action,
        group_id=group_id,
        actor_id=actor_id,
        target_id=target_id,
        details=details,
    )

    if LOG_CHANNEL_ID is None:
        return

    label = _ACTION_LABELS.get(action, action.value)
    lines = [f"{label}"]

    if group_title:
        lines.append(f"📍 گروه: {html.escape(group_title)}")
    if actor_name:
        lines.append(f"👮 توسط: {html.escape(actor_name)}")
    if target_name:
        lines.append(f"🎯 روی: {html.escape(target_name)}")
    if details:
        lines.append(f"📝 جزئیات: {html.escape(details)}")

    text = "\n".join(lines)

    try:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Failed to send log to channel: {e}")


async def warn_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User, reason: str):
    warnings_count = warning_repository.get_warn_count(group.id, user.id)
    await log_action(
        context,
        action=LogAction.WARN,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details=f"اخطار ({warnings_count} / {MAX_WARN})" + (f" | دلیل: {reason}" if reason else "")
    )

async def unwarn_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User):
    warnings_count = warning_repository.get_warn_count(group.id, user.id)
    await log_action(
        context,
        action=LogAction.UNWARN,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details=f"اخطار حذف شد ({warnings_count} / {MAX_WARN})"
    )

async def mute_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User, formatted, reason: str):    
    await log_action(
        context,
        action=LogAction.MUTE,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details=f"مدت: {formatted}" + (f" | دلیل: {reason}" if reason else "")
       )
    
async def unmute_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User):    
    await log_action(
        context,
        action=LogAction.UNMUTE,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details="از میوت خارج شد"
       )

async def ban_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User):    
    await log_action(
        context,
        action=LogAction.BAN,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details="بن شد"
       )

async def unban_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User):    
    await log_action(
        context,
        action=LogAction.UNBAN,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details="از بن خارج شد"
       )
    
async def delete_message_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User, count):

    await log_action(
        context,
        action=LogAction.DELETE_MESSAGE,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details=f"پیام حذف شد" + (f" | تعداد: {count}" if count else "1")
       )
    
async def bad_word_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User, word: str):

    await log_action(
        context,
        action=LogAction.BAD_WORD_DETECTED,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details=f"پیام ممنوعه حذف شد ({word})"
       )

async def whisper_log(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User):
    
    await log_action(
        context,
        action=LogAction.WHISPER_SENT,
        group_id=group.id,
        group_title=group.title,
        actor_id=moderator.id,
        actor_name=moderator.full_name,
        target_id=user.id,
        target_name=user.full_name,
        details="یک پیام نجوا شد"
       )