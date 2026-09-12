import html
from telegram import Update
from telegram.ext import ContextTypes
from repositories import (
    message_repository, group_repository,
    warning_repository, mute_repository, member_events_repository
)


def _format_hour_range(hour: int) -> str:
    return f"{hour:02d}:00 - {(hour + 1) % 24:02d}:00"

async def report_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group = group_repository.create_or_get_group(
        update.effective_chat.id, update.effective_chat.title
    )

    users = message_repository.get_top_users(group.id, 5)
    messages_count = message_repository.today_messages_count(group.id)
    yesterday_count = message_repository.yesterday_messages_count(group.id)
    deleted_messages = message_repository.today_deleted_messages_count(group.id)
    warnings_count = warning_repository.today_warnings_count(group.id)
    mutes_count = mute_repository.today_mutes_count(group.id)
    busiest = message_repository.get_busiest_hour(group.id)
    joins_count = member_events_repository.today_joins_count(group.id)
    leaves_count = member_events_repository.today_leaves_count(group.id)

    if users:
        user_lines = [
            f"{i}. {html.escape(name)} — {count} پیام"
            for i, (name, count) in enumerate(users, start=1)
        ]
        users_text = "👑 فعال‌ترین اعضا:\n" + "\n".join(user_lines)
    else:
        users_text = "👑 فعال‌ترین اعضا:\nهنوز پیامی ثبت نشده"

    if yesterday_count > 0:
        diff_percent = round(((messages_count - yesterday_count) / yesterday_count) * 100)
        sign = "+" if diff_percent >= 0 else ""
        trend_text = f"{sign}{diff_percent}٪ نسبت به دیروز"
    elif messages_count > 0:
        trend_text = "دیروز پیامی نبود 📈"
    else:
        trend_text = "بدون تغییر"

    busiest_text = _format_hour_range(busiest[0]) if busiest else "هنوز داده‌ای نیست"

    lines = [
        "📊 گزارش امروز گروه",
        "━━━━━━━━━━━━━━",
        "",
        "💬 مجموع پیام‌ها:",
        f"{messages_count}",
        "",
        users_text,
        "",
        "━━━━━━━━━━━━━━",
        "",
        "🚫 پیام حذف‌شده:",
        f"{deleted_messages}",
        "",
        "⚠️ اخطارها:",
        f"{warnings_count}",
        "",
        "🔇 میوت‌ها:",
        f"{mutes_count}",
        "",
        "━━━━━━━━━━━━━━",
        "",
        "🔥 شلوغ‌ترین ساعت",
        busiest_text,
        "",
        "━━━━━━━━━━━━━━",
        "",
        "👋 اعضای جدید:",
        f"{joins_count}",
        "",
        "🚪 خروج اعضا:",
        f"{leaves_count}",
        "",
        "━━━━━━━━━━━━━━",
        "",
        "📈 نسبت به دیروز",
        trend_text,
    ]

    await context.bot.send_message(update.effective_chat.id, text="\n".join(lines))