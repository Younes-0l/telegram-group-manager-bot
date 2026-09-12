from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from telegram import ChatPermissions
from telegram.constants import ParseMode
from .settings import *
from repositories import group_members_repository, mute_repository
from services.helpers import check_requirements, get_reply_member_data, parse_duration, schedule_delete
from services.moderation import apply_mute


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return

    tel_user, group, user = get_reply_member_data(update)

    if not context.args:
        msg = await update.message.reply_text("لطفاً مدت‌زمان رو مشخص کن، مثلاً: /mute 1h")
        schedule_delete(context, msg)
        return

    duration_str = context.args[0]
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else None
    _, moderator = group_members_repository.resolve_ids(update.effective_chat.id, update.effective_user.id)

    if duration_str != "0":
        duration = parse_duration(duration_str)
        if duration is None:
            msg = await update.message.reply_text(
                "فرمت زمان اشتباهه. نمونه‌های درست: 30m, 2h, 1d, 1w"
            )
            schedule_delete(context, msg)
            return

    try:
        formatted = await apply_mute(context, group, user, moderator, reason, duration)
        duration_text = "دائمی" if formatted is None else f"تا {formatted}"
        text = f" تا ({duration_text}) میوت شد!"
        if reason:
            text += f"\nدلیل: {reason}"
        msg = await update.message.reply_text(f'🔇 <a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a>{text}', parse_mode=ParseMode.HTML)

    except TelegramError:
        msg = await update.message.reply_text(
            "ربات دسترسی لازم برای میوت کردن را ندارد."
        )
    except Exception as e:
        print(e)
        msg = await update.message.reply_text(
            "خطایی رخ داد."
        )
    
    schedule_delete(context, msg)

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return

    tel_user, group, user = get_reply_member_data(update)

    try:
        await context.bot.restrict_chat_member(
            chat_id=group.chat_id,
            user_id=user.telegram_id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        mute_repository.unmute(group.id, user.id)

        msg = await update.message.reply_text(f'🔊 <a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> از میوت خارج شد.', parse_mode=ParseMode.HTML)

    except TelegramError:
        msg = await update.message.reply_text(
            "ربات دسترسی لازم برای آنمیوت کردن را ندارد."
        )
    except Exception as e:
        print(e)
        msg = await update.message.reply_text(
            "خطایی رخ داد."
        )
    
    schedule_delete(context, msg)
   