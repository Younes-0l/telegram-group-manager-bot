from repositories.logs_repository import get_user_logs
from services.logger import _ACTION_LABELS
from services.helpers import format_datetime, get_reply_member_data, schedule_delete
from telegram.ext import ContextTypes
from telegram import Update
import html


async def handle_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tel_user, group, user = get_reply_member_data(update)

    logs = get_user_logs(group.id, user.id, limit=10)

    if not logs:
        msg = await update.message.reply_text("این کاربر هیچ سابقه‌ای نداره ✅")
        schedule_delete(context, msg)
        return

    lines = []
    for log in logs:
        label = _ACTION_LABELS.get(log.action, log.action)
        date_str = format_datetime(log.created_at)
        line = f"{label} — {date_str}"
        if log.details:
            line += f"\n     <i>{html.escape(log.details)}</i>"
        lines.append(line)

    safe_name = html.escape(tel_user.full_name)
    text = (
        f"📋 <b>تاریخچه‌ی</b> "
        f'<a href="tg://user?id={tel_user.id}">{safe_name}</a>\n\n'
        + "\n\n".join(lines)
    )

    msg = await update.message.reply_text(text, parse_mode="HTML")
    schedule_delete(context, msg, seconds=60)