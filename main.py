from telegram.ext import ApplicationBuilder, CommandHandler, filters, MessageHandler, CallbackQueryHandler, ChatMemberHandler
from handlers import welcome, moderation, bad_words, purge, warning, mute, ban, rules, whisper, logs
from database.database import create_tables
from telegram import Update
from services.statistics import report_message, daily_report_job
from handlers.settings import TOKEN
from datetime import time
from zoneinfo import ZoneInfo


create_tables()

def main():
    print("Starting Bot ...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ChatMemberHandler(moderation.track_chat_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.welcome))

    app.add_handler(CommandHandler("rules", rules.rules))
    app.add_handler(CommandHandler("setrules", rules.set_rules))
    app.add_handler(CommandHandler("deleterules", rules.delete_rules))

    app.add_handler(CommandHandler("report", report_message))

    app.add_handler(CommandHandler("warn", warning.add_warn))
    app.add_handler(CommandHandler("removewarn", warning.remove_warn))
    app.add_handler(CommandHandler("getwarn", warning.get_warns))
    app.add_handler(CommandHandler("clearwarn", warning.clear_warn))

    app.add_handler(CommandHandler("mute", mute.mute))
    app.add_handler(CommandHandler("unmute", mute.unmute))
    
    app.add_handler(CommandHandler("ban", ban.ban))
    app.add_handler(CommandHandler("unban", ban.unban))
    app.add_handler(CommandHandler("kick", ban.kick))

    app.add_handler(CommandHandler("addfilter", bad_words.add_filter))
    app.add_handler(CommandHandler("removefilter", bad_words.remove_filter))
    app.add_handler(CommandHandler("getfilter", bad_words.get_filters))


    app.add_handler(CommandHandler("delete", purge.handle_delete_command))

    app.add_handler(CommandHandler("help", moderation.help))
    app.add_handler(CommandHandler("logs", logs.handle_history_command))
    
    app.add_handler(MessageHandler(filters.ALL, moderation.handle_message), group=-1)
    app.add_handler(CommandHandler("whisper", whisper.handle_whisper_command), group=0)
    app.add_handler(CallbackQueryHandler(whisper.whisper_callback, pattern=r"^whisper_\d+$"), group=0)
    app.job_queue.run_repeating(whisper.cleanup_job, interval=3600, first=10)
    
    app.job_queue.run_daily(moderation.daily_report_job,time=time(hour=23, minute=59, tzinfo=ZoneInfo("Asia/Tehran")))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
