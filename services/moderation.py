from telegram.ext import ContextTypes
from telegram import ChatPermissions, Update
from repositories import mute_repository, users_repository, warning_repository
from services.helpers import format_datetime, parse_duration
from services.logger import mute_log, warn_log
from datetime import datetime, timezone
from handlers.settings import *
from database.models import Group, User


async def apply_mute(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User, reason: str, duration: datetime):
    mute_until = datetime.now(timezone.utc) + duration

    await context.bot.restrict_chat_member(
        chat_id=group.chat_id,
        user_id=user.telegram_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=mute_until
    )

    mute = mute_repository.mute(group.id, user.id, moderator.id, reason, mute_until)
    formatted = format_datetime(mute.muted_until)
    await mute_log(context, group, user, moderator, formatted, reason)

    return formatted

async def apply_warn(context: ContextTypes.DEFAULT_TYPE, group: Group, user: User, moderator: User, reason: str):
    warn, warnings_count = warning_repository.add_warn(group.id, user.id, moderator.id, reason)
    await warn_log(context, group, user, moderator, reason)


    if warnings_count >= MAX_WARN:
        duration = parse_duration(f"{MUTE_TIME}m")
        warning_repository.clear_warns(group.id, user.id)
        reason = "دریافت اخطار زیاد."
        formatted = await apply_mute(context, group, user, moderator.id, reason, duration)
        return True, warn.reason, formatted
    
    else:
        return False, warn.reason, warnings_count

async def cache_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.username:
        context.bot_data.setdefault("username_map", {})
        context.bot_data["username_map"][user.username.lower()] = user.id

async def sync_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        users_repository.create_or_update_user(
            telegram_id=user.id,
            full_name=user.full_name,
            username=user.username
        )