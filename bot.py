// --- START FILE: bot.py ---
import os
import random
import time
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus # Import ChatMemberStatus for checking member status

# ✅ حذف جميع الملفات التي قد تسبب قفل قاعدة البيانات (ملاحظة: هذا سيؤدي إلى فقدان البيانات عند كل إعادة تشغيل)
for file in ["ProtectionBot.session", "ProtectionBot.session-journal", "bot.sqlite3"]:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"Removed {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")


# بيانات البوت (يُفضل استخدام متغيرات البيئة بدلاً من كتابتها هنا مباشرةً لأسباب أمنية)
api_id = 26977113
api_hash = "9248c3a0471142764cb438997f287285"
bot_token = "8100374611:AAHNFZKrJUc4hhdqeVr0woAWw9RdCD2Ddg8"

# تشغيل البوت
app = Client("ProtectionBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# تخزين الرتب (المفتاح هو الآيدي، القيمة True للدلالة على وجود الرتبة)
# تم توحيد تعريف الرتب هنا
ranks = {
    "the_goat": {"7601607055": True},  # The GOAT خاص بالمطور الأساسي فقط
    "dev": {},         # رتبة المطورين الثانويين
    "m": {},           # رتبة M
    "owner_main": {},  # المالك الأساسي
    "owner": {},       # المالك
    "creator": {},     # المنشئ (يُقصد منشئ القروب في تليجرام تلقائياً، أو رتبة تمنح يدوياً)
    "admin": {},       # المدير (رتبة إدارية)
    "moderator": {},   # الأدمن (رتبة إشرافية أقل)
    "vip": {},         # المميز (رتبة شرفية بصلاحيات محدودة أو بدون)
    "supervisor": {},  # المشرف (رتبة إشرافية)
    "beautiful": {}    # العضو الجميل 🌟 (رتبة شرفية بدون صلاحيات)
}

# ترتيب الرتب من الأقوى للأضعف (كلما زاد الرقم زادت القوة)
rank_order = {
    "the_goat": 10, # أعلى رتبة
    "dev": 9,
    "m": 8,
    "owner_main": 7,
    "owner": 6,
    "creator": 5,  # المنشئ الطبيعي للقروب يملك صلاحيات، هذه رتبة يمكن منحها يدوياً مع صلاحيات
    "admin": 4,
    "moderator": 3,
    "vip": 2,
    "supervisor": 1,
    "beautiful": 0  # العضو الجميل بدون صلاحيات
}

# أسماء الرتب للعرض في الرسائل
rank_display_names = {
    "the_goat": "The GOAT",
    "dev": "المطور",
    "m": "M",
    "owner_main": "المالك الأساسي",
    "owner": "المالك",
    "creator": "المنشئ",
    "admin": "المدير",
    "moderator": "الأدمن",
    "vip": "المميز",
    "supervisor": "المشرف",
    "beautiful": "العضو الجميل"
}

# 🛠 دوال مساعدة للحصول على معلومات المستخدم والرتب 🛠

def get_target_user(client, message, allow_self=False):
    """
    الحصول على المستخدم المستهدف من الرد على رسالة أو من المعرف/الآيدي في نص الأمر.
    يعيد (كائن المستخدم, رسالة الخطأ)
    """
    user = None
    error_message = None

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        # البحث عن المعرف أو الآيدي بعد الأمر الأول
        text_parts = message.text.split()
        if len(text_parts) > 1:
            user_arg = text_parts[1] # الجزء الثاني من النص بعد الأمر

            try:
                if user_arg.startswith('@'):
                    # البحث عن طريق المعرف
                    user = client.get_users(user_arg)
                else:
                    # البحث عن طريق الآيدي
                    user = client.get_users(int(user_arg))
            except Exception:
                error_message = "❌ **لم يتم العثور على المستخدم. تأكد من إدخال المعرف أو الآيدي الصحيح!**"
                return None, error_message
        else:
             error_message = "❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**"
             return None, error_message

    if user and not allow_self and str(user.id) == str(message.from_user.id):
         return None, "❌ **لا يمكنك تنفيذ هذا الأمر على نفسك!**"

    if user and user.is_bot:
         return None, "❌ **لا يمكنك تنفيذ هذا الأمر على بوت آخر!**"


    return user, error_message

def get_user_highest_rank(user_id_str):
    """
    الحصول على أعلى رتبة يمتلكها المستخدم وقوتها بناءً على ترتيب الرتب.
    يعيد (اسم الرتبة, قوة الرتبة) أو (None, -inf) إذا لم يمتلك رتبة
    """
    highest_rank = None
    highest_order = -float('inf')

    for rank, users in ranks.items():
        if user_id_str in users:
            order = rank_order.get(rank, -float('inf'))
            if order > highest_order:
                highest_order = order
                highest_rank = rank
    return highest_rank, highest_order

# 👑 أوامر إدارة الرتب 👑

# رفع رتبة لمستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def promote_user_cmd(client, message):
    text = message.text.split()
    if len(text) < 3 or text[0] != "رفع":
        return

    rank_key_arg = text[1].lower()
    user_arg = text[2] if len(text) > 2 else None

    # البحث عن مفتاح الرتبة الداخلي من النص المُدخل (السماح بالاسم العربي أو المفتاح)
    target_rank_key = None
    for key, display in rank_display_names.items():
         if display.lower() == rank_key_arg or key == rank_key_arg:
              target_rank_key = key
              break

    if target_rank_key is None:
        return message.reply_text("❌ **الرتبة غير موجودة!**\nالرتب المتاحة: " + " - ".join(rank_display_names.values()))

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    target_user_id = str(user.id)
    target_highest_rank, target_order = get_user_highest_rank(target_user_id)
    target_rank_order_value = rank_order.get(target_rank_key, -float('inf'))

    # التحقق من أن الرافع أعلى من المرفوع
    if sender_order < target_rank_order_value:
        return message.reply_text(f"❌ **لا يمكنك رفع شخص إلى رتبة ({rank_display_names.get(target_rank_key, target_rank_key)}) أعلى من رتبتك!**")

    # التحقق من أن الرتبة الجديدة أعلى من الرتبة الحالية للمستخدم (إذا كان لديه رتبة)
    if target_highest_rank is not None and target_rank_order_value <= target_order:
         return message.reply_text(f"❌ **لا يمكنك رفع شخص إلى رتبة ({rank_display_names.get(target_rank_key, target_rank_key)}) مساوية أو أقل من رتبته الحالية ({rank_display_names.get(target_highest_rank, target_highest_rank)})!**")

    # إزالة الرتبة القديمة (إذا كان يمتلك واحدة، واختياري حسب المنطق المطلوب - هنا نفترض أن الشخص يمكن أن يمتلك رتبة واحدة فقط)
    # if target_highest_rank:
    #     del ranks[target_highest_rank][target_user_id]

    # إضافة الرتبة الجديدة (نضيفها فقط، مما يعني يمكن للمستخدم امتلاك عدة رتب، أو نعدل الكود ليحتفظ بأعلى رتبة فقط)
    # بما أن نظام الترتيب يعتمد على "أعلى رتبة"، فالسماح بامتلاك عدة رتب لا يضر، لكن أوامر "تنزيل" يجب أن تكون دقيقة.
    # لنبقي على إمكانية امتلاك عدة رتب كما يبدو في البناء الأصلي للـ `ranks`.

    ranks[target_rank_key][target_user_id] = True
    message.reply_text(f"✅ **تم رفع {user.mention} إلى {rank_display_names.get(target_rank_key, target_rank_key)} بنجاح!**", parse_mode="HTML")


# تنزيل رتبة لمستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def demote_user_cmd(client, message):
    text = message.text.split()
    if len(text) < 3 or text[0] != "تنزيل":
        return

    rank_key_arg = text[1].lower()
    user_arg = text[2] if len(text) > 2 else None

    # البحث عن مفتاح الرتبة الداخلي من النص المُدخل
    target_rank_key = None
    for key, display in rank_display_names.items():
         if display.lower() == rank_key_arg or key == rank_key_arg:
              target_rank_key = key
              break

    if target_rank_key is None:
        return message.reply_text("❌ **الرتبة غير موجودة!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    target_user_id = str(user.id)
    target_rank_order_value = rank_order.get(target_rank_key, -float('inf'))

    # التحقق من أن الرافع أعلى من الرتبة المراد تنزيلها
    if sender_order < target_rank_order_value:
        return message.reply_text(f"❌ **لا يمكنك تنزيل رتبة ({rank_display_names.get(target_rank_key, target_rank_key)}) أعلى من رتبتك!**")

    # التحقق من أن المستخدم يمتلك هذه الرتبة
    if target_user_id not in ranks.get(target_rank_key, {}):
        return message.reply_text(f"❌ **المستخدم {user.mention} لا يمتلك هذه الرتبة ({rank_display_names.get(target_rank_key, target_rank_key)})!**", parse_mode="HTML")

    # إزالة الرتبة
    del ranks[target_rank_key][target_user_id]
    message.reply_text(f"✅ **تم تنزيل {user.mention} من {rank_display_names.get(target_rank_key, target_rank_key)}!**", parse_mode="HTML")

# التحقق من رتبة المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def my_rank_cmd(client, message):
    if message.text != "رتبتي":
        return

    user_id = str(message.from_user.id)
    # الحصول على جميع رتب المستخدم وعرضها بأسماء العرض
    user_ranks_display = [
        rank_display_names.get(rank, rank) for rank, users in ranks.items() if user_id in users
    ]

    if user_ranks_display:
        message.reply_text(f"👑 **رتبتك:** `{', '.join(user_ranks_display)}`")
    else:
        message.reply_text("❌ **ما عندك أي رتبة في البوت!**")

# أمر "تنزيل الكل" - إزالة جميع الرتب الممنوحة يدوياً للمستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_all_ranks_cmd(client, message):
    text = message.text.split()
    if len(text) < 3 or text[0] != "تنزيل" or text[1] != "الكل":
        return # Not "تنزيل الكل" command

    user_arg = text[2] if len(text) > 2 else None

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    target_user_id = str(user.id)
    target_highest_rank, target_order = get_user_highest_rank(target_user_id)

    # التحقق من أن الرافع أعلى من المرفوع
    if sender_order <= target_order:
         return message.reply_text("❌ **لا يمكنك إزالة رتب من شخص رتبته مساوية أو أعلى منك!**")

    removed_ranks_count = 0
    for rank_key in ranks:
        if target_user_id in ranks[rank_key]:
            del ranks[rank_key][target_user_id]
            removed_ranks_count += 1

    if removed_ranks_count > 0:
        message.reply_text(f"✅ **تم إزالة جميع الرتب الممنوحة يدوياً عن {user.mention}!**", parse_mode="HTML")
    else:
        message.reply_text(f"ℹ️ **المستخدم {user.mention} لا يمتلك أي رتب ممنوحة يدوياً لإزالتها!**", parse_mode="HTML")


# كشف معلومات المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def check_user_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "كشف":
        # Check if the 'كشف' command is locked in this group
        # Note: lock_unlock_commands affects group_settings
        # The original code checked protection_settings, let's make it use group_settings for consistency
        if chat_id in group_settings and group_settings[chat_id].get("كشف", False):
            return message.reply_text("🚫 **أمر كشف مقفل في هذا القروب!**")

        # Get target user
        user, error_message = get_target_user(client, message, allow_self=True) # Allow checking self

        if error_message:
             # If no user provided but command is "كشف", default to sender
             if message.text.lower() == "كشف":
                 user = message.from_user
                 error_message = None # Clear error as we default to sender
             else:
                 return message.reply_text(error_message)


        user_id = user.id
        username = f"@{user.username}" if user.username else "🚫 لا يوجد معرف"
        full_name = user.first_name + (" " + user.last_name if user.last_name else "")
        is_bot = "✅ نعم" if user.is_bot else "❌ لا"

        # Get user's ranks in the bot system
        user_ranks_display = [
            rank_display_names.get(rank, rank) for rank, users in ranks.items() if str(user_id) in users
        ]
        ranks_text = "، ".join(user_ranks_display) if user_ranks_display else "🚫 لا يوجد"

        # Get user's status in the chat (owner, admin, member, restricted, etc.)
        chat_member = None
        try:
             chat_member = client.get_chat_member(message.chat.id, user_id)
        except Exception:
             # User might not be a member, or bot lacks permission
             pass

        chat_status_text = "👤 **عضو عادي**"
        if chat_member:
             if chat_member.status == ChatMemberStatus.OWNER:
                  chat_status_text = "👑 **مالك القروب**"
             elif chat_member.status == ChatMemberStatus.ADMINISTRATOR:
                  chat_status_text = "🛡️ **مشرف القروب**"
             elif chat_member.status == ChatMemberStatus.RESTRICTED:
                  chat_status_text = "🚷 **مقيد في القروب**"
             elif chat_member.status == ChatMemberStatus.BANNED:
                  chat_status_text = "🚫 **محظور من القروب**"
             elif chat_member.status == ChatMemberStatus.LEFT:
                  chat_status_text = "🚪 **غادر القروب**"
             elif chat_member.status == ChatMemberStatus.BOT: # Should be handled by is_bot check, but good to have
                  chat_status_text = "🤖 **بوت**"


        message.reply_text(f"""
👤 **معلومات المستخدم:**
━━━━━━━━━━━━━
👤 **الاسم:** {full_name}
🆔 **الآيدي:** `{user_id}`
🔗 **المعرف:** {username}
🤖 **بوت:** {is_bot}
🏅 **رتبته في البوت:** {ranks_text}
🗳️ **حالة في القروب:** {chat_status_text}
━━━━━━━━━━━━━
""")

# 🔒 قفل وفتح الأوامر في القروب 🔒
group_settings = {} # إعدادات القروب (للقفل/الفتح، القوانين، الرابط، الردود التلقائية، إلخ)

@app.on_message(filters.text & filters.group & filters.incoming)
def lock_unlock_commands_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 2 or (text[0] != "قفل" and text[0] != "فتح"):
        return # Not a lock/unlock command

    command_or_feature = text[1].lower() # e.g., 'كشف', 'روابط', 'صور'

    # Check sender rank: only owner or main_owner can lock/unlock commands
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("owner", 0): # 'owner' rank or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**")

    if chat_id not in group_settings:
        group_settings[chat_id] = {}

    action = text[0] # "قفل" or "فتح"

    if action == "قفل":
        group_settings[chat_id][command_or_feature] = True
        message.reply_text(f"🔒 **تم قفل {command_or_feature} بنجاح!**")
    elif action == "فتح":
        group_settings[chat_id][command_or_feature] = False
        message.reply_text(f"🔓 **تم فتح {command_or_feature} بنجاح!**")

# 🚫 أوامر الإدارة (حظر، كتم، تقييد، إلخ) 🚫

# أمر حظر المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def ban_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("حظر"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for ban
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank in the bot's system
    if target_order >= sender_order:
         return message.reply_text("❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**")

    try:
        client.ban_chat_member(message.chat.id, user.id)
        message.reply_text(f"🚫 **تم حظر {user.mention} من القروب!**", parse_mode="HTML")
    except Exception as e:
         # Catch exceptions like insufficient bot permissions or targeting chat owner/admin
         message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية حظر في هذا القروب أو أن المستخدم الذي تحاول حظره أعلى من البوت رتبة في تليجرام.")

# أمر إلغاء الحظر
@app.on_message(filters.text & filters.group & filters.incoming)
def unban_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("الغاء الحظر"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for unban
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    # For unban, the target might not be in the group, so get_target_user might fail get_users
    # It's better to get the user ID from the argument directly or reply, and then try unbanning
    # Telegram unban works by ID even if user is not found by get_users.
    user_id_arg = None
    if message.reply_to_message:
        user_id_arg = str(message.reply_to_message.from_user.id)
    else:
        text_parts = message.text.split()
        if len(text_parts) > 2: # Expecting "الغاء الحظر [معرف/@ايدي]"
             user_id_arg = text_parts[2]

    if not user_id_arg:
        return message.reply_text("❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**")

    # Try to get user object for mention, but proceed with ID if fetch fails
    user_obj = None
    try:
        if user_id_arg.startswith('@'):
            user_obj = client.get_users(user_id_arg)
        else:
            user_obj = client.get_users(int(user_id_arg))
        target_user_id = user_obj.id
        mention_text = user_obj.mention
    except Exception:
        target_user_id = None
        mention_text = f"المستخدم ذو الآيدي `{user_id_arg}`" # Fallback mention


    if target_user_id is None:
         # If arg was not @username or a valid ID string
         return message.reply_text("❌ **الرجاء إدخال معرف مستخدم (@username) أو آيدي مستخدم صحيح بعد الأمر!**")

    # Optional: Check sender rank vs target rank if target is in ranks (less critical for unban)
    # target_highest_rank, target_order = get_user_highest_rank(str(target_user_id))
    # if target_order > sender_order: # Allow unbanning equal/lower ranks only?
    #     return message.reply_text("❌ **لا يمكنك إلغاء حظر شخص لديه رتبة أعلى منك!**")

    try:
        client.unban_chat_member(message.chat.id, target_user_id)
        message.reply_text(f"✅ **تم إلغاء حظر {mention_text} بنجاح!**", parse_mode="HTML")
    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما المستخدم ليس محظوراً أصلاً أو أن البوت لا يملك صلاحية إلغاء الحظر.")


# أمر طرد المستخدم (يتم بالحظر ثم فك الحظر فوراً)
@app.on_message(filters.text & filters.group & filters.incoming)
def kick_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("طرد"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for kick
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank
    if target_order >= sender_order:
         return message.reply_text("❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**")

    try:
        client.ban_chat_member(message.chat.id, user.id)
        client.unban_chat_member(message.chat.id, user.id)
        message.reply_text(f"👢 **تم طرد {user.mention} من القروب!**", parse_mode="HTML")
    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية طرد في هذا القروب أو أن المستخدم الذي تحاول طرده أعلى من البوت رتبة في تليجرام.")


# أمر كتم المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def mute_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("كتم"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for mute
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank
    if target_order >= sender_order:
         return message.reply_text("❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**")

    try:
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
        message.reply_text(f"🔇 **تم كتم {user.mention} في القروب!**", parse_mode="HTML")
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية كتم في هذا القروب أو أن المستخدم الذي تحاول كتمه أعلى من البوت رتبة في تليجرام.")

# أمر إلغاء الكتم
@app.on_message(filters.text & filters.group & filters.incoming)
def unmute_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("الغاء الكتم"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for unmute
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")


    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    # Optional: Check sender rank vs target rank (less critical for unmute)
    # target_highest_rank, target_order = get_user_highest_rank(str(user.id))
    # if target_order > sender_order: # Allow unmute equal/lower ranks only?
    #      return message.reply_text("❌ **لا يمكنك إلغاء كتم شخص لديه رتبة أعلى منك!**")

    try:
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=True))
        message.reply_text(f"🔊 **تم إلغاء كتم {user.mention}!**", parse_mode="HTML")
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما المستخدم ليس مكتوماً أصلاً أو أن البوت لا يملك صلاحية إلغاء الكتم.")

# أمر تقييد المستخدم (منع كل شيء تقريباً)
@app.on_message(filters.text & filters.group & filters.incoming)
def restrict_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("تقييد"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for restrict
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank
    if target_order >= sender_order:
         return message.reply_text("❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**")

    try:
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_send_polls=False, # Add poll permission
            can_change_info=False, # Add info permission
            can_invite_users=False, # Add invite permission
            can_pin_messages=False # Add pin permission
        ))
        message.reply_text(f"🚷 **تم تقييد {user.mention} في القروب!**", parse_mode="HTML")
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية تقييد في هذا القروب أو أن المستخدم الذي تحاول تقييده أعلى من البوت رتبة في تليجرام.")

# أمر فك التقييد (إعادة الصلاحيات الأساسية)
@app.on_message(filters.text & filters.group & filters.incoming)
def unrestrict_user_cmd(client, message):
    text = message.text.lower()
    if not text.startswith("فك التقييد"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for unrestrict
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    # Optional: Check sender rank vs target rank (less critical for unrestrict)
    # target_highest_rank, target_order = get_user_highest_rank(str(user.id))
    # if target_order > sender_order:
    #      return message.reply_text("❌ **لا يمكنك فك تقييد شخص لديه رتبة أعلى منك!**")

    try:
        # Grant basic permissions back
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=False, # Usually admins change info
            can_invite_users=True,
            can_pin_messages=False # Usually admins pin messages
        ))
        message.reply_text(f"✅ **تم فك التقييد عن {user.mention}!**", parse_mode="HTML")
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما المستخدم ليس مقيداً أصلاً أو أن البوت لا يملك صلاحية فك التقييد.")

# أمر رفع جميع القيود عن المستخدم (نفس فك التقييد تقريباً)
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_restrictions_cmd(client, message):
    text = message.text.lower()
    # Renaming command for clarity or keeping as is
    if not text.startswith("رفع القيود"): # Original command name
        return

    # This command seems redundant with "فك التقييد". Let's keep it, but it performs the same action.
    # Can choose to remove one or map both commands to the same function.
    # For now, map both to the refined unrestrict_user_cmd logic.

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**")

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message)

    # Optional: Check sender rank vs target rank
    # target_highest_rank, target_order = get_user_highest_rank(str(user.id))
    # if target_order > sender_order:
    #      return message.reply_text("❌ **لا يمكنك رفع القيود عن شخص لديه رتبة أعلى منك!**")

    try:
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False
        ))
        message.reply_text(f"✅ **تم رفع جميع القيود عن {user.mention}!**", parse_mode="HTML")
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** {e}")

# طرد جميع البوتات من القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_bots_cmd(client, message):
    text = message.text.lower()
    if text == "طرد البوتات":
        sender_id = str(message.from_user.id)
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

        # Check if sender has admin rank or higher
        if sender_order < rank_order.get("admin", 0):
             return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

        try:
            banned_count = 0
            # get_chat_members might require admin rights
            for member in client.get_chat_members(message.chat.id):
                if member.user.is_bot and member.user.id != client.me.id: # Don't ban self
                    client.ban_chat_member(message.chat.id, member.user.id)
                    banned_count += 1
            message.reply_text(f"✅ **تم طرد {banned_count} بوت من القروب!**")
        except Exception as e:
            message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** {e}")

# طرد جميع الحسابات المحذوفة (Deleted Accounts)
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_deleted_accounts_cmd(client, message):
    text = message.text.lower()
    if text == "طرد المحذوفين":
        sender_id = str(message.from_user.id)
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

        # Check if sender has admin rank or higher
        if sender_order < rank_order.get("admin", 0):
             return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

        try:
            banned_count = 0
            # get_chat_members might require admin rights
            for member in client.get_chat_members(message.chat.id):
                if member.user.is_deleted:
                    client.ban_chat_member(message.chat.id, member.user.id)
                    banned_count += 1
            message.reply_text(f"✅ **تم طرد {banned_count} حساب محذوف من القروب!**")
        except Exception as e:
            message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** {e}")


# كشف جميع البوتات في القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def check_bots_cmd(client, message):
    text = message.text.lower()
    if text == "كشف البوتات":
        try:
            # get_chat_members might require admin rights
            chat_members = client.get_chat_members(message.chat.id)
            bots = [member.user.mention for member in chat_members if member.user.is_bot and member.user.id != client.me.id] # Exclude self

            if bots:
                message.reply_text(f"🤖 **البوتات الموجودة في القروب:**\n" + "\n".join(bots), parse_mode="HTML")
            else:
                message.reply_text("✅ **لا يوجد بوتات أخرى في القروب!**")
        except Exception as e:
            message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** {e}")

# 🛡️ نظام الحماية من السبام، الروابط، الميديا، إلخ 🛡️
protection_settings = {} # إعدادات الحماية لكل قروب (الروابط، التكرار، التوجيه، الصور، إلخ)

# أوامر قفل وفتح الحماية (للروابط، التكرار، إلخ)
@app.on_message(filters.text & filters.group & filters.incoming)
def lock_unlock_protection_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 2 or (text[0] != "قفل" and text[0] != "فتح"):
        return # Not a protection lock/unlock command

    feature = text[1].lower() # e.g., 'روابط', 'تكرار', 'صور'

    # Check sender rank: admin or higher can lock/unlock protection features
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

    # List of valid features to prevent locking arbitrary strings
    valid_features = ["الروابط", "تكرار", "التوجيه", "الصور", "الفيديو", "الملصقات", "المعرفات", "التاك", "البوتات", "الكلمات"] # Added "الكلمات"

    if feature not in valid_features:
         return message.reply_text(f"❌ **ميزة الحماية '{feature}' غير موجودة.**\nالميزات المتاحة: " + " - ".join(valid_features))


    if chat_id not in protection_settings:
        protection_settings[chat_id] = {}

    action = text[0] # "قفل" or "فتح"

    if action == "قفل":
        protection_settings[chat_id][feature] = True
        message.reply_text(f"🔒 **تم قفل {feature} بنجاح!**")
    elif action == "فتح":
        protection_settings[chat_id][feature] = False
        message.reply_text(f"🔓 **تم فتح {feature} بنجاح!**")


# منع الروابط
@app.on_message(filters.text & filters.group & filters.incoming)
def block_links_handler(client, message):
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id in protection_settings and protection_settings[chat_id].get("الروابط", False):
        # Basic link detection
        if any(word in message.text.lower() for word in ["http://", "https://", "t.me/", "telegram.me/", ".com", ".net", ".org", ".ir"]):
            try:
                message.delete()
                # Optional: Reply with a warning
                # message.reply_text("🚫 **ممنوع إرسال الروابط في هذا القروب!**")
            except Exception:
                pass # Bot may not have permission to delete


# منع التكرار (السبام)
# Store {chat_id: {user_id: [timestamp1, timestamp2, ...]}}
user_messages_history = {}

@app.on_message(filters.text & filters.group & filters.incoming)
def anti_flood_handler(client, message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id in protection_settings and protection_settings[chat_id].get("تكرار", False):
        current_time = time.time()
        flood_limit = 5 # Max messages allowed
        flood_timeframe = 5 # Timeframe in seconds

        if chat_id not in user_messages_history:
            user_messages_history[chat_id] = {}
        if user_id not in user_messages_history[chat_id]:
            user_messages_history[chat_id][user_id] = []

        # Add current message timestamp and remove old ones
        user_messages_history[chat_id][user_id].append(current_time)
        user_messages_history[chat_id][user_id] = [
            ts for ts in user_messages_history[chat_id][user_id] if current_time - ts < flood_timeframe
        ]

        # Check if user exceeded the limit
        if len(user_messages_history[chat_id][user_id]) > flood_limit:
            try:
                message.delete()
                # Optional: Reply with a warning once
                # message.reply_text(f"🚫 **{message.from_user.mention} ممنوع التكرار في القروب!**", parse_mode="HTML")
            except Exception:
                pass # Bot may not have permission

# منع التوجيه (Forwarded messages)
@app.on_message(filters.forwarded & filters.group & filters.incoming)
def block_forwarded_handler(client, message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id in protection_settings and protection_settings[chat_id].get("التوجيه", False):
        try:
            message.delete()
            # message.reply_text("🚫 **ممنوع إرسال الرسائل الموجهة في هذا القروب!**")
        except Exception:
            pass # Bot may not have permission


# منع الصور والفيديوهات والملصقات والملفات والرسائل الصوتية والفيديو الملاحظات
@app.on_message(filters.media & filters.group & filters.incoming) # Use filters.media for various media types
def block_media_handler(client, message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id not in protection_settings:
        return

    should_delete = False
    reason = ""

    if protection_settings[chat_id].get("الصور", False) and message.photo:
        should_delete = True
        reason = "الصور"
    elif protection_settings[chat_id].get("الفيديو", False) and message.video:
        should_delete = True
        reason = "الفيديو"
    elif protection_settings[chat_id].get("الملصقات", False) and message.sticker:
        should_delete = True
        reason = "الملصقات"
    elif protection_settings[chat_id].get("الملفات", False) and message.document: # Added files protection
        should_delete = True
        reason = "الملفات"
    elif protection_settings[chat_id].get("الصوت", False) and message.audio: # Added audio protection
        should_delete = True
        reason = "الصوت"
    elif protection_settings[chat_id].get("الملاحظات الصوتية", False) and message.voice: # Added voice note protection
        should_delete = True
        reason = "الملاحظات الصوتية"
    elif protection_settings[chat_id].get("الملاحظات المرئية", False) and message.video_note: # Added video note protection
        should_delete = True
        reason = "الملاحظات المرئية"
    elif protection_settings[chat_id].get("الجهات", False) and message.contact: # Added contact protection
        should_delete = True
        reason = "الجهات"
    elif protection_settings[chat_id].get("المواقع", False) and message.location: # Added location protection
        should_delete = True
        reason = "المواقع"
    elif protection_settings[chat_id].get("الألعاب", False) and message.game: # Added game protection
        should_delete = True
        reason = "الألعاب"
    elif protection_settings[chat_id].get("الاستطلاعات", False) and message.poll: # Added poll protection
        should_delete = True
        reason = "الاستطلاعات"


    if should_delete:
        try:
            message.delete()
            # message.reply_text(f"🚫 **ممنوع إرسال {reason} في هذا القروب!**")
        except Exception:
            pass # Bot may not have permission


# منع المعرفات والتاك والكلمات الممنوعة
@app.on_message(filters.text & filters.group & filters.incoming)
def block_tags_mentions_words_handler(client, message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    text = message.text

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id not in protection_settings:
        return

    should_delete = False
    reason = ""

    # Prevent mentions like @username, @channel, but not commands
    if protection_settings[chat_id].get("المعرفات", False) and "@" in text and not text.startswith('@'):
         # More sophisticated check might be needed to distinguish mentions from email/commands
         if any(part.startswith('@') and len(part) > 1 for part in text.split()):
              should_delete = True
              reason = "المعرفات"

    # Prevent hashtags
    if not should_delete and protection_settings[chat_id].get("التاك", False) and "#" in text:
        if any(part.startswith('#') and len(part) > 1 for part in text.split()):
            should_delete = True
            reason = "التاك"

    # Prevent mentions of bots (assuming bots start with @ and end with bot, or have 'bot' in username)
    if not should_delete and protection_settings[chat_id].get("البوتات", False) and "@" in text:
         # Check if a mentioned user is a bot
         mentions = [word for word in text.split() if word.startswith('@') and len(word) > 1]
         if mentions:
              try:
                   # Try fetching the user object for each mention to check if it's a bot
                   for mention in mentions:
                        user = client.get_users(mention)
                        if user.is_bot:
                             should_delete = True
                             reason = "منشن البوتات"
                             break # Found a bot mention, delete and stop
              except Exception:
                   pass # Ignore if user not found

    # Prevent banned words (requires 'الكلمات' protection feature and a list of banned words)
    if not should_delete and protection_settings[chat_id].get("الكلمات", False):
        banned_words = protection_settings[chat_id].get("banned_words", []) # Get banned words for this group
        # Check if any banned word is in the message (case-insensitive)
        if any(word.lower() in text.lower() for word in banned_words):
            should_delete = True
            reason = "الكلمات الممنوعة"

    if should_delete:
        try:
            message.delete()
            # message.reply_text(f"🚫 **ممنوع إرسال {reason} في هذا القروب!**")
        except Exception:
            pass # Bot may not have permission

# أمر إضافة كلمة لقائمة المنع
@app.on_message(filters.text & filters.group & filters.incoming)
def add_banned_word_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0] != "اضف" or text[1] != "كلمة":
        return # Not "اضف كلمة" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

    word_to_ban = " ".join(text[2:]).strip().lower()
    if not word_to_ban:
         return message.reply_text("❌ **الرجاء تحديد الكلمة المراد منعها بعد الأمر.**")

    if chat_id not in protection_settings:
        protection_settings[chat_id] = {}
    if "banned_words" not in protection_settings[chat_id]:
        protection_settings[chat_id]["banned_words"] = []

    if word_to_ban in protection_settings[chat_id]["banned_words"]:
         return message.reply_text(f"ℹ️ **الكلمة '{word_to_ban}' موجودة بالفعل في قائمة المنع.**")

    protection_settings[chat_id]["banned_words"].append(word_to_ban)
    message.reply_text(f"✅ **تم إضافة الكلمة '{word_to_ban}' إلى قائمة المنع!**")

# أمر حذف كلمة من قائمة المنع
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_banned_word_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0] != "حذف" or text[1] != "كلمة":
        return # Not "حذف كلمة" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

    word_to_unban = " ".join(text[2:]).strip().lower()
    if not word_to_unban:
         return message.reply_text("❌ **الرجاء تحديد الكلمة المراد حذفها من قائمة المنع بعد الأمر.**")

    if chat_id not in protection_settings or "banned_words" not in protection_settings[chat_id]:
        return message.reply_text("ℹ️ **لا توجد قائمة كلمات ممنوعة لهذا القروب.**")

    if word_to_unban in protection_settings[chat_id]["banned_words"]:
        protection_settings[chat_id]["banned_words"].remove(word_to_unban)
        message.reply_text(f"✅ **تم حذف الكلمة '{word_to_unban}' من قائمة المنع!**")
    else:
        message.reply_text(f"ℹ️ **الكلمة '{word_to_unban}' غير موجودة في قائمة المنع.**")

# أمر عرض قائمة الكلمات الممنوعة
@app.on_message(filters.text & filters.group & filters.incoming)
def show_banned_words_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "قائمة المنع":
        if chat_id in protection_settings and "banned_words" in protection_settings[chat_id]:
            banned_words = protection_settings[chat_id]["banned_words"]
            if banned_words:
                words_list = "\n".join([f"• {word}" for word in banned_words])
                message.reply_text(f"🚫 **قائمة الكلمات الممنوعة في القروب:**\n{words_list}")
            else:
                message.reply_text("✅ **قائمة الكلمات الممنوعة فارغة.**")
        else:
             message.reply_text("ℹ️ **لا توجد قائمة كلمات ممنوعة لهذا القروب.**")


# 📜 أوامر إعدادات القروب (القوانين، الرابط، إلخ) 📜

# عرض القوانين
@app.on_message(filters.text & filters.group & filters.incoming)
def show_rules_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "القوانين":
        rules = group_config.get(chat_id, {}).get("rules", "🚫 لا توجد قوانين محددة لهذا القروب.")
        message.reply_text(f"📜 **قوانين القروب:**\n{rules}")

# تعديل القوانين
@app.on_message(filters.text & filters.group & filters.incoming)
def set_rules_cmd(client, message):
    text = message.text
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if text.lower().startswith("ضع قوانين"):
        # Check sender rank: owner or main_owner needed
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
        if sender_order < rank_order.get("owner", 0):
            return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**")

        # Get the text after "ضع قوانين " (case-insensitive check for the prefix)
        prefix = "ضع قوانين"
        if not text.lower().startswith(prefix):
            return # Should not happen due to outer check, but for safety
        new_rules = text[len(prefix):].strip()


        if not new_rules:
            return message.reply_text("❌ **الرجاء تحديد القوانين بعد الأمر.**")

        if chat_id not in group_config:
            group_config[chat_id] = {}

        group_config[chat_id]["rules"] = new_rules
        message.reply_text(f"✅ **تم تحديث قوانين القروب!**")

# عرض رابط القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def show_link_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "الرابط":
        group_link = group_config.get(chat_id, {}).get("link", "🚫 لا يوجد رابط مسجل.")
        message.reply_text(f"🔗 **رابط القروب:**\n{group_link}")

# تعديل رابط القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def set_link_cmd(client, message):
    text = message.text
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if text.lower().startswith("اضف رابط ="):
        # Check sender rank: owner or main_owner needed
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
        if sender_order < rank_order.get("owner", 0):
            return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**")

        # Get the text after "اضف رابط = " (case-insensitive prefix check)
        prefix = "اضف رابط ="
        if not text.lower().startswith(prefix):
             return # Should not happen
        new_link = text[len(prefix):].strip()


        if not new_link:
            return message.reply_text("❌ **الرجاء تحديد الرابط بعد علامة '='.**")

        if chat_id not in group_config:
            group_config[chat_id] = {}

        group_config[chat_id]["link"] = new_link
        message.reply_text(f"✅ **تم تحديث رابط القروب!**")

# عرض قائمة المالكين والإداريين والمميزين (حسب الرتب المحددة في الكود)
@app.on_message(filters.text & filters.group & filters.incoming)
def show_ranks_list_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id) # Not strictly needed but good context

    # Map command text to the rank key(s)
    role_map = {
        "المالك": ["owner", "owner_main"], # Show both main and sub owners
        "المالكين": ["owner", "owner_main"],
        "المدراء": ["admin"],
        "الادمن": ["moderator"],
        "المشرفين": ["supervisor"],
        "المميزين": ["vip"],
        "المطورين": ["dev"], # Includes main dev if they have the rank key
        "the goat": ["the_goat"],
        "m": ["m"],
        "المنشئين": ["creator"],
        "الاعضاء الجميلين": ["beautiful"]
    }

    rank_keys_to_show = role_map.get(text) # Get the list of internal keys

    if rank_keys_to_show is None:
        return # Not one of the commands handled here

    all_members = {} # Collect all members for the requested rank keys
    display_names_shown = [] # To show which ranks were included

    for rank_key in rank_keys_to_show:
        if rank_key in ranks:
            all_members.update(ranks[rank_key]) # Add user IDs from this rank
            display_names_shown.append(rank_display_names.get(rank_key, rank_key))


    if not all_members:
        # Use a generic name if multiple ranks were requested, otherwise use the single display name
        display_name_text = "الرتب المطلوبة" if len(display_names_shown) > 1 else display_names_shown[0] if display_names_shown else text
        return message.reply_text(f"🚫 **لا يوجد أي أعضاء في رتبة {display_name_text} في البوت.**")

    member_list_lines = []
    # Iterate through unique user IDs collected
    for user_id_str in all_members.keys():
        try:
            user = client.get_users(int(user_id_str))
            # Find all ranks this user has from the list being shown
            user_specific_ranks = [rank_display_names.get(key, key) for key in rank_keys_to_show if user_id_str in ranks.get(key, {})]
            ranks_text = "، ".join(user_specific_ranks)
            member_list_lines.append(f"• {user.mention} ({ranks_text})")
        except Exception:
            # Handle cases where user might not be found
            member_list_lines.append(f"• مستخدم غير معروف (ID: {user_id_str})")

    # Title based on requested ranks
    title_text = " و ".join(display_names_shown) if len(display_names_shown) > 1 else display_names_shown[0]
    message.reply_text(f"🏅 **قائمة {title_text} في البوت:**\n" + "\n".join(member_list_lines), parse_mode="HTML")


# إضافة قناة للقروب (لا يوجد استخدام واضح لهذا في الكود المتبقي)
@app.on_message(filters.text & filters.group & filters.incoming)
def add_channel_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0] != "اضف" or text[1] != "قناه":
        return # Not "اضف قناه" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Check sender rank: owner or main_owner needed
    if sender_order < rank_order.get("owner", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**")

    channel_username_arg = text[2].replace("@", "") # Remove @ if present

    if not channel_username_arg:
        return message.reply_text("❌ **الرجاء إدخال معرف القناة بعد الأمر.**")

    # Optional: Validate channel exists and bot is admin there
    try:
        channel = client.get_chat(channel_username_arg)
        if channel.type != "channel":
             return message.reply_text("❌ **المدخل ليس قناة!**")
        # Check bot admin status in channel (optional but recommended)
        me_in_channel = client.get_chat_member(channel.id, client.me.id)
        if not me_in_channel.status == ChatMemberStatus.ADMINISTRATOR:
             return message.reply_text(f"❌ **البوت ليس مشرفاً في القناة @{channel_username_arg}!**")

        # Store channel ID instead of username for robustness
        channel_id_str = str(channel.id)

        if chat_id not in group_config:
            group_config[chat_id] = {}
        if "channels" not in group_config[chat_id]:
            group_config[chat_id]["channels"] = []

        if channel_id_str in group_config[chat_id]["channels"]:
             return message.reply_text(f"ℹ️ **القناة @{channel.username} مضافة بالفعل لهذا القروب!**")


        group_config[chat_id]["channels"].append(channel_id_str)
        message.reply_text(f"✅ **تم إضافة القناة @{channel.username} ({channel.id}) للقروب!**") # Show ID as well
    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء إضافة القناة:** تأكد من أن المعرف صحيح وأن البوت في القناة ومشرف بها. {e}")


# حذف قناة من القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_channel_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0] != "حذف" or text[1] != "قناه":
        return # Not "حذف قناه" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Check sender rank: owner or main_owner needed
    if sender_order < rank_order.get("owner", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**")

    channel_username_or_id = text[2].replace("@", "") # Remove @ if present

    if chat_id not in group_config or "channels" not in group_config[chat_id]:
        return message.reply_text("🚫 **لا توجد قنوات مضافة لهذا القروب!**")

    channel_list = group_config[chat_id]["channels"]

    # Try to find the channel ID based on username or ID input
    target_channel_id = None
    channel_display_name = channel_username_or_id

    try:
        # First, try fetching the chat by username or ID to get the correct ID
        channel_chat = client.get_chat(channel_username_or_id)
        target_channel_id = str(channel_chat.id)
        channel_display_name = channel_chat.username if channel_chat.username else str(channel_chat.id)
    except Exception:
         # If fetching fails, assume the input might be a raw ID string already stored
         if channel_username_or_id.isdigit():
             target_channel_id = channel_username_or_id


    if target_channel_id and target_channel_id in channel_list:
        channel_list.remove(target_channel_id)
        message.reply_text(f"✅ **تم حذف القناة @{channel_display_name} ({target_channel_id}) من القروب!**")
    else:
        message.reply_text(f"🚫 **القناة @{channel_username_or_id} غير موجودة في القائمة المضافة لهذا القروب!**")

# 🗑️ أوامر المسح والتنظيف 🗑️
@app.on_message(filters.text & filters.group & filters.incoming)
def delete_commands_cmd(client, message):
    text = message.text.lower()
    chat_id = message.chat.id
    sender_id = str(message.from_user.id)

    # Check sender permissions for *any* delete command first
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Assuming 'admin' or higher can use delete commands
    if sender_order < rank_order.get("admin", 0):
        # Exception for "مسح بالرد" if it's intended for lower ranks? Original comment said مشرفين (admins).
        # Let's keep all 'مسح' commands restricted to admin or higher for consistency.
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

    # --- Specific delete commands ---

    # مسح الكل (Delete last 100 messages + command message)
    if text == "مسح الكل":
        try:
            # Get message IDs to delete, including the command message itself
            message_ids_to_delete = list(range(message.message_id - 99, message.message_id + 1))
            client.delete_messages(chat_id, message_ids_to_delete)
            # No reply needed as the command message is deleted
            return
        except Exception as e:
             # Reply will be sent to the chat if deletion fails
             message.reply_text(f"❌ **حدث خطأ أثناء مسح الرسائل:** ربما البوت ليس لديه صلاحية حذف. {e}")
             return # Stop processing


    # مسح المحظورين (Clear ban list)
    elif text == "مسح المحظورين":
        try:
            banned_count = 0
            # client.get_chat_bans requires admin rights in the group
            # It returns a generator of ChatMember objects with status 'kicked'
            for member in client.get_chat_bans(chat_id):
                 # Check if the member is actually kicked/banned
                 if member.status == ChatMemberStatus.KICKED:
                      client.unban_chat_member(chat_id, member.user.id)
                      banned_count += 1
            message.reply_text(f"✅ **تم مسح قائمة المحظورين بنجاح! ({banned_count} مستخدم)**")
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء مسح قائمة المحظورين:** ربما البوت ليس لديه صلاحية. {e}")


    # مسح المكتومين (Clear restricted list)
    elif text == "مسح المكتومين":
        try:
            restricted_count = 0
            # get_chat_members with filter RESTRICTED is the correct way
            # Note: This might take time for large groups
            # Need to iterate as it's a generator
            for member in client.get_chat_members(chat_id, filter=ChatMemberStatus.RESTRICTED):
                # Ensure it's actually restricted
                if member.status == ChatMemberStatus.RESTRICTED:
                     # Unrestrict by setting can_send_messages=True (Telegram default allows other permissions implicitly)
                     client.restrict_chat_member(chat_id, member.user.id, ChatPermissions(can_send_messages=True))
                     restricted_count += 1
            message.reply_text(f"✅ **تم مسح قائمة المكتومين بنجاح! ({restricted_count} مستخدم)**")
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء مسح قائمة المكتومين:** ربما البوت ليس لديه صلاحية. {e}")

    # مسح الرتب (e.g., مسح admin)
    elif text.startswith("مسح "):
        parts = text.split()
        if len(parts) == 2: # Expecting "مسح [role]"
            role_arg = parts[1]
            # Find the internal rank key from the role argument (match display name or key)
            target_rank_key = None
            for key, display in rank_display_names.items():
                 if display.lower() == role_arg or key.lower() == role_arg:
                      target_rank_key = key
                      break

            if target_rank_key and target_rank_key in ranks:
                 # Prevent clearing higher ranks or equal to the sender's highest rank
                 target_order = rank_order.get(target_rank_key, -float('inf'))
                 if target_order >= sender_order:
                      display_name = rank_display_names.get(target_rank_key, target_rank_key)
                      return message.reply_text(f"❌ **لا يمكنك مسح رتبة ({display_name}) مساوية أو أعلى من رتبتك!**")

                 # Clear the rank dictionary for this key
                 ranks[target_rank_key] = {}
                 display_name = rank_display_names.get(target_rank_key, target_rank_key)
                 return message.reply_text(f"✅ **تم مسح جميع {display_name} من البوت!**")

        # --- مسح [number] fallback ---
        # If it wasn't "مسح [role]", try to parse as "مسح [number]"
        if len(parts) == 2:
             try:
                 num = int(parts[1])
                 if num <= 0: return message.reply_text("❌ **يجب إدخال رقم موجب بعد 'مسح'!**")
                 if num > 200: num = 200 # Limit to avoid API limits or abuse
                 # Get message IDs to delete, including the command message
                 message_ids_to_delete = list(range(message.message_id - num + 1, message.message_id + 1)) # +1 to include command
                 client.delete_messages(chat_id, message_ids_to_delete)
                 # No reply needed
                 return
             except ValueError:
                  pass # Not a number, continue checking other commands

    # مسح قائمة المنع (Clear banned words list in protection_settings)
    # This command is handled by delete_messages_cmd, which check text.lower()
    # The 'مسح قائمة المنع' check is done above.
    # Let's put the specific conditions inside the main handler body
    # This block is now redundant as it's covered by the 'elif text == "..."' checks

    # This section is removed as it was redundant. The checks for specific commands like
    # "مسح قائمة المنع", "مسح الردود", "مسح الأوامر المضافة", "مسح الايدي", etc.,
    # are integrated into the main `delete_commands_cmd` function based on `text == "..."`

    # مسح بالرد (Delete replied message + command message)
    elif text == "مسح بالرد" and message.reply_to_message:
        try:
            # Delete the replied message and the command message
            message_ids_to_delete = [message.reply_to_message.message_id, message.message_id]
            client.delete_messages(chat_id, message_ids_to_delete)
            # No reply needed
            return
        except Exception as e:
             # Reply will be sent to the chat if deletion fails
             message.reply_text(f"❌ **حدث خطأ أثناء مسح الرسالة:** ربما البوت ليس لديه صلاحية حذف. {e}")
             return # Stop processing

    # مسح قائمة المنع
    elif text == "مسح قائمة المنع":
        if chat_id in protection_settings and "banned_words" in protection_settings[chat_id]:
            protection_settings[chat_id]["banned_words"] = []
            message.reply_text("✅ **تم مسح قائمة الكلمات الممنوعة!**")
        else:
             message.reply_text("ℹ️ **لا توجد قائمة كلمات ممنوعة لهذا القروب.**")

    # مسح الردود (Clear group-specific auto-replies)
    elif text == "مسح الردود":
        if chat_id in group_config and "auto_replies" in group_config[chat_id]:
            group_config[chat_id]["auto_replies"] = {}
            message.reply_text("✅ **تم مسح جميع الردود التلقائية الخاصة بهذا القروب!**")
        else:
             message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة بهذا القروب.**")

    # مسح الأوامر المضافة (Clear group-specific custom commands)
    elif text == "مسح الأوامر المضافة":
        if chat_id in group_config and "custom_commands" in group_config[chat_id]:
            group_config[chat_id]["custom_commands"] = {}
            message.reply_text("✅ **تم مسح جميع الأوامر المضافة الخاصة بهذا القروب!**")
        else:
             message.reply_text("ℹ️ **لا توجد أوامر مضافة خاصة بهذا القروب.**")

    # مسح الايدي (Clear ID info config)
    elif text == "مسح الايدي":
        if chat_id in group_config and "id_info" in group_config[chat_id]:
            del group_config[chat_id]["id_info"] # Delete key
            message.reply_text("✅ **تم مسح بيانات الايدي!**")
        else:
             message.reply_text("ℹ️ **لا توجد بيانات ايدي مخزنة لهذا القروب.**")

    # مسح الترحيب (Clear welcome message config)
    elif text == "مسح الترحيب":
        if chat_id in group_config and "welcome_message" in group_config[chat_id]:
            del group_config[chat_id]["welcome_message"]
            message.reply_text("✅ **تم مسح رسالة الترحيب!**")
        else:
             message.reply_text("ℹ️ **لا توجد رسالة ترحيب مخزنة لهذا القروب.**")

    # مسح الرابط (Clear group link config)
    elif text == "مسح الرابط":
        if chat_id in group_config and "link" in group_config[chat_id]:
            del group_config[chat_id]["link"]
            message.reply_text("✅ **تم مسح رابط القروب!**")
        else:
             message.reply_text("ℹ️ **لا يوجد رابط قروب مخزن لهذا القروب.**")

    # If the command started with "مسح" but didn't match any specific handler
    # This case is handled by the initial check and the subsequent `elif`.
    # If it gets here, it means text.startswith("مسح") is true but none of the specific elifs matched.
    # Could be "مسح" with no args, or "مسح invalid_arg". The number/role checks cover common patterns.
    # No need for a generic "invalid مسح command" message as it might be ambiguous.
    pass # Command not recognized by this handler


# 💬 نظام الردود التلقائية (عامة + خاصة بالقروب) 💬

# قائمة الردود التلقائية العامة (افتراضية)
# تم دمج custom_responses هنا وإضافة بعض الردود السعودية
global_auto_replies = {
    "السلام عليكم": ["وعليكم السلام ورحمة الله وبركاته 🤍", "وعليكم السلام، كيف الحال؟", "عليكم السلام يا حبيب الشعب!"],
    "كيف الحال": ["بخير دامك بخير 🌚", "الحال من بعضه يالذيب", "كل شي تمام وانت؟", "🔥 الحال من بعضه، لكن معاك يصير أحسن! 🔥"],
    "هلا": ["هلا وغلا 💛", "يا مرحبا ومسهلا", "هلا والله!", "🌟 هلا والله بأهل الطيب والمجد! 🌟"],
    "بخير": ["دوم يارب 🙏", "أهم شي انك بخير", "بخيرك يا غالي"],
    "وينك": ["موجود، وش عندك؟", "هنا موجود وش تبي؟", "موجود بس مشغول شوي 😴"],
    "تصميم": ["تبي تصميم؟ روح لمصمم، مو هنا! 😎", "جيب فكرة وأنا أصمم لك", "التصميم فن، تبي درس؟", "🎨 الإبداع هو هوايتي، التصميم عالمي! 🎨"],
    "احبك": ["وأنا أحبك بعد ❤️", "الله يسعدك، الحب لك يا ذيب!", "يا حبي لك، شعور متبادل 🥰", "❤️ وأنا أحبك بعد! الله يديم المحبة! ❤️"],
    "مع السلامة": ["في أمان الله، لا تطول الغيبة!", "يالله توكل على الله، نشوفك على خير", "مع السلامة لا تنسى تمرنا"],
    "وش تسوي": ["جالس أطقها وأروق 😎", "مشغول شوي، أنت وش عندك؟", "جالس أبرمج بوتات، وانت؟"],
    "هاه": ["هاه وش؟ وش تبي؟", "هاه بنفسك؟", "هاه على هاه تهااااااااه"],
    "وين الناس": ["موجودين بس مختفين", "الناس في الدوامات وانت تدورهم؟", "كلهم مشغولين، وش عندك؟"],
    "قفل الموضوع": ["أوك تم القفل 🔒", "انتهى النقاش، نقطة.", "يالله خلاص نغير السالفة"],
    "ما عندي سالفة": ["ما عليك، الحياة سالفة بحد ذاتها", "يعني جالس تضيع وقتك؟", "خلك مثلي، بدون سالفة ولا هم"],
    "اقلب وجهك": ["وجهك مقلوب أصلاً 😂", "مو على كيفك، أنا ثابت هنا!", "يالله امش وخلنا نرتاح"],
    "وش رايك": ["رايي مثل رايك، وش بعد؟", "ما عندي راي، بس قول انت وش رايك؟", "رايي سر خطير، ما ينقال هنا"],
    "وش الجديد": ["الجديد اني صرت ذكي أكثر!", "مافي جديد، نفس الروتين", "الجديد عندي اني صرت أطول شوي 😜"],
    "وينك مختفي": ["موجود بس انت اللي مختفي", "مختفي بس أراقبك من بعيد 😏", "مختفي في عالم البرمجة"],
    "كم الساعة": ["افتح جوالك وشوف 😆", "مدري والله، ليه مستعجل؟", "الوقت لا ينتظر أحد، وأنت بعد لا تنتظر"],
    "ورع": ["أنا أكبر منك يا ورع 😂", "كلنا كنا ورعان، ليش زعلان؟", "ورع بعزك؟"],
    "وش ذا": ["ذا اللي تشوفه، وش تبيني أقول؟", "مدري بس شكله غريب", "هذا اللي ما له تفسير"],
    "هادي": ["هادي لكنه ذيب! 😏", "هادي بس وقت اللزوم انفجر", "هادي مع اللي يستاهل"],
    "اشغلني": ["تحمل، هذا جزء من الحياة", "يالله لا تشيل همه", "تحملني، أنا البوت ولازم أكون معك"],
    "طفشان": ["طفشان؟ يالله خذلك فلة!", "طفش من الحياة ولا من الدراسة؟", "الحياة حلوة، لا تصير كئيب"],
    "وش احسن فريق": ["أكيد الأهلي السعودي 💚🔥", "الأهلي وبس والباقي خس", "كل الفرق كويسة، بس الأهلي أسطورة"], # تباهي سعودي بالأهلي
    "وش تتابع": ["أتابعك وأشوف وش بتسوي 😏", "ما أتابع شي، أنا بوت مو بني آدم", "تتابع مسلسلات؟ أنا أتابع برمجة"],
    "فطورك": ["خبز وشاهي وريحان ☕", "فطور كذا بدون شاورما؟ ما يصلح", "أحلى فطور تميس وقشطة"], # أكلات شعبية
    "غداك": ["كبسة أكيد، أنت وش غداك؟", "الغدا رز ولا ما نعتبره غدا", "ما غديت للحين، تراك جوعتني"], # الكبسة
    "عشاءك": ["عشاء خفيف، لازم نحافظ على الجسم 😎", "برجر ولا بيتزا؟ القرار صعب", "أي شي ينفع عشاء، حتى شاهي وحلا"],
    "جاي": ["حيّاك الله، البيت بيتك", "على هونك، لا تستعجل", "جايك؟ متى وصلت؟"] # إضافة جمل شائعة
}

# الرد التلقائي على العبارات (يفحص أولاً الردود الخاصة بالقروب، ثم الردود العامة)
@app.on_message(filters.text & filters.group & filters.incoming)
def auto_reply_handler(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    # 1. تحقق من الردود الخاصة بالقروب أولاً
    if chat_id in group_config and "auto_replies" in group_config[chat_id]:
        group_replies = group_config[chat_id]["auto_replies"]
        for trigger, replies in group_replies.items():
            # استخدام 'in' للسماح بتطابق جزء من الكلمة أو عبارة
            if trigger in text and replies:
                reply = random.choice(replies)
                message.reply_text(reply)
                return # تم الرد، توقف المعالجة

    # 2. إذا لم يتم العثور على رد في إعدادات القروب، تحقق من الردود العامة
    for key in global_auto_replies:
        # استخدام 'in' للسماح بتطابق جزء من الكلمة أو عبارة
        if key in text:
            reply = random.choice(global_auto_replies[key])
            message.reply_text(reply)
            return # تم الرد، توقف المعالجة

    # لا يوجد رد تلقائي مطابق
    pass

# أمر إضافة رد تلقائي خاص بالقروب
# هذا الأمر تم إضافته سابقاً في مرحلة التخطيط، وتم وضعه هنا ليكون مع أوامر الردود
# @app.on_message(filters.text & filters.group & filters.incoming)
# def add_auto_reply_cmd(client, message): # هذه الدالة تم تعريفها سابقاً، نتركها هناك.

# أمر حذف رد تلقائي خاص بالقروب
# هذا الأمر تم إضافته سابقاً في مرحلة التخطيط، وتم وضعه هنا ليكون مع أوامر الردود
# @app.on_message(filters.text & filters.group & filters.incoming)
# def remove_auto_reply_cmd(client, message): # هذه الدالة تم تعريفها سابقاً، نتركها هناك.

# أمر عرض الردود التلقائية الخاصة بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def show_group_auto_replies_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "ردود القروب":
        if chat_id in group_config and "auto_replies" in group_config[chat_id]:
            group_replies = group_config[chat_id]["auto_replies"]
            if group_replies:
                reply_list = []
                for trigger, replies in group_replies.items():
                    replies_text = " / ".join(replies)
                    reply_list.append(f"• `{trigger}`: {replies_text}")
                message.reply_text(f"💬 **الردود التلقائية الخاصة بهذا القروب:**\n" + "\n".join(reply_list))
            else:
                message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة مضافة لهذا القروب.**")
        else:
            message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة مضافة لهذا القروب.**")


# 🛠 لوحة تحكم المطور الأساسي (في الخاص) 🛠

# المطور الأساسي (أنت) - يجب أن يكون آيدي مستخدم تليجرام
main_dev = "7601607055"  # حط آيديك هنا

# قائمة المطورين الثانويين (للسماح لهم ببعض الأوامر الخاصة)
# هذا القاموس يمكن حفظه لتحميله عند تشغيل البوت
secondary_devs = {} # {user_id_str: "اسم اختياري"}

# التحقق من المطور الأساسي
def is_main_dev(user_id):
    return str(user_id) == main_dev

# التحقق من المطورين الثانويين
def is_secondary_dev(user_id):
    return str(user_id) in secondary_devs

# التحقق إذا كان المستخدم مطوراً (أساسي أو ثانوي)
def is_dev(user_id):
    return is_main_dev(user_id) or is_secondary_dev(user_id)


# رفض أي شخص يحاول يستخدم أوامر المطورين (في الخاص)
@app.on_message(filters.text & filters.private & filters.incoming)
def dev_commands_gatekeeper(client, message):
    # Commands handled by dev_commands_handler below will be checked there
    # This handler can act as a general gatekeeper for *any* text message in private chat
    # that doesn't match other private handlers if desired, but it's simpler to check inside
    # the dev_commands_handler itself. Remove this specific gatekeeper function.
    pass # Removed this function as logic is integrated into the main dev handler


# أوامر المطورين في الخاص
@app.on_message(filters.text & filters.private & filters.incoming)
def dev_commands_handler(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Check if user is a developer
    if not is_dev(user_id):
        return message.reply_text("🚫 **هذه الأوامر مخصصة للشيخ @rnp_e فقط**")

    # --- أوامر المطور الأساسي فقط ---
    if is_main_dev(user_id):
        if text.startswith("اضافة مطور"):
            # Expecting reply or @username/id
            target_user, error_message = get_target_user(client, message, allow_self=False)

            if error_message:
                 return message.reply_text(error_message)

            target_user_id_str = str(target_user.id)

            if target_user_id_str == main_dev:
                 return message.reply_text("❌ **لا يمكنك إضافة المطور الأساسي كمطور ثانوي!**")

            if target_user_id_str in secondary_devs:
                 return message.reply_text(f"ℹ️ **المستخدم {target_user.mention} هو بالفعل مطور ثانوي!**", parse_mode="HTML")

            secondary_devs[target_user_id_str] = target_user.first_name # Store name as value
            message.reply_text(f"✅ **تم إضافة {target_user.mention} كمطور ثانوي!**", parse_mode="HTML")

        elif text.startswith("حذف مطور"):
            # Expecting reply or @username/id
            target_user, error_message = get_target_user(client, message, allow_self=False)

            if error_message:
                 return message.reply_text(error_message)

            target_user_id_str = str(target_user.id)

            if target_user_id_str == main_dev:
                 return message.reply_text("❌ **لا يمكنك حذف المطور الأساسي من قائمة المطورين!**")

            if target_user_id_str in secondary_devs:
                del secondary_devs[target_user_id_str]
                message.reply_text(f"✅ **تم حذف {target_user.mention} من قائمة المطورين الثانويين**", parse_mode="HTML")
            else:
                message.reply_text(f"🚫 **المستخدم {target_user.mention} ليس في قائمة المطورين الثانويين!**", parse_mode="HTML")

        elif text == "قائمة المطورين":
            if secondary_devs:
                dev_list_lines = []
                for dev_id_str, name in secondary_devs.items():
                    try:
                        dev_user = client.get_users(int(dev_id_str))
                        dev_list_lines.append(f"• {dev_user.mention} ({name})")
                    except Exception:
                        dev_list_lines.append(f"• مستخدم غير معروف (ID: {dev_id_str}) ({name})")
                dev_list_text = "\n".join(dev_list_lines)
                message.reply_text(f"🛠 **قائمة المطورين الثانويين:**\n{dev_list_text}", parse_mode="HTML")
            else:
                message.reply_text("🚫 **لا يوجد مطورين ثانويين حالياً.**")

        # --- أوامر لوحة تحكم المطور الأساسي (تظهر مع زر) ---
        elif text == "لوحة التحكم" or text == "/panel": # Add a command trigger for the panel
             # This will trigger the admin_panel handler below
             pass # Let the admin_panel handler handle this specific command


# لوحة تحكم المطور الأساسي (يتم عرضها كرد على أمر معين مثل "لوحة التحكم" أو "/panel")
@app.on_message(filters.text & filters.private & filters.incoming)
def admin_panel_cmd(client, message):
    user_id = str(message.from_user.id)
    text = message.text.lower()

    # This handler specifically triggers for "لوحة التحكم" or "/panel"
    if text != "لوحة التحكم" and text != "/panel":
        return

    if not is_main_dev(user_id):
        return message.reply_text("🚫 **هذه اللوحة مخصصة للشيخ @rnp_e فقط!**")

    # Fetching dialogs and users can take time, especially for large accounts
    # Consider adding a loading message.
    try:
        message.reply_text("⏳ **جاري تجميع بيانات لوحة التحكم... قد يستغرق هذا بعض الوقت.**")
        dialogs = client.get_dialogs()
        chat_count = 0
        invite_links = []
        # Iterate through dialogs to count groups/supergroups and get invite links
        for dialog in dialogs:
            if dialog.chat.type in ["supergroup", "group"]:
                chat_count += 1
                try:
                    # Check if bot is admin and can export invite link
                    chat_member = client.get_chat_member(dialog.chat.id, client.me.id)
                    if chat_member.status == ChatMemberStatus.ADMINISTRATOR and chat_member.privileges and chat_member.privileges.can_invite_users:
                         invite_link = client.export_chat_invite_link(dialog.chat.id)
                         invite_links.append(f"[{dialog.chat.title}]({invite_link})")
                    else:
                         invite_links.append(f"[{dialog.chat.title}] (البوت ليس مشرفاً)") # Indicate if bot is not admin or lacks permission

                except Exception:
                    # Handle cases where getting chat member or link fails
                     invite_links.append(f"[{dialog.chat.title}] (خطأ في جلب الرابط)")

        # Getting total user count in all chats the bot is in is complex and slow
        # A simple count of private dialogs might be a proxy, or track users who interacted
        # Let's keep the original `client.get_users()` call, but note it might be slow/approximate
        # client.get_users() in some contexts gets *all* users known to the client, which is huge.
        # A better metric is users who have *interacted* with the bot or are in tracked groups.
        # The original code used `len(client.get_users())` which is likely incorrect for "users interacted".
        # Let's remove the user count for simplicity and accuracy concerns in a general panel.
        # user_count = "غير متاح بسهولة" # Or track actively interacting users separately

        invite_links_text = "\n".join(invite_links) if invite_links else "🚫 **لا يوجد قروبات مفعّل فيها البوت**"

        panel_text = f"""
📊 **لوحة التحكم الخاصة بك**:
━━━━━━━━━━━━
👥 **عدد القروبات المشترك بها:** {chat_count}
🔗 **روابط القروبات:**
{invite_links_text}
━━━━━━━━━━━━
"""

        # Define inline keyboard buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart_bot"),
             InlineKeyboardButton("📢 إرسال إذاعة", callback_data="broadcast")],
            # Consider removing disable/enable bot buttons unless implemented carefully
            # [InlineKeyboardButton("🚫 تعطيل البوت", callback_data="disable_bot"),
            #  InlineKeyboardButton("✅ تفعيل البوت", callback_data="enable_bot")],
             [InlineKeyboardButton("قائمة المطورين الثانويين", callback_data="list_secondary_devs")] # Add button to list devs
        ])

        message.reply_text(panel_text, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء إعداد لوحة التحكم:** {e}")


# التحكم في البوت من اللوحة (عبر الأزرار)
@app.on_callback_query()
def handle_admin_buttons(client, callback_query):
    user_id = str(callback_query.from_user.id)

    if not is_main_dev(user_id):
        return callback_query.answer("🚫 **هذه الأوامر مخصصة للشيخ @rnp_e فقط!**", show_alert=True)

    data = callback_query.data
    chat_id = callback_query.message.chat.id # Chat where the panel message is

    if data == "restart_bot":
        callback_query.answer("جاري إعادة تشغيل البوت...", show_alert=True)
        callback_query.edit_message_text("🔄 **جاري إعادة تشغيل البوت...**")
        # كود إعادة التشغيل هنا (يتطلب مكتبات مثل os أو sys وقد لا يعمل في كل بيئة استضافة)
        # مثال بسيط (قد يتطلب صلاحيات خاصة):
        # os.execv(sys.executable, ['python'] + sys.argv)
        # أو استخدام مكتبات مثل restart (pip install restart)
        # restart.restart()
        # بما أن إعادة التشغيل الحقيقية معقدة وتعتمد على بيئة التشغيل، نكتفي بالرسالة
        # في تطبيق حقيقي، ستحتاج لوضع هذا البوت داخل سكريبت يشغله باستمرار ويعيد تشغيله عند الحاجة.

    elif data == "broadcast":
        callback_query.answer("ارسل رسالة الإذاعة الآن في الخاص", show_alert=True)
        # Logic to get the next message from this user and send it as broadcast
        # This requires a state mechanism (e.g., user_states = {user_id: "waiting_for_broadcast_message"})
        # Since state is lost on restart, this is complex. Placeholder message for now.
        callback_query.message.reply_text("📢 **ارسل رسالة الإذاعة الآن في هذا الدردشة الخاصة.** (ميزة الإذاعة تتطلب تطبيق لوجيك خاص لتخزين الرسالة وإعادة إرسالها لكل القروبات)")

    # Disable/Enable buttons removed as they require state persistence or external control
    # elif data == "disable_bot":
    #     callback_query.answer("تم تعطيل البوت!", show_alert=True)
    #     callback_query.edit_message_text("🚫 **تم تعطيل البوت!**")
    #     # كود تعطيل البوت هنا (يتطلب تعديل في بداية عمل البوت للتوقف إذا كان معطلاً)
    #
    # elif data == "enable_bot":
    #     callback_query.answer("تم تفعيل البوت!", show_alert=True)
    #     callback_query.edit_message_text("✅ **تم تفعيل البوت!**")
    #     # كود تفعيل البوت هنا

    elif data == "list_secondary_devs":
         # Trigger the list devs command logic
         # Since list_secondary_devs is a callback, we handle it here directly
         if secondary_devs:
             dev_list_lines = []
             for dev_id_str, name in secondary_devs.items():
                 try:
                     dev_user = client.get_users(int(dev_id_str))
                     dev_list_lines.append(f"• {dev_user.mention} ({name})")
                 except Exception:
                     dev_list_lines.append(f"• مستخدم غير معروف (ID: {dev_id_str}) ({name})")
             dev_list_text = "\n".join(dev_list_lines)
             callback_query.edit_message_text(f"🛠 **قائمة المطورين الثانويين:**\n{dev_list_text}", parse_mode="HTML", reply_markup=callback_query.message.reply_markup) # Keep the panel buttons
         else:
             callback_query.edit_message_text("🚫 **لا يوجد مطورين ثانويين حالياً.**", reply_markup=callback_query.message.reply_markup) # Keep the panel buttons


# 🏦 نظام البنك، الممتلكات، الوظائف، السجن 🏦
# ملاحظة: هذه الأنظمة تتطلب حفظ البيانات (Persistence) وإلا ستفقد عند كل إعادة تشغيل.
# القواميس الحالية تخزن البيانات في الذاكرة فقط.

# تخزين بيانات البنك والممتلكات والأسهم والقروض وما شابه
bank_accounts = {}  # الحسابات البنكية {user_id_str: balance}
user_properties = {}  # ممتلكات المستخدمين {user_id_str: {item_name: quantity}}
stock_market = {"value": 100}  # قيمة الأسهم المتغيرة (مثال بسيط)
loans = {}  # القروض {user_id_str: amount_due}
insurance = {}  # التأمين على الممتلكات {user_id_str: {item_name: expiry_timestamp}}
vip_cards = {}  # بطاقات VIP {user_id_str: expiry_timestamp}
user_jobs = {}  # الوظائف {user_id_str: "job_name"} (شرطة/عصابة)
gang_leaders = {}  # رؤساء العصابات {user_id_str: True}
# banned_users = {} # المستخدمين المعاقبين بالسجن {user_id_str: end_timestamp} - يختلف عن حظر القروب

# 🏦 نظام البنك الأساسي 🏦
@app.on_message(filters.text & filters.group & filters.incoming)
def bank_system_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Ensure user has a bank account before most operations
    if text != "انشاء حساب بنكي" and user_id not in bank_accounts:
         # Don't reply for every command, only for bank-related ones
         if any(text.startswith(cmd) for cmd in ["رصيدي", "راتبي", "بخشيش", "استثمار", "شراء", "بيع", "العجلة", "سجن", "سجني", "سداد ديوني"]):
              return message.reply_text("❌ **يجب إنشاء حساب بنكي أولًا! استخدم أمر: انشاء حساب بنكي**")
         else:
              return # Not a bank command

    # Initialize user's balance if creating account
    if text == "انشاء حساب بنكي":
        if user_id in bank_accounts:
            return message.reply_text("🚫 **لديك حساب بنكي بالفعل! رصيدك الحالي: {bank_accounts[user_id]}💰**")
        bank_accounts[user_id] = 5000  # يبدأ كل لاعب برصيد 5000
        message.reply_text("✅ **تم إنشاء حساب بنكي لك! رصيدك الابتدائي: 5000💰**")

    elif text == "رصيدي": # Added command to check balance
         message.reply_text(f"🏦 **رصيدك الحالي: {bank_accounts.get(user_id, 0)}💰**")


    elif text == "راتبي":
        # Check if user has a job, otherwise default salary
        salary = 0
        job = user_jobs.get(user_id)
        if job == "شرطة":
            salary = 1500
        elif job == "عصابة":
            salary = 5000
        elif user_id in gang_leaders: # Check if leader (takes precedence)
            salary = 10000
        else: # Default salary if no specific job/role
            salary = 2000

        # VIP card doubles salary
        if user_id in vip_cards and vip_cards[user_id] > time.time():
            salary *= 2

        bank_accounts[user_id] = bank_accounts.get(user_id, 0) + salary
        message.reply_text(f"💰 **تم إضافة {salary} ريال إلى حسابك كراتب! رصيدك الحالي: {bank_accounts[user_id]}**")

    elif text == "بخشيش":
        tip = random.randint(100, 500)
        bank_accounts[user_id] += tip
        message.reply_text(f"💸 **حصلت على بخشيش بقيمة {tip} ريال! رصيدك الحالي: {bank_accounts[user_id]}**")

    elif text.startswith("استثمار"):
        try:
            parts = text.split()
            if len(parts) < 2:
                 return message.reply_text("❌ **استخدم الصيغة الصحيحة: استثمار [المبلغ]**")
            amount = int(parts[1])
            if amount <= 0:
                 return message.reply_text("❌ **يجب أن يكون مبلغ الاستثمار موجباً!**")

            if bank_accounts[user_id] < amount:
                return message.reply_text("🚫 **ليس لديك ما يكفي للاستثمار! رصيدك الحالي: {bank_accounts[user_id]}**")

            # Simulate stock market fluctuation
            stock_market["value"] += random.randint(-10, 15) # Change market value slightly
            # Calculate profit/loss based on current market value
            profit_percentage = (stock_market["value"] - 100) / 100 # If value is 110, 10% profit
            earnings = int(amount * profit_percentage * (random.random() * 0.5 + 0.75)) # Add some randomness to earnings

            bank_accounts[user_id] += earnings

            if earnings >= 0:
                 message.reply_text(f"📈 **استثمرت {amount} ريال في السوق، وحققت ربحاً قدره {earnings} ريال! رصيدك الحالي: {bank_accounts[user_id]}**")
            else:
                 message.reply_text(f"📉 **استثمرت {amount} ريال في السوق، وتكبدت خسارة قدرها {-earnings} ريال! رصيدك الحالي: {bank_accounts[user_id]}**")

        except (ValueError, IndexError):
            return message.reply_text("❌ **استخدم الصيغة الصحيحة: استثمار [المبلغ] (المبلغ يجب أن يكون رقماً صحيحاً)**")
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء الاستثمار: {e}**")


# 🎡 عجلة الحظ 🎡
@app.on_message(filters.text & filters.group & filters.incoming)
def spin_wheel_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    if text == "العجلة":
        spin_cost = 5000000 # 5 مليون
        if user_id not in bank_accounts or bank_accounts[user_id] < spin_cost:
            return message.reply_text(f"🚫 **يجب أن تمتلك {spin_cost} ريال لتدوير العجلة! رصيدك الحالي: {bank_accounts.get(user_id, 0)}**")

        bank_accounts[user_id] -= spin_cost
        prizes = [
            ("🚗 سيارة", "item", "سيارة", 1), # Item prize
            ("💎 ماسة", "item", "ماسة", 1), # Item prize (assuming الماسة is an item)
            ("🎲 x2 الأرباح لمدة 3 دقائق", "boost", "double_earnings", 180), # Boost prize (duration in seconds)
            ("💰 10 مليون ريال", "money", 10000000), # Money prize
            ("🚫 لا شيء", "none", 0) # No prize
        ]
        prize_name, prize_type, prize_value, *prize_args = random.choice(prizes) # Unpack prize details

        message.reply_text(f"🎡 **درت العجلة... ودفعت {spin_cost} ريال.**\n**وحصلت على:** {prize_name}")

        if prize_type == "money":
            bank_accounts[user_id] = bank_accounts.get(user_id, 0) + prize_value
            message.reply_text(f"🎉 **مبروك! تم إضافة {prize_value} ريال لرصيدك! رصيدك الحالي: {bank_accounts[user_id]}**")
        elif prize_type == "item":
            item_name = prize_value
            quantity = prize_args[0] if prize_args else 1
            # Ensure user_properties structure exists
            if user_id not in user_properties:
                user_properties[user_id] = {}
            if item_name not in user_properties[user_id]:
                 user_properties[user_id][item_name] = 0
            user_properties[user_id][item_name] += quantity
            message.reply_text(f"📦 **مبروك! تم إضافة {quantity} من '{item_name}' إلى ممتلكاتك!**")
        elif prize_type == "boost":
            boost_name = prize_value
            duration = prize_args[0] if prize_args else 0
            # Implement boost logic (requires checking boost status in relevant handlers)
            # This is complex without persistence; placeholder
            message.reply_text(f"⚡ **حصلت على ميزة '{boost_name}' لمدة {duration} ثانية! (تتطلب تطبيق خاص للاستفادة منها)**")
        elif prize_type == "none":
            message.reply_text("😔 **حظ أوفر في المرة القادمة!**")


# 🏠 نظام الممتلكات 🏠
@app.on_message(filters.text & filters.group & filters.incoming)
def property_system_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Ensure user has a bank account
    if user_id not in bank_accounts:
         return # Handled by bank_system_cmd gatekeeper

    # Available properties and their buy/sell prices
    property_prices = {
        "سيارة": {"buy": 200000, "sell": 150000},
        "بيت": {"buy": 500000, "sell": 400000},
        "متجر": {"buy": 1000000, "sell": 800000},
        "مزرعة": {"buy": 750000, "sell": 600000},
        "أرض": {"buy": 300000, "sell": 250000},
        "يخت": {"buy": 5000000, "sell": 4000000},
        "طائرة": {"buy": 10000000, "sell": 8000000},
        "ماسة": {"buy": 500000, "sell": 450000} # Added الماسة if it's tradable
    }
    available_items = list(property_prices.keys())

    if text.startswith("شراء"):
        parts = text.split()
        if len(parts) < 3:
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: شراء [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة: " + ", ".join(available_items))

        try:
            quantity = int(parts[1])
            if quantity <= 0: return message.reply_text("❌ **يجب أن تكون الكمية موجبة!**")
            item_name = parts[2] # Assuming item name is a single word

            if item_name not in property_prices:
                return message.reply_text(f"🚫 **الممتلكات '{item_name}' غير متاحة للشراء.**\nالمتاحة: " + ", ".join(available_items))

            cost = property_prices[item_name]["buy"] * quantity

            if bank_accounts[user_id] < cost:
                return message.reply_text(f"🚫 **رصيدك غير كافي لشراء {quantity} من {item_name}! التكلفة: {cost} ريال، رصيدك: {bank_accounts[user_id]}**")

            bank_accounts[user_id] -= cost

            # Ensure user_properties structure exists
            if user_id not in user_properties:
                user_properties[user_id] = {}
            if item_name not in user_properties[user_id]:
                 user_properties[user_id][item_name] = 0

            user_properties[user_id][item_name] += quantity
            message.reply_text(f"✅ **تم شراء {quantity} من {item_name} مقابل {cost} ريال بنجاح!**")

        except (ValueError, IndexError):
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: شراء [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة: " + ", ".join(available_items))
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء الشراء: {e}**")


    elif text.startswith("بيع"):
        parts = text.split()
        if len(parts) < 3:
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: بيع [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة للبيع: " + ", ".join(available_items))

        try:
            quantity = int(parts[1])
            if quantity <= 0: return message.reply_text("❌ **يجب أن تكون الكمية موجبة!**")
            item_name = parts[2] # Assuming item name is a single word

            if item_name not in property_prices:
                return message.reply_text(f"🚫 **الممتلكات '{item_name}' غير متاحة للبيع.**\nالمتاحة: " + ", ".join(available_items))

            # Ensure user_properties structure exists and item quantity is sufficient
            if user_id not in user_properties or item_name not in user_properties[user_id] or user_properties[user_id][item_name] < quantity:
                 owned = user_properties.get(user_id, {}).get(item_name, 0)
                 return message.reply_text(f"🚫 **أنت لا تملك هذه الكمية من {item_name}! لديك {owned} فقط.**")

            sell_price_per_item = property_prices[item_name]["sell"]
            total_earnings = sell_price_per_item * quantity

            bank_accounts[user_id] += total_earnings
            user_properties[user_id][item_name] -= quantity

            # Clean up if quantity drops to 0
            if user_properties[user_id][item_name] == 0:
                 del user_properties[user_id][item_name]
                 if not user_properties[user_id]:
                      del user_properties[user_id] # Remove user entry if no properties left

            message.reply_text(f"✅ **تم بيع {quantity} من {item_name} مقابل {total_earnings} ريال! رصيدك الحالي: {bank_accounts[user_id]}**")

        except (ValueError, IndexError):
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: بيع [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة للبيع: " + ", ".join(available_items))
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء البيع: {e}**")

    elif text == "ممتلكاتي": # Added command to show properties
         if user_id not in user_properties or not user_properties[user_id]:
              return message.reply_text("🏠 **لا تمتلك أي ممتلكات حالياً.**")

         property_lines = []
         for item, quantity in user_properties[user_id].items():
              property_lines.append(f"• {item}: {quantity}")

         message.reply_text("🏠 **ممتلكاتك:**\n" + "\n".join(property_lines))


# 🚔 نظام الشرطة والعصابات والسجن 🚔
# `banned_users` used here for prison time is separate from Telegram ban list

@app.on_message(filters.text & filters.group & filters.incoming)
def job_prison_system_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Check if user is currently in prison (Telegram ban status is separate)
    if user_id in banned_users and banned_users[user_id] > time.time():
         remaining_time = int(banned_users[user_id] - time.time())
         minutes = remaining_time // 60
         seconds = remaining_time % 60
         return message.reply_text(f"⏳ **أنت مسجون حالياً!** تبقى لك {minutes} دقيقة و {seconds} ثانية. لا يمكنك استخدام الأوامر.")
         # Note: This check needs to be at the very beginning of ALL command handlers if prison should block commands.
         # For simplicity, I'll only apply it within this specific handler for prison-related commands.

    # Ensure user has a bank account for job/prison actions
    if user_id not in bank_accounts:
         return # Handled by bank_system_cmd gatekeeper


    if text == "انضم شرطة":
        if user_id in user_jobs or user_id in gang_leaders:
            return message.reply_text("🚫 **لديك وظيفة أو منصب بالفعل!**")
        user_jobs[user_id] = "شرطة"
        message.reply_text("👮‍♂️ **أنت الآن شرطي! راتبك أقل لكنك لا تسجن.**")

    elif text == "انضم عصابة":
        if user_id in user_jobs or user_id in gang_leaders:
            return message.reply_text("🚫 **لديك وظيفة أو منصب بالفعل!**")
        user_jobs[user_id] = "عصابة"
        message.reply_text("🔫 **أنت الآن عضو عصابة! راتبك عالي لكنك معرض للسجن.**")

    elif text == "انضم رئيس عصابة": # Note: The original code used "انضم كرئيس عصابة"
        if user_id in user_jobs or user_id in gang_leaders:
            return message.reply_text("🚫 **لديك وظيفة أو منصب بالفعل!**")
        # Optional: Limit to one gang leader?
        # if gang_leaders:
        #     return message.reply_text("🚫 **يوجد رئيس عصابة بالفعل!**")
        gang_leaders[user_id] = True
        user_jobs[user_id] = "رئيس عصابة" # Store job as well
        message.reply_text("💀 **أنت الآن رئيس العصابة! راتبك أعلى لكن فرصتك في السجن أكبر.**")

    elif text == "ترجل": # Added command to leave job/position
         if user_id in gang_leaders:
              del gang_leaders[user_id]
              del user_jobs[user_id] # Remove job too
              message.reply_text("✅ **تخليت عن منصب رئيس العصابة!**")
         elif user_id in user_jobs:
              del user_jobs[user_id]
              message.reply_text("✅ **تخليت عن وظيفتك!**")
         else:
              message.reply_text("ℹ️ **أنت لا تشغل أي منصب أو وظيفة حالياً.**")

    elif text.startswith("سجن"): # Gang member/leader tries to avoid prison
        # Check if the user issuing the command is a gang member or leader
        if user_id not in gang_leaders and user_jobs.get(user_id) != "عصابة":
            return message.reply_text("🚫 **فقط أفراد العصابة يمكنهم محاولة تجنب السجن!**")

        # Simulate chance of getting caught and sent to prison
        chance = random.randint(1, 10) # Chance out of 10
        prison_duration = 3600 # 1 hour in seconds

        if chance <= 3:  # 30% chance of getting caught
            banned_users[user_id] = time.time() + prison_duration
            message.reply_text("🚔 **تم القبض عليك! أنت الآن في السجن لمدة ساعة.**")
        else: # 70% chance of success
            message.reply_text("🔫 **نجوت من الشرطة هذه المرة!**")

    elif text == "سجني": # Check prison status
        if user_id in banned_users and banned_users[user_id] > time.time():
            remaining_time = int(banned_users[user_id] - time.time())
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            message.reply_text(f"⏳ **أنت مسجون حالياً!** تبقى لك {minutes} دقيقة و {seconds} ثانية.")
        elif user_id in banned_users and banned_users[user_id] <= time.time():
             del banned_users[user_id] # Time served, release user
             message.reply_text("✅ **تم الإفراج عنك من السجن!**")
        else:
            message.reply_text("✅ **أنت لست مسجوناً حالياً.**")

    elif text == "سداد ديوني": # Pay bail to get out of prison
        if user_id in banned_users and banned_users[user_id] > time.time():
            bail_amount = 5000
            if bank_accounts[user_id] < bail_amount:
                return message.reply_text(f"🚫 **رصيدك ({bank_accounts[user_id]}) غير كافي لسداد كفالة السجن البالغة {bail_amount} ريال!**")

            bank_accounts[user_id] -= bail_amount
            del banned_users[user_id]
            message.reply_text(f"💸 **تم دفع كفالة السجن ({bail_amount} ريال)، وتم الإفراج عنك! رصيدك الحالي: {bank_accounts[user_id]}**")
        else:
            message.reply_text("ℹ️ **أنت لست مسجوناً لسداد الكفالة.**")


# 🎁 مكافأة الشرطة من المطور (في الخاص) 🎁
# This command is for the main developer only, sent in private chat
@app.on_message(filters.text & filters.private & filters.incoming)
def reward_police_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Check if user is the main developer
    if user_id != main_dev:
        return # Handled by dev_commands_handler gatekeeper

    if text.startswith("مكافأة الشرطة"):
        reward_amount = 5000
        police_count = 0
        try:
            for user, job in user_jobs.items():
                if job == "شرطة":
                    bank_accounts[user] = bank_accounts.get(user, 0) + reward_amount
                    # Attempt to notify the user
                    try:
                        police_user_obj = client.get_users(int(user))
                        client.send_message(user, f"🎁 **تم منحك مكافأة شرطة بقيمة {reward_amount} ريال من المطور!**")
                    except Exception:
                        # Handle cases where sending message fails (e.g., user blocked bot)
                        print(f"Could not send reward message to police user ID: {user}")
                    police_count += 1

            message.reply_text(f"✅ **تم إرسال مكافأة بقيمة {reward_amount} ريال لـ {police_count} فرد من أفراد الشرطة!**")
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء إرسال مكافأة الشرطة:** {e}")


# 🛑 نظام البلاغات 🛑
# هذا النظام يتطلب حفظ البيانات (Persistence) أيضاً.

# تخزين بيانات البلاغات
reports = {}  # عدد البلاغات المُرسلة من كل مستخدم يوميًا {user_id_str: count} (يحتاج إعادة تعيين يومية)
user_reported_count = {} # عدد البلاغات المستلمة على كل مستخدم {user_id_str: count}
report_limits = {}  # الحد المطلوب للبلاغات على مستخدم قبل العقوبة {chat_id_str: limit}
linked_channels = {}  # القروبات المرتبطة بالقنوات لإرسال البلاغات إليها {chat_id_str: channel_id_str}

# 📢 أمر الإبلاغ 📢
@app.on_message(filters.text & filters.group & filters.incoming)
def report_message_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    if text == "بلاغ" and message.reply_to_message:
        target_message = message.reply_to_message
        target_user = target_message.from_user
        target_user_id = str(target_user.id)

        if target_user_id == user_id:
             return message.reply_text("❌ **لا يمكنك الإبلاغ عن نفسك!**")
        if target_user.is_bot:
             return message.reply_text("❌ **لا يمكنك الإبلاغ عن بوت!**")

        # --- Check daily report limit for the sender ---
        # This requires daily reset logic, which isn't implemented.
        # For now, let's remove the daily limit check or implement a simple one.
        # Simple in-memory check (resets on bot restart):
        # if user_id not in reports: reports[user_id] = 0
        # if reports[user_id] >= 3: # Example limit
        #     return message.reply_text("🚫 **لقد استخدمت جميع البلاغات اليومية المسموح بها!**")
        # reports[user_id] += 1
        # Removing daily limit check for now due to lack of daily reset logic.

        # --- Update report count on the reported user ---
        if target_user_id not in user_reported_count:
            user_reported_count[target_user_id] = 0
        user_reported_count[target_user_id] += 1

        # --- Get the required report limit for this chat ---
        max_reports = report_limits.get(chat_id, 5) # Default limit is 5

        # --- Construct the report message ---
        report_text = f"""
🚨 **بلاغ جديد في القروب:** {message.chat.title} (`{chat_id}`)
👤 **المُبلغ:** {message.from_user.mention} (`{user_id}`)
🔹 **المُبلغ عنه:** {target_user.mention} (`{target_user_id}`)
📝 **الرسالة المبلغ عنها:**
```
{target_message.text or target_message.caption or 'رسالة غير نصية'}
```
🔗 **رابط الرسالة:** [انتقل للرسالة]({target_message.link})
📢 **عدد البلاغات على المستخدم:** {user_reported_count[target_user_id]} / {max_reports}
"""
        # Append message ID for easy lookup/action if needed
        report_text += f"\n🆔 **آيدي الرسالة:** `{target_message.id}`"

        # --- Prepare inline buttons for actions if report count reaches limit ---
        buttons = None
        if user_reported_count[target_user_id] >= max_reports:
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔇 كتم المستخدم", callback_data=f"mute_{target_user_id}_{chat_id}")],
                [InlineKeyboardButton("🚷 تقييد المستخدم", callback_data=f"restrict_{target_user_id}_{chat_id}")],
                # Add other actions? Kick, Ban?
                # [InlineKeyboardButton("👢 طرد المستخدم", callback_data=f"kick_{target_user_id}_{chat_id}")],
                # [InlineKeyboardButton("🚫 حظر المستخدم", callback_data=f"ban_{target_user_id}_{chat_id}")],
                 [InlineKeyboardButton("✅ تجاهل", callback_data=f"ignore_report_{target_user_id}_{chat_id}")] # Option to clear count
            ])

        # --- Send the report message ---
        report_sent = False
        # 1. Send to linked channel if exists and bot is admin there
        if chat_id in linked_channels:
            channel_id = linked_channels[chat_id]
            try:
                 # Verify bot is admin in the linked channel
                 me_in_channel = client.get_chat_member(int(channel_id), client.me.id)
                 if me_in_channel.status == ChatMemberStatus.ADMINISTRATOR:
                      client.send_message(int(channel_id), report_text, reply_markup=buttons, parse_mode="Markdown")
                      report_sent = True
                 else:
                     # If bot isn't admin, remove the linked channel entry? Or just fallback?
                     print(f"Bot is not admin in linked channel {channel_id} for chat {chat_id}. Falling back to main_dev/group.")
                     # Fallback below
            except Exception as e:
                 print(f"Error sending report to linked channel {channel_id}: {e}. Falling back.")
                 # Fallback below

        # 2. Fallback: Send to main_dev and the group itself if no linked channel worked
        if not report_sent:
            try:
                 client.send_message(int(main_dev), report_text, reply_markup=buttons, parse_mode="Markdown")
                 # Optionally send a less detailed message to the group
                 client.send_message(message.chat.id, f"✅ **تم إرسال بلاغ عن {target_user.mention} للإدارة! ({user_reported_count[target_user_id]} بلاغات مسجلة)**", parse_mode="HTML")
            except Exception as e:
                 message.reply_text(f"❌ **حدث خطأ أثناء إرسال البلاغ:** {e}")


    # Only reply if the command was specifically "بلاغ"
    # No need for a separate reply here as it's done inside the 'if' block


# 🔧 تحديد عدد البلاغات المطلوبة للعقوبة 🔧
@app.on_message(filters.text & filters.group & filters.incoming)
def set_report_limit_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0] != "ضع" or text[1] != "البلاغات":
        return # Not "ضع البلاغات" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

    try:
        limit = int(text[2])
        if limit <= 0:
            return message.reply_text("❌ **يجب أن يكون عدد البلاغات أكبر من صفر.**")
        report_limits[chat_id] = limit
        message.reply_text(f"✅ **تم تحديد الحد الأدنى للبلاغات على المستخدمين إلى {limit} بلاغات قبل اتخاذ إجراء!**")
    except (ValueError, IndexError):
        message.reply_text("❌ **استخدم الصيغة الصحيحة:** ضع البلاغات [الرقم]")


# 🔗 ربط القروب بالقناة (لإرسال البلاغات إليها) 🔗
@app.on_message(filters.text & filters.group & filters.incoming)
def link_group_to_channel_cmd(client, message):
    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0] != "ربط" or text[1] != "القناة":
        return # Not "ربط القناة" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("owner", 0): # Owner or main_owner needed
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**")

    channel_username_or_id = text[2]

    try:
        # Get channel object by username or ID to verify and get ID
        channel_chat = client.get_chat(channel_username_or_id)
        if channel_chat.type != "channel":
            return message.reply_text("❌ **المدخل ليس قناة!**")

        # Check if bot is admin in the target channel and has send messages permission
        me_in_channel = client.get_chat_member(channel_chat.id, client.me.id)
        if not (me_in_channel.status == ChatMemberStatus.ADMINISTRATOR and me_in_channel.privileges and me_in_channel.privileges.can_post_messages):
             return message.reply_text(f"❌ **البوت ليس مشرفاً في القناة أو لا يملك صلاحية إرسال الرسائل فيها!**")

        linked_channels[chat_id] = str(channel_chat.id) # Store channel ID as string
        message.reply_text(f"✅ **تم ربط القروب بالقناة {channel_chat.mention} (`{channel_chat.id}`) بنجاح! سيتم إرسال البلاغات هناك.**", parse_mode="HTML")
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء ربط القناة:** تأكد من أن المعرف/الآيدي صحيح وأن البوت مشرف في القناة ويملك صلاحية إرسال الرسائل. {e}")

# ⚖ تنفيذ العقوبات بناءً على البلاغات (من خلال أزرار Inline) ⚖
@app.on_callback_query()
def handle_report_actions(client, callback_query):
    data = callback_query.data
    user_id = str(callback_query.from_user.id)

    # Check if the user clicking the button has permission (e.g., admin or higher rank in bot system)
    # This check is important so any user can't click admin buttons
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher required to action on reports
         return callback_query.answer("❌ **لا تملك صلاحية تنفيذ هذا الإجراء!**", show_alert=True)

    parts = data.split("_")
    action = parts[0] # e.g., mute, restrict, ignore_report

    if action in ["mute", "restrict", "kick", "ban"]:
        if len(parts) != 3:
             return callback_query.answer("❌ **خطأ في بيانات الزر.**", show_alert=True)

        target_user_id = int(parts[1])
        chat_id = int(parts[2])

        # Optional: Check if the admin clicking has higher rank than the target user (if target is in bot ranks)
        # target_highest_rank, target_order = get_user_highest_rank(str(target_user_id))
        # if target_order >= sender_order:
        #      return callback_query.answer("❌ **لا يمكنك تنفيذ هذا الإجراء على شخص لديه رتبة مساوية أو أعلى منك!**", show_alert=True)

        try:
            # Attempt to get target user for mention in reply
            target_user_mention = f"المستخدم ذو الآيدي `{target_user_id}`"
            try:
                 target_user_obj = client.get_users(target_user_id)
                 target_user_mention = target_user_obj.mention
            except Exception:
                 pass # Ignore if user fetch fails, use ID in message

            if action == "mute":
                client.restrict_chat_member(chat_id, target_user_id, ChatPermissions(can_send_messages=False))
                callback_query.edit_message_text(f"🔇 **تم كتم المستخدم {target_user_mention} بنجاح!**", parse_mode="HTML")
                callback_query.answer("تم كتم المستخدم.", show_alert=False) # Small confirmation
            elif action == "restrict":
                client.restrict_chat_member(chat_id, target_user_id, ChatPermissions(
                    can_send_messages=False, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                    can_send_polls=False, can_change_info=False,
                    can_invite_users=False, can_pin_messages=False
                ))
                callback_query.edit_message_text(f"🚷 **تم تقييد المستخدم {target_user_mention} بنجاح!**", parse_mode="HTML")
                callback_query.answer("تم تقييد المستخدم.", show_alert=False)
            elif action == "kick": # Example for kick button
                 client.ban_chat_member(chat_id, target_user_id)
                 time.sleep(1) # Short delay before unbanning
                 client.unban_chat_member(chat_id, target_user_id)
                 callback_query.edit_message_text(f"👢 **تم طرد المستخدم {target_user_mention} بنجاح!**", parse_mode="HTML")
                 callback_query.answer("تم طرد المستخدم.", show_alert=False)
            elif action == "ban": # Example for ban button
                 client.ban_chat_member(chat_id, target_user_id)
                 callback_query.edit_message_text(f"🚫 **تم حظر المستخدم {target_user_mention} بنجاح!**", parse_mode="HTML")
                 callback_query.answer("تم حظر المستخدم.", show_alert=False)

            # Clear report count for this user after action
            if str(target_user_id) in user_reported_count:
                 del user_reported_count[str(target_user_id)]


        except Exception as e:
             # Report action failed (e.g., bot not admin, targeting owner)
             callback_query.answer(f"❌ فشل الإجراء: {e}", show_alert=True)
             # Optionally edit the message to indicate failure
             callback_query.message.reply_text(f"❌ **فشل تنفيذ الإجراء ({action}) على المستخدم ذو الآيدي `{target_user_id}` في القروب `{chat_id}`.**\nالسبب: {e}")


    elif action == "ignore_report":
         if len(parts) != 3:
             return callback_query.answer("❌ **خطأ في بيانات الزر.**", show_alert=True)
         target_user_id = parts[1]
         chat_id = parts[2] # Not strictly needed but good context
         # Clear report count for this user
         if target_user_id in user_reported_count:
              del user_reported_count[target_user_id]
         callback_query.edit_message_text(f"✅ **تم تجاهل البلاغات وإزالة سجلها للمستخدم.**")
         callback_query.answer("تم تجاهل البلاغات.", show_alert=False)


    elif data == "list_secondary_devs": # Handle this callback from the panel button
         # This logic is duplicated from the dev_commands_handler, consolidate or call that logic
         if secondary_devs:
             dev_list_lines = []
             for dev_id_str, name in secondary_devs.items():
                 try:
                     dev_user = client.get_users(int(dev_id_str))
                     dev_list_lines.append(f"• {dev_user.mention} ({name})")
                 except Exception:
                     dev_list_lines.append(f"• مستخدم غير معروف (ID: {dev_id_str}) ({name})")
             dev_list_text = "\n".join(dev_list_lines)
             callback_query.message.reply_text(f"🛠 **قائمة المطورين الثانويين:**\n{dev_list_text}", parse_mode="HTML")
         else:
             callback_query.message.reply_text("🚫 **لا يوجد مطورين ثانويين حالياً.**")

         callback_query.answer() # Answer the callback


# 🏆 نظام التفاعل والأوسمة 🏆
# هذا النظام يتطلب حفظ البيانات (Persistence).

# تخزين بيانات التفاعل
user_activity = {}  # نقاط التفاعل لكل عضو {user_id_str: points}
group_activity = {}  # نقاط التفاعل لكل قروب {chat_id_str: points}
user_achievements = {} # أوسمة المستخدمين {user_id_str: ["وسام1", "وسام2"]}


# 📝 احتساب التفاعل بناءً على نوع المشاركة
@app.on_message(filters.group & filters.incoming) # Apply to all message types in groups
def track_activity_handler(client, message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Ignore bots
    if message.from_user.is_bot:
         return

    # Initialize if needed
    if chat_id not in group_activity:
        group_activity[chat_id] = 0
    if user_id not in user_activity:
        user_activity[user_id] = 0
    if user_id not in user_achievements:
        user_achievements[user_id] = []


    # Assign points based on message type
    points_gained = 0
    if message.text:
        points_gained = 1
        if len(message.text) > 50: points_gained += 1 # Bonus for longer text
    elif message.photo:
        points_gained = 2
    elif message.sticker:
        points_gained = 1
    elif message.animation: # GIF
        points_gained = 2
    elif message.video:
         points_gained = 3
    elif message.audio:
         points_gained = 1
    elif message.voice:
         points_gained = 2
    elif message.video_note:
         points_gained = 2
    # Add points for other media types if needed


    if points_gained > 0:
         user_activity[user_id] += points_gained
         group_activity[chat_id] += points_gained

         # --- Check for achievements based on accumulated points ---
         current_points = user_activity[user_id]

         # Achievement 1: المتفاعل النشيط (100 نقاط)
         if current_points >= 100 and "💬 متفاعل نشيط" not in user_achievements[user_id]:
              user_achievements[user_id].append("💬 متفاعل نشيط")
              message.reply_text(f"🏅 **تهانينا {message.from_user.mention}! حصلت على وسام '💬 متفاعل نشيط' بسبب نشاطك في القروب!**", parse_mode="HTML")

         # Achievement 2: متفاعل قوي (300 نقاط)
         if current_points >= 300 and "🔥 متفاعل قوي" not in user_achievements[user_id]:
              user_achievements[user_id].append("🔥 متفاعل قوي")
              message.reply_text(f"🔥 **مذهل {message.from_user.mention}! أنت الآن '🔥 متفاعل قوي'! استمر!**", parse_mode="HTML")

         # Achievement 3: متفاعل ذهبي (500 نقاط)
         if current_points >= 500 and "🎖 متفاعل ذهبي" not in user_achievements[user_id]:
              user_achievements[user_id].append("🎖 متفاعل ذهبي")
              message.reply_text(f"🎖 **إنجاز عظيم {message.from_user.mention}! لقد وصلت إلى '🎖 متفاعل ذهبي'!**", parse_mode="HTML")

         # Achievement 4: أسطورة التفاعل (1000 نقاط)
         if current_points >= 1000 and "🏆 أسطورة التفاعل" not in user_achievements[user_id]:
              user_achievements[user_id].append("🏆 أسطورة التفاعل")
              message.reply_text(f"🏆 **لا يصدق {message.from_user.mention}! لقد أصبحت '🏆 أسطورة التفاعل' في البوت!**", parse_mode="HTML")

         # Optional: Reply showing current points or rank title based on points?
         # This could be spammy if done on every message. Maybe do it on a command like "تفاعلي".
         # The original code had a reply showing rank title here - let's keep it, but maybe make it less chatty.
         # Let's reply only when a new achievement is unlocked.
         # Original code replied every time: message.reply_text(f"🏅 **تم تسجيل تفاعلك! لقبك الحالي:** {title}")
         # This is too much. Remove the automatic reply about current points/title.


# 📊 عرض توب المتفاعلين في القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def top_users_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "توب المتفاعلين":
        # Filter users by those who have been active in this specific chat? Or overall?
        # Current user_activity is global. top_users_cmd is in filters.group.
        # Should filter by users who have sent messages in THIS group recently, or show overall top?
        # Let's show overall top from user_activity dictionary, but mention the group context.
        # To show top users *in this group*, you'd need activity tracked per user *per group*.
        # Sticking to global user_activity for simplicity as per original code.

        # Sort users by activity points
        # Get user objects for mentions (can be slow for many users)
        # Let's fetch user objects for the top N users
        top_n = 10
        sorted_users_ids = sorted(user_activity, key=user_activity.get, reverse=True)[:top_n]

        if not sorted_users_ids:
            return message.reply_text("🚫 **لا يوجد تفاعل كافي لعرض التوب!**")

        top_text_lines = ["🏆 **توب المتفاعلين في البوت:**\n"]
        for rank, user_id_str in enumerate(sorted_users_ids, start=1):
            points = user_activity[user_id_str]
            mention_text = f"المستخدم ذو الآيدي `{user_id_str}`"
            try:
                user = client.get_users(int(user_id_str))
                mention_text = user.mention
            except Exception:
                pass # Ignore if user fetch fails

            # Get user's current rank title based on points (same logic as in track_activity)
            if points >= 1000: title = "🏆 أسطورة التفاعل"
            elif points >= 500: title = "🎖 متفاعل ذهبي"
            elif points >= 300: title = "🔥 متفاعل قوي"
            elif points >= 100: title = "💬 متفاعل نشيط"
            else: title = "🙂 مشارك"

            top_text_lines.append(f"{rank} - {mention_text} ({title}) - {points} نقطة 🔥")

        message.reply_text("\n".join(top_text_lines), parse_mode="HTML")

# 📢 عرض توب القروبات الأكثر تفاعلًا
@app.on_message(filters.text & filters.private & filters.incoming)
def top_groups_cmd(client, message):
    text = message.text.lower()

    if text == "توب القروبات":
        # group_activity is global, this command is in private chat, makes sense.
        sorted_groups = sorted(group_activity.items(), key=lambda item: item[1], reverse=True)[:20]

        if not sorted_groups:
            return message.reply_text("🚫 **لا يوجد تفاعل كافي لعرض التوب!**")

        top_text_lines = ["🏆 **أكثر القروبات تفاعلًا:**\n"]
        for rank, (group_id_str, points) in enumerate(sorted_groups, start=1):
            chat_title = f"القروب ذو الآيدي `{group_id_str}`"
            try:
                chat = client.get_chat(int(group_id_str))
                chat_title = chat.title
            except Exception:
                pass # Ignore if chat fetch fails

            top_text_lines.append(f"{rank} - {chat_title} - {points} نقطة 🔥")

        message.reply_text("\n".join(top_text_lines))

# 🔄 تصفير نقاط التفاعل لعضو معين
@app.on_message(filters.text & filters.group & filters.incoming)
def reset_user_activity_cmd(client, message):
    text = message.text.split()
    if len(text) < 2 or text[0] != "صفر" or text[1] != "نقاط":
         return # Not "صفر نقاط" command

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")


    # Get target user from reply or argument
    user, error_message = get_target_user(client, message, allow_self=False) # Cannot reset self? Original code allowed. Let's allow.
    user, error_message = get_target_user(client, message, allow_self=True) # Allow resetting self

    if error_message:
         return message.reply_text(error_message)

    target_user_id_str = str(user.id)

    # Optional: Prevent resetting points of users with equal/higher rank?
    # target_highest_rank, target_order = get_user_highest_rank(target_user_id_str)
    # if target_order >= sender_order:
    #      return message.reply_text("❌ **لا يمكنك تصفير نقاط شخص لديه رتبة مساوية أو أعلى منك!**")


    if target_user_id_str in user_activity:
        user_activity[target_user_id_str] = 0
        # Clear achievements too? Original code didn't, let's match.
        # if target_user_id_str in user_achievements:
        #     user_achievements[target_user_id_str] = []
        message.reply_text(f"✅ **تم تصفير نقاط التفاعل لـ {user.mention}!**", parse_mode="HTML")
    else:
        message.reply_text(f"ℹ️ **المستخدم {user.mention} لا يمتلك نقاط تفاعل مسجلة لتصفيرها.**", parse_mode="HTML")


# 🔄 تصفير جميع النقاط في القروب (يقصد نقاط التفاعل)
@app.on_message(filters.text & filters.group & filters.incoming)
def reset_group_activity_cmd(client, message):
    text = message.text.lower()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if text == "صفر كل التفاعل":
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
        if sender_order < rank_order.get("admin", 0): # Admin or higher needed
            return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**")

        # This clears the group's total activity points
        if chat_id in group_activity:
            group_activity[chat_id] = 0

        # This should probably also clear *user* activity points *within this group*
        # But user_activity is global. Clearing global user_activity based on a group command is wrong.
        # To truly clear "all points in the group", activity must be tracked per user per group.
        # Given the current global user_activity structure, this command is misleading.
        # It only clears the group's *total* activity score.
        # A better command might be "صفر نقاطي في القروب" or require a per-group activity system.
        # Let's clarify what this command does based on the current global structure.
        # It clears the *group's accumulated score*, NOT individual user scores.
        # Let's modify the message to be accurate or change the command/logic.
        # Original code implies clearing all user points in the group, which the global dict doesn't support easily.
        # Let's keep the original action (clearing group_activity) but provide an accurate message.
        # Alternatively, iterate all users in the group and set their global score to 0? No, that's wrong.

        # Let's make this command clear *only* the group's total score.
        if chat_id in group_activity:
            group_activity[chat_id] = 0
            message.reply_text("✅ **تم تصفير نقاط التفاعل الكلية المسجلة لهذا القروب!**")
        else:
            message.reply_text("ℹ️ **لا توجد نقاط تفاعل كلية مسجلة لهذا القروب لتصفيرها.**")

        # If the intent was to reset user points for users *in this group*, the data structure needs change.
        # Since we are aiming for correctness based on the provided code structure, stick to clearing group_activity.


# 🎭 نظام تحليل المشاعر (بسيط جداً) 🎭
# ملاحظة: هذا التحليل بسيط جداً وقد يعطي نتائج غير دقيقة أو مزعجة.
# @app.on_message(filters.text & filters.group & filters.incoming)
# def analyze_sentiment_handler(client, message): # Original handler name
#     text = message.text.lower()
#
#     # Do not analyze commands
#     if text.startswith("/") or any(text.startswith(cmd) for cmd in ["رفع", "تنزيل", "رتبتي", "كشف", "قفل", "فتح", "حظر", "الغاء الحظر", "طرد", "كتم", "الغاء الكتم", "تقييد", "فك التقييد", "رفع القيود", "طرد البوتات", "طرد المحذوفين", "كشف البوتات", "القوانين", "ضع قوانين", "الرابط", "اضف رابط =", "المالك", "المالكين", "الإداريين", "المميزين", "اضف قناه", "حذف قناه", "مسح", "انشاء حساب بنكي", "رصيدي", "راتبي", "بخشيش", "استثمار", "العجلة", "شراء", "بيع", "ممتلكاتي", "انضم شرطة", "انضم عصابة", "انضم رئيس عصابة", "ترجل", "سجن", "سجني", "سداد ديوني", "بلاغ", "ضع البلاغات", "ربط القناة", "توب المتفاعلين", "توب القروبات", "صفر نقاط", "صفر كل التفاعل", "اضف كلمة", "حذف كلمة", "قائمة المنع", "ردود القروب"]):
#          return # Skip commands
#
#     positive_words = ["شكرا", "ممتاز", "رائع", "جميل", "احبك", "ممتن", "عظيم", "احسنت", "مبدع", "اسطورة"] # Added more words
#     negative_words = ["سيء", "غبي", "ممل", "كرهتك", "مزعج", "خايس", "وع", "قبيح", "اكره", "مشكلة"] # Added more words
#
#     text_for_analysis = text # Use the lowercased text
#
#     is_positive = any(word in text_for_analysis for word in positive_words)
#     is_negative = any(word in text_for_analysis for word in negative_words)
#
#     # Prioritize negative if both positive and negative words are present
#     if is_negative:
#         message.reply_text("😢 **يبدو أنك غير سعيد، حاول أن تأخذ استراحة قصيرة!**")
#     elif is_positive:
#         message.reply_text("😊 **رسالتك إيجابية! استمر في نشر الطاقة الإيجابية 💖**")
#     # No reply for neutral messages to reduce spam


# ✅ أمر /start الفلاوي (في الخاص) ✅
@app.on_message(filters.command("start") & filters.private & filters.incoming)
def start_command(client, message):
    user_name = message.from_user.first_name # اسم المستخدم

    # 🌟 أزرار الانلاين: زر المطور + زر إضافة البوت + زر قناة البوت
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 أضفني لقروبك", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("👨‍💻 المطوّر", url="https://t.me/rnp_e")],
        [InlineKeyboardButton("📢 قناة البوت", url="https://t.me/mwote")]
    ])

    # 🌟 رسالة الترحيب الفلاوية باللهجة السعودية/الخليجية
    welcome_text = f"""هلااااااا والله يا {user_name} 👋😎
🌟 شرفت البوت الأسطوري!
🔹 إذا تبي حماية وكنترول كامل، ضيفني قروبك ولا عليك من شي 🔥
🔹 إذا عندك أي مشكلة أو اقتراح، مطوّري **@rnp_e** موجود ما يقصر 💪
📢 تابع قناة البوت للمستجدات هنا: **@mwote**

أنا هنا للمساعدة في إدارة قروبك وحمايته، وجايب معي فعاليات وألعاب 😉 جرب ترسل لي "لوحة التحكم" في الخاص إذا كنت المطور الأساسي!
"""

    # إرسال الرسالة مع الأزرار
    message.reply_text(welcome_text, reply_markup=keyboard, parse_mode="Markdown") # Use Markdown for bold/links

# --- نهاية الدوال ---


# 🔥 تشغيل البوت 🔥
# تأكد من أن app.run() يتم استدعاؤها مرة واحدة فقط في نهاية السكريبت
if __name__ == "__main__":
    print("البوت يعمل...")
    app.run()
# --- END FILE: bot.py ---