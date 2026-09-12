from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .settings import *
from .admin import is_admin
import time
from repositories import bad_words_repository, group_repository, users_repository, message_repository,        member_events_repository
from services.statistics import report_message
from services.moderation import apply_warn, cache_user, sync_user
from services.helpers import get_target_member_data, has_link, schedule_delete


async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        return
    
    msg = update.message
    chat = update.effective_chat
    user = update.effective_user

    now = int(time.time())
    data = context.chat_data.setdefault(user.id, {
        "times": [],
    })
    data["times"].append(now)
    data["times"] = [t for t in data["times"] if now - t <= SPAM_TIME]

    if len(data["times"]) >= SPAM_REPEAT:
        tel_user, group, user = get_target_member_data(update)
        status, value = await apply_warn(context, group, user)
        try:
            await msg.delete()
        except Exception:
            pass

        data["times"] = []
        if status:
            await chat.send_message(f'<a href="tg://user?id={user.id}">{user.full_name}</a> به دلیل اسپم تا {value} میوت شد!', parse_mode=ParseMode.HTML)
        else:
            msg = await chat.send_message(f'<a href="tg://user?id={user.id}">{user.full_name}</a> کاربر عزیز لطفا اسپم نکن ({value}/{MAX_WARN})', parse_mode=ParseMode.HTML)
            schedule_delete(context, msg)


async def delete_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        return

    msg = update.message
    user = update.effective_user

    await msg.delete()
    msg = await context.bot.send_message(
        chat_id=msg.chat.id,
        text=(f'<a href="tg://user?id={user.id}">{user.full_name}</a> عزیز لطفا لینک نفرست!'),
        parse_mode=ParseMode.HTML
    )
    schedule_delete(context, msg, 60)

async def handle_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
            return

    msg = update.message
    user = update.effective_user
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    group_id = group.id
    bad_words = bad_words_repository.get_bad_words(group_id)

    for bw in bad_words:
        text = msg.text.lower()
        if bw.word in text:
            
            await msg.delete()
            msg = await context.bot.send_message(
                chat_id=msg.chat.id,
                text=(f'<a href="tg://user?id={user.id}">{user.full_name}</a> عزیز لطفا از ارسال کلمات ممنوعه خودداری کنید!'),
                parse_mode=ParseMode.HTML
            )
            schedule_delete(context, msg, 60)
            return

ACTIVE_STATUSES = {"member", "administrator", "creator"}

async def track_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    was_active = old_status in ACTIVE_STATUSES
    is_active = new_status in ACTIVE_STATUSES

    if was_active == is_active:
        return

    tel_user = result.new_chat_member.user
    group = group_repository.create_or_get_group(
        update.effective_chat.id, update.effective_chat.title
    )
    user = users_repository.create_or_update_user(
        telegram_id=tel_user.id,
        full_name=tel_user.full_name,
        username=tel_user.username
    )

    if not was_active and is_active:
        member_events_repository.add_event(group.id, user.id, "joined")
    elif was_active and not is_active:
        member_events_repository.add_event(group.id, user.id, "left")
    
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

async def daily_report_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = group_repository.get_all_groups()
    for group in groups:
        await report_message(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group = group_repository.create_or_get_group(update.effective_chat.id, update.effective_chat.title)
    tel_user = update.effective_user
    user = users_repository.create_or_get_user(tel_user.id, tel_user.full_name, tel_user.username)

    message_repository.save_message(
        group_id=group.id,
        user_id=user.id,
        message_id=update.message.id
    )

    await cache_user(update, context)
    await sync_user(update, context)

    try:
        # await anti_spam(update, context)

        await handle_bad_words(update, context)

        # if has_link(update.message):
            # await delete_link(update, context)

    except Exception as e:
        print(f"Error: {e}")