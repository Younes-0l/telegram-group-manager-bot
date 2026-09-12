from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .settings import *
from services.helpers import check_requirements, get_reply_user, get_reply_member_data
from services.logger import ban_log, unban_log
from repositories import group_members_repository

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return

    tel_user = get_reply_user(update)

    await context.bot.ban_chat_member(
        update.effective_chat.id,
        tel_user.id
    )

    await context.bot.unban_chat_member(
        update.effective_chat.id,
        tel_user.id
    )



    await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> کیک شد!', parse_mode=ParseMode.HTML)

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return
    
    tel_user, group, user = get_reply_member_data(update)

    await context.bot.ban_chat_member(
        update.effective_chat.id,
        tel_user.id
    )
    
    _, moderator = group_members_repository.resolve_ids(update.effective_chat.id, update.effective_user.id)
    await ban_log(context, group, user, moderator)


    await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> بن شد!', parse_mode=ParseMode.HTML)

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_requirements(update, context):
        return

    tel_user, group, user = get_reply_member_data(update)

    await context.bot.unban_chat_member(
        update.effective_chat.id,
        tel_user.id
    )

    _, moderator = group_members_repository.resolve_ids(update.effective_chat.id, update.effective_user.id)
    await unban_log(context, group, user, moderator)

    await update.message.reply_text(f'<a href="tg://user?id={tel_user.id}">{tel_user.full_name}</a> از بن خارج شد', parse_mode=ParseMode.HTML)

