from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .settings import *
from repositories import group_members_repository, warning_repository
from services.helpers import get_reply_member_data, get_target_member_data, check_requirements, schedule_delete
from services.moderation import apply_warn
import html


async def add_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return

    tel_user, group, user = get_reply_member_data(update)
    reason = " ".join(context.args) if context.args else None
    _, moderator = group_members_repository.resolve_ids(update.effective_chat.id, update.effective_user.id)

    status, reason, value = await apply_warn(context, group, user, moderator, reason)
    if status:    
        msg = await update.message.reply_text(f'🔊 <a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> تا {value} میوت شد!\nدلیل: {reason if reason is not None else ""}، دریافت اخطار زیاد.', parse_mode=ParseMode.HTML)

    else:
        if reason is not None:
            msg = await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a>به دلیل {reason} اخطار گرفت! ({value}/{MAX_WARN})', parse_mode=ParseMode.HTML)
        else:
            msg = await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> اخطار گرفت! ({value}/{MAX_WARN})', parse_mode=ParseMode.HTML)

    schedule_delete(context, msg)

async def remove_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return
    
    tel_user, group, user = get_reply_member_data(update)
    warnings_count = warning_repository.get_warn_count(group.id, user.id)

    if warnings_count == 0:
        msg = await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> کاربر هیچ اخطاری ندارد! ({warnings_count}/{MAX_WARN})', parse_mode=ParseMode.HTML)
        return
    
    else:
        warnings_count = warning_repository.remove_last_warning(group.id, user.id)
        msg = await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> یکی از اخطار های کاربر حذف شد. ({warnings_count}/{MAX_WARN})', parse_mode=ParseMode.HTML)

    schedule_delete(context, msg)

async def get_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tel_user, group, user = get_target_member_data(update)
    warnings = warning_repository.get_active_warnings_count(group.id, user.id)
    safe_name = html.escape(tel_user.full_name)

    
    if not warnings:
        text = (
            f'<a href="tg://user?id={tel_user.id}">{safe_name}</a> '
            f"هیچ اخطار فعالی نداره ✅"
        )
        msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)    

    else:
        lines = []
        for i, warn in enumerate(warnings, start=1):
            reason = html.escape(warn.reason) if warn.reason else "بدون دلیل ثبت‌شده"
            date_str = warn.created_at.strftime("%Y/%m/%d - %H:%M")
            lines.append(f"<b>{i}.</b> {reason}\n     <i>🗓 {date_str}</i>")

        warnings_text = "\n\n".join(lines)

        text = (
            f'⚠️ <b>لیست اخطارهای</b> '
            f'<a href="tg://user?id={tel_user.id}">{safe_name}</a>\n'
            f"تعداد: <b>{len(warnings)}</b> اخطار\n"
            f"{'─' * 20}\n\n"
            f"{warnings_text}"
        )
        msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    schedule_delete(context, msg)

async def clear_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not await check_requirements(update, context):
        return

    tel_user, group, user = get_reply_member_data(update)
    warn = warning_repository.get_warn_count(group.id, user.id)

    if warn == 0:
        msg = await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> کاربر هیچ اخطاری ندارد! ({warn}/{MAX_WARN})', parse_mode=ParseMode.HTML)
        return
    
    else:
        warning_repository.clear_warns(group.id, user.id)
        msg = await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a>.تمامی اخطار های کاربر حذف شد', parse_mode=ParseMode.HTML)

    schedule_delete(context, msg)