import os
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("CJ_BOT_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0")) or None

HELP_TEXT = """
📖 <b>راهنمای ربات مدیریت گروه</b>
━━━━━━━━━━━━━━

👤 <b>دستورات عمومی</b>

/rules — نمایش قوانین گروه
/report — گزارش آماری امروز گروه
/whisper — ارسال پیام نجوا 🤫
    <i>روی پیام شخص ریپلای کن و بنویس:</i>
    <code>/whisper متن پیام</code>

━━━━━━━━━━━━━━

🛡 <b>دستورات مدیریتی</b> (فقط ادمین‌ها)

<b>▫️ مدیریت اخطار</b>
<code>/warn</code> — ثبت اخطار (ریپلای + دلیل)
<code>/removewarn</code> — کم کردن یک اخطار (ریپلای)
<code>/clearwarn</code> — پاک کردن همه‌ی اخطارها (ریپلای)
<code>/getwarn</code> — نمایش لیست اخطارهای کاربر (ریپلای)

<b>▫️ میوت و بن</b>
<code>/mute [مدت] [دلیل]</code> — میوت کردن (ریپلای)
    مثال: <code>/mute 1h اسپم</code>
    برای میوت دائمی: <code>/mute 0</code>
<code>/unmute</code> — خارج کردن از میوت (ریپلای)
<code>/ban</code> — بن کردن (ریپلای)
<code>/unban</code> — آنبن کردن (ریپلای)
<code>/kick</code> — اخراج از گروه (ریپلای)

<b>▫️ فیلتر کلمات</b>
<code>/addfilter کلمه</code> — افزودن کلمه‌ی ممنوعه
<code>/removefilter کلمه</code> — حذف کلمه‌ی ممنوعه
<code>/getfilter</code> — نمایش لیست کلمات فیلترشده

<b>▫️ مدیریت پیام‌ها</b>
<code>/delete</code> — حذف پیام (ریپلای)
<code>/delete [تعداد]</code> — حذف چند پیام اخیر
    مثال: <code>/delete 10</code>

<b>▫️ قوانین گروه</b>
<code>/setrules متن</code> — تنظیم قوانین گروه
<code>/deleterules</code> — حذف قوانین گروه

<b>▫️ سوابق</b>
<code>/logs</code> — نمایش تاریخچه‌ی کاربر (ریپلای)

━━━━━━━━━━━━━━
💡 <i>در اکثر دستورات مدیریتی، کافیه روی پیام کاربر موردنظر ریپلای کنی.</i>
"""


SPAM_TIME = 2
SPAM_REPEAT = 5
MUTE_TIME = 2
MAX_WARN = 3

MAX_PURGE = 100