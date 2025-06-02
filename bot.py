import os
import random
import time
import json
import sys # Import sys for simulated restart
import re # Import re for regex link detection

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus # Import ChatMemberStatus for checking member status

# 🚫 ملاحظة هامة: حذف الملفات يؤدي إلى فقدان البيانات! 🚫
# ✅ تم التعليق على هذا الجزء للسماح بحفظ البيانات في ملف json
# for file in ["ProtectionBot.session", "ProtectionBot.session-journal", "bot.sqlite3"]:
#     if os.path.exists(file):
#         try:
#             os.remove(file)
#             print(f"Removed {file}")
#         except Exception as e:
#             print(f"Error removing {file}: {e}")

# بيانات البوت (يُفضل استخدام متغيرات البيئة بدلاً من كتابتها هنا مباشرةً لأسباب أمنية)
# تم استبدال القيم بالقيم الموجودة في طلب المستخدم/الكود السابق
api_id = 26977113 # REPLACE WITH YOUR API ID
api_hash = "9248c3a0471142764cb438997f287285" # REPLACE WITH YOUR API HASH
bot_token = "8100374611:AAHNFZKrJUc4hhdqeVr0woAWw9RdCD2DdgY" # REPLACE WITH YOUR BOT TOKEN

# معلومات المطور وقناة البوت
main_dev = "7601607055"  # آيدي المطور الأساسي @rnp_e
bot_channel_username = "mwote" # معرف قناة البوت @mwote
bot_name_arabic = "ارثر" # اسم البوت بالعربي للتفاعل معه

# تشغيل البوت
app = Client("ProtectionBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# 💾 حفظ وتحميل البيانات 💾
DATA_FILE = "bot_data.json"

# تخزين البيانات في قواميس عامة (سيتم حفظها في ملف)
# تم دمج جميع القواميس هنا لسهولة الحفظ والتحميل
bot_data = {
    "ranks": {
        "the_goat": {"7601607055": True},  # The GOAT خاص بالمطور الأساسي فقط
        "dev": {},         # رتبة المطورين الثانويين
        "m": {},           # رتبة M
        "owner_main": {},  # المالك الأساسي (يمكن استخدامه للمالكين المساعدين)
        "owner": {},       # المالك
        "creator": {},     # المنشئ (يمكن استخدامه لمنح رتبة شبيهة بمنشئ القروب يدوياً)
        "admin": {},       # المدير (رتبة إدارية عليا)
        "moderator": {},   # الأدمن (رتبة إشرافية أقل)
        "vip": {},         # المميز (رتبة شرفية بصلاحيات محدودة أو بدون)
        "supervisor": {},  # المشرف (رتبة إشرافية)
        "beautiful": {}    # العضو الجميل 🌟 (رتبة شرفية بدون صلاحيات)
    },
    "rank_order": { # ترتيب الرتب من الأقوى للأضعف (كلما زاد الرقم زادت القوة)
        "the_goat": 10, # أعلى رتبة
        "dev": 9,
        "m": 8,
        "owner_main": 7,
        "owner": 6,
        "creator": 5,
        "admin": 4,
        "moderator": 3,
        "vip": 2,
        "supervisor": 1,
        "beautiful": 0
    },
    "rank_display_names": { # أسماء الرتب للعرض في الرسائل
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
    },
    "group_settings": {},       # إعدادات القروب (للقفل/الفتح، القوانين، الرابط، الردود التلقائية، الأوامر المضافة إلخ) {chat_id_str: {setting_key: value}}
    "protection_settings": {},  # إعدادات الحماية لكل قروب (الروابط، التكرار، التوجيه، الصور، إلخ) {chat_id_str: {feature_key: True/False, "banned_words": []}}
    "user_messages_history": {},# سجل رسائل المستخدمين للتحكم بالسبام {chat_id_str: {user_id_str: [timestamp1, ...]}}
    "bank_accounts": {},        # الحسابات البنكية {user_id_str: balance}
    "user_properties": {},      # ممتلكات المستخدمين {user_id_str: {item_name: quantity}}
    "stock_market": {"value": 100}, # قيمة الأسهم المتغيرة (مثال بسيط) - Needs global update logic if truly fluctuating
    "loans": {},                # القروض {user_id_str: amount_due} - Not implemented yet
    "insurance": {},            # التأمين على الممتلكات {user_id_str: {item_name: expiry_timestamp}} - Not implemented yet
    "vip_cards": {},            # بطاقات VIP {user_id_str: expiry_timestamp} - Needs expiry check
    "user_jobs": {},            # الوظائف {user_id_str: "job_name"} (شرطة/عصابة/رئيس عصابة)
    "gang_leaders": {},         # رؤساء العصابات {user_id_str: True} - redundant with user_jobs but kept for legacy
    "banned_users": {},         # المستخدمين المعاقبين بالسجن {user_id_str: end_timestamp} - Prison system
    "reports": {},              # عدد البلاغات المُرسلة من كل مستخدم يوميًا {user_id_str: {date: count}} - Needs daily reset logic
    "user_reported_count": {},  # عدد البلاغات المستلمة على كل مستخدم {user_id_str: count} - Used for report action threshold
    "report_limits": {},        # الحد المطلوب للبلاغات على مستخدم قبل العقوبة {chat_id_str: limit}
    "linked_channels": {},      # القروبات المرتبطة بالقنوات لإرسال البلاغات إليها {chat_id_str: [channel_id_str, ...]} - Renamed from linked_report_channels in code, kept name in data structure for clarity. Let's use linked_report_channels consistently.
    "user_activity": {},        # نقاط التفاعل لكل عضو {user_id_str: points} - Global activity
    "group_activity": {},       # نقاط التفاعل لكل قروب {chat_id_str: points} - Global group score
    "user_achievements": {},    # أوسمة المستخدمين {user_id_str: ["وسام1", "وسام2"]}
    "secondary_devs": {},       # قائمة المطورين الثانويين {user_id_str: "اسم اختياري"}
    "global_auto_replies": {   # الردود التلقائية العامة (افتراضية)
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
        "جاي": ["حيّاك الله، البيت بيتك", "على هونك، لا تستعجل", "جايك؟ متى وصلت؟"],
        "مساء الخير": ["مساء النور والسرور 🌹", "مساء الورد يا حلو", "يسعد مساكم بكل خير"] # إضافة تحية
    },
     # قائمة الكلمات المفتاحية لمنع الإباحيات - يجب مراجعتها بحذر شديد
    "pornography_keywords": [
        "نياكه", "ممحونه", "سكس", "مص", "قحبه", "شراميط", "نيك", "طيز", "كس", "زب",
        "عاهره", "اباحيه", "سحاق", "لواط", "اغتصاب", "افلام ممنوعه", "مقاطع وصخه",
        "كساس", "اير", "شرموطه", "ديوث", "سكسي", "قحاب", "خول", "خنيث", "شواذ", "سحاقيات", "بنوتي", "مقاطع سيكس",
        "صور سيكس", "افلام سكس", "اغاني سكس", "موقع سكس", "شات سكس", "قروب سكس", "تبادل زوجات", "محارم", "لواط اطفال",
        "نيك جماعي", "اهات", "آهات", "ورعان", "مشتهيه", "زب صناعي", "كس صناعي", "مخنثات", "متحولين", "سادي", "مازوخي",
        "اغراء", "عاريات", "لباس داخلي شفاف", "عضوي التناسلي", "فرج", "قضيب", "ثدي", "مؤخرة", "بزاز", "كوس", "شفشفه",
        "دعاره", "فاجرة", "مومس", "مومسات", "شبق", "مني", "سائل منوي", "قذف", "استمناء", "عاده سريه", "بظر", "شفرين",
        "كس مشعر", "كس املس", "طيز كبير", "ثدي كبير", "مؤخرة كبيرة", "نيك عنيف", "سكس عنيف", "اغتصاب جماعي", "تعذيب جنسي",
        "شرمطة", "شرميط", "متناكة", "قوا", "مقوى", "انحراف", "منحرفه", "منحرف", "قروب انحراف", "شات انحراف", "تبادل انحراف",
        "عصابات سكس", "شرطة سكس", "سجن سكس", "سجينه سكس", "مسجون سكس", "دعارة اطفال", "نيك اطفال", "ورعان صغار",
        "بنات صغار سكس", "لواط صغار", "سحاق صغار", "انتصاب", "رعشة", "نشوة جنسية", "سكس حيوانات", "بهيمية", "نيك البهيمة",
        "نيك حيوان", "سكس مع حيوانات", "عبودية جنسية", "BDSM", "قيود جنسية", "تعليق جنسي", "اكل البراز", "شرب البول",
        "نيك ميت", "nkrofelia", "نيك اجباري", "اغتصاب قسري", "هتك عرض", "تحرش جنسي", "اختصاب", "مشتهية", "مبادل",
        "منيكة", "كواد", "خولات", "ديوثين", "قواد", "شواذ صغار", "لوطي", "لسبين", "سكس كام", "شات كام", "مقاطع كام",
        "بث مباشر سكس", "لايف سكس", "اوفلاين سكس", "تنزيل سكس", "مشاهدة سكس", "رابط سكس", "جروب سكس", "قناة سكس",
        "باترون سكس", "اشتراك سكس", "vip سكس", "سكس مجاني", "سكس عربي", "سكس اجنبي", "سكس مترجم", "سكس طبيعي",
        "سكس صناعي", "العاب جنسية", "ادوات جنسية", "مساج جنسي", "تدليك جنسي", "علاج جنسي", "صحة جنسية", # بعض الكلمات قد تكون حميدة، يجب الحذر جداً
        "ثقافة جنسية", "تربية جنسية", "توعية جنسية", "امراض جنسية", "عقم", "خصوبة", "حمل", "ولادة", "اجهاض", "منشطات جنسية",
        "ضعف جنسي", "برود جنسي", "سرعة قذف", "تاخير قذف", "تضخيم ذكر", "تجميل مهبل", "عمليات تجميل جنسية", "شذوذ جنسي",
        "انحرافات جنسية", "ميول جنسية", "هوية جنسية", "جندر", "مثليين", "مزدوجين", "متحولين جنسيا", "خواجه", "نيج" # إضافة كلمات جديدة
    ],
    "cooldowns": {} # Added cooldowns here for persistence
}

# اختصارات لسهولة الوصول للبيانات
ranks = bot_data["ranks"]
rank_order = bot_data["rank_order"]
rank_display_names = bot_data["rank_display_names"]
group_settings = bot_data["group_settings"]
protection_settings = bot_data["protection_settings"]
user_messages_history = bot_data["user_messages_history"]
bank_accounts = bot_data["bank_accounts"]
user_properties = bot_data["user_properties"]
stock_market = bot_data["stock_market"]
loans = bot_data["loans"]
insurance = bot_data["insurance"]
vip_cards = bot_data["vip_cards"]
user_jobs = bot_data["user_jobs"]
gang_leaders = bot_data["gang_leaders"]
banned_users = bot_data["banned_users"]
reports = bot_data["reports"]
user_reported_count = bot_data["user_reported_count"]
report_limits = bot_data["report_limits"]
linked_channels = bot_data["linked_channels"] # Renamed to linked_report_channels in logic, but keeping key name
user_activity = bot_data["user_activity"]
group_activity = bot_data["group_activity"]
user_achievements = bot_data["user_achievements"]
secondary_devs = bot_data["secondary_devs"]
global_auto_replies = bot_data["global_auto_replies"]
pornography_keywords = bot_data["pornography_keywords"]
# Access cooldowns directly from bot_data where needed, or create a shortcut
# cooldowns = bot_data["cooldowns"] # If you want a shortcut

def load_data():
    """Loads bot data from the JSON file."""
    global bot_data, ranks, rank_order, rank_display_names, group_settings, protection_settings, user_messages_history, bank_accounts, user_properties, stock_market, loans, insurance, vip_cards, user_jobs, gang_leaders, banned_users, reports, user_reported_count, report_limits, linked_channels, user_activity, group_activity, user_achievements, secondary_devs, global_auto_replies, pornography_keywords # Add cooldowns here
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                loaded_data = json.load(f)
                # Update the global dictionaries with loaded data, preserving existing structure
                # Check for each key and update individually to handle missing keys in older files
                if "ranks" in loaded_data: bot_data["ranks"].update(loaded_data["ranks"])
                # rank_order and rank_display_names are mostly static, update if needed but might override custom
                # For safety, maybe don't update these from file unless specifically designed
                # bot_data["rank_order"].update(loaded_data.get("rank_order", {}))
                # bot_data["rank_display_names"].update(loaded_data.get("rank_display_names", {}))
                if "group_settings" in loaded_data: bot_data["group_settings"].update(loaded_data.get("group_settings", {}))
                if "protection_settings" in loaded_data: bot_data["protection_settings"].update(loaded_data.get("protection_settings", {}))
                if "user_messages_history" in loaded_data: bot_data["user_messages_history"].update(loaded_data.get("user_messages_history", {}))
                if "bank_accounts" in loaded_data: bot_data["bank_accounts"].update(loaded_data.get("bank_accounts", {}))
                if "user_properties" in loaded_data: bot_data["user_properties"].update(loaded_data.get("user_properties", {}))
                # Initialize sub-dictionaries if they don't exist after update
                for user_id in bot_data["user_properties"]:
                     if not isinstance(bot_data["user_properties"][user_id], dict):
                           bot_data["user_properties"][user_id] = {} # Fix corrupted entry
                if "stock_market" in loaded_data: bot_data["stock_market"].update(loaded_data.get("stock_market", {}))
                if "loans" in loaded_data: bot_data["loans"].update(loaded_data.get("loans", {}))
                if "insurance" in loaded_data: bot_data["insurance"].update(loaded_data.get("insurance", {}))
                if "vip_cards" in loaded_data: bot_data["vip_cards"].update(loaded_data.get("vip_cards", {}))
                if "user_jobs" in loaded_data: bot_data["user_jobs"].update(loaded_data.get("user_jobs", {}))
                if "gang_leaders" in loaded_data: bot_data["gang_leaders"].update(loaded_data.get("gang_leaders", {}))
                if "banned_users" in loaded_data: bot_data["banned_users"].update(loaded_data.get("banned_users", {}))
                if "reports" in loaded_data: bot_data["reports"].update(loaded_data.get("reports", {}))
                if "user_reported_count" in loaded_data: bot_data["user_reported_count"].update(loaded_data.get("user_reported_count", {}))
                if "report_limits" in loaded_data: bot_data["report_limits"].update(loaded_data.get("report_limits", {}))
                # Handle old linked_channels key gracefully if structure changed {chat_id: channel_id} to {chat_id: [channel_id]}
                loaded_linked_channels = loaded_data.get("linked_channels", {})
                for cid, val in loaded_linked_channels.items():
                    if isinstance(val, str): # Old format {chat_id: channel_id_str}
                         if cid not in bot_data["linked_channels"]: bot_data["linked_channels"][cid] = []
                         if val not in bot_data["linked_channels"][cid]: bot_data["linked_channels"][cid].append(val)
                    elif isinstance(val, list): # New format {chat_id: [channel_id_str, ...]}
                         if cid not in bot_data["linked_channels"]: bot_data["linked_channels"][cid] = []
                         for item in val:
                              if item not in bot_data["linked_channels"][cid]: bot_data["linked_channels"][cid].append(item)
                    # Handle cases where linked_channels might be corrupted or not a list/string
                    elif isinstance(val, dict): # Example: if it was mistakenly saved as a dict {}
                         bot_data["linked_channels"][cid] = [] # Reset to empty list

                if "user_activity" in loaded_data: bot_data["user_activity"].update(loaded_data.get("user_activity", {}))
                if "group_activity" in loaded_data: bot_data["group_activity"].update(loaded_data.get("group_activity", {}))
                if "user_achievements" in loaded_data: bot_data["user_achievements"].update(loaded_data.get("user_achievements", {}))
                 # Ensure achievement entries are lists
                for user_id in bot_data["user_achievements"]:
                     if not isinstance(bot_data["user_achievements"][user_id], list):
                          bot_data["user_achievements"][user_id] = [] # Fix corrupted entry

                if "secondary_devs" in loaded_data: bot_data["secondary_devs"].update(loaded_data.get("secondary_devs", {}))
                # Global auto replies could be updated, but might override defaults. Safer not to, unless specifically saving/loading these.
                # bot_data["global_auto_replies"].update(loaded_data.get("global_auto_replies", {}))
                # Ensure pornography_keywords exists
                if "pornography_keywords" in loaded_data: bot_data["pornography_keywords"] = loaded_data["pornography_keywords"]
                else: bot_data["pornography_keywords"] = [] # Initialize if missing

                # Load cooldowns
                if "cooldowns" in loaded_data: bot_data["cooldowns"].update(loaded_data.get("cooldowns", {}))
                else: bot_data["cooldowns"] = {} # Initialize if missing

                # Re-assign shortcuts (already done by the global assignment after bot_data definition)
                # No need to re-assign here if the global dictionaries are updated in place or replaced correctly.
                # The `global` keyword makes the functions refer to the top-level variables.
                # A better pattern might be to pass bot_data to functions or use a class.
                # Sticking to global for now as per code style.

            print("Data loaded successfully.")
        except json.JSONDecodeError:
             print(f"Error decoding JSON from {DATA_FILE}. File might be corrupt. Starting with default data.")
             # Optionally, back up the corrupt file before overwriting or exiting
             # os.rename(DATA_FILE, f"{DATA_FILE}.corrupt_{int(time.time())}")
             # Continue with default empty bot_data defined above
        except Exception as e:
            print(f"Error loading data: {e}. Starting with default data.")
            # Continue with default empty bot_data defined above
    else:
        print("Data file not found. Starting with empty data.")
        # Ensure bot_data has the initial structure even if file doesn't exist
        # This is handled by the initial definition of bot_data


def save_data():
    """Saves bot data to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(bot_data, f, indent=4)
        # print("Data saved successfully.") # Too chatty
    except Exception as e:
        print(f"Error saving data: {e}")


# Load data when the bot starts
load_data()


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
                elif user_arg.isdigit(): # Ensure it's digits before converting to int
                    # البحث عن طريق الآيدي
                    user = client.get_users(int(user_arg))
                else:
                     error_message = "❌ **الرجاء إدخال المعرف (@username) أو الآيدي (الرقم) الصحيح!**"
                     return None, error_message
            except Exception:
                error_message = "❌ **لم يتم العثور على المستخدم. تأكد من إدخال المعرف أو الآيدي الصحيح!**"
                return None, error_message
        else:
             error_message = "❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**"
             return None, error_message

    if user and not allow_self and str(user.id) == str(message.from_user.id):
         return None, "❌ **لا يمكنك تنفيذ هذا الأمر على نفسك!**"

    # Allow targeting bots for some commands (like `كشف`) but block for moderation
    # Let's keep the general block here, and refine per command if a bot should be targetable.
    # The original code had this block in get_target_user, let's move it to specific mod commands.
    # if user and user.is_bot:
    #      return None, "❌ **لا يمكنك تنفيذ هذا الأمر على بوت آخر!**"

    # Ensure user is not None before returning
    if user is None:
         error_message = "❌ **لم يتم تحديد المستخدم المستهدف بشكل صحيح.**" # Generic error if logic failed somehow
         return None, error_message


    return user, error_message

def get_user_highest_rank(user_id_str):
    """
    الحصول على أعلى رتبة يمتلكها المستخدم وقوتها بناءً على ترتيب الرتب.
    يعيد (اسم الرتبة, قوة الرتبة) أو (None, -inf) إذا لم يمتلك رتبة
    """
    highest_rank = None
    highest_order = -float('inf')

    # Ensure user_id_str is string for consistent lookup
    user_id_str = str(user_id_str)

    # Check all ranks and find the highest order for the user
    for rank, users in ranks.items():
        if user_id_str in users:
            order = rank_order.get(rank, -float('inf'))
            if order > highest_order:
                highest_order = order
                highest_rank = rank
    return highest_rank, highest_order

# التحقق من المطور الأساسي
def is_main_dev(user_id):
    return str(user_id) == main_dev

# التحقق من المطورين الثانويين
def is_secondary_dev(user_id):
    return str(user_id) in secondary_devs

# التحقق إذا كان المستخدم مطوراً (أساسي أو ثانوي)
def is_dev(user_id):
    return is_main_dev(user_id) or is_secondary_dev(user_id)

# Check if user is in prison (bot's internal system)
def is_in_prison(user_id_str):
    user_id_str = str(user_id_str)
    return user_id_str in banned_users and banned_users[user_id_str] > time.time()

# Global check for prison status - should be applied to most commands that alter state or perform actions
# Placed as the first handler (after essential system handlers like start)
# Note: This handler needs to be carefully ordered if using message.stop_propagation()
# It should run early to block commands, but allow commands like "سجني".
# Let's make it a simple check that replies but doesn't stop propagation for ALL messages.
# Instead, add the prison check *inside* individual command handlers where needed, OR use a decorator.
# Using a decorator is cleaner but adds complexity. Manual check is simpler for now.
# Remove the global prison_check_handler and add checks inside commands.

# @app.on_message(filters.group & filters.incoming)
# def prison_check_handler(client, message):
#     # Removed global prison check handler
#     pass


# 🤖 معالج تفاعل الذكاء الاصطناعي (تم حذفه بناءً على الطلب) 🤖
# @app.on_message(filters.text & filters.group & filters.incoming)
# def ai_interaction_handler(client, message):
#     # This function is removed as per user request
#     pass


# 👑 أوامر إدارة الرتب 👑

# رفع رتبة لمستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def promote_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    if len(text) < 3 or text[0] != "رفع":
        return

    rank_key_arg = text[1].lower()

    # البحث عن مفتاح الرتبة الداخلي من النص المُدخل (السماح بالاسم العربي أو المفتاح)
    target_rank_key = None
    for key, display in rank_display_names.items():
         if display.lower() == rank_key_arg or key == rank_key_arg:
              target_rank_key = key
              break

    if target_rank_key is None:
        return message.reply_text("❌ **الرتبة غير موجودة!**\nالرتب المتاحة: " + " - ".join(rank_display_names.values()), quote=True)

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent promoting a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك رفع رتبة لبوت آخر!**", quote=True)

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    target_user_id = str(user.id)
    target_highest_rank, target_order = get_user_highest_rank(target_user_id)
    target_rank_order_value = rank_order.get(target_rank_key, -float('inf'))

    # التحقق من أن الرافع أعلى من رتبة الهدف المراد منحها
    if sender_order < target_rank_order_value:
        return message.reply_text(f"❌ **لا يمكنك رفع شخص إلى رتبة ({rank_display_names.get(target_rank_key, target_rank_key)}) أعلى من رتبتك!**", quote=True)

     # التحقق من أن الرافع أعلى من رتبة الشخص المستهدف الحالية (لا يمكن رفع شخص مساوي أو أعلى منك)
    if target_order >= sender_order:
        return message.reply_text(f"❌ **لا يمكنك رفع شخص لديه رتبة ({rank_display_names.get(target_highest_rank, 'لا شيء')}) مساوية أو أعلى من رتبتك ({rank_display_names.get(sender_highest_rank, 'لا شيء')})!**", quote=True)


    # إضافة الرتبة الجديدة. إذا كان يمتلك رتب متعددة، يتم تخزينها.
    # Ensure the rank key exists in ranks dictionary before adding user
    if target_rank_key not in ranks:
        ranks[target_rank_key] = {}

    ranks[target_rank_key][target_user_id] = True
    save_data() # Save data after modification
    message.reply_text(f"✅ **تم رفع {user.mention} إلى {rank_display_names.get(target_rank_key, target_rank_key)} بنجاح!**", parse_mode="HTML", quote=True)


# تنزيل رتبة لمستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def demote_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    if len(text) < 3 or text[0] != "تنزيل":
        return

    rank_key_arg = text[1].lower()

    # البحث عن مفتاح الرتبة الداخلي من النص المُدخل
    target_rank_key = None
    for key, display in rank_display_names.items():
         if display.lower() == rank_key_arg or key == rank_key_arg:
              target_rank_key = key
              break

    if target_rank_key is None:
        return message.reply_text("❌ **الرتبة غير موجودة!**", quote=True)

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent demoting a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك تنزيل رتبة لبوت آخر!**", quote=True)

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    target_user_id = str(user.id)
    target_highest_rank, target_order = get_user_highest_rank(target_user_id)
    target_rank_order_value = rank_order.get(target_rank_key, -float('inf'))


    # التحقق من أن الرافع أعلى من الرتبة المراد تنزيلها
    if sender_order < target_rank_order_value:
        return message.reply_text(f"❌ **لا يمكنك تنزيل رتبة ({rank_display_names.get(target_rank_key, target_rank_key)}) أعلى من رتبتك!**", quote=True)

     # التحقق من أن الرافع أعلى من رتبة الشخص المستهدف الحالية (لا يمكن تنزيل شخص مساوي أو أعلى منك)
    if target_order >= sender_order:
        return message.reply_text(f"❌ **لا يمكنك تنزيل رتبة من شخص لديه رتبة ({rank_display_names.get(target_highest_rank, 'لا شيء')}) مساوية أو أعلى من رتبتك ({rank_display_names.get(sender_highest_rank, 'لا شيء')})!**", quote=True)


    # التحقق من أن المستخدم يمتلك هذه الرتبة
    if target_user_id not in ranks.get(target_rank_key, {}):
        return message.reply_text(f"❌ **المستخدم {user.mention} لا يمتلك هذه الرتبة ({rank_display_names.get(target_rank_key, target_rank_key)})!**", parse_mode="HTML", quote=True)

    # إزالة الرتبة
    del ranks[target_rank_key][target_user_id]
    save_data() # Save data after modification
    message.reply_text(f"✅ **تم تنزيل {user.mention} من {rank_display_names.get(target_rank_key, target_rank_key)}!**", parse_mode="HTML", quote=True)

# التحقق من رتبة المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def my_rank_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    if message.text.lower() != "رتبتي": # Use .lower() for case-insensitivity
        return

    user_id = str(message.from_user.id)
    # الحصول على جميع رتب المستخدم وعرضها بأسماء العرض
    user_ranks_display = [
        rank_display_names.get(rank, rank) for rank, users in ranks.items() if user_id in users
    ]

    # Also check Telegram status for creator/admin/owner
    chat_member_status = None
    try:
         chat_member = client.get_chat_member(message.chat.id, user_id)
         chat_member_status = chat_member.status
    except Exception:
         pass # User might not be a member anymore or bot lacks permission

    telegram_ranks = []
    # Note: ChatMemberStatus.CREATOR is often the same as OWNER in Pyrogram > 2.0
    # Let's check OWNER first, then ADMIN
    if chat_member_status == ChatMemberStatus.OWNER:
         telegram_ranks.append("👑 مالك القروب (تيليجرام)")
    elif chat_member_status == ChatMemberStatus.ADMINISTRATOR:
         telegram_ranks.append("🛡️ مشرف القروب (تيليجرام)")
    elif chat_member_status == ChatMemberStatus.CREATOR: # If CREATOR is distinct, add it
         if ChatMemberStatus.OWNER not in telegram_ranks: # Avoid duplication if OWNER and CREATOR are same
              telegram_ranks.append("🛠️ منشئ القروب (تيليجرام)")


    all_ranks_display = user_ranks_display + telegram_ranks

    if all_ranks_display:
        # Combine unique ranks and format for display
        unique_ranks = list(dict.fromkeys(all_ranks_display)) # Removes duplicates while preserving order
        message.reply_text(f"👑 **رتبتك:** `{', '.join(unique_ranks)}`", quote=True)
    else:
        message.reply_text("❌ **ما عندك أي رتبة في البوت أو في تيليجرام!**", quote=True)

# أمر "تنزيل الكل" - إزالة جميع الرتب الممنوحة يدوياً للمستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_all_ranks_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    if len(text) < 2 or text[0] != "تنزيل" or text[1].lower() != "الكل": # Use lower() for "الكل"
        return # Not "تنزيل الكل" command

    user_arg_index = 2 # Index for user argument if not reply

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent action on a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك إزالة رتب من بوت آخر!**", quote=True)

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    target_user_id = str(user.id)
    target_highest_rank, target_order = get_user_highest_rank(target_user_id)

    # التحقق من أن الرافع أعلى من المرفوع
    if target_user_id == main_dev: # Explicitly prevent removing ranks from main dev
         return message.reply_text("❌ **لا يمكنك إزالة رتب من المطور الأساسي!**", quote=True)
    if sender_order <= target_order:
         return message.reply_text("❌ **لا يمكنك إزالة رتب من شخص رتبته مساوية أو أعلى منك!**", quote=True)

    removed_ranks_count = 0
    # Iterate over a copy of keys to allow modification during iteration
    for rank_key in list(ranks.keys()):
        # Do not remove the_goat rank even if sender is higher (the_goat is permanent for main dev)
        if rank_key == "the_goat":
             continue
        if target_user_id in ranks[rank_key]:
            del ranks[rank_key][target_user_id]
            removed_ranks_count += 1

    save_data() # Save data after modification

    if removed_ranks_count > 0:
        message.reply_text(f"✅ **تم إزالة جميع الرتب الممنوحة يدوياً عن {user.mention}!**", parse_mode="HTML", quote=True)
    else:
        message.reply_text(f"ℹ️ **المستخدم {user.mention} لا يمتلك أي رتب ممنوحة يدوياً لإزالتها!**", parse_mode="HTML", quote=True)


# كشف معلومات المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def check_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower().split(maxsplit=1) # Split command and potential argument
    command = text[0]
    user_arg = text[1] if len(text) > 1 else None

    chat_id = str(message.chat.id)

    if command == "كشف":
        # Check if the 'كشف' command is locked in this group
        # Note: lock_unlock_commands affects group_settings
        if chat_id in group_settings and group_settings[chat_id].get("كشف", False):
            return message.reply_text("🚫 **أمر كشف مقفل في هذا القروب!**", quote=True)

        # Get target user
        # get_target_user needs the original message object
        user, error_message = get_target_user(client, message, allow_self=True) # Allow checking self

        if error_message:
             # If command was just "كشف" with no arg/reply, default to sender
             if len(message.text.split()) == 1 and message.text.lower() == "كشف":
                 user = message.from_user
                 error_message = None # Clear error as we default to sender
             else:
                 return message.reply_text(error_message, quote=True)

        # Allow checking the bot itself, but block other bots
        if user.is_bot and str(user.id) != str(client.me.id):
             return message.reply_text("❌ **لا يمكنك كشف معلومات بوت آخر غيري!**", quote=True)


        user_id = user.id
        username = f"@{user.username}" if user.username else "🚫 لا يوجد معرف"
        full_name = user.first_name + (" " + user.last_name if user.last_name else "")
        is_bot_text = "✅ نعم" if user.is_bot else "❌ لا"

        # Get user's ranks in the bot system
        user_ranks_display = [
            rank_display_names.get(rank, rank) for rank, users in ranks.items() if str(user_id) in users
        ]
        ranks_text = "، ".join(user_ranks_display) if user_ranks_display else "🚫 لا يوجد"

        # Get user's status in the chat (owner, admin, member, restricted, etc.)
        chat_status_text = "👤 **عضو عادي**"
        try:
             chat_member = client.get_chat_member(message.chat.id, user_id)
             if chat_member.status == ChatMemberStatus.OWNER:
                  chat_status_text = "👑 **مالك القروب**"
             elif chat_member.status == ChatMemberStatus.ADMINISTRATOR:
                  chat_status_text = "🛡️ **مشرف القروب**"
             elif chat_member.status == ChatMemberStatus.RESTRICTED:
                  chat_status_text = "🚷 **مقيد في القروب**"
             elif chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.KICKED]:
                  chat_status_text = "🚫 **محظور/مطرد من القروب**"
             elif chat_member.status == ChatMemberStatus.LEFT:
                  chat_status_text = "🚪 **غادر القروب**"
             # BOT status is covered by is_bot_text
        except Exception:
             # User might not be a member, or bot lacks permission to get status
             pass


        # Check if user is in bot's prison system
        prison_status = "✅ لا"
        if is_in_prison(str(user_id)):
             remaining_time = int(banned_users[str(user_id)] - time.time())
             minutes = remaining_time // 60
             seconds = remaining_time % 60
             prison_status = f"⏳ نعم (تبقى: {minutes}د {seconds}ث)"


        message.reply_text(f"""
👤 **معلومات المستخدم:**
━━━━━━━━━━━━━
👤 **الاسم:** {full_name}
🆔 **الآيدي:** `{user_id}`
🔗 **المعرف:** {username}
🤖 **بوت:** {is_bot_text}
🏅 **رتبته في البوت:** {ranks_text}
🗳️ **حالة في القروب:** {chat_status_text}
🚨 **مسجون في البوت:** {prison_status}
━━━━━━━━━━━━━
""", parse_mode="HTML", quote=True) # Quote the message


# 🔒 قفل وفتح الأوامر في القروب 🔒
@app.on_message(filters.text & filters.group & filters.incoming)
def lock_unlock_commands_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 2 or (text[0].lower() != "قفل" and text[0].lower() != "فتح"): # Use .lower()
        return # Not a lock/unlock command

    action = text[0].lower() # "قفل" or "فتح"
    command_or_feature = text[1].lower() # e.g., 'كشف', 'روابط', 'صور'

    # Check sender rank: only owner or main_owner can lock/unlock commands
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Allow admins to lock/unlock some specific protection features maybe?
    # User request was "هذا الأمر مخصص للمالكين فقط" -> rank_order.get("owner", 0)
    # Let's stick to owner/main_owner for locking COMMANDS. Protection features have a separate handler.
    if sender_order < rank_order.get("owner", 0): # 'owner' rank or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**", quote=True)

    # List of valid commands/features that can be locked/unlocked via this command
    # This should match the commands checked in the gatekeeper or command handlers
    valid_lockable_commands = [
        "كشف", "رتبتي", "القوانين", "الرابط", "توب المتفاعلين", # General info commands
        # Bank/Game Commands (as per help text)
        "انشاء حساب بنكي", "رصيدي", "راتبي", "بخشيش", "استثمار", "العجلة",
        "شراء", "بيع", "ممتلكاتي", "انضم شرطة", "انضم عصابة", "انضم رئيس عصابة",
        "ترجل", "سجن", "سجني", "سداد ديوني", "بلاغ", "ايديي", "ايدي", "اوامري"
        # Note: admin/moderation commands should generally NOT be lockable by lower ranks via this.
        # Protection features like 'روابط' 'صور' etc are locked via `lock_unlock_protection_cmd`.
        # Use first word of commands for lookup
    ]
    # Map multi-word commands to their first word for lookup if needed
    command_lookup = {}
    for cmd in valid_lockable_commands:
         parts = cmd.split()
         if parts:
              command_lookup[parts[0].lower()] = cmd # Store full command with first word as key

    # Also add the full command strings directly as keys for exact match
    for cmd in valid_lockable_commands:
        command_lookup[cmd.lower()] = cmd


    # Check if the input matches a command prefix or a full command
    command_or_feature_key = None
    if command_or_feature in command_lookup:
         command_or_feature_key = command_lookup[command_or_feature] # Use the full command as the key
    # Add specific check for two-word commands if the input matches the first word
    elif len(text) > 2:
         two_word_prefix = text[1].lower() + " " + text[2].lower()
         if two_word_prefix in command_lookup:
              command_or_feature_key = command_lookup[two_word_prefix]


    if command_or_feature_key is None:
         return message.reply_text(f"❌ **الأمر/الميزة '{text[1]}' غير قابل للقفل/الفتح بهذا الأمر.**\nالأوامر المتاحة للقفل/الفتح: " + " - ".join(valid_lockable_commands), quote=True)


    if chat_id not in group_settings:
        group_settings[chat_id] = {}

    if action == "قفل":
        group_settings[chat_id][command_or_feature_key] = True
        save_data() # Save data
        message.reply_text(f"🔒 **تم قفل أمر '{command_or_feature_key}' بنجاح!**", quote=True)
    elif action == "فتح":
        # Ensure the key exists before trying to delete or set to False
        if command_or_feature_key in group_settings[chat_id]:
             group_settings[chat_id][command_or_feature_key] = False # Use False instead of deleting key
             # del group_settings[chat_id][command_or_feature] # Alternative: remove key entirely
             save_data() # Save data
             message.reply_text(f"🔓 **تم فتح أمر '{command_or_feature_key}' بنجاح!**", quote=True)
        else:
             message.reply_text(f"ℹ️ **أمر '{command_or_feature_key}' ليس مقفلاً بالفعل.**", quote=True)

# Check if a command is locked for this group (used in individual command handlers)
def is_command_locked(chat_id_str, command_name):
     # Handle multi-word commands correctly by checking the full command string as the key
     # Also check the first word as a potential key if the command is multi-word
     command_name_lower = command_name.lower()
     first_word = command_name_lower.split(maxsplit=1)[0]

     if chat_id_str not in group_settings:
          return False

     # Check for the full command string as the key
     if group_settings[chat_id_str].get(command_name_lower, False):
          return True

     # If the command is multi-word, also check if its first word is locked (less precise, could be confusing)
     # Let's stick to locking the full command string key for clarity.
     # The lock command itself uses the full command key.
     return False


# 🚫 أوامر الإدارة (حظر، كتم، تقييد، إلخ) 🚫

# أمر حظر المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def ban_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("حظر"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for ban
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    # Try to get user object from reply or argument, allow targeting bots (but Telegram will block banning bot accounts)
    user, error_message = get_target_user(client, message, allow_self=False) # Disallow banning self

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Explicitly prevent mod actions on bots
    if user.is_bot:
         return message.reply_text("❌ **لا يمكنك حظر بوت!**", quote=True)

    target_user_id = str(user.id)
    target_highest_rank, target_order = get_user_highest_rank(target_user_id)

    # Prevent moderating users with equal or higher rank in the bot's system
    if target_order >= sender_order:
         return message.reply_text(f"❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**", quote=True)

    try:
        # Attempt to ban via Telegram API
        client.ban_chat_member(message.chat.id, user.id)
        message.reply_text(f"🚫 **تم حظر {user.mention} من القروب!**", parse_mode="HTML", quote=True)
    except Exception as e:
         # Catch exceptions like insufficient bot permissions or targeting chat owner/admin
         message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية حظر في هذا القروب أو أن المستخدم الذي تحاول حظره أعلى من البوت رتبة في تليجرام.\nالتفاصيل: {e}", quote=True)

# أمر إلغاء الحظر
@app.on_message(filters.text & filters.group & filters.incoming)
def unban_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("الغاء الحظر"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for unban
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

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
        return message.reply_text("❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**", quote=True)

    # Try to get user object for mention, but proceed with ID if fetch fails
    target_user_id = None
    mention_text = f"المستخدم ذو الآيدي `{user_id_arg}`" # Fallback mention

    try:
        if user_id_arg.startswith('@'):
            user_obj = client.get_users(user_id_arg)
            target_user_id = user_obj.id
            mention_text = user_obj.mention
        elif user_id_arg.isdigit():
            target_user_id = int(user_id_arg)
            try:
                 user_obj = client.get_users(target_user_id)
                 mention_text = user_obj.mention
            except Exception:
                 pass # User object fetch failed, use ID in mention
        else:
             return message.reply_text("❌ **الرجاء إدخال معرف مستخدم (@username) أو آيدي مستخدم صحيح بعد الأمر!**", quote=True)


    except ValueError:
        return message.reply_text("❌ **الرجاء إدخال معرف مستخدم (@username) أو آيدي مستخدم صحيح بعد الأمر!**", quote=True)
    except Exception:
         # get_users might fail if user doesn't exist or bot can't see them, but ID might still be valid for unban
         if user_id_arg.isdigit():
              target_user_id = int(user_id_arg)
         else:
              return message.reply_text("❌ **حدث خطأ في التعرف على المستخدم، تأكد من المعرف أو الآيدي.**", quote=True)


    if target_user_id is None:
         return message.reply_text("❌ **الرجاء إدخال معرف مستخدم (@username) أو آيدي مستخدم صحيح بعد الأمر!**", quote=True)

    # Optional: Check sender rank vs target rank if target is in ranks (less critical for unban)
    # target_highest_rank, target_order = get_user_highest_rank(str(target_user_id))
    # if target_order > sender_order: # Allow unbanning equal/lower ranks only?
    #     return message.reply_text("❌ **لا يمكنك إلغاء حظر شخص لديه رتبة أعلى منك!**")

    try:
        client.unban_chat_member(message.chat.id, target_user_id)
        message.reply_text(f"✅ **تم إلغاء حظر {mention_text} بنجاح!**", parse_mode="HTML", quote=True)
    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما المستخدم ليس محظوراً أصلاً أو أن البوت لا يملك صلاحية إلغاء الحظر.\nالتفاصيل: {e}", quote=True)


# أمر طرد المستخدم (يتم بالحظر ثم فك الحظر فوراً)
@app.on_message(filters.text & filters.group & filters.incoming)
def kick_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("طرد"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for kick
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent action on a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك طرد بوت آخر!**", quote=True)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank
    if target_order >= sender_order:
         return message.reply_text(f"❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**", quote=True)

    try:
        client.ban_chat_member(message.chat.id, user.id)
        # Add a small delay before unbanning to ensure kick takes effect
        time.sleep(1)
        client.unban_chat_member(message.chat.id, user.id)
        message.reply_text(f"👢 **تم طرد {user.mention} من القروب!**", parse_mode="HTML", quote=True)
    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية طرد في هذا القروب أو أن المستخدم الذي تحاول طرده أعلى من البوت رتبة في تليجرام.\nالتفاصيل: {e}", quote=True)


# أمر كتم المستخدم
@app.on_message(filters.text & filters.group & filters.incoming)
def mute_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("كتم"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for mute
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent action on a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك كتم بوت آخر!**", quote=True)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank
    if target_order >= sender_order:
         return message.reply_text(f"❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**", quote=True)

    try:
        # Set can_send_messages to False
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
        message.reply_text(f"🔇 **تم كتم {user.mention} في القروب!**", parse_mode="HTML", quote=True)
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية كتم في هذا القروب أو أن المستخدم الذي تحاول كتمه أعلى من البوت رتبة في تليجرام.\nالتفاصيل: {e}", quote=True)

# أمر إلغاء الكتم
@app.on_message(filters.text & filters.group & filters.incoming)
def unmute_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("الغاء الكتم"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for unmute
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)


    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent action on a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك إلغاء كتم بوت آخر!**", quote=True)

    # Optional: Check sender rank vs target rank (less critical for unmute)
    # target_highest_rank, target_order = get_user_highest_rank(str(user.id))
    # if target_order > sender_order: # Allow unmute equal/lower ranks only?
    #      return message.reply_text("❌ **لا يمكنك إلغاء كتم شخص لديه رتبة أعلى منك!**", quote=True)

    try:
        # Setting can_send_messages=True is usually enough to "unmute"
        # Set all common permissions back
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            # Keep others False by default for normal members
            can_change_info=False,
            can_invite_users=True, # Usually members can invite unless restricted
            can_pin_messages=False
        ))
        message.reply_text(f"🔊 **تم إلغاء كتم {user.mention}!**", parse_mode="HTML", quote=True)
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما المستخدم ليس مكتوماً أصلاً أو أن البوت لا يملك صلاحية إلغاء الكتم.\nالتفاصيل: {e}", quote=True)

# أمر تقييد المستخدم (منع كل شيء تقريباً)
@app.on_message(filters.text & filters.group & filters.incoming)
def restrict_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("تقييد"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for restrict
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent action on a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك تقييد بوت آخر!**", quote=True)

    target_highest_rank, target_order = get_user_highest_rank(str(user.id))

    # Prevent moderating users with equal or higher rank
    if target_order >= sender_order:
         return message.reply_text(f"❌ **لا يمكنك تنفيذ هذا الأمر على شخص لديه رتبة مساوية أو أعلى منك في البوت!**", quote=True)

    try:
        # Restrict almost all permissions by providing an empty ChatPermissions object
        # A non-empty object with permissions set to False is more explicit
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_send_polls=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_topics=False, # New in topic-enabled groups
            can_send_audios=False,
            can_send_documents=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_video_notes=False,
            can_send_voices=False,
            can_send_stickers=False,
            can_send_animations=False, # GIFs
            can_use_inline_bots=False # Prevent inline bots if desired
        ))
        message.reply_text(f"🚷 **تم تقييد {user.mention} في القروب!**", parse_mode="HTML", quote=True)
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية تقييد في هذا القروب أو أن المستخدم الذي تحاول تقييده أعلى من البوت رتبة في تليجرام.\nالتفاصيل: {e}", quote=True)

# أمر فك التقييد (إعادة الصلاحيات الأساسية)
@app.on_message(filters.text & filters.group & filters.incoming)
def unrestrict_user_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("فك التقييد"):
        return

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

    # Check if sender has admin rank or higher for unrestrict
    if sender_order < rank_order.get("admin", 0):
         return message.reply_text("❌ **ليس لديك الصلاحية لاستخدام هذا الأمر! هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    user, error_message = get_target_user(client, message, allow_self=False)

    if error_message:
         return message.reply_text(error_message, quote=True)

    # Prevent action on a bot
    if user.is_bot:
        return message.reply_text("❌ **لا يمكنك فك تقييد بوت آخر!**", quote=True)

    # Optional: Check sender rank vs target rank (less critical for unrestrict)
    # target_highest_rank, target_order = get_user_highest_rank(str(user.id))
    # if target_order > sender_order:
    #      return message.reply_text("❌ **لا يمكنك فك تقييد شخص لديه رتبة أعلى منك!**", quote=True)

    try:
        # Grant basic permissions back (allow sending messages and media)
        client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            # Keep others False by default for normal members
            can_change_info=False, # Normal members shouldn't change group info
            can_invite_users=True, # Normal members can invite
            can_pin_messages=False, # Normal members shouldn't pin
            can_manage_topics=False, # Normal members shouldn't manage topics
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voices=True,
            can_send_stickers=True,
            can_send_animations=True, # GIFs
            can_use_inline_bots=True # Allow inline bots
        ))
        message.reply_text(f"✅ **تم فك التقييد عن {user.mention}!**", parse_mode="HTML", quote=True)
    except Exception as e:
        message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما المستخدم ليس مقيداً أصلاً أو أن البوت لا يملك صلاحية فك التقييد.\nالتفاصيل: {e}", quote=True)

# أمر رفع جميع القيود عن المستخدم (نفس فك التقييد تقريباً)
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_restrictions_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if not text.startswith("رفع القيود"):
        return

    # This command is an alias for "فك التقييد". Map it to the same logic.
    # Re-use the unrestrict_user_cmd logic by pretending the command was "فك التقييد"
    message.text = "فك التقييد" + message.text[len("رفع القيود"):] # Change text to match unrestrict command
    unrestrict_user_cmd(client, message)


# طرد جميع البوتات من القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_bots_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if text == "طرد البوتات":
        sender_id = str(message.from_user.id)
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

        # Check if sender has admin rank or higher
        if sender_order < rank_order.get("admin", 0):
             return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

        try:
            banned_count = 0
            # get_chat_members with filter=ChatMembersFilter.BOTS requires Pyrogram v2.0+ and bot to be admin with 'Manage Group' rights.
            # This is more efficient than iterating all members.
            # Assuming Pyrogram v2.0+ and necessary permissions:
            # get_chat_members is a generator, need to iterate
            bots_to_ban = list(client.get_chat_members(message.chat.id, filter="bots")) # Get all bots once

            for member in bots_to_ban:
                if member.user.id != client.me.id: # Don't ban self
                    try:
                        client.ban_chat_member(message.chat.id, member.user.id)
                        banned_count += 1
                        # Optional: Add a small delay to avoid hitting API limits quickly
                        time.sleep(0.2) # Reduced delay slightly
                    except Exception as e:
                        print(f"Failed to ban bot {member.user.id}: {e}") # Log failure

            if banned_count > 0:
                message.reply_text(f"✅ **تم طرد {banned_count} بوت من القروب!**", quote=True)
            else:
                message.reply_text("ℹ️ **لم يتم العثور على بوتات أخرى في القروب لطردها.**", quote=True)

        except Exception as e:
            # This might happen if the bot isn't admin or lacks permissions (get_chat_members call itself might fail)
            message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية جلب قائمة البوتات أو طردها.\nالتفاصيل: {e}", quote=True)


# طرد جميع الحسابات المحذوفة (Deleted Accounts)
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_deleted_accounts_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if text == "طرد المحذوفين":
        sender_id = str(message.from_user.id)
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)

        # Check if sender has admin rank or higher
        if sender_order < rank_order.get("admin", 0):
             return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

        try:
            banned_count = 0
            # get_chat_members might require admin rights
            # Iterating through all members can be slow in huge groups
            # Consider using a limit or different approach for very large groups
            all_members = client.get_chat_members(message.chat.id) # Get all members (generator)
            deleted_accounts_to_ban = [member.user for member in all_members if member.user.is_deleted] # Filter in memory

            for user in deleted_accounts_to_ban:
                 try:
                      client.ban_chat_member(message.chat.id, user.id)
                      banned_count += 1
                      # Optional: Add a small delay
                      time.sleep(0.2) # Reduced delay slightly
                 except Exception as e:
                      print(f"Failed to ban deleted account {user.id}: {e}") # Log failure

            if banned_count > 0:
                message.reply_text(f"✅ **تم طرد {banned_count} حساب محذوف من القروب!**", quote=True)
            else:
                 message.reply_text("ℹ️ **لم يتم العثور على حسابات محذوفة في القروب لطردها.**", quote=True)

        except Exception as e:
            message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية جلب الأعضاء أو طردها.\nالتفاصيل: {e}", quote=True)


# كشف جميع البوتات في القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def check_bots_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    if text == "كشف البوتات":
        try:
            # get_chat_members with filter="bots" is more efficient
            # Requires bot to be admin with 'Manage Group' rights
            chat_members = client.get_chat_members(message.chat.id, filter="bots")
            bots = [member.user.mention for member in chat_members if member.user.id != client.me.id] # Exclude self

            if bots:
                bots_list_text = "\n".join(bots)
                # Split into multiple messages if list is too long (Telegram message limit)
                if len(bots_list_text) > 4000: # Check total length
                     chunk_size = 1500 # Approximate chunk size
                     chunks = [bots_list_text[i:i+chunk_size] for i in range(0, len(bots_list_text), chunk_size)]
                     message.reply_text("🤖 **البوتات الموجودة في القروب (الجزء 1):**\n" + chunks[0], parse_mode="HTML", quote=True)
                     for i, chunk in enumerate(chunks[1:], start=2):
                          # Find a natural split point (like newline) if possible within chunk
                          message.reply_text(f"🤖 **البوتات الموجودة في القروب (الجزء {i}):**\n" + chunk, parse_mode="HTML", quote=True)
                else:
                     message.reply_text(f"🤖 **البوتات الموجودة في القروب:**\n" + bots_list_text, parse_mode="HTML", quote=True)

            else:
                message.reply_text("✅ **لا يوجد بوتات أخرى في القروب!**", quote=True)
        except Exception as e:
             # This might happen if the bot isn't admin or lacks permissions
            message.reply_text(f"❌ **حدث خطأ أثناء تنفيذ الأمر:** ربما البوت ليس لديه صلاحية جلب قائمة البوتات.\nالتفاصيل: {e}", quote=True)

# 🛡️ نظام الحماية من السبام، الروابط، الميديا، إلخ 🛡️

# أوامر قفل وفتح الحماية (للروابط، التكرار، إلخ)
@app.on_message(filters.text & filters.group & filters.incoming)
def lock_unlock_protection_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 2 or (text[0].lower() != "قفل" and text[0].lower() != "فتح"): # Use .lower()
        return # Not a protection lock/unlock command

    action = text[0].lower() # "قفل" or "فتح"
    feature = text[1].lower() # e.g., 'روابط', 'تكرار', 'صور'

    # Check sender rank: admin or higher can lock/unlock protection features
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    # List of valid features to prevent locking arbitrary strings
    valid_features = [
        "الروابط", "تكرار", "التوجيه", "الصور", "الفيديو", "الملصقات",
        "المعرفات", "التاك", "البوتات", "الكلمات", "الملفات", "الصوت",
        "الملاحظات الصوتية", "الملاحظات المرئية", "الجهات", "المواقع",
        "الألعاب", "الاستطلاعات", "اباحيات" # Added pornography
    ]

    if feature not in valid_features:
         return message.reply_text(f"❌ **ميزة الحماية '{feature}' غير موجودة.**\nالميزات المتاحة: " + " - ".join(valid_features), quote=True)


    if chat_id not in protection_settings:
        protection_settings[chat_id] = {}

    if action == "قفل":
        protection_settings[chat_id][feature] = True
        save_data() # Save data
        message.reply_text(f"🔒 **تم قفل {feature} بنجاح!**", quote=True)
    elif action == "فتح":
        if feature in protection_settings[chat_id]:
            protection_settings[chat_id][feature] = False # Use False instead of deleting
            # del protection_settings[chat_id][feature] # Alternative: remove key
            save_data() # Save data
            message.reply_text(f"🔓 **تم فتح {feature} بنجاح!**", quote=True)
        else:
             message.reply_text(f"ℹ️ **ميزة الحماية '{feature}' ليست مقفلة بالفعل.**", quote=True)


# منع الروابط
@app.on_message(filters.text & filters.group & filters.incoming)
def block_links_handler(client, message):
    # No prison check needed for automatic message deletion handlers
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id) # Use user_id for checking rank
    text_to_check = message.text or message.caption # Check text or caption

    if not text_to_check: return # Nothing to check

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id in protection_settings and protection_settings[chat_id].get("الروابط", False):
        # Basic link detection using regex for better accuracy
        link_pattern = re.compile(r'(https?://\S+|t\.me/\S+|telegram\.me/\S+|www\.\S+\.\S+|[^@\s]+\.[a-z]{2,})', re.IGNORECASE) # Added common TLDs

        if link_pattern.search(text_to_check):
            try:
                client.delete_messages(chat_id, message.message_id)
                # Optional: Reply with a warning (can be spammy)
                # client.send_message(chat_id, "🚫 **ممنوع إرسال الروابط في هذا القروب!**", reply_to_message_id=message.message_id)
            except Exception:
                pass # Bot may not have permission to delete


# منع التكرار (السبام)
@app.on_message(filters.text & filters.group & filters.incoming)
def anti_flood_handler(client, message):
    # No prison check needed for automatic message deletion handlers
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id in protection_settings and protection_settings[chat_id].get("تكرار", False):
        current_time = time.time()
        flood_limit = 7 # Increased slightly
        flood_timeframe = 6 # Increased slightly

        # Ensure chat_id and user_id exist in history
        if chat_id not in user_messages_history:
            user_messages_history[chat_id] = {}
        if user_id not in user_messages_history[chat_id]:
            user_messages_history[chat_id][user_id] = []

        # Add current message timestamp and remove old ones (older than timeframe)
        user_messages_history[chat_id][user_id].append(current_time)
        user_messages_history[chat_id][user_id] = [
            ts for ts in user_messages_history[chat_id][user_id] if current_time - ts < flood_timeframe
        ]

        # Check if user exceeded the limit
        if len(user_messages_history[chat_id][user_id]) > flood_limit:
            try:
                client.delete_messages(chat_id, message.message_id)
                # Optional: Reply with a warning once per user per time window
                # Requires tracking warnings {chat_id: {user_id: last_warning_time}}
                # For simplicity, skipping warning message to avoid spam
            except Exception:
                pass # Bot may not have permission


# منع التوجيه (Forwarded messages)
@app.on_message(filters.forwarded & filters.group & filters.incoming)
def block_forwarded_handler(client, message):
    # No prison check needed for automatic message deletion handlers
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Do not apply protection to admins or higher
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    if sender_order >= rank_order.get("admin", 0):
         return # Admins/Owners are exempt

    if chat_id in protection_settings and protection_settings[chat_id].get("التوجيه", False):
        try:
            client.delete_messages(chat_id, message.message_id)
            # client.send_message(chat_id, "🚫 **ممنوع إرسال الرسائل الموجهة في هذا القروب!**", reply_to_message_id=message.message_id)
        except Exception:
            pass # Bot may not have permission


# منع الصور والفيديوهات والملصقات والملفات والرسائل الصوتية والفيديو الملاحظات وغيرها
@app.on_message(filters.media & filters.group & filters.incoming) # Use filters.media for various media types
def block_media_handler(client, message):
    # No prison check needed for automatic message deletion handlers
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

    # Check for specific media types based on protection settings
    if protection_settings[chat_id].get("الصور", False) and message.photo:
        should_delete = True
        reason = "الصور"
    elif protection_settings[chat_id].get("الفيديو", False) and message.video:
        should_delete = True
        reason = "الفيديو"
    elif protection_settings[chat_id].get("الملصقات", False) and message.sticker:
        should_delete = True
        reason = "الملصقات"
    elif protection_settings[chat_id].get("الملفات", False) and message.document:
        should_delete = True
        reason = "الملفات"
    elif protection_settings[chat_id].get("الصوت", False) and message.audio:
        should_delete = True
        reason = "الصوت"
    elif protection_settings[chat_id].get("الملاحظات الصوتية", False) and message.voice:
        should_delete = True
        reason = "الملاحظات الصوتية"
    elif protection_settings[chat_id].get("الملاحظات المرئية", False) and message.video_note:
        should_delete = True
        reason = "الملاحظات المرئية"
    elif protection_settings[chat_id].get("الجهات", False) and message.contact:
        should_delete = True
        reason = "الجهات"
    elif protection_settings[chat_id].get("المواقع", False) and message.location:
        should_delete = True
        reason = "المواقع"
    elif protection_settings[chat_id].get("الألعاب", False) and message.game:
        should_delete = True
        reason = "الألعاب"
    elif protection_settings[chat_id].get("الاستطلاعات", False) and message.poll:
        should_delete = True
        reason = "الاستطلاعات"


    if should_delete:
        try:
            client.delete_messages(chat_id, message.message_id)
            # client.send_message(chat_id, f"🚫 **ممنوع إرسال {reason} في هذا القروب!**", reply_to_message_id=message.message_id)
        except Exception:
            pass # Bot may not have permission


# منع المعرفات والتاك والكلمات الممنوعة والاباحيات
@app.on_message(filters.text & filters.group & filters.incoming)
def block_text_content_handler(client, message):
    # No prison check needed for automatic message deletion handlers
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

    # Prevent mentions like @username, @channel, but not commands starting with / or @
    # Improve regex for mentions to be more accurate and avoid emails etc.
    mention_pattern = re.compile(r'(?<!\S)@\w+', re.IGNORECASE)
    # Also exclude mentions that are part of a command "/command @user" or "@botname command"
    # This handler runs AFTER the prison check, but BEFORE other text handlers like auto-reply/custom commands.
    # We need to check if the *first word* is a command before blocking mentions in the message.
    first_word = text.split(maxsplit=1)[0]
    is_command_like = first_word.startswith('/') or first_word.lower() in [
        "رفع", "تنزيل", "كشف", "حظر", "الغاء", "طرد", "كتم", "تقييد", "فك", "مسح",
        "اضف", "حذف", "ضع", "ربط", "انشاء", "شراء", "بيع", "انضم", "ترجل", "سجن",
        "سداد", "بلاغ", "ايدي" # Include relevant command starters
    ]

    if protection_settings[chat_id].get("المعرفات", False) and mention_pattern.search(text) and not is_command_like:
         should_delete = True
         reason = "المعرفات"

    # Prevent hashtags
    hashtag_pattern = re.compile(r'(?<!\S)#\w+', re.IGNORECASE)
    if not should_delete and protection_settings[chat_id].get("التاك", False) and hashtag_pattern.search(text):
        should_delete = True
        reason = "التاك"

    # Prevent mentions of bots (assuming mentions start with @)
    if not should_delete and protection_settings[chat_id].get("البوتات", False) and "@" in text and not is_command_like:
         # Check if any mentioned user is a bot
         mentions = [word.lstrip('@') for word in text.split() if word.startswith('@') and len(word) > 1]
         if mentions:
              try:
                   # Attempt to get user object for each mention
                   # Use get_chat for robustness with public channels/groups too
                   for mention in mentions:
                        try:
                             entity = client.get_chat(mention)
                             if entity.type == "bot":
                                  should_delete = True
                                  reason = "منشن البوتات"
                                  break # Found a bot mention, delete and stop
                        except Exception:
                             pass # Ignore if user/chat not found

              except Exception:
                   pass # Ignore general errors

    # Prevent banned words (requires 'الكلمات' protection feature and a list of banned words)
    if not should_delete and protection_settings[chat_id].get("الكلمات", False):
        banned_words = protection_settings[chat_id].get("banned_words", []) # Get banned words for this group
        # Check if any banned word is in the message (case-insensitive, match whole words or phrases)
        text_lower = text.lower()
        if any(re.search(r'\b' + re.escape(word.lower()) + r'\b', text_lower) for word in banned_words if word): # Use regex for whole words
            should_delete = True
            reason = "الكلمات الممنوعة"

    # Prevent pornography keywords
    if not should_delete and protection_settings[chat_id].get("اباحيات", False):
        # Use the global pornography_keywords list
        text_lower = text.lower()
        # Check for keyword presence (can match parts of words, refine with regex if needed)
        if any(keyword.lower() in text_lower for keyword in pornography_keywords if keyword): # Ensure keyword is not empty
            should_delete = True
            reason = "الإباحيات"

    if should_delete:
        try:
            client.delete_messages(chat_id, message.message_id)
            # Optional: Reply with a warning (can be spammy)
            # client.send_message(chat_id, f"🚫 **ممنوع إرسال {reason} في هذا القروب!**", reply_to_message_id=message.message_id, quote=True)
        except Exception:
            pass # Bot may not have permission


# أمر إضافة كلمة لقائمة المنع (for "الكلمات" protection)
@app.on_message(filters.text & filters.group & filters.incoming)
def add_banned_word_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    # Use shlex.split for better handling of quotes and spaces in phrases if needed
    # For simplicity, stick to split(maxsplit=2) for now
    text = message.text.split(maxsplit=2) # Split "اضف كلمة", then the rest
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "اضف" or text[1].lower() != "كلمة": # Use .lower()
        return # Not "اضف كلمة" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    word_to_ban = text[2].strip() # Keep original case if needed, or enforce lower
    if not word_to_ban:
         return message.reply_text("❌ **الرجاء تحديد الكلمة/العبارة المراد منعها بعد الأمر.**", quote=True)

    # Store words in lowercase for case-insensitive matching later
    word_to_ban_lower = word_to_ban.lower()

    if chat_id not in protection_settings:
        protection_settings[chat_id] = {}
    if "banned_words" not in protection_settings[chat_id]:
        protection_settings[chat_id]["banned_words"] = []

    # Check for duplicates in lowercase
    if word_to_ban_lower in [w.lower() for w in protection_settings[chat_id]["banned_words"]]:
         return message.reply_text(f"ℹ️ **الكلمة/العبارة '{word_to_ban}' موجودة بالفعل في قائمة المنع.**", quote=True)

    # Store the word/phrase as entered by the user (or lowercase, decide consistently)
    # Storing lowercase is simpler for matching
    protection_settings[chat_id]["banned_words"].append(word_to_ban_lower)
    save_data() # Save data
    message.reply_text(f"✅ **تم إضافة الكلمة/العبارة '{word_to_ban}' إلى قائمة المنع!**", quote=True)

# أمر حذف كلمة من قائمة المنع
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_banned_word_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split(maxsplit=2) # Split "حذف كلمة", then the rest
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "حذف" or text[1].lower() != "كلمة": # Use .lower()
        return # Not "حذف كلمة" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    word_to_unban = text[2].strip() # Keep original case
    if not word_to_unban:
         return message.reply_text("❌ **الرجاء تحديد الكلمة/العبارة المراد حذفها من قائمة المنع بعد الأمر.**", quote=True)

    # Match case-insensitively for removal
    word_to_unban_lower = word_to_unban.lower()

    if chat_id not in protection_settings or "banned_words" not in protection_settings[chat_id]:
        return message.reply_text("ℹ️ **لا توجد قائمة كلمات ممنوعة لهذا القروب.**", quote=True)

    banned_words_list = protection_settings[chat_id]["banned_words"]
    found_index = -1
    for i, word in enumerate(banned_words_list):
         if word.lower() == word_to_unban_lower:
              found_index = i
              break

    if found_index != -1:
        del banned_words_list[found_index]
        save_data() # Save data
        message.reply_text(f"✅ **تم حذف الكلمة/العبارة '{word_to_unban}' من قائمة المنع!**", quote=True)
    else:
        message.reply_text(f"ℹ️ **الكلمة/العبارة '{word_to_unban}' غير موجودة في قائمة المنع.**", quote=True)


# أمر عرض قائمة الكلمات الممنوعة
@app.on_message(filters.text & filters.group & filters.incoming)
def show_banned_words_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "قائمة المنع":
        if chat_id in protection_settings and "banned_words" in protection_settings[chat_id]:
            banned_words = protection_settings[chat_id]["banned_words"]
            if banned_words:
                words_list = "\n".join([f"• `{word}`" for word in banned_words])
                # Split message if too long
                if len(words_list) > 4000: # Approx limit
                     chunk_size = 1500
                     chunks = [words_list[i:i+chunk_size] for i in range(0, len(words_list), chunk_size)]
                     message.reply_text(f"🚫 **قائمة الكلمات الممنوعة في القروب (الجزء 1):**\n{chunks[0]}", parse_mode="Markdown", quote=True)
                     for i, chunk in enumerate(chunks[1:], start=2):
                         message.reply_text(f"🚫 **قائمة الكلمات الممنوعة في القروب (الجزء {i}):**\n{chunk}", parse_mode="Markdown", quote=True)
                else:
                    message.reply_text(f"🚫 **قائمة الكلمات الممنوعة في القروب:**\n{words_list}", parse_mode="Markdown", quote=True)
            else:
                message.reply_text("✅ **قائمة الكلمات الممنوعة فارغة.**", quote=True)
        else:
             message.reply_text("ℹ️ **لا توجد قائمة كلمات ممنوعة لهذا القروب.**", quote=True)


# 📜 أوامر إعدادات القروب (القوانين، الرابط، إلخ) 📜

# عرض القوانين
@app.on_message(filters.text & filters.group & filters.incoming)
def show_rules_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "القوانين":
        # Use group_settings dictionary
        rules = group_settings.get(chat_id, {}).get("rules", "🚫 لا توجد قوانين محددة لهذا القروب.")
        message.reply_text(f"📜 **قوانين القروب:**\n{rules}", quote=True)

# تعديل القوانين
@app.on_message(filters.text & filters.group & filters.incoming)
def set_rules_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    # Use regex to find the text after "ضع قوانين" allowing for spaces
    import re
    match = re.match(r"ضع قوانين\s*(.+)", text.lower())

    if match:
        # Check sender rank: owner or main_owner needed
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
        if sender_order < rank_order.get("owner", 0):
            return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**", quote=True)

        new_rules = match.group(1).strip()

        if not new_rules:
            # If no text after command, maybe they want to clear rules? Or ask for text?
            # Let's ask for text for now.
            return message.reply_text("❌ **الرجاء تحديد القوانين بعد الأمر.**", quote=True)

        if chat_id not in group_settings:
            group_settings[chat_id] = {}

        group_settings[chat_id]["rules"] = new_rules
        save_data() # Save data
        message.reply_text(f"✅ **تم تحديث قوانين القروب!**", quote=True)

# عرض رابط القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def show_link_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "الرابط":
        # Use group_settings dictionary
        group_link = group_settings.get(chat_id, {}).get("link", "🚫 لا يوجد رابط مسجل.")
        message.reply_text(f"🔗 **رابط القروب:**\n{group_link}", quote=True, disable_web_page_preview=True) # Disable preview by default

# تعديل رابط القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def set_link_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    # Use regex to find the link after "اضف رابط =" allowing for variations in spacing
    import re
    match = re.match(r"اضف رابط\s*=\s*(.+)", text.lower())

    if match:
        # Check sender rank: owner or main_owner needed
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
        if sender_order < rank_order.get("owner", 0):
            return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**", quote=True)

        new_link = match.group(1).strip()

        if not new_link:
            return message.reply_text("❌ **الرجاء تحديد الرابط بعد علامة '='.**", quote=True)

        # Basic validation that it looks like a link (optional)
        if not (new_link.startswith("http://") or new_link.startswith("https://") or new_link.startswith("t.me/") or new_link.startswith("telegram.me/")):
             return message.reply_text("❌ **الرابط المدخل لا يبدو صحيحاً.**", quote=True)


        if chat_id not in group_settings:
            group_settings[chat_id] = {}

        group_settings[chat_id]["link"] = new_link
        save_data() # Save data
        message.reply_text(f"✅ **تم تحديث رابط القروب!**", quote=True, disable_web_page_preview=True) # Disable preview for cleaner link

    # Handle "اضف رابط" without "=" (e.g. if user just pastes a link after)
    elif text.lower().startswith("اضف رابط"):
         parts = text.split(maxsplit=1)
         if len(parts) > 1 and parts[1].strip():
              link_candidate = parts[1].strip()
              # Check sender rank
              sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
              if sender_order < rank_order.get("owner", 0):
                  return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**", quote=True)

              # Basic validation
              if not (link_candidate.startswith("http://") or link_candidate.startswith("https://") or link_candidate.startswith("t.me/") or link_candidate.startswith("telegram.me/")):
                   return message.reply_text("❌ **الرابط المدخل لا يبدو صحيحاً.**", quote=True)

              if chat_id not in group_settings:
                  group_settings[chat_id] = {}

              group_settings[chat_id]["link"] = link_candidate
              save_data() # Save data
              message.reply_text(f"✅ **تم تحديث رابط القروب!**", quote=True, disable_web_page_preview=True) # Disable preview for cleaner link
         else:
              # If just "اضف رابط" or "اضف رابط "
               return message.reply_text("❌ **الرجاء تحديد الرابط بعد الأمر.**", quote=True)


# عرض قائمة المالكين والإداريين والمميزين (حسب الرتب المحددة في الكود)
@app.on_message(filters.text & filters.group & filters.incoming)
def show_ranks_list_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

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

    all_members_ids = set() # Use a set to store unique user IDs
    display_names_shown = [] # To show which ranks were included

    for rank_key in rank_keys_to_show:
        # Ensure the rank_key exists in the actual ranks data
        if rank_key in ranks:
            all_members_ids.update(ranks[rank_key].keys()) # Add user IDs from this rank
            display_names_shown.append(rank_display_names.get(rank_key, rank_key))

    if not all_members_ids:
        # Use a generic name if multiple ranks were requested, otherwise use the single display name
        display_name_text = "الرتب المطلوبة" if len(display_names_shown) > 1 else display_names_shown[0] if display_names_shown else text
        return message.reply_text(f"🚫 **لا يوجد أي أعضاء في رتبة {display_name_text} في البوت.**", quote=True)

    member_list_lines = []
    # Iterate through unique user IDs collected
    for user_id_str in all_members_ids:
        try:
            # Fetch user object for mention
            user = client.get_users(int(user_id_str))
            # Find all ranks this user has *from the list being shown*
            user_specific_ranks = [rank_display_names.get(key, key) for key in rank_keys_to_show if user_id_str in ranks.get(key, {})]
            ranks_text = "، ".join(user_specific_ranks)
            member_list_lines.append(f"• {user.mention} ({ranks_text})")
        except Exception:
            # Handle cases where user might not be found (e.g., deleted account)
            member_list_lines.append(f"• مستخدم غير معروف (ID: {user_id_str})")

    # Title based on requested ranks
    title_text = " و ".join(display_names_shown) if len(display_names_shown) > 1 else (display_names_shown[0] if display_names_shown else text)

    # Split message if too long
    list_text = "\n".join(member_list_lines)
    if len(list_text) + len(title_text) > 4000: # Approx limit
         chunk_size = 1500 # Approximate chunk size
         chunks = [list_text[i:i+chunk_size] for i in range(0, len(list_text), chunk_size)]
         message.reply_text(f"🏅 **قائمة {title_text} في البوت (الجزء 1):**\n" + chunks[0], parse_mode="HTML", quote=True)
         for i, chunk in enumerate(chunks[1:], start=2):
              message.reply_text(f"🏅 **قائمة {title_text} في البوت (الجزء {i}):**\n" + chunk, parse_mode="HTML", quote=True)
    else:
         message.reply_text(f"🏅 **قائمة {title_text} في البوت:**\n" + list_text, parse_mode="HTML", quote=True)


# إضافة قناة للقروب (لربطها بالبلاغات مثلاً)
@app.on_message(filters.text & filters.group & filters.incoming)
def add_channel_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "اضف" or text[1].lower() != "قناه": # Use .lower()
        return # Not "اضف قناه" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Check sender rank: owner or main_owner needed
    if sender_order < rank_order.get("owner", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**", quote=True)

    channel_username_or_id = text[2].replace("@", "") # Remove @ if present

    if not channel_username_or_id:
        return message.reply_text("❌ **الرجاء إدخال معرف/آيدي القناة بعد الأمر.**", quote=True)

    # Validate channel exists and bot is admin there with correct permissions
    try:
        # Use get_chat to handle both username and ID
        channel = client.get_chat(channel_username_or_id)
        if channel.type != "channel":
             return message.reply_text("❌ **المدخل ليس قناة!**", quote=True)

        # Check bot admin status in channel and if it can post messages
        me_in_channel = client.get_chat_member(channel.id, client.me.id)
        if not (me_in_channel.status == ChatMemberStatus.ADMINISTRATOR and me_in_channel.privileges and me_in_channel.privileges.can_post_messages):
             # Try to get channel username for display, fallback to ID
             channel_display_name = channel.username if channel.username else str(channel.id)
             return message.reply_text(f"❌ **البوت ليس مشرفاً في القناة @{channel_display_name} أو لا يملك صلاحية إرسال الرسائل فيها!**", quote=True)


        # Store channel ID instead of username for robustness
        channel_id_str = str(channel.id)

        if chat_id not in group_settings:
            group_settings[chat_id] = {}
        # Let's store channels explicitly for reports vs others if needed later
        # Use the key 'linked_report_channels'
        if "linked_report_channels" not in group_settings[chat_id]:
            group_settings[chat_id]["linked_report_channels"] = []

        if channel_id_str in group_settings[chat_id]["linked_report_channels"]:
             # Try to get channel username for display, fallback to ID
             channel_display_name = channel.username if channel.username else str(channel.id)
             return message.reply_text(f"ℹ️ **القناة @{channel_display_name} مضافة بالفعل لهذا القروب!**", quote=True)


        group_settings[chat_id]["linked_report_channels"].append(channel_id_str)
        save_data() # Save data
        # Try to get channel username for display, fallback to ID
        channel_display_name = channel.username if channel.username else str(channel.id)
        message.reply_text(f"✅ **تم إضافة القناة @{channel_display_name} (`{channel.id}`) للقروب!**", parse_mode="HTML", quote=True) # Show ID as well
    except Exception as e:
         message.reply_text(f"❌ **حدث خطأ أثناء إضافة القناة:** تأكد من أن المعرف/الآيدي صحيح وأن البوت في القناة ومشرف بها ويملك صلاحية إرسال الرسائل.\nالتفاصيل: {e}", quote=True)


# حذف قناة من القروب
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_channel_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "حذف" or text[1].lower() != "قناه": # Use .lower()
        return # Not "حذف قناه" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Check sender rank: owner or main_owner needed
    if sender_order < rank_order.get("owner", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمالكين فقط!**", quote=True)

    channel_username_or_id = text[2].replace("@", "") # Remove @ if present

    if chat_id not in group_settings or "linked_report_channels" not in group_settings[chat_id]:
        return message.reply_text("🚫 **لا توجد قنوات مضافة لهذا القروب!**", quote=True)

    channel_list = group_settings[chat_id]["linked_report_channels"]

    # Try to find the channel ID based on username or ID input
    target_channel_id_str = None
    channel_display_name = channel_username_or_id # Default display name

    try:
        # First, try fetching the chat by username or ID to get the correct ID
        channel_chat = client.get_chat(channel_username_or_id)
        target_channel_id_str = str(channel_chat.id)
        channel_display_name = channel_chat.username if channel_chat.username else str(channel_chat.id)
    except Exception:
         # If fetching fails, assume the input might be a raw ID string already stored
         if channel_username_or_id.isdigit():
             target_channel_id_str = channel_username_or_id
         else:
              # If it's not a digit and fetch failed, it's not a valid channel/ID
              return message.reply_text(f"🚫 **القناة @{channel_username_or_id} غير موجودة أو لا يمكن الوصول إليها!**", quote=True)


    if target_channel_id_str and target_channel_id_str in channel_list:
        channel_list.remove(target_channel_id_str)
        save_data() # Save data
        message.reply_text(f"✅ **تم حذف القناة @{channel_display_name} (`{target_channel_id_str}`) من القروب!**", parse_mode="HTML", quote=True)
    else:
        # Try to find by display name in case the user entered the stored ID directly
        found = False
        channel_id_to_remove = None
        for stored_channel_id in channel_list:
             try:
                  stored_channel_chat = client.get_chat(int(stored_channel_id))
                  stored_display_name = stored_channel_chat.username if stored_channel_chat.username else str(stored_channel_chat.id)
                  if stored_display_name.lower() == channel_username_or_id.lower():
                       channel_id_to_remove = stored_channel_id
                       channel_display_name = stored_display_name
                       found = True
                       break
             except Exception:
                  pass # Ignore if fetching stored channel fails

        if found and channel_id_to_remove:
             channel_list.remove(channel_id_to_remove)
             save_data() # Save data
             message.reply_text(f"✅ **تم حذف القناة @{channel_display_name} (`{channel_id_to_remove}`) من القروب!**", parse_mode="HTML", quote=True)
        else:
             message.reply_text(f"🚫 **القناة @{channel_username_or_id} غير موجودة في القائمة المضافة لهذا القروب!**", quote=True)


# 🗑️ أوامر المسح والتنظيف 🗑️
@app.on_message(filters.text & filters.group & filters.incoming)
def delete_commands_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = message.chat.id
    sender_id = str(message.from_user.id)

    # Check sender permissions for *any* delete command first
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    # Assuming 'admin' or higher can use delete commands
    if sender_order < rank_order.get("admin", 0):
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    # --- Specific delete commands ---

    # مسح الكل (Delete last 100 messages + command message)
    if text == "مسح الكل":
        try:
            # Get message IDs to delete, including the command message itself
            # Telegram API allows deleting a range. message_id is the last message ID.
            # Delete from message_id - 99 up to message_id (inclusive, total 100)
            # Max number of messages to delete in one go is 100
            num_to_delete = 100
            message_ids_to_delete = list(range(message.message_id - num_to_delete + 1, message.message_id + 1))
            # Filter out message IDs that might be too old (older than 48 hours cannot be deleted by bot)
            # This requires fetching the message timestamp, which adds complexity.
            # For simplicity, assume recent messages, but be aware of the 48-hour limit.
            # Delete in chunks of 100
            chunk_size = 100
            for i in range(0, len(message_ids_to_delete), chunk_size):
                chunk_to_delete = message_ids_to_delete[i : i + chunk_size]
                try:
                     # Use filter=filters.create(lambda _, m: (time.time() - m.date.timestamp()) < 48*3600) if fetching messages
                     # But here we just have IDs, so we rely on the API to handle the age limit.
                     client.delete_messages(chat_id, chunk_to_delete)
                     # Optional delay between chunks
                     time.sleep(0.1) # Small delay
                except Exception as e:
                     print(f"Failed to delete messages chunk: {e}")
                     # Don't break, try to delete other chunks
                     # message.reply_text(f"⚠️ حدث خطأ أثناء مسح جزء من الرسائل: {e}", quote=True) # Avoid spamming error

            # No reply needed as the command message is deleted
            return
        except Exception as e:
             # Reply will be sent to the chat if deletion fails for the command message itself
             message.reply_text(f"❌ **حدث خطأ أثناء مسح الرسائل:** ربما البوت ليس لديه صلاحية حذف.\nالتفاصيل: {e}", quote=True)
             return # Stop processing


    # مسح المحظورين (Clear ban list) - Clears Telegram bans
    elif text == "مسح المحظورين":
        try:
            banned_count = 0
            # client.get_chat_bans requires admin rights in the group
            # It returns a generator of ChatMember objects with status 'kicked' or 'banned'
            # Need to iterate and unban
            # Note: This can be slow for large groups with many bans
            # get_chat_bans returns up to 200 users by default, can use limit/offset for more
            for member in client.get_chat_bans(chat_id):
                 # Ensure it's a kicked/banned member, not just restricted
                 if member.status in [ChatMemberStatus.KICKED, ChatMemberStatus.BANNED]:
                      try:
                           client.unban_chat_member(chat_id, member.user.id)
                           banned_count += 1
                           # Optional delay
                           time.sleep(0.2) # Small delay
                      except Exception as e:
                           print(f"Failed to unban user {member.user.id}: {e}") # Log failure

            message.reply_text(f"✅ **تم مسح قائمة المحظورين في تيليجرام بنجاح! ({banned_count} مستخدم)**", quote=True)
        except Exception as e:
             # This might happen if bot lacks permissions or there's an API issue
             message.reply_text(f"❌ **حدث خطأ أثناء مسح قائمة المحظورين:** ربما البوت ليس لديه صلاحية جلب قائمة المحظورين أو إلغاء الحظر.\nالتفاصيل: {e}", quote=True)


    # مسح المكتومين (Clear restricted list) - Clears Telegram restrictions
    elif text == "مسح المكتومين":
        try:
            restricted_count = 0
            # get_chat_members with filter RESTRICTED is the correct way
            # Note: This might take time for large groups
            # Need to iterate as it's a generator
            # get_chat_members returns up to 200 users by default
            for member in client.get_chat_members(chat_id, filter=ChatMemberStatus.RESTRICTED):
                # Ensure it's actually restricted
                if member.status == ChatMemberStatus.RESTRICTED:
                     try:
                          # Unrestrict by setting basic permissions back
                          client.restrict_chat_member(chat_id, member.user.id, ChatPermissions(
                              can_send_messages=True, can_send_media_messages=True,
                              can_send_other_messages=True, can_add_web_page_previews=True,
                              can_send_polls=True, can_change_info=False,
                              can_invite_users=True, can_pin_messages=False,
                              can_manage_topics=False, can_send_audios=True,
                              can_send_documents=True, can_send_photos=True,
                              can_send_videos=True, can_send_video_notes=True,
                              can_send_voices=True, can_send_stickers=True,
                              can_send_animations=True, can_use_inline_bots=True
                          ))
                          restricted_count += 1
                          # Optional delay
                          time.sleep(0.2) # Small delay
                     except Exception as e:
                          print(f"Failed to unrestrict user {member.user.id}: {e}") # Log failure

            message.reply_text(f"✅ **تم مسح قائمة المقيدين في تيليجرام بنجاح! ({restricted_count} مستخدم)**", quote=True)
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء مسح قائمة المقيدين:** ربما البوت ليس لديه صلاحية جلب قائمة المقيدين أو فك التقييد.\nالتفاصيل: {e}", quote=True)

    # مسح الرتب (e.g., مسح admin) - Clears bot ranks
    elif text.startswith("مسح "):
        parts = text.split()
        if len(parts) >= 2: # Expecting "مسح [role]" or "مسح [number]"
            arg = parts[1].lower() # Get the argument after "مسح"

            # Try matching role name first
            target_rank_key = None
            for key, display in rank_display_names.items():
                 if display.lower() == arg or key.lower() == arg:
                      target_rank_key = key
                      break

            if target_rank_key and target_rank_key in ranks:
                 # Prevent clearing higher ranks or equal to the sender's highest rank
                 # Also prevent clearing the_goat rank
                 if target_rank_key == "the_goat":
                      return message.reply_text("❌ **لا يمكنك مسح رتبة The GOAT!**", quote=True)

                 target_order = rank_order.get(target_rank_key, -float('inf'))
                 if sender_order <= target_order:
                      display_name = rank_display_names.get(target_rank_key, target_rank_key)
                      return message.reply_text(f"❌ **لا يمكنك مسح رتبة ({display_name}) مساوية أو أعلى من رتبتك!**", quote=True)

                 # Clear the rank dictionary for this key
                 cleared_count = len(ranks[target_rank_key])
                 ranks[target_rank_key] = {}
                 save_data() # Save data
                 display_name = rank_display_names.get(target_rank_key, target_rank_key)
                 return message.reply_text(f"✅ **تم مسح جميع {display_name} من البوت! ({cleared_count} مستخدم)**", quote=True)

            # --- مسح [number] fallback ---
            # If it wasn't "مسح [role]", try to parse the argument as a number for deleting messages
            if len(parts) == 2: # Ensure it's exactly "مسح [number]"
                 try:
                     num = int(parts[1])
                     if num <= 0: return message.reply_text("❌ **يجب إدخال رقم موجب بعد 'مسح'!**", quote=True)
                     if num > 200: num = 200 # Limit to avoid API limits or abuse, max 100 per call, can make multiple calls
                     # Get message IDs to delete, including the command message
                     # Delete messages up to 'num' messages *before* the command message, plus the command message itself.
                     # Need to fetch messages to ensure they are within the 48-hour limit.
                     # A more reliable way is to fetch, filter by age, then delete.
                     # Simplest way: generate potential IDs and delete in chunks, hoping they are recent.

                     messages_to_delete = []
                     # Fetch messages, starting from the command message ID and going back
                     # Fetching 'num + 1' messages to include the command itself
                     try:
                          # Fetching can be slow for large 'num'. Use a limit.
                          # Pyrogram's delete_messages handles lists of IDs.
                          # Fetching 200 messages might be okay.
                          fetched_messages = client.get_chat_history(chat_id, limit=num + 1)
                          message_ids_to_delete = [msg.id for msg in fetched_messages if (time.time() - msg.date.timestamp()) < 48 * 3600] # Filter messages older than 48 hours
                          # Ensure the command message is in the list to be deleted
                          if message.id not in message_ids_to_delete:
                               message_ids_to_delete.append(message.id)

                          if not message_ids_to_delete:
                               return message.reply_text("ℹ️ **لا توجد رسائل حديثة يمكن مسحها.**", quote=True)

                          # Delete in chunks of 100
                          chunk_size = 100
                          deleted_count = 0
                          for i in range(0, len(message_ids_to_delete), chunk_size):
                              chunk_to_delete = message_ids_to_delete[i : i + chunk_size]
                              try:
                                   client.delete_messages(chat_id, chunk_to_delete)
                                   deleted_count += len(chunk_to_delete) # Count messages in the chunk
                                   time.sleep(0.1) # Small delay
                              except Exception as e:
                                   print(f"Failed to delete messages chunk: {e}")
                                   # Continue trying other chunks

                          # No reply needed if deletion was successful, as the command message is deleted.
                          # If deleted_count == 0, it means the command message wasn't deleted either.
                          if deleted_count == 0:
                               message.reply_text("❌ **فشل مسح الرسائل:** ربما البوت ليس لديه صلاحية حذف أو الرسائل قديمة جداً.", quote=True)
                          return # Stop processing


                     except Exception as e:
                          # Reply will be sent to the chat if deletion fails
                          message.reply_text(f"❌ **حدث خطأ أثناء مسح الرسائل:** ربما البوت ليس لديه صلاحية جلب السجل أو حذف الرسائل.\nالتفاصيل: {e}", quote=True)
                          return # Stop processing

                 except ValueError:
                      pass # Not a number, the 'ms7' command didn't match a role or number

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
             message.reply_text(f"❌ **حدث خطأ أثناء مسح الرسالة:** ربما البوت ليس لديه صلاحية حذف أو الرسالة المردود عليها قديمة جداً.\nالتفاصيل: {e}", quote=True)
             return # Stop processing

    # مسح قائمة المنع (Clears group-specific banned words)
    elif text == "مسح قائمة المنع":
        if chat_id in protection_settings and "banned_words" in protection_settings[chat_id]:
            count = len(protection_settings[chat_id]["banned_words"])
            protection_settings[chat_id]["banned_words"] = []
            save_data() # Save data
            message.reply_text(f"✅ **تم مسح قائمة الكلمات الممنوعة! ({count} كلمة/عبارة)**", quote=True)
        else:
             message.reply_text("ℹ️ **لا توجد قائمة كلمات ممنوعة لهذا القروب.**", quote=True)

    # مسح الردود (Clear group-specific auto-replies)
    elif text == "مسح الردود":
        if chat_id in group_settings and "auto_replies" in group_settings[chat_id]:
            count = len(group_settings[chat_id]["auto_replies"])
            group_settings[chat_id]["auto_replies"] = {}
            # Clean up the auto_replies key if it's the only thing left
            if chat_id in group_settings and not group_settings[chat_id]["auto_replies"]:
                 # Consider removing the chat_id key if the dictionary becomes empty
                 pass # Keep the chat_id key and empty dict for potential future settings
            save_data() # Save data
            message.reply_text(f"✅ **تم مسح جميع الردود التلقائية الخاصة بهذا القروب! ({count} رد)**", quote=True)
        else:
             message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة بهذا القروب.**", quote=True)

    # مسح الأوامر المضافة (Clear group-specific custom commands)
    elif text == "مسح الأوامر المضافة":
        if chat_id in group_settings and "custom_commands" in group_settings[chat_id]:
            count = len(group_settings[chat_id]["custom_commands"])
            group_settings[chat_id]["custom_commands"] = {}
            # Clean up the custom_commands key
            if chat_id in group_settings and not group_settings[chat_id]["custom_commands"]:
                 pass # Keep key and empty dict
            save_data() # Save data
            message.reply_text(f"✅ **تم مسح جميع الأوامر المضافة الخاصة بهذا القروب! ({count} أمر)**", quote=True)
        else:
             message.reply_text("ℹ️ **لا توجد أوامر مضافة خاصة بهذا القروب.**", quote=True)

    # مسح الايدي (Clear ID info config - Assuming this stored custom ID card config)
    elif text == "مسح الايدي":
        # Assuming 'id_info' stores custom ID card settings per group
        if chat_id in group_settings and "id_info" in group_settings[chat_id]:
            del group_settings[chat_id]["id_info"] # Delete key
            # Clean up the chat_id key if dictionary becomes empty
            if chat_id in group_settings and not group_settings[chat_id]:
                 del group_settings[chat_id]
            save_data() # Save data
            message.reply_text("✅ **تم مسح بيانات الايدي المخصصة لهذا القروب!**", quote=True)
        else:
             message.reply_text("ℹ️ **لا توجد بيانات ايدي مخصصة مخزنة لهذا القروب.**", quote=True)

    # مسح الترحيب (Clear welcome message config)
    elif text == "مسح الترحيب":
        if chat_id in group_settings and "welcome_message" in group_settings[chat_id]:
            del group_settings[chat_id]["welcome_message"]
            # Clean up chat_id key if empty
            if chat_id in group_settings and not group_settings[chat_id]:
                 del group_settings[chat_id]
            save_data() # Save data
            message.reply_text("✅ **تم مسح رسالة الترحيب!**", quote=True)
        else:
             message.reply_text("ℹ️ **لا توجد رسالة ترحيب مخزنة لهذا القروب.**", quote=True)

    # مسح الرابط (Clear group link config)
    elif text == "مسح الرابط":
        if chat_id in group_settings and "link" in group_settings[chat_id]:
            del group_settings[chat_id]["link"]
            # Clean up chat_id key if empty
            if chat_id in group_settings and not group_settings[chat_id]:
                 del group_settings[chat_id]
            save_data() # Save data
            message.reply_text("✅ **تم مسح رابط القروب!**", quote=True)
        else:
             message.reply_text("ℹ️ **لا يوجد رابط قروب مخزن لهذا القروب.**", quote=True)

    # مسح القنوات المضافة (Clears linked report channels)
    elif text == "مسح القنوات":
         if chat_id in group_settings and "linked_report_channels" in group_settings[chat_id]:
              count = len(group_settings[chat_id]["linked_report_channels"])
              group_settings[chat_id]["linked_report_channels"] = []
              # Clean up key
              if chat_id in group_settings and not group_settings[chat_id]["linked_report_channels"]:
                   pass # Keep key and empty list
              save_data() # Save data
              message.reply_text(f"✅ **تم مسح جميع القنوات المضافة لهذا القروب! ({count} قناة)**", quote=True)
         else:
              message.reply_text("ℹ️ **لا توجد قنوات مضافة لهذا القروب.**", quote=True)

    pass # Command not recognized by this handler


# 💬 نظام الردود التلقائية (عامة + خاصة بالقروب) 💬

# الرد التلقائي على العبارات (يفحص أولاً الردود الخاصة بالقروب، ثم الردود العامة)
@app.on_message(filters.text & filters.group & filters.incoming)
def auto_reply_handler(client, message):
    # No prison check needed for auto-replies
    # This handler should be AFTER custom command handler and protection handlers.

    text = message.text.lower()
    chat_id = str(message.chat.id)

    # 1. تحقق من الردود الخاصة بالقروب أولاً
    if chat_id in group_settings and "auto_replies" in group_settings[chat_id]:
        group_replies = group_settings[chat_id]["auto_replies"]
        for trigger, replies in group_replies.items():
            # استخدام 'in' للسماح بتطابق جزء من الكلمة أو عبارة
            # Consider using regex for whole word matching if needed
            if trigger in text and replies:
                reply = random.choice(replies)
                message.reply_text(reply, quote=True)
                return # تم الرد، توقف المعالجة

    # 2. إذا لم يتم العثور على رد في إعدادات القروب، تحقق من الردود العامة
    # Access global_auto_replies via bot_data as it might have been loaded
    if "global_auto_replies" in bot_data:
        global_replies = bot_data["global_auto_replies"]
        for key in global_replies:
            # استخدام 'in' للسماح بتطابق جزء من الكلمة أو عبارة
            # Consider using regex for whole word matching if needed
            if key in text and global_replies[key]: # Ensure the reply list is not empty
                reply = random.choice(global_replies[key])
                message.reply_text(reply, quote=True)
                return # تم الرد، توقف المعالجة

    # لا يوجد رد تلقائي مطابق
    pass


# أمر إضافة رد تلقائي خاص بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def add_auto_reply_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split(maxsplit=2) # Split "اضف رد", trigger, and response
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "اضف" or text[1].lower() != "رد": # Use .lower()
        return # Not "اضف رد" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    # Check for format "اضف رد [الكلمة المفتاحية] = [الرد]"
    parts_after_command = text[2].split("=", maxsplit=1)
    if len(parts_after_command) < 2:
         return message.reply_text("❌ **استخدم الصيغة الصحيحة: اضف رد [الكلمة المفتاحية] = [الرد]**", quote=True)

    trigger = parts_after_command[0].strip().lower()
    reply_text = parts_after_command[1].strip()

    if not trigger or not reply_text:
         return message.reply_text("❌ **الرجاء تحديد الكلمة المفتاحية والرد بشكل صحيح.**", quote=True)

    if chat_id not in group_settings:
        group_settings[chat_id] = {}
    if "auto_replies" not in group_settings[chat_id]:
        group_settings[chat_id]["auto_replies"] = {}

    # Store replies as a list to allow multiple responses per trigger
    if trigger not in group_settings[chat_id]["auto_replies"]:
        group_settings[chat_id]["auto_replies"][trigger] = []

    # Prevent adding duplicate replies for the same trigger
    if reply_text in group_settings[chat_id]["auto_replies"][trigger]:
         return message.reply_text(f"ℹ️ **الرد '{reply_text}' موجود بالفعل للكلمة المفتاحية '{trigger}'.**", quote=True)

    group_settings[chat_id]["auto_replies"][trigger].append(reply_text)
    save_data() # Save data
    message.reply_text(f"✅ **تم إضافة الرد التلقائي للكلمة المفتاحية '{trigger}' بنجاح!**", quote=True)


# أمر حذف رد تلقائي خاص بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_auto_reply_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split(maxsplit=2) # Split "حذف رد", trigger, and optional specific response
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "حذف" or text[1].lower() != "رد": # Use .lower()
        return # Not "حذف رد" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    # Check for format "حذف رد [الكلمة المفتاحية]" or "حذف رد [الكلمة المفتاحية] = [الرد المحدد]"
    parts_after_command = text[2].split("=", maxsplit=1)
    trigger = parts_after_command[0].strip().lower()
    specific_reply_text = parts_after_command[1].strip() if len(parts_after_command) > 1 else None

    if not trigger:
        return message.reply_text("❌ **الرجاء تحديد الكلمة المفتاحية للرد المراد حذفه.**", quote=True)

    if chat_id not in group_settings or "auto_replies" not in group_settings[chat_id]:
        return message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة مضافة لهذا القروب.**", quote=True)

    group_replies = group_settings[chat_id]["auto_replies"]

    if trigger not in group_replies:
         return message.reply_text(f"ℹ️ **لا يوجد رد تلقائي مسجل للكلمة المفتاحية '{trigger}'.**", quote=True)

    if specific_reply_text is None:
        # Delete all replies for this trigger
        del group_replies[trigger]
        # If no other replies for this group, maybe clean up the 'auto_replies' key?
        if not group_replies:
             del group_settings[chat_id]["auto_replies"]
             # Consider removing the chat_id key if the dictionary becomes empty
             # if chat_id in group_settings and not group_settings[chat_id]: # Clean up chat entry if empty
             #      del group_settings[chat_id]

        save_data() # Save data
        message.reply_text(f"✅ **تم حذف جميع الردود التلقائية للكلمة المفتاحية '{trigger}'!**", quote=True)
    else:
        # Delete only the specific reply text
        if specific_reply_text in group_replies[trigger]:
            group_replies[trigger].remove(specific_reply_text)
            # If the list for this trigger becomes empty, remove the trigger key
            if not group_replies[trigger]:
                 del group_replies[trigger]
                 # Clean up group entry if empty
                 if not group_replies:
                      del group_settings[chat_id]["auto_replies"]
                      # if chat_id in group_settings and not group_settings[chat_id]:
                      #      del group_settings[chat_id]

            save_data() # Save data
            message.reply_text(f"✅ **تم حذف الرد المحدد '{specific_reply_text}' للكلمة المفتاحية '{trigger}'!**", quote=True)
        else:
            message.reply_text(f"ℹ️ **الرد المحدد '{specific_reply_text}' غير موجود للكلمة المفتاحية '{trigger}'.**", quote=True)


# أمر عرض الردود التلقائية الخاصة بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def show_group_auto_replies_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "ردود القروب":
        if chat_id in group_settings and "auto_replies" in group_settings[chat_id]:
            group_replies = group_settings[chat_id]["auto_replies"]
            if group_replies:
                reply_list = []
                for trigger, replies in group_replies.items():
                    # Join multiple replies with '|' or similar separator
                    replies_text = " | ".join(replies)
                    reply_list.append(f"• `{trigger}`: {replies_text}")

                list_text = "\n".join(reply_list)
                # Split message if too long
                if len(list_text) > 4000: # Approx limit
                     chunk_size = 1500
                     chunks = [list_text[i:i+chunk_size] for i in range(0, len(list_text), chunk_size)]
                     message.reply_text(f"💬 **الردود التلقائية الخاصة بهذا القروب (الجزء 1):**\n" + chunks[0], parse_mode="Markdown", quote=True)
                     for i, chunk in enumerate(chunks[1:], start=2):
                          message.reply_text(f"💬 **الردود التلقائية الخاصة بهذا القروب (الجزء {i}):**\n" + chunk, parse_mode="Markdown", quote=True)
                else:
                    message.reply_text(f"💬 **الردود التلقائية الخاصة بهذا القروب:**\n" + list_text, parse_mode="Markdown", quote=True)
            else:
                message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة مضافة لهذا القروب.**", quote=True)
        else:
            message.reply_text("ℹ️ **لا توجد ردود تلقائية خاصة مضافة لهذا القروب.**", quote=True)


# 🛠 لوحة تحكم المطور الأساسي (في الخاص) 🛠

# أوامر المطورين في الخاص
@app.on_message(filters.text & filters.private & filters.incoming)
def dev_commands_handler(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Check if user is a developer
    if not is_dev(user_id):
        # Only reply for unknown commands if it's not the main dev panel trigger
        if text not in ["لوحة التحكم", "/panel"]:
             return message.reply_text(f"🚫 **هذه الأوامر مخصصة للشيخ @rnp_e فقط**")
        else:
             # Let admin_panel_cmd handle the reply for "لوحة التحكم" / "/panel"
             pass


    # --- أوامر المطور الأساسي فقط ---
    if is_main_dev(user_id):
        if text.startswith("اضافة مطور"):
            # Expecting reply or @username/id
            # Need to handle parsing the argument if not a reply
            parts = text.split()
            if len(parts) < 2 and not message.reply_to_message:
                 return message.reply_text("❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**")

            # Use get_target_user, allow targeting bots? No, secondary dev should be human.
            user, error_message = get_target_user(client, message, allow_self=False)

            if error_message:
                 return message.reply_text(error_message)

            target_user_id_str = str(user.id)

            if target_user_id_str == main_dev:
                 return message.reply_text("❌ **لا يمكنك إضافة المطور الأساسي كمطور ثانوي!**")

            if target_user_id_str in secondary_devs:
                 return message.reply_text(f"ℹ️ **المستخدم {user.mention} هو بالفعل مطور ثانوي!**", parse_mode="HTML")

            # Optionally get a display name from the command if provided, otherwise use first name
            display_name = user.first_name
            if len(parts) > 2 and not message.reply_to_message:
                 # If user provided ID/username and a name after that
                 display_name_parts = parts[2:] # Everything after "اضافة مطور [user]"
                 if display_name_parts:
                      display_name = " ".join(display_name_parts)


            secondary_devs[target_user_id_str] = display_name # Store name as value
            save_data() # Save data
            message.reply_text(f"✅ **تم إضافة {user.mention} كمطور ثانوي بالاسم '{display_name}'!**", parse_mode="HTML")

        elif text.startswith("حذف مطور"):
            # Expecting reply or @username/id
            # Need to handle parsing the argument if not a reply
            parts = text.split()
            if len(parts) < 2 and not message.reply_to_message:
                 return message.reply_text("❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**")

            user, error_message = get_target_user(client, message, allow_self=False)

            if error_message:
                 return message.reply_text(error_message)

            target_user_id_str = str(user.id)

            if target_user_id_str == main_dev:
                 return message.reply_text("❌ **لا يمكنك حذف المطور الأساسي من قائمة المطورين!**")

            if target_user_id_str in secondary_devs:
                del secondary_devs[target_user_id_str]
                save_data() # Save data
                message.reply_text(f"✅ **تم حذف {user.mention} من قائمة المطورين الثانويين**", parse_mode="HTML")
            else:
                message.reply_text(f"🚫 **المستخدم {user.mention} ليس في قائمة المطورين الثانويين!**", parse_mode="HTML")

        elif text == "قائمة المطورين":
            if secondary_devs:
                dev_list_lines = []
                # Sort secondary devs by ID or name if needed
                # Let's sort by name for better readability
                sorted_devs = sorted(secondary_devs.items(), key=lambda item: item[1].lower())

                for dev_id_str, name in sorted_devs:
                    try:
                        dev_user = client.get_users(int(dev_id_str))
                        dev_list_lines.append(f"• {dev_user.mention} ({name})")
                    except Exception:
                        dev_list_lines.append(f"• مستخدم غير معروف (ID: {dev_id_str}) ({name})") # Include name even if user not found

                dev_list_text = "\n".join(dev_list_lines)
                # Include main dev at the top
                try:
                     main_dev_user = client.get_users(int(main_dev))
                     main_dev_line = f"👑 • {main_dev_user.mention} (المطور الأساسي)"
                except Exception:
                     main_dev_line = f"👑 • مستخدم غير معروف (ID: {main_dev}) (المطور الأساسي)"

                full_list_text = f"🛠 **قائمة المطورين:**\n{main_dev_line}\n" + dev_list_text
                message.reply_text(full_list_text, parse_mode="HTML")
            else:
                 # Only main dev exists
                 try:
                      main_dev_user = client.get_users(int(main_dev))
                      main_dev_line = f"👑 • {main_dev_user.mention} (المطور الأساسي)"
                 except Exception:
                      main_dev_line = f"👑 • مستخدم غير معروف (ID: {main_dev}) (المطور الأساسي)"
                 message.reply_text(f"🛠 **قائمة المطورين:**\n{main_dev_line}\n🚫 **لا يوجد مطورين ثانويين حالياً.**", parse_mode="HTML")


        elif text == "اعادة تشغيل": # Add restart command here for main dev
             message.reply_text("🔄 **جاري إعادة تشغيل البوت...**")
             # Attempt graceful shutdown and restart
             # Note: This requires a process manager (like systemd, Docker restart policy, supervisor)
             # to actually restart the script after it exits.
             # Using os.execv is a common method, but might behave differently based on environment.
             try:
                  save_data() # Save data before restarting
                  print("Attempting to restart bot...")
                  # Use os.execv to replace current process with a new one
                  # sys.executable is the path to the python interpreter
                  # sys.argv is the list of command-line arguments passed to the current script
                  os.execv(sys.executable, [sys.executable] + sys.argv)
             except Exception as e:
                  message.reply_text(f"❌ **فشل إعادة التشغيل:** {e}")
                  print(f"Restart failed: {e}")

        elif text == "ايقاف البوت": # Add stop command for main dev
             message.reply_text("🛑 **جاري إيقاف البوت...**")
             try:
                  save_data() # Save data before stopping
                  print("Stopping bot...")
                  app.stop() # Stop Pyrogram client
                  # exit the script gracefully
                  sys.exit(0)
             except Exception as e:
                  message.reply_text(f"❌ **فشل إيقاف البوت:** {e}")
                  print(f"Stop failed: {e}")


        # --- أوامر لوحة تحكم المطور الأساسي (تظهر مع زر) ---
        # This specific trigger is handled by admin_panel_cmd below


# لوحة تحكم المطور الأساسي (يتم عرضها كرد على أمر معين مثل "لوحة التحكم" أو "/panel")
@app.on_message(filters.text & filters.private & filters.incoming)
def admin_panel_cmd(client, message):
    user_id = str(message.from_user.id)
    text = message.text.lower()

    # This handler specifically triggers for "لوحة التحكم" or "/panel"
    if text != "لوحة التحكم" and text != "/panel":
        return # Not the panel command

    if not is_main_dev(user_id):
        return message.reply_text(f"🚫 **هذه اللوحة مخصصة للشيخ @rnp_e فقط!**", quote=True)

    # Fetching dialogs can take time, especially for large accounts
    # Consider adding a loading message.
    try:
        sent_message = message.reply_text("⏳ **جاري تجميع بيانات لوحة التحكم... قد يستغرق هذا بعض الوقت.**", quote=True)
        dialogs = client.get_dialogs()
        chat_count = 0
        invite_links = []
        # Iterate through dialogs to count groups/supergroups and get invite links
        for dialog in dialogs:
            # Exclude private chats and channels unless specified
            if dialog.chat.type in ["supergroup", "group"]:
                chat_count += 1
                # Try to get invite link
                invite_link_text = "(لا يمكن جلب الرابط)" # Default if cannot get link
                try:
                    # Check if bot is admin and can export invite link
                    chat_member = client.get_chat_member(dialog.chat.id, client.me.id)
                    if chat_member.status == ChatMemberStatus.ADMINISTRATOR and chat_member.privileges and chat_member.privileges.can_invite_users:
                         invite_link = client.export_chat_invite_link(dialog.chat.id)
                         invite_link_text = f"[الرابط]({invite_link})"
                    elif chat_member.status == ChatMemberStatus.ADMINISTRATOR:
                         invite_link_text = "(البوت مشرف لكن لا يمكنه جلب الرابط)"
                    else:
                         invite_link_text = "(البوت ليس مشرفاً)"

                except Exception:
                    # Handle cases where getting chat member or link fails
                     invite_link_text = "(خطأ في جلب الرابط)"

                # Sanitize chat title for Markdown link if needed
                chat_title = dialog.chat.title.replace("[", "").replace("]", "")
                invite_links.append(f"[{chat_title}] {invite_link_text}")

        invite_links_text = "\n".join(invite_links) if invite_links else "🚫 **لا يوجد قروبات مفعّل فيها البوت**"

        # Get bot username dynamically
        bot_username = client.get_me().username

        panel_text = f"""
📊 **لوحة التحكم الخاصة بـ @{bot_username}**:
━━━━━━━━━━━━
👥 **عدد القروبات المشترك بها:** {chat_count}
🔗 **روابط القروبات:**
{invite_links_text}
━━━━━━━━━━━━
"""

        # Define inline keyboard buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart_bot_panel"),
             InlineKeyboardButton("📢 إرسال إذاعة", callback_data="broadcast")],
             [InlineKeyboardButton("🛠 قائمة المطورين الثانويين", callback_data="list_secondary_devs_panel")], # Add button to list devs
             [InlineKeyboardButton("📊 توب القروبات", callback_data="top_groups_panel")] # Add button for top groups
        ])

        # Edit the loading message with the actual panel
        sent_message.edit_text(panel_text, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
         # Edit the loading message to show error
         sent_message.edit_text(f"❌ **حدث خطأ أثناء إعداد لوحة التحكم:** {e}")


# التحكم في البوت من اللوحة (عبر الأزرار)
@app.on_callback_query()
def handle_admin_buttons(client, callback_query):
    user_id = str(callback_query.from_user.id)

    # Only main dev can use these panel buttons
    # Handle report action callbacks separately below.
    # Check if this is a panel callback data
    panel_callbacks = ["restart_bot_panel", "broadcast", "list_secondary_devs_panel", "top_groups_panel"]
    if callback_query.data in panel_callbacks:
        if not is_main_dev(user_id):
            return callback_query.answer("🚫 **هذه الأوامر مخصصة للشيخ @rnp_e فقط!**", show_alert=True)

        data = callback_query.data
        # chat_id = callback_query.message.chat.id # Chat where the panel message is - usually private chat with dev

        if data == "restart_bot_panel": # Use a distinct callback_data
            callback_query.answer("جاري إعادة تشغيل البوت...", show_alert=True)
            # Edit the button message state
            try:
                callback_query.edit_message_text(callback_query.message.text + "\n\n" + "🔄 **جاري إعادة تشغيل البوت...**", reply_markup=callback_query.message.reply_markup)
            except Exception:
                 # Handle message edit failure (e.g., message too old)
                 pass # Continue with restart attempt

            # Attempt graceful shutdown and restart
            # Note: This requires a process manager
            try:
                 save_data() # Save data before restarting
                 print("Attempting to restart bot...")
                 os.execv(sys.executable, [sys.executable] + sys.argv) # Use sys.executable twice as per common practice
            except Exception as e:
                 callback_query.message.reply_text(f"❌ **فشل إعادة التشغيل:** {e}")
                 print(f"Restart failed: {e}")

        elif data == "broadcast":
            callback_query.answer("ارسل رسالة الإذاعة الآن في الخاص", show_alert=True)
            # This requires a state mechanism (e.g., user_states = {user_id: "waiting_for_broadcast_message"})
            # Since state is lost on restart, this is complex. Placeholder message for now.
            # A simple implementation: the *next* message from the main dev in private chat is the broadcast message.
            # This is a basic implementation and needs careful handling to avoid accidental broadcasts.
            # A robust implementation would involve a specific state, confirmation, etc.
            callback_query.message.reply_text("📢 **ارسل رسالة الإذاعة الآن في هذا الدردشة الخاصة.** (البوت سيرسل رسالتك القادمة لجميع القروبات)\n\n**ملاحظة:** هذه الميزة تتطلب تطبيق لوجيك إضافي لتخزين نية الإذاعة والرسالة نفسها بشكل آمن.")
            # You would then need a separate handler for filters.private that checks if user_id is main_dev
            # and if a broadcast is pending.
            # Example (basic):
            # @app.on_message(filters.text & filters.private & filters.user(main_dev) & ~filters.command(["start", "panel", ...])) # Exclude other known commands
            # def handle_broadcast_message(client, message):
            #     # Check if user_id is in a broadcast_state
            #     # If so:
            #     # message_to_broadcast = message.text
            #     # Get list of chat IDs (e.g., from saved group_activity or dialogs cache)
            #     # for chat_id_str in bot_data.get("group_activity", {}).keys():
            #     #    try: client.send_message(int(chat_id_str), message_to_broadcast)
            #     #    except: pass # Handle blocked or left chats
            #     # message.reply_text("✅ تم إرسال الإذاعة.")
            #     # Reset broadcast state for user

        elif data == "list_secondary_devs_panel": # Handle this callback from the panel button
             # This logic is duplicated from the dev_commands_handler, consolidate or call that logic
             if secondary_devs:
                 dev_list_lines = []
                 sorted_devs = sorted(secondary_devs.items(), key=lambda item: item[1].lower())
                 for dev_id_str, name in sorted_devs:
                     try:
                         dev_user = client.get_users(int(dev_id_str))
                         dev_list_lines.append(f"• {dev_user.mention} ({name})")
                     except Exception:
                         dev_list_lines.append(f"• مستخدم غير معروف (ID: {dev_id_str}) ({name})")
                 dev_list_text = "\n".join(dev_list_lines)

                 try:
                      main_dev_user = client.get_users(int(main_dev))
                      main_dev_line = f"👑 • {main_dev_user.mention} (المطور الأساسي)"
                 except Exception:
                      main_dev_line = f"👑 • مستخدم غير معروف (ID: {main_dev}) (المطور الأساسي)"

                 full_list_text = f"🛠 **قائمة المطورين:**\n{main_dev_line}\n" + dev_list_text

                 # Edit the panel message to show the list, keep the buttons
                 # Check if the message is too long to edit, if so, send new message
                 if len(callback_query.message.text) + len(full_list_text) > 4096: # Pyrogram text limit
                     callback_query.message.reply_text(full_list_text, parse_mode="HTML") # Send as new message
                 else:
                     callback_query.edit_message_text(full_list_text, parse_mode="HTML", reply_markup=callback_query.message.reply_markup) # Edit existing message

             else:
                 # Only main dev exists
                 try:
                      main_dev_user = client.get_users(int(main_dev))
                      main_dev_line = f"👑 • {main_dev_user.mention} (المطور الأساسي)"
                 except Exception:
                      main_dev_line = f"👑 • مستخدم غير معروف (ID: {main_dev}) (المطور الأساسي)"

                 full_list_text = f"🛠 **قائمة المطورين:**\n{main_dev_line}\n🚫 **لا يوجد مطورين ثانويين حالياً.**"
                 callback_query.edit_message_text(full_list_text, parse_mode="HTML", reply_markup=callback_query.message.reply_markup)

             callback_query.answer() # Answer the callback query

        elif data == "top_groups_panel":
             # Trigger the top groups command logic
             # This logic is duplicated from the top_groups_cmd function. Consolidate or call.
             # Let's duplicate for now to keep it simple within the callback handler.
             # Sort by value (points), handle potential non-int values with .get
             sorted_groups = sorted(group_activity.items(), key=lambda item: item[1] if isinstance(item[1], (int, float)) else 0, reverse=True)[:20]


             if not sorted_groups:
                 callback_query.edit_message_text("🚫 **لا يوجد تفاعل كافي لعرض توب القروبات!**", reply_markup=callback_query.message.reply_markup, quote=True)
             else:
                top_text_lines = ["🏆 **أكثر القروبات تفاعلًا:**\n"]
                for rank, (group_id_str, points) in enumerate(sorted_groups, start=1):
                    chat_title = f"القروب ذو الآيدي `{group_id_str}`"
                    try:
                        chat = client.get_chat(int(group_id_str))
                        chat_title = chat.title.replace("[", "").replace("]", "") # Sanitize title
                    except Exception:
                        pass # Ignore if chat fetch fails

                    top_text_lines.append(f"{rank} - {chat_title} - {int(points)} نقطة 🔥") # Cast points to int for display

                list_text = "\n".join(top_text_lines)
                # Edit the panel message to show the list, keep the buttons
                # Check message length before editing
                if len(callback_query.message.text) + len(list_text) > 4096: # Pyrogram text limit
                     callback_query.message.reply_text(list_text, quote=True) # Send as new message
                else:
                     callback_query.edit_message_text(list_text, reply_markup=callback_query.message.reply_markup, quote=True) # Edit existing message

             callback_query.answer() # Answer the callback query

    # Handle report actions (mute, restrict, ignore) triggered by inline buttons in report messages
    # This part should be separate from the main dev panel buttons but uses the same handler
    # The logic is implemented below in `handle_report_actions`.
    # Ensure this handler processes report actions correctly.
    # Note: The callback data for reports is different (e.g., mutereport_...).
    # This check is handled by the @app.on_callback_query(filters.regex("...")) decorator
    # No need for an else here if the regex filter is specific enough.


# 🏦 نظام البنك، الممتلكات، الوظائف، السجن 🏦
@app.on_message(filters.text & filters.group & filters.incoming)
def bank_property_job_prison_system_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         # Allow 'سجني' command even if in prison
         if message.text.lower() != "سجني":
              remaining_time = int(banned_users[str(message.from_user.id)] - time.time())
              minutes = remaining_time // 60
              seconds = remaining_time % 60 # Corrected modulo
              message.reply_text(f"⏳ **أنت مسجون حالياً!** تبقى لك {minutes} دقيقة و {seconds} ثانية. لا يمكنك استخدام الأوامر.", quote=True)
              return # Block all commands except 'سجني'
         # If it is 'سجني', let it pass to the handler below


    text = message.text.lower()
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    # Get the first word(s) of the command for locking check
    text_parts = text.split(maxsplit=2) # Split into [command, arg1, rest]
    command_prefix = text_parts[0]
    two_word_command = " ".join(text_parts[:2]) if len(text_parts) > 1 else None

    # Check if command is locked in group settings
    # Check for two-word commands first, then single-word commands
    if two_word_command and is_command_locked(chat_id, two_word_command):
         return message.reply_text(f"🚫 **أمر '{two_word_command}' مقفل في هذا القروب!**", quote=True)
    elif is_command_locked(chat_id, command_prefix):
         return message.reply_text(f"🚫 **أمر '{command_prefix}' مقفل في هذا القروب!**", quote=True)


    # --- 🏦 نظام البنك الأساسي 🏦 ---

    # Initialize user's balance if creating account
    if text == "انشاء حساب بنكي":
        if user_id in bank_accounts:
            return message.reply_text(f"🚫 **لديك حساب بنكي بالفعل! رصيدك الحالي: {bank_accounts.get(user_id, 0)}💰**", quote=True)
        bank_accounts[user_id] = 5000  # يبدأ كل لاعب برصيد 5000
        save_data() # Save data
        message.reply_text("✅ **تم إنشاء حساب بنكي لك! رصيدك الابتدائي: 5000💰**", quote=True)
        return # Command handled

    # Ensure user has a bank account for other bank/job/property operations
    # Allow 'سجني' and 'سداد ديوني' even if no bank account to inform user/allow bail if they earn cash later
    bank_commands_needed_account = ["رصيدي", "راتبي", "بخشيش", "استثمار", "العجلة",
                                     "شراء", "بيع", "ممتلكاتي", "انضم شرطة", "انضم عصابة",
                                     "انضم رئيس عصابة", "ترجل"]
    if any(text.startswith(cmd) for cmd in bank_commands_needed_account):
         if user_id not in bank_accounts:
              return message.reply_text("❌ **يجب إنشاء حساب بنكي أولًا! استخدم أمر: انشاء حساب بنكي**", quote=True)


    if text == "رصيدي": # Added command to check balance
         message.reply_text(f"🏦 **رصيدك الحالي: {bank_accounts.get(user_id, 0)}💰**", quote=True)

    elif text == "راتبي":
        # Check last salary time to prevent spamming salary (requires persistence for last_salary_time)
        # Add a simple cooldown (in-memory, resets on restart)
        salary_cooldown = 3600 # 1 hour
        # Use bot_data to store cooldowns persistently
        if "cooldowns" not in bot_data:
             bot_data["cooldowns"] = {}
        if "last_salary_time" not in bot_data["cooldowns"]:
             bot_data["cooldowns"]["last_salary_time"] = {}

        last_salary_time = bot_data["cooldowns"]["last_salary_time"].get(user_id, 0)
        current_time = time.time()

        if current_time - last_salary_time < salary_cooldown:
             remaining = int(salary_cooldown - (current_time - last_salary_time))
             minutes = remaining // 60
             seconds = remaining % 60
             return message.reply_text(f"⏳ **لقد استلمت راتبك مؤخراً!** انتظر {minutes} دقيقة و {seconds} ثانية.", quote=True)

        salary = 0
        job = user_jobs.get(user_id)
        if job == "شرطة":
            salary = 1500
        elif user_id in gang_leaders: # Check if leader (takes precedence)
             salary = 10000
        elif job == "عصابة": # Check gang member after leader
             salary = 5000
        else: # Default salary if no specific job/role
            salary = 2000

        # VIP card doubles salary (requires VIP card system)
        # Add VIP card check with persistence
        if user_id in vip_cards and vip_cards[user_id] > time.time():
             salary *= 2
             vip_text = " (راتب مضاعف مع بطاقة VIP!)"
        else:
             vip_text = ""


        bank_accounts[user_id] = bank_accounts.get(user_id, 0) + salary
        bot_data["cooldowns"]["last_salary_time"][user_id] = current_time # Update last salary time
        save_data() # Save data

        job_text = job if job else "عضو عادي"
        message.reply_text(f"💰 **أنت تعمل كـ {job_text}. تم إضافة {salary} ريال إلى حسابك كراتب! رصيدك الحالي: {bank_accounts[user_id]}**{vip_text}", quote=True)

    elif text == "بخشيش":
        # Add a cooldown for tipping
        tip_cooldown = 60 # 1 minute
        if "cooldowns" not in bot_data:
             bot_data["cooldowns"] = {}
        if "last_tip_time" not in bot_data["cooldowns"]:
             bot_data["cooldowns"]["last_tip_time"] = {}

        last_tip_time = bot_data["cooldowns"]["last_tip_time"].get(user_id, 0)
        current_time = time.time()
        if current_time - last_tip_time < tip_cooldown:
             remaining = int(tip_cooldown - (current_time - last_tip_time))
             seconds = remaining
             return message.reply_text(f"⏳ **انتظر قليلاً قبل طلب بخشيش آخر!** تبقى لك {seconds} ثانية.", quote=True)


        tip = random.randint(100, 500)
        bank_accounts[user_id] = bank_accounts.get(user_id, 0) + tip
        bot_data["cooldowns"]["last_tip_time"][user_id] = current_time
        save_data() # Save data
        message.reply_text(f"💸 **حصلت على بخشيش بقيمة {tip} ريال! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)

    elif text.startswith("استثمار"):
        # Add cooldown for investment
        invest_cooldown = 300 # 5 minutes
        if "cooldowns" not in bot_data:
             bot_data["cooldowns"] = {}
        if "last_invest_time" not in bot_data["cooldowns"]:
             bot_data["cooldowns"]["last_invest_time"] = {}

        last_invest_time = bot_data["cooldowns"]["last_invest_time"].get(user_id, 0)
        current_time = time.time()
        if current_time - last_invest_time < invest_cooldown:
             remaining = int(invest_cooldown - (current_time - last_invest_time))
             minutes = remaining // 60
             seconds = remaining % 60
             return message.reply_text(f"⏳ **لا يمكنك الاستثمار الآن!** انتظر {minutes} دقيقة و {seconds} ثانية.", quote=True)

        try:
            parts = text.split()
            if len(parts) < 2:
                 return message.reply_text("❌ **استخدم الصيغة الصحيحة: استثمار [المبلغ]**", quote=True)
            amount = int(parts[1])
            if amount <= 0:
                 return message.reply_text("❌ **يجب أن يكون مبلغ الاستثمار موجباً!**", quote=True)

            if bank_accounts.get(user_id, 0) < amount:
                return message.reply_text(f"🚫 **ليس لديك ما يكفي للاستثمار! رصيدك الحالي: {bank_accounts.get(user_id, 0)}**", quote=True)

            # Simulate stock market fluctuation
            # Market value should also be persistent and change globally over time, not per investment
            # Add logic to change market value globally periodically if desired.
            # Simple simulation based on a fixed base: earnings are random +/- percentage of investment
            percentage_change = random.uniform(-0.15, 0.20) # -15% to +20% change
            earnings = int(amount * percentage_change)

            bank_accounts[user_id] = bank_accounts.get(user_id, 0) + earnings
            bot_data["cooldowns"]["last_invest_time"][user_id] = current_time # Update last invest time
            save_data() # Save data

            if earnings >= 0:
                 message.reply_text(f"📈 **استثمرت {amount} ريال وحققت ربحاً قدره {earnings} ريال! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)
            else:
                 message.reply_text(f"📉 **استثمرت {amount} ريال وتكبدت خسارة قدرها {-earnings} ريال! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)

        except (ValueError, IndexError):
            return message.reply_text("❌ **استخدم الصيغة الصحيحة: استثمار [المبلغ] (المبلغ يجب أن يكون رقماً صحيحاً)**", quote=True)
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء الاستثمار: {e}**", quote=True)


    # --- 🎡 عجلة الحظ 🎡 ---
    elif text == "العجلة":
        spin_cost = 5000000 # 5 مليون
        if user_id not in bank_accounts or bank_accounts.get(user_id, 0) < spin_cost:
            return message.reply_text(f"🚫 **يجب أن تمتلك {spin_cost} ريال لتدوير العجلة! رصيدك الحالي: {bank_accounts.get(user_id, 0)}**", quote=True)

        # Add cooldown for spin
        spin_cooldown = 7200 # 2 hours
        if "cooldowns" not in bot_data:
             bot_data["cooldowns"] = {}
        if "last_spin_time" not in bot_data["cooldowns"]:
             bot_data["cooldowns"]["last_spin_time"] = {}

        last_spin_time = bot_data["cooldowns"]["last_spin_time"].get(user_id, 0)
        current_time = time.time()
        if current_time - last_spin_time < spin_cooldown:
             remaining = int(spin_cooldown - (current_time - last_spin_time))
             minutes = remaining // 60
             seconds = remaining % 60
             return message.reply_text(f"⏳ **لقد درت العجلة مؤخراً!** انتظر {minutes} دقيقة و {seconds} ثانية.", quote=True)


        bank_accounts[user_id] = bank_accounts.get(user_id, 0) - spin_cost # Deduct cost first
        prizes = [
            ("🚗 سيارة", "item", "سيارة", 1), # Item prize
            ("💎 ماسة", "item", "ماسة", 1), # Item prize
            ("💰 10 مليون ريال", "money", 10000000), # Money prize
            ("💰 20 مليون ريال", "money", 20000000),
            ("💰 5 مليون ريال", "money", 5000000), # Win back cost
            ("💰 1 مليون ريال", "money", 1000000),
            ("💰 500 ألف ريال", "money", 500000),
            ("💰 100 ألف ريال", "money", 100000),
            ("🚫 لا شيء", "none", 0), # No prize
            ("💰 خسارة 500 ألف ريال", "money", -500000), # Negative prize example
            ("💰 خسارة 1 مليون ريال", "money", -1000000), # Negative prize example
            # Add boost prizes if implemented
            # ("🎲 مضاعفة الأرباح لمدة ساعة", "boost", "double_earnings", 3600) # Boost prize example
        ]
        prize_name, prize_type, prize_value, *prize_args = random.choice(prizes) # Unpack prize details

        message.reply_text(f"🎡 **درت العجلة... ودفعت {spin_cost} ريال.**\n**وحصلت على:** {prize_name}", quote=True)

        if prize_type == "money":
            bank_accounts[user_id] = bank_accounts.get(user_id, 0) + prize_value
            if prize_value >= 0:
                 message.reply_text(f"🎉 **مبروك! تم إضافة {prize_value} ريال لرصيدك! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)
            else:
                 message.reply_text(f"💔 **للأسف! تم خصم {-prize_value} ريال من رصيدك! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)
        elif prize_type == "item":
            item_name = prize_value
            quantity = prize_args[0] if prize_args else 1
            # Ensure user_properties structure exists
            if user_id not in user_properties:
                user_properties[user_id] = {}
            if item_name not in user_properties[user_id]:
                 user_properties[user_id][item_name] = 0
            user_properties[user_id][item_name] += quantity
            message.reply_text(f"📦 **مبروك! تم إضافة {quantity} من '{item_name}' إلى ممتلكاتك!**", quote=True)
        elif prize_type == "boost":
            boost_name = prize_value
            duration = prize_args[0] if prize_args else 0
            # Implement boost logic (requires checking boost status in relevant handlers)
            # This is complex without persistence; placeholder
            message.reply_text(f"⚡ **حصلت على ميزة '{boost_name}' لمدة {duration} ثانية! (تتطلب تطبيق لوجيك خاص للاستفادة منها)**", quote=True)
        elif prize_type == "none":
            message.reply_text("😔 **حظ أوفر في المرة القادمة!**", quote=True)

        bot_data["cooldowns"]["last_spin_time"][user_id] = current_time # Update last spin time
        save_data() # Save data


    # --- 🏠 نظام الممتلكات 🏠 ---

    # Available properties and their buy/sell prices (moved inside function to be accessible)
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
        parts = text.split(maxsplit=2) # Split "شراء", quantity, rest as item name
        if len(parts) < 3:
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: شراء [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة: " + ", ".join(available_items), quote=True)

        try:
            quantity = int(parts[1])
            if quantity <= 0: return message.reply_text("❌ **يجب أن تكون الكمية موجبة!**", quote=True)
            item_name = parts[2].strip()

            if item_name not in property_prices:
                return message.reply_text(f"🚫 **الممتلكات '{item_name}' غير متاحة للشراء.**\nالمتاحة: " + ", ".join(available_items), quote=True)

            cost = property_prices[item_name]["buy"] * quantity

            if bank_accounts.get(user_id, 0) < cost:
                return message.reply_text(f"🚫 **رصيدك غير كافي لشراء {quantity} من {item_name}! التكلفة: {cost} ريال، رصيدك: {bank_accounts.get(user_id, 0)}**", quote=True)

            bank_accounts[user_id] -= cost

            # Ensure user_properties structure exists
            if user_id not in user_properties:
                user_properties[user_id] = {}
            if item_name not in user_properties[user_id]:
                 user_properties[user_id][item_name] = 0

            user_properties[user_id][item_name] += quantity
            save_data() # Save data
            message.reply_text(f"✅ **تم شراء {quantity} من {item_name} مقابل {cost} ريال بنجاح! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)

        except (ValueError, IndexError):
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: شراء [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة: " + ", ".join(available_items), quote=True)
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء الشراء: {e}**", quote=True)


    elif text.startswith("بيع"):
        parts = text.split(maxsplit=2) # Split "بيع", quantity, rest as item name
        if len(parts) < 3:
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: بيع [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة للبيع: " + ", ".join(available_items), quote=True)

        try:
            quantity = int(parts[1])
            if quantity <= 0: return message.reply_text("❌ **يجب أن تكون الكمية موجبة!**", quote=True)
            item_name = parts[2].strip() # Assuming item name is the rest of the text

            if item_name not in property_prices:
                return message.reply_text(f"🚫 **الممتلكات '{item_name}' غير متاحة للبيع.**\nالمتاحة: " + ", ".join(available_items), quote=True)

            # Ensure user_properties structure exists and item quantity is sufficient
            if user_id not in user_properties or item_name not in user_properties[user_id] or user_properties[user_id].get(item_name, 0) < quantity:
                 owned = user_properties.get(user_id, {}).get(item_name, 0)
                 return message.reply_text(f"🚫 **أنت لا تملك هذه الكمية من {item_name}! لديك {owned} فقط.**", quote=True)

            sell_price_per_item = property_prices[item_name]["sell"]
            total_earnings = sell_price_per_item * quantity

            bank_accounts[user_id] = bank_accounts.get(user_id, 0) + total_earnings
            user_properties[user_id][item_name] = user_properties[user_id].get(item_name, 0) - quantity

            # Clean up if quantity drops to 0
            if user_properties[user_id][item_name] <= 0: # Use <= 0 to handle potential negative from errors
                 del user_properties[user_id][item_name]
                 if user_id in user_properties and not user_properties[user_id]: # Check if user has any properties left
                      del user_properties[user_id] # Remove user entry if no properties left

            save_data() # Save data
            message.reply_text(f"✅ **تم بيع {quantity} من {item_name} مقابل {total_earnings} ريال! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)

        except (ValueError, IndexError):
            return message.reply_text(f"❌ **استخدم الصيغة الصحيحة: بيع [الكمية] [اسم الممتلكات]**\nالممتلكات المتاحة للبيع: " + ", ".join(available_items), quote=True)
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء البيع: {e}**", quote=True)

    elif text == "ممتلكاتي": # Added command to show properties
         if user_id not in user_properties or not user_properties.get(user_id):
              return message.reply_text("🏠 **لا تمتلك أي ممتلكات حالياً.**", quote=True)

         property_lines = []
         for item, quantity in user_properties[user_id].items():
              property_lines.append(f"• {item}: {quantity}")

         message.reply_text("🏠 **ممتلكاتك:**\n" + "\n".join(property_lines), quote=True)


    # --- 🚔 نظام الشرطة والعصابات والسجن 🚔 ---

    elif text == "انضم شرطة":
        if user_id in user_jobs:
            return message.reply_text(f"🚫 **لديك وظيفة بالفعل ({user_jobs[user_id]})! ترجل أولاً قبل الانضمام لوظيفة أخرى.**", quote=True)
        # Gang leaders are also in user_jobs now, so check user_jobs is sufficient
        # if user_id in gang_leaders:
        #      return message.reply_text("🚫 **أنت رئيس عصابة! ترجل أولاً.**", quote=True)

        user_jobs[user_id] = "شرطة"
        save_data() # Save data
        message.reply_text("👮‍♂️ **أنت الآن شرطي! راتبك أقل لكنك لا تسجن في البوت.**", quote=True)

    elif text == "انضم عصابة":
        if user_id in user_jobs:
            return message.reply_text(f"🚫 **لديك وظيفة بالفعل ({user_jobs[user_id]})! ترجل أولاً قبل الانضمام لوظيفة أخرى.**", quote=True)
        # if user_id in gang_leaders:
        #      return message.reply_text("🚫 **أنت رئيس عصابة! ترجل أولاً.**", quote=True)

        user_jobs[user_id] = "عصابة"
        save_data() # Save data
        message.reply_text("🔫 **أنت الآن عضو عصابة! راتبك عالي لكنك معرض للسجن.**", quote=True)

    elif text == "انضم رئيس عصابة":
        if user_id in user_jobs:
            return message.reply_text(f"🚫 **لديك وظيفة بالفعل ({user_jobs[user_id]})! ترجل أولاً قبل الانضمام لوظيفة أخرى.**", quote=True)
        # if user_id in gang_leaders:
        #      return message.reply_text("🚫 **أنت بالفعل رئيس عصابة!**", quote=True)

        # Optional: Limit to one gang leader? (Check if any leader exists)
        # if any(job == "رئيس عصابة" for job in user_jobs.values()):
        #      return message.reply_text("🚫 **يوجد رئيس عصابة بالفعل! لا يمكن أن يكون هناك أكثر من رئيس واحد.**", quote=True)

        gang_leaders[user_id] = True # Keep for explicit check if needed, although job is also stored
        user_jobs[user_id] = "رئيس عصابة" # Store job as well
        save_data() # Save data
        message.reply_text("💀 **أنت الآن رئيس العصابة! راتبك أعلى لكن فرصتك في السجن أكبر.**", quote=True)

    elif text == "ترجل": # Added command to leave job/position
         if user_id in gang_leaders: # Check leader first as it's a specific role
              del gang_leaders[user_id]
              # Keep the job entry until next job? Or remove? Remove job entry too.
              if user_id in user_jobs: del user_jobs[user_id]
              save_data() # Save data
              message.reply_text("✅ **تخليت عن منصب رئيس العصابة!**", quote=True)
         elif user_id in user_jobs:
              del user_jobs[user_id]
              save_data() # Save data
              message.reply_text("✅ **تخليت عن وظيفتك!**", quote=True)
         else:
              message.reply_text("ℹ️ **أنت لا تشغل أي منصب أو وظيفة حالياً.**", quote=True)

    elif text.startswith("سجن"): # Gang member/leader tries to avoid prison
        # Check if the user issuing the command is a gang member or leader
        if user_jobs.get(user_id) not in ["عصابة", "رئيس عصابة"]:
            return message.reply_text("🚫 **فقط أفراد العصابة يمكنهم محاولة تجنب السجن!**", quote=True)

        # Check for cooldown on trying to avoid prison
        prison_try_cooldown = 300 # 5 minutes
        if "cooldowns" not in bot_data:
             bot_data["cooldowns"] = {}
        if "last_prison_try_time" not in bot_data["cooldowns"]:
             bot_data["cooldowns"]["last_prison_try_time"] = {}

        last_prison_try_time = bot_data["cooldowns"]["last_prison_try_time"].get(user_id, 0)
        current_time = time.time()
        if current_time - last_prison_try_time < prison_try_cooldown:
             remaining = int(prison_try_cooldown - (current_time - last_prison_try_time))
             minutes = remaining // 60
             seconds = remaining % 60
             return message.reply_text(f"⏳ **لقد حاولت تجنب السجن مؤخراً!** انتظر {minutes} دقيقة و {seconds} ثانية.", quote=True)


        # Simulate chance of getting caught and sent to prison
        chance = random.randint(1, 10) # Chance out of 10
        prison_duration = 120 # 2 minutes in seconds (Reduced for easier testing)
        bail_amount = 5000 # Bail amount (moved here)

        bot_data["cooldowns"]["last_prison_try_time"][user_id] = current_time # Update last try time regardless of outcome

        if chance <= 4:  # Increased chance of getting caught (40%)
            banned_users[user_id] = time.time() + prison_duration
            save_data() # Save data
            message.reply_text(f"🚔 **تم القبض عليك! أنت الآن في السجن لمدة {prison_duration // 60} دقائق. يمكنك دفع كفالة {bail_amount} ريال للخروج مبكراً (سداد ديوني).**", quote=True)
        else: # 60% chance of success
            save_data() # Save data even if successful to log last try time
            message.reply_text("🔫 **نجوت من الشرطة هذه المرة!**", quote=True)

    elif text == "سجني": # Check prison status
        # The prison check at the top allows this command to bypass the block.
        user_id = str(message.from_user.id) # Re-get user_id inside handler

        if is_in_prison(user_id):
            remaining_time = int(banned_users[user_id] - time.time())
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            message.reply_text(f"⏳ **أنت مسجون حالياً!** تبقى لك {minutes} دقيقة و {seconds} ثانية.", quote=True)
        elif user_id in banned_users and banned_users[user_id] <= time.time():
             # Time served, release user and inform them if they ask "سجني" after release time
             del banned_users[user_id]
             save_data() # Save data
             message.reply_text("✅ **تم الإفراج عنك من السجن!**", quote=True)
        else:
            message.reply_text("✅ **أنت لست مسجوناً حالياً.**", quote=True)

    elif text == "سداد ديوني": # Pay bail to get out of prison
        # Allow this command even if no bank account to inform user
        if user_id not in bank_accounts:
             return message.reply_text("❌ **يجب إنشاء حساب بنكي أولًا لدفع الكفالة! استخدم أمر: انشاء حساب بنكي**", quote=True)

        # Check if user is in prison using the dedicated function
        if is_in_prison(user_id):
            bail_amount = 5000 # Bail amount (defined above in 'سجن' command)
            if bank_accounts.get(user_id, 0) < bail_amount:
                return message.reply_text(f"🚫 **رصيدك ({bank_accounts.get(user_id, 0)}) غير كافي لسداد كفالة السجن البالغة {bail_amount} ريال!**", quote=True)

            bank_accounts[user_id] = bank_accounts.get(user_id, 0) - bail_amount
            del banned_users[user_id] # Release user from prison
            save_data() # Save data
            message.reply_text(f"💸 **تم دفع كفالة السجن ({bail_amount} ريال)، وتم الإفراج عنك! رصيدك الحالي: {bank_accounts[user_id]}**", quote=True)
        else:
            message.reply_text("ℹ️ **أنت لست مسجوناً لسداد الكفالة.**", quote=True)


# 🎁 مكافأة الشرطة من المطور (في الخاص) 🎁
# This command is for the main developer only, sent in private chat
@app.on_message(filters.text & filters.private & filters.incoming)
def reward_police_cmd(client, message):
    text = message.text.lower()
    user_id = str(message.from_user.id)

    # Check if user is the main developer
    if user_id != main_dev:
        # Handled by dev_commands_handler gatekeeper earlier, no need to reply again
        return

    if text.startswith("مكافأة الشرطة"):
        parts = text.split()
        reward_amount_arg = 5000 # Default reward

        if len(parts) > 2: # Expecting "مكافأة الشرطة [المبلغ]"
             try:
                  reward_amount_arg = int(parts[2])
                  if reward_amount_arg <= 0:
                       return message.reply_text("❌ **يجب أن تكون قيمة المكافأة موجبة.**")
             except ValueError:
                  return message.reply_text("❌ **قيمة المكافأة يجب أن تكون رقماً.**")


        reward_amount = reward_amount_arg
        police_count = 0
        # Find all users with the "شرطة" job
        police_users = [user for user, job in user_jobs.items() if job == "شرطة"]

        if not police_users:
             return message.reply_text("ℹ️ **لا يوجد أفراد شرطة في البوت حالياً.**")

        try:
            for user in police_users:
                # Ensure the user has a bank account before giving reward
                if user not in bank_accounts:
                     bank_accounts[user] = 0 # Initialize if missing
                bank_accounts[user] += reward_amount
                # Attempt to notify the user (non-critical failure)
                try:
                    police_user_obj = client.get_users(int(user))
                    client.send_message(int(user), f"🎁 **تم منحك مكافأة شرطة بقيمة {reward_amount} ريال من المطور!** رصيدك الجديد: {bank_accounts[user]}💰")
                except Exception:
                    # Handle cases where sending message fails (e.g., user blocked bot)
                    print(f"Could not send reward message to police user ID: {user}")
                police_count += 1

            save_data() # Save data after modifying bank_accounts
            message.reply_text(f"✅ **تم إرسال مكافأة بقيمة {reward_amount} ريال لـ {police_count} فرد من أفراد الشرطة!**")
        except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء إرسال مكافأة الشرطة:** {e}")


# 🛑 نظام البلاغات 🛑

# 📢 أمر الإبلاغ 📢
@app.on_message(filters.text & filters.group & filters.incoming)
def report_message_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)

    # Check if 'بلاغ' command is locked
    if is_command_locked(chat_id, "بلاغ"):
         return message.reply_text("🚫 **أمر البلاغ مقفل في هذا القروب!**", quote=True)


    if text == "بلاغ" and message.reply_to_message:
        target_message = message.reply_to_message
        target_user = target_message.from_user
        target_user_id = str(target_user.id)

        # Prevent reporting self or bots
        if target_user_id == user_id:
             return message.reply_text("❌ **لا يمكنك الإبلاغ عن نفسك!**", quote=True)
        if target_user.is_bot:
             return message.reply_text("❌ **لا يمكنك الإبلاغ عن بوت!**", quote=True)

        # --- Check daily report limit for the sender ---
        # This requires daily reset logic, which isn't implemented here.
        # For simplicity, removing the daily limit check for now.
        # A proper implementation would involve storing {user_id: {date: count}} and resetting daily.
        # Example (requires getting current date string):
        # today_str = time.strftime("%Y-%m-%d")
        # if user_id not in reports: reports[user_id] = {}
        # if today_str not in reports[user_id]: reports[user_id][today_str] = 0
        # report_limit_per_user_daily = 5 # Example limit
        # if reports[user_id][today_str] >= report_limit_per_user_daily:
        #      return message.reply_text(f"🚫 **لقد استخدمت جميع البلاغات اليومية المسموح بها! ({report_limit_per_user_daily})**", quote=True)
        # reports[user_id][today_str] += 1


        # --- Update report count on the reported user ---
        if target_user_id not in user_reported_count:
            user_reported_count[target_user_id] = 0
        user_reported_count[target_user_id] += 1
        save_data() # Save data


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
        report_text += f"\n🆔 **آيدي الرسالة في القروب:** `{target_message.id}`"

        # --- Prepare inline buttons for actions if report count reaches limit ---
        buttons = None
        if user_reported_count[target_user_id] >= max_reports:
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔇 كتم المستخدم", callback_data=f"mutereport_{target_user_id}_{chat_id}")], # Distinct callback data
                [InlineKeyboardButton("🚷 تقييد المستخدم", callback_data=f"restrictreport_{target_user_id}_{chat_id}")], # Distinct callback data
                # Add more options if implemented
                # [InlineKeyboardButton("👢 طرد", callback_data=f"kickreport_{target_user_id}_{chat_id})],
                # [InlineKeyboardButton("🚫 حظر", callback_data=f"banreport_{target_user_id}_{chat_id})],
                [InlineKeyboardButton("✅ تجاهل البلاغات", callback_data=f"ignorereport_{target_user_id}_{chat_id}")] # Distinct callback data
            ])

        # --- Send the report message ---
        report_sent = False
        # 1. Send to linked channel(s) if exists and bot is admin there
        # Use linked_report_channels from group_settings
        # Note: Using `linked_channels` key in bot_data, but the logic uses `linked_report_channels` in `group_settings`.
        # Let's stick to `linked_report_channels` inside `group_settings`.
        linked_report_channels_list = group_settings.get(chat_id, {}).get("linked_report_channels", [])

        # Send report to all linked channels
        for channel_id_str in linked_report_channels_list:
            try:
                 channel_id = int(channel_id_str)
                 # Verify bot is admin in the linked channel and can post
                 me_in_channel = client.get_chat_member(channel_id, client.me.id)
                 if me_in_channel.status == ChatMemberStatus.ADMINISTRATOR and me_in_channel.privileges and me_in_channel.privileges.can_post_messages:
                      client.send_message(channel_id, report_text, reply_markup=buttons, parse_mode="Markdown")
                      report_sent = True # Report sent to at least one channel
                 else:
                     print(f"Bot is not admin or lacks post permission in linked channel {channel_id} for chat {chat_id}. Skipping.")
            except Exception as e:
                 print(f"Error sending report to linked channel {channel_id_str}: {e}. Skipping.")
                 # Continue trying other linked channels or fallback


        # 2. Fallback: Send to main_dev if report wasn't sent to any linked channel
        if not report_sent: # Check if report_sent is still False
            try:
                 client.send_message(int(main_dev), report_text, reply_markup=buttons, parse_mode="Markdown")
                 report_sent = True # Report sent to main dev
            except Exception as e:
                 print(f"Error sending report to main_dev {main_dev}: {e}")
                 # If sending to main_dev fails, the report isn't sent anywhere actionable.

        # 3. Send confirmation message to the group
        if report_sent:
            message.reply_text(f"✅ **تم إرسال بلاغ عن {target_user.mention} للإدارة! ({user_reported_count[target_user_id]} بلاغات مسجلة)**", parse_mode="HTML", quote=True)
        else:
             # If report couldn't be sent to any admin/channel
             message.reply_text(f"❌ **حدث خطأ أثناء إرسال البلاغ.** لا يمكن إرسال التقرير للإدارة. الرجاء التواصل مع المطور.\nالتفاصيل: (لم يتم العثور على قناة بلاغات مرتبطة أو المطور الأساسي)", quote=True)


    # Only reply if the command was specifically "بلاغ" and not a reply
    # The check above covers "بلاغ" with reply. No need for a separate reply here.


# 🔧 تحديد عدد البلاغات المطلوبة للعقوبة 🔧
@app.on_message(filters.text & filters.group & filters.incoming)
def set_report_limit_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    # Check for two-word command
    if len(text) < 3 or text[0].lower() != "ضع" or text[1].lower() != "البلاغات": # Use .lower()
        return # Not "ضع البلاغات" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    try:
        limit = int(text[2])
        if limit <= 0:
            return message.reply_text("❌ **يجب أن يكون عدد البلاغات أكبر من صفر.**", quote=True)
        report_limits[chat_id] = limit
        save_data() # Save data
        message.reply_text(f"✅ **تم تحديد الحد الأدنى للبلاغات على المستخدمين إلى {limit} بلاغات قبل اتخاذ إجراء!**", quote=True)
    except (ValueError, IndexError):
        message.reply_text("❌ **استخدم الصيغة الصحيحة:** ضع البلاغات [الرقم]", quote=True)


# 🔗 ربط القروب بالقناة (لإرسال البلاغات إليها) 🔗
# Moved this command logic to `add_channel_cmd` and `remove_channel_cmd` for consistency,
# using `linked_report_channels` key in `group_settings`.
# The commands "اضف قناه" and "حذف قناه" now handle this.
# Keeping this handler as a placeholder but it won't trigger as the commands are handled elsewhere.
@app.on_message(filters.text & filters.group & filters.incoming)
def link_group_to_channel_cmd_placeholder(client, message):
     text = message.text.lower()
     # This command is handled by add_channel_cmd and remove_channel_cmd now.
     if text.startswith("ربط القناة") or text.startswith("الغاء ربط القناة"):
          message.reply_text("ℹ️ **تم استبدال هذا الأمر بالأوامر:** `اضف قناه [معرف/آيدي القناة]` و `حذف قناه [معرف/آيدي القناة]`", quote=True)
          return # Do nothing else


# ⚖ تنفيذ العقوبات بناءً على البلاغات (من خلال أزرار Inline) ⚖
# Filter callback data starting with action + "report_"
@app.on_callback_query(filters.regex("^(mute|restrict|ignore)report_"))
def handle_report_actions(client, callback_query):
    data = callback_query.data
    user_id = str(callback_query.from_user.id) # User who clicked the button

    # Check if the user clicking the button has permission (e.g., admin or higher rank in bot system)
    sender_highest_rank, sender_order = get_user_highest_rank(user_id)
    # Allow developers (main + secondary) to action reports too
    if not is_dev(user_id) and sender_order < rank_order.get("admin", 0): # Admin or higher required to action on reports
         return callback_query.answer("❌ **لا تملك صلاحية تنفيذ هذا الإجراء!**", show_alert=True)

    parts = data.split("_")
    # Expected format: action_report_target_user_id_chat_id
    if len(parts) != 4 or parts[1] != "report":
         return callback_query.answer("❌ **خطأ في بيانات الزر.**", show_alert=True)

    action = parts[0] # e.g., mute, restrict, ignore
    target_user_id = int(parts[2])
    chat_id = int(parts[3])

    # Prevent acting on users with equal or higher rank than the admin clicking
    target_highest_rank, target_order = get_user_highest_rank(str(target_user_id))
    if target_order >= sender_order:
         return callback_query.answer("❌ **لا يمكنك تنفيذ هذا الإجراء على شخص لديه رتبة مساوية أو أعلى منك!**", show_alert=True)

    try:
        # Attempt to get target user for mention in reply
        target_user_mention = f"المستخدم ذو الآيدي `{target_user_id}`"
        try:
             target_user_obj = client.get_users(target_user_id)
             target_user_mention = target_user_obj.mention
        except Exception:
             pass # Ignore if user fetch fails, use ID in message

        action_successful = False # Flag to indicate if Telegram action succeeded

        if action == "mute":
            try:
                client.restrict_chat_member(chat_id, target_user_id, ChatPermissions(can_send_messages=False))
                action_successful = True
                edit_text = f"🔇 **تم كتم المستخدم {target_user_mention} في القروب (`{chat_id}`) بنجاح!**"
            except Exception as e:
                 edit_text = f"❌ **فشل كتم المستخدم {target_user_mention} في القروب (`{chat_id}`).**\nالسبب: {e}"
                 callback_query.answer(f"❌ فشل الإجراء: {e}", show_alert=True)

        elif action == "restrict":
             try:
                client.restrict_chat_member(chat_id, target_user_id, ChatPermissions()) # Restrict all
                action_successful = True
                edit_text = f"🚷 **تم تقييد المستخدم {target_user_mention} في القروب (`{chat_id}`) بنجاح!**"
             except Exception as e:
                  edit_text = f"❌ **فشل تقييد المستخدم {target_user_mention} في القروب (`{chat_id}`).**\nالسبب: {e}"
                  callback_query.answer(f"❌ فشل الإجراء: {e}", show_alert=True)

        elif action == "ignorereport":
             # Clear report count for this user regardless of Telegram action success
             if str(target_user_id) in user_reported_count:
                  del user_reported_count[str(target_user_id)]
                  save_data() # Save data
             edit_text = f"✅ **تم تجاهل البلاغات وإزالة سجلها للمستخدم {target_user_mention}.**"
             # No need to answer twice if an error occurred above
             if 'action_successful' not in locals(): # Only answer if no mute/restrict action was attempted
                  callback_query.answer("تم تجاهل البلاغات.", show_alert=False)
             callback_query.edit_message_text(edit_text, parse_mode="HTML")
             return # Ignore action is complete


        # If mute or restrict was attempted and successful, clear the report count
        if action_successful:
             if str(target_user_id) in user_reported_count:
                  del user_reported_count[str(target_user_id)]
                  save_data() # Save data
             callback_query.answer("تم تنفيذ الإجراء.", show_alert=False) # Small confirmation
             callback_query.edit_message_text(edit_text, parse_mode="HTML") # Edit the report message

        else:
            # Action failed, just edit the message with the error, don't clear count
             callback_query.edit_message_text(edit_text, parse_mode="HTML")


    except Exception as e:
         # Catch any unexpected errors during callback handling
         callback_query.answer(f"❌ حدث خطأ غير متوقع: {e}", show_alert=True)
         print(f"Unexpected error in handle_report_actions: {e}")
         # Optionally edit the message to indicate failure
         callback_query.message.reply_text(f"❌ **حدث خطأ غير متوقع أثناء معالجة بلاغ:** {e}")


# 🏆 نظام التفاعل والأوسمة 🏆

# 📝 احتساب التفاعل بناءً على نوع المشاركة
@app.on_message(filters.group & filters.incoming & (filters.media | filters.text)) # Apply to media and text messages in groups
def track_activity_handler(client, message):
    # No prison check needed for activity tracking
    # This handler should be positioned *after* protection handlers that delete messages.

    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    # Ignore bots
    if message.from_user and message.from_user.is_bot:
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
        # Minimum length to earn points for text
        if len(message.text.strip()) > 3: # Require more than just a few characters/emoji
             points_gained = 1
             if len(message.text) > 50: points_gained += 1 # Bonus for longer text
             if len(message.text) > 200: points_gained += 1 # Extra bonus for very long text

    elif message.photo:
        points_gained = 3 # Higher points for media
    elif message.sticker:
        points_gained = 2
    elif message.animation: # GIF
        points_gained = 3
    elif message.video:
         points_gained = 4
    elif message.audio:
         points_gained = 2
    elif message.voice:
         points_gained = 3
    elif message.video_note:
         points_gained = 3
    elif message.document: # Files
         points_gained = 2
    elif message.contact: # Contacts
         points_gained = 1
    elif message.location: # Location
         points_gained = 1
    elif message.game: # Games (sending game link/instance)
         points_gained = 1
    elif message.poll: # Polls
         points_gained = 1
    elif message.dice: # Dice
         points_gained = 1

    # Add points for replies, forwards? Could make it too complex. Stick to basic types for now.
    # if message.reply_to_message: points_gained += 0.5 # Bonus for replying?

    if points_gained > 0:
         # Ensure activity scores are treated as numbers (could be loaded as strings from JSON)
         current_user_points = user_activity.get(user_id, 0)
         current_group_points = group_activity.get(chat_id, 0)

         user_activity[user_id] = current_user_points + points_gained
         group_activity[chat_id] = current_group_points + points_gained

         # --- Check for achievements based on accumulated points ---
         current_points = user_activity[user_id] # Use the updated points

         # Define achievements and their point thresholds
         achievements = {
             100: "💬 متفاعل نشيط",
             300: "🔥 متفاعل قوي",
             500: "🎖 متفاعل ذهبي",
             1000: "🏆 أسطورة التفاعل",
             2500: "👑 ملك التفاعل", # New higher tier
             5000: "🌌 أسطورة الأساطير" # New highest tier
         }

         # Check if user unlocked any new achievements
         unlocked_achievement = None
         # Check thresholds in descending order to award highest applicable achievement
         for threshold in sorted(achievements.keys(), reverse=True):
             achievement_name = achievements[threshold]
             if current_points >= threshold and achievement_name not in user_achievements[user_id]:
                  user_achievements[user_id].append(achievement_name)
                  unlocked_achievement = achievement_name # Store the unlocked achievement
                  # Only announce the highest unlocked achievement at this time
                  # break # Uncomment this line if you only want to announce the single highest achievement

         if unlocked_achievement:
              save_data() # Save data immediately when achievement is unlocked
              # Use specific emojis/text for achievement levels if desired
              emoji_map = {
                  "💬 متفاعل نشيط": "💬", "🔥 متفاعل قوي": "🔥", "🎖 متفاعل ذهبي": "🎖",
                  "🏆 أسطورة التفاعل": "🏆", "👑 ملك التفاعل": "👑", "🌌 أسطورة الأساطير": "🌌"
              }
              emoji = emoji_map.get(unlocked_achievement, "🏅")
              message.reply_text(f"{emoji} **تهانينا {message.from_user.mention}! حصلت على وسام '{unlocked_achievement}'!** أنت مبدع!", parse_mode="HTML", quote=True)

         # Save data periodically or after a batch of messages instead of every message for performance
         # For now, saving on every activity change and achievement unlock.


# 📊 عرض توب المتفاعلين في القروب (Shows global top)
@app.on_message(filters.text & filters.group & filters.incoming)
def top_users_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)

    # Check if command is locked
    if is_command_locked(chat_id, "توب المتفاعلين"):
         return message.reply_text("🚫 **أمر توب المتفاعلين مقفل في هذا القروب!**", quote=True)

    if text == "توب المتفاعلين":
        # user_activity is GLOBAL. This command is in filters.group.
        # To show top users *in this group*, activity needs to be tracked PER USER PER GROUP.
        # Let's keep it showing GLOBAL top users from user_activity, but mention it's global.
        # To track per group: user_group_activity = {chat_id: {user_id: points}}

        # For now, show global top users
        top_n = 10
        # Sort users by activity points, ensure value is int/float for sorting
        # Use sorted with a lambda function that handles potential non-numeric values
        sorted_users_ids = sorted(user_activity, key=lambda x: user_activity.get(x, 0) if isinstance(user_activity.get(x), (int, float)) else 0, reverse=True)[:top_n]

        if not sorted_users_ids:
            return message.reply_text("🚫 **لا يوجد تفاعل كافي لعرض التوب!**", quote=True)

        top_text_lines = ["🏆 **توب المتفاعلين في البوت:**\n"]
        for rank, user_id_str in enumerate(sorted_users_ids, start=1):
            points = user_activity.get(user_id_str, 0) # Use .get for safety
            # Ensure points is a number
            if not isinstance(points, (int, float)):
                 points = 0 # Default to 0 if not a number

            mention_text = f"المستخدم ذو الآيدي `{user_id_str}`"
            try:
                user = client.get_users(int(user_id_str))
                mention_text = user.mention
            except Exception:
                pass # Ignore if user fetch fails (e.g., deleted account)

            # Determine user's current rank title based on points (same logic as in track_activity)
            if points >= 5000: title = "🌌 أسطورة الأساطير"
            elif points >= 2500: title = "👑 ملك التفاعل"
            elif points >= 1000: title = "🏆 أسطورة التفاعل"
            elif points >= 500: title = "🎖 متفاعل ذهبي"
            elif points >= 300: title = "🔥 متفاعل قوي"
            elif points >= 100: title = "💬 متفاعل نشيط"
            else: title = "🙂 مشارك" # Default title


            # Show achievements
            achievements_list = user_achievements.get(user_id_str, [])
            achievements_text = f" - الأوسمة: {', '.join(achievements_list)}" if achievements_list else ""

            top_text_lines.append(f"{rank} - {mention_text} ({title}) - {int(points)} نقطة 🔥{achievements_text}") # Cast points to int for display

        list_text = "\n".join(top_text_lines)
        # Split message if too long
        if len(list_text) > 4000: # Approx limit
             chunk_size = 1500 # Approximate chunk size
             chunks = [list_text[i:i+chunk_size] for i in range(0, len(list_text), chunk_size)]
             message.reply_text("🏆 **توب المتفاعلين في البوت (الجزء 1):**\n" + chunks[0], parse_mode="HTML", quote=True)
             for i, chunk in enumerate(chunks[1:], start=2):
                  message.reply_text(f"🏆 **توب المتفاعلين في البوت (الجزء {i}):**\n" + chunk, parse_mode="HTML", quote=True)
        else:
             message.reply_text("🏆 **توب المتفاعلين في البوت:**\n" + list_text, parse_mode="HTML", quote=True)


# 📢 عرض توب القروبات الأكثر تفاعلًا (Shows global group activity)
@app.on_message(filters.text & filters.private & filters.incoming)
def top_groups_cmd(client, message):
    text = message.text.lower()

    if text == "توب القروبات":
        # group_activity is global, this command is in private chat, makes sense.
        # Sort by value (points), handle potential non-int values with .get
        sorted_groups = sorted(group_activity.items(), key=lambda item: item[1] if isinstance(item[1], (int, float)) else 0, reverse=True)[:20]

        if not sorted_groups:
            return message.reply_text("🚫 **لا يوجد تفاعل كافي لعرض توب القروبات!**", quote=True)

        top_text_lines = ["🏆 **أكثر القروبات تفاعلًا:**\n"]
        for rank, (group_id_str, points) in enumerate(sorted_groups, start=1):
            chat_title = f"القروب ذو الآيدي `{group_id_str}`"
            try:
                chat = client.get_chat(int(group_id_str))
                chat_title = chat.title.replace("[", "").replace("]", "") # Sanitize title
            except Exception:
                pass # Ignore if chat fetch fails

            top_text_lines.append(f"{rank} - {chat_title} - {int(points)} نقطة 🔥") # Cast points to int for display

        list_text = "\n".join(top_text_lines)
        # Split message if too long
        if len(list_text) > 4000: # Approx limit
             chunk_size = 1500
             chunks = [list_text[i:i+chunk_size] for i in range(0, len(list_text), chunk_size)]
             message.reply_text("🏆 **أكثر القروبات تفاعلًا (الجزء 1):**\n" + chunks[0], quote=True)
             for i, chunk in enumerate(chunks[1:], start=2):
                  message.reply_text(f"🏆 **أكثر القروبات تفاعلًا (الجزء {i}):**\n" + chunk, quote=True)
        else:
             message.reply_text("🏆 **أكثر القروبات تفاعلًا:**\n" + list_text, quote=True)


# 🔄 تصفير نقاط التفاعل لعضو معين (Global user activity reset)
@app.on_message(filters.text & filters.group & filters.incoming)
def reset_user_activity_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split()
    if len(text) < 2 or text[0].lower() != "صفر" or text[1].lower() != "نقاط": # Use .lower()
         return # Not "صفر نقاط" command

    sender_id = str(message.from_user.id)
    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)


    # Get target user from reply or argument
    user, error_message = get_target_user(client, message, allow_self=True) # Allow resetting self

    if error_message:
         return message.reply_text(error_message, quote=True)

    target_user_id_str = str(user.id)

    # Prevent resetting points of users with equal/higher rank?
    # target_highest_rank, target_order = get_user_highest_rank(target_user_id_str)
    # if target_order >= sender_order and target_user_id_str != sender_id: # Allow resetting self
    #      return message.reply_text("❌ **لا يمكنك تصفير نقاط شخص لديه رتبة مساوية أو أعلى منك!**", quote=True)

    if target_user_id_str in user_activity:
        user_activity[target_user_id_str] = 0
        # Clear achievements too? Let's do it for a full reset related to points.
        if target_user_id_str in user_achievements:
             user_achievements[target_user_id_str] = []
        save_data() # Save data
        message.reply_text(f"✅ **تم تصفير نقاط التفاعل والأوسمة لـ {user.mention}!**", parse_mode="HTML", quote=True)
    else:
        message.reply_text(f"ℹ️ **المستخدم {user.mention} لا يمتلك نقاط تفاعل مسجلة لتصفيرها.**", parse_mode="HTML", quote=True)


# 🔄 تصفير جميع النقاط في القروب (Clears group's total activity score)
@app.on_message(filters.text & filters.group & filters.incoming)
def reset_group_activity_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if text == "صفر كل التفاعل":
        sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
        if sender_order < rank_order.get("admin", 0): # Admin or higher needed
            return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

        # This clears the group's total activity points
        if chat_id in group_activity:
            group_activity[chat_id] = 0
            save_data() # Save data
            message.reply_text("✅ **تم تصفير نقاط التفاعل الكلية المسجلة لهذا القروب!**", quote=True)
        else:
            message.reply_text("ℹ️ **لا توجد نقاط تفاعل كلية مسجلة لهذا القروب لتصفيرها.**", quote=True)

        # Note: This does NOT reset individual user points. User points are global.
        # To reset user points within a group, activity needs to be tracked per group.


# ℹ️ أمر عرض الآيدي الخاص بالمستخدم ℹ️
@app.on_message(filters.text & filters.group & filters.incoming)
def show_my_id_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    if message.text.lower() == "ايديي": # Use .lower()
        user_id = message.from_user.id
        message.reply_text(f"🆔 **آيديك هو:** `{user_id}`", quote=True)


# ℹ️ أمر عرض آيدي مستخدم آخر (بالرد أو الآيدي/المعرف) ℹ️
@app.on_message(filters.text & filters.group & filters.incoming)
def show_user_id_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower().split(maxsplit=1)
    command = text[0]

    if command == "ايدي":
        if len(text) == 1 and not message.reply_to_message:
             return message.reply_text("❌ **الرجاء الرد على رسالة المستخدم أو إدخال المعرف/الآيدي بعد الأمر!**", quote=True)

        # Use get_target_user to handle reply or argument
        user, error_message = get_target_user(client, message, allow_self=True) # Allow checking self

        if error_message:
             # If command was just "ايدي" with no arg/reply, default to sender
             if len(message.text.split()) == 1 and message.text.lower() == "ايدي":
                 user = message.from_user
                 error_message = None # Clear error
             else:
                 return message.reply_text(error_message, quote=True)

        # Allow checking bots including self bot
        # if user.is_bot and str(user.id) != str(client.me.id):
        #      return message.reply_text("❌ **لا يمكنك كشف معلومات بوت آخر غيري!**", quote=True) # This check is in check_user_cmd, not needed here

        message.reply_text(f"🆔 **آيدي المستخدم {user.mention} هو:** `{user.id}`", parse_mode="HTML", quote=True)


# 📄 أمر عرض قائمة الأوامر (Help Command) 📄
@app.on_message(filters.text & filters.group & filters.incoming)
def show_commands_cmd(client, message):
     # Add prison check
     if is_in_prison(str(message.from_user.id)):
          return # Handled by individual command checks

     text = message.text.lower()
     if text == "الأوامر" or text == "/help":

         # Dynamically get bot username
         try:
              bot_username = client.get_me().username
         except Exception:
              bot_username = "البوت" # Fallback

         # List of actual rank display names currently configured
         available_ranks_display = list(rank_display_names.values())


         commands_text = f"""
🤖 **أوامر بوت {bot_name_arabic}:**
━━━━━━━━━━━━━━━
**⚙️ الأوامر العامة:**
- `رتبتي`: لعرض رتبتك في البوت.
- `كشف` أو `كشف بالرد/المعرف/الآيدي`: لعرض معلومات عضو.
- `ايديي`: لعرض آيديك.
- `ايدي بالرد/المعرف/الآيدي`: لعرض آيدي عضو آخر.
- `القوانين`: لعرض قوانين القروب.
- `الرابط`: لعرض رابط القروب.
- `توب المتفاعلين`: لعرض قائمة بأكثر الأعضاء تفاعلاً (على مستوى البوت).
- `ردود القروب`: لعرض قائمة الردود التلقائية الخاصة بالقروب.
- `اوامري`: لعرض قائمة الأوامر المضافة يدوياً في القروب.
- `بلاغ بالرد`: للإبلاغ عن رسالة مخالفة (يتطلب تفعيل نظام البلاغات).

**🛡️ أوامر الحماية (للمشرفين والأعلى):**
- `قفل [الميزة]` / `فتح [الميزة]`: لقفل أو فتح ميزات الحماية (الروابط، تكرار، التوجيه، الصور، الفيديو، الملصقات، المعرفات، التاك، البوتات، الكلمات، الملفات، الصوت، الملاحظات الصوتية، الملاحظات المرئية، الجهات، المواقع، الألعاب، الاستطلاعات، اباحيات).
- `اضف كلمة [الكلمة/العبارة]`: لإضافة كلمة/عبارة لقائمة الكلمات الممنوعة في القروب.
- `حذف كلمة [الكلمة/العبارة]`: لحذف كلمة/عبارة من قائمة الكلمات الممنوعة.
- `قائمة المنع`: لعرض قائمة الكلمات الممنوعة.

**🛠️ أوامر الإدارة (للمشرفين والأعلى):**
- `حظر بالرد/المعرف/الآيدي`: لحظر عضو من القروب.
- `الغاء الحظر بالمعرف/الآيدي`: لفك حظر عضو.
- `طرد بالرد/المعرف/الآيدي`: لطرد عضو من القروب.
- `كتم بالرد/المعرف/الآيدي`: لكتم عضو في القروب.
- `الغاء الكتم بالرد/المعرف/الآيدي`: لفك كتم عضو.
- `تقييد بالرد/المعرف/الآيدي`: لتقييد عضو في القروب (منع معظم الصلاحيات).
- `فك التقييد بالرد/المعرف/الآيدي`: لفك تقييد عضو.
- `رفع القيود بالرد/المعرف/الآيدي`: (نفس فك التقييد).
- `طرد البوتات`: لطرد جميع البوتات من القروب.
- `طرد المحذوفين`: لطرد جميع الحسابات المحذوفة.
- `كشف البوتات`: لعرض قائمة البوتات في القروب.
- `مسح [العدد]`: لمسح آخر عدد محدد من الرسائل (حتى 200).
- `مسح بالرد`: لمسح الرسالة المردود عليها ورسالة الأمر.
- `صفر نقاط بالرد/المعرف/الآيدي`: لتصفير نقاط تفاعل عضو (على مستوى البوت).
- `صفر كل التفاعل`: لتصفير نقاط التفاعل الكلية المسجلة للقروب.
- `ضع البلاغات [الرقم]`: لتحديد عدد البلاغات المطلوبة قبل اتخاذ إجراء آلي.
- `اضف رد [كلمة مفتاحية] = [الرد]`: لإضافة رد تلقائي خاص بالقروب.
- `حذف رد [كلمة مفتاحية]` أو `حذف رد [كلمة مفتاحية] = [الرد المحدد]`: لحذف رد تلقائي.
- `اضف امر [كلمة الأمر] = [الرد/النص]`: لإضافة أمر مخصص خاص بالقروب.
- `حذف امر [كلمة الأمر]`: لحذف أمر مخصص.

**👑 أوامر المالك والأعلى:**
- `رفع [الرتبة] بالرد/المعرف/الآيدي`: لرفع رتبة عضو في البوت (الرتب: {", ".join(available_ranks_display)}).
- `تنزيل [الرتبة] بالرد/المعرف/الآيدي`: لتنزيل رتبة عضو.
- `تنزيل الكل بالرد/المعرف/الآيدي`: لإزالة جميع الرتب اليدوية لعضو.
- `مسح [الرتبة]`: لمسح جميع أعضاء رتبة معينة من البوت.
- `مسح قائمة المنع`: لمسح جميع الكلمات الممنوعة في القروب.
- `مسح الردود`: لمسح جميع الردود التلقائية الخاصة بالقروب.
- `مسح الأوامر المضافة`: لمسح جميع الأوامر المضافة في القروب.
- `مسح الايدي`: لمسح بيانات أمر الايدي المخصصة.
- `مسح الترحيب`: لمسح رسالة الترحيب المخصصة.
- `مسح الرابط`: لمسح رابط القروب المخزن.
- `اضف قناه [معرف/آيدي القناة]`: لإضافة قناة مرتبطة بالقروب (للبلاغات مثلاً).
- `حذف قناه [معرف/آيدي القناة]`: لحذف قناة مرتبطة.
- `مسح القنوات`: لمسح جميع القنوات المضافة للقروب.

**🏦 أوامر البنك والألعاب:**
- `انشاء حساب بنكي`: لإنشاء حساب بنكي في البوت.
- `رصيدي`: لعرض رصيدك.
- `راتبي`: لاستلام راتبك (يومياً).
- `بخشيش`: للحصول على مبلغ عشوائي (يوجد وقت انتظار).
- `استثمار [المبلغ]`: لاستثمار مبلغ في السوق والحصول على ربح/خسارة عشوائي (يوجد وقت انتظار).
- `العجلة`: لتجربة حظك في عجلة الحظ (تكلفة 5 مليون، يوجد وقت انتظار).
- `شراء [الكمية] [الممتلكات]`: لشراء ممتلكات (مثل سيارة، بيت).
- `بيع [الكمية] [الممتلكات]`: لبيع ممتلكات.
- `ممتلكاتي`: لعرض ممتلكاتك.
- `انضم شرطة`: للانضمام لوظيفة الشرطة.
- `انضم عصابة`: للانضمام لوظيفة العصابة.
- `انضم رئيس عصابة`: للانضمام كـ رئيس عصابة.
- `ترجل`: لترك وظيفتك أو منصبك.
- `سجن`: لمحاولة تجنب السجن (لأفراد العصابة، يوجد وقت انتظار).
- `سجني`: لعرض حالة سجنك المتبقية.
- `سداد ديوني`: لدفع الكفالة والخروج من السجن (إذا كنت مسجوناً).

"""
         # Add Admin Panel hint for main dev in private chat
         if is_main_dev(message.from_user.id):
              commands_text += "\n**🛠️ لوحة تحكم المطور الأساسي (في الخاص):** ارسل 'لوحة التحكم' أو /panel في الخاص للوصول إلى اللوحة الإدارية."

         # Send commands in private chat to avoid spam
         try:
             client.send_message(message.from_user.id, commands_text, parse_mode="Markdown", disable_web_page_preview=True)
             message.reply_text("✅ **تم إرسال قائمة الأوامر إلى الدردشة الخاصة بك.**", quote=True)
         except Exception as e:
             message.reply_text(f"❌ **حدث خطأ أثناء إرسال قائمة الأوامر في الخاص.** يرجى التأكد من أنك لم تقم بحظر البوت.\nالتفاصيل: {e}", quote=True)


# 📄 نظام الأوامر المضافة (خاصة بالقروب) 📄
# Store custom commands {chat_id: {command_trigger: response_text}} in group_settings

# أمر إضافة أمر مخصص خاص بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def add_custom_command_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split(maxsplit=2) # Split "اضف امر", trigger, and response
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "اضف" or text[1].lower() != "امر": # Use .lower()
        return # Not "اضف امر" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    # Check for format "اضف امر [كلمة الأمر] = [الرد/النص]"
    parts_after_command = text[2].split("=", maxsplit=1)
    if len(parts_after_command) < 2:
         return message.reply_text("❌ **استخدم الصيغة الصحيحة: اضف امر [كلمة الأمر] = [الرد/النص]**", quote=True)

    command_trigger = parts_after_command[0].strip().lower() # Store trigger in lowercase
    response_text = parts_after_command[1].strip()

    if not command_trigger or not response_text:
         return message.reply_text("❌ **الرجاء تحديد الأمر والرد بشكل صحيح.**", quote=True)

    # Check if this command trigger conflicts with a built-in command
    # Get list of all built-in command triggers (first word of multi-word commands)
    # Updated list to match the commands help text
    built_in_commands = {
        "رفع", "تنزيل", "رتبتي", "كشف", "قفل", "فتح", "حظر", "الغاء الحظر", "طرد",
        "كتم", "الغاء الكتم", "تقييد", "فك التقييد", "رفع القيود", "طرد البوتات",
        "طرد المحذوفين", "كشف البوتات", "القوانين", "ضع قوانين", "الرابط", "اضف رابط",
        "المالك", "المدراء", "الادمن", "المشرفين", "المميزين", "اضف قناه", "حذف قناه",
        "مسح", "انشاء حساب بنكي", "رصيدي", "راتبي", "بخشيش", "استثمار", "العجلة",
        "شراء", "بيع", "ممتلكاتي", "انضم شرطة", "انضم عصابة", "انضم رئيس عصابة",
        "ترجل", "سجن", "سجني", "سداد ديوني", "بلاغ", "ضع البلاغات", "ربط القناة",
        "توب المتفاعلين", "صفر نقاط", "صفر كل التفاعل", "اضف كلمة", "حذف كلمة",
        "قائمة المنع", "ردود القروب", "اضف رد", "حذف رد", "اضف امر", "حذف امر",
        "اوامري", "ايديي", "ايدي", "الأوامر", "/help", "/start", "/panel" # Add common aliases
    }


    # Check if the custom trigger is one of the built-in command triggers
    if command_trigger in built_in_commands or command_trigger.startswith('/'):
         return message.reply_text(f"❌ **الأمر '{command_trigger}' يتعارض مع أمر مدمج أو أمر يبدأ بـ '/'!**", quote=True)


    if chat_id not in group_settings:
        group_settings[chat_id] = {}
    if "custom_commands" not in group_settings[chat_id]:
        group_settings[chat_id]["custom_commands"] = {}

    # Store custom command response
    group_settings[chat_id]["custom_commands"][command_trigger] = response_text
    save_data() # Save data
    message.reply_text(f"✅ **تم إضافة الأمر المخصص '{command_trigger}' بنجاح!**", quote=True)


# أمر حذف أمر مخصص خاص بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def remove_custom_command_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.split(maxsplit=2) # Split "حذف امر", trigger
    chat_id = str(message.chat.id)
    sender_id = str(message.from_user.id)

    if len(text) < 3 or text[0].lower() != "حذف" or text[1].lower() != "امر": # Use .lower()
        return # Not "حذف امر" command

    sender_highest_rank, sender_order = get_user_highest_rank(sender_id)
    if sender_order < rank_order.get("admin", 0): # Admin or higher needed
        return message.reply_text("❌ **هذا الأمر مخصص للمشرفين أو أعلى!**", quote=True)

    command_trigger = text[2].strip().lower() # Use lowercase trigger for matching

    if not command_trigger:
        return message.reply_text("❌ **الرجاء تحديد الأمر المخصص المراد حذفه.**", quote=True)

    if chat_id not in group_settings or "custom_commands" not in group_settings[chat_id]:
        return message.reply_text("ℹ️ **لا توجد أوامر مضافة خاصة بهذا القروب.**", quote=True)

    custom_commands = group_settings[chat_id]["custom_commands"]

    if command_trigger in custom_commands:
        del custom_commands[command_trigger]
        # Clean up if no custom commands left
        if not custom_commands:
             del group_settings[chat_id]["custom_commands"]
             # Consider removing the chat_id key if the dictionary becomes empty
             # if chat_id in group_settings and not group_settings[chat_id]:
             #      del group_settings[chat_id]

        save_data() # Save data
        message.reply_text(f"✅ **تم حذف الأمر المخصص '{command_trigger}'!**", quote=True)
    else:
        message.reply_text(f"ℹ️ **الأمر المخصص '{command_trigger}' غير موجود في قائمة الأوامر المضافة.**", quote=True)


# معالج للأوامر المضافة (يجب أن يأتي قبل الردود التلقائية)
@app.on_message(filters.text & filters.group & filters.incoming)
def custom_command_handler(client, message):
    # No prison check needed for custom commands
    # This handler should be AFTER protection handlers.

    text = message.text.strip().lower() # Match command trigger case-insensitively
    chat_id = str(message.chat.id)

    if chat_id in group_settings and "custom_commands" in group_settings[chat_id]:
        custom_commands = group_settings[chat_id]["custom_commands"]
        # Check for exact match with a custom command trigger
        if text in custom_commands:
            response = custom_commands[text]
            message.reply_text(response, quote=True)
            message.stop_propagation() # Stop other handlers (like auto-reply)
            return

    # If not a custom command, allow other handlers (like auto_reply_handler) to process


# أمر عرض قائمة الأوامر المضافة الخاصة بالقروب
@app.on_message(filters.text & filters.group & filters.incoming)
def show_custom_commands_cmd(client, message):
    # Add prison check
    if is_in_prison(str(message.from_user.id)):
         return # Handled by individual command checks

    text = message.text.lower()
    chat_id = str(message.chat.id)

    if text == "اوامري":
        if chat_id in group_settings and "custom_commands" in group_settings[chat_id]:
            custom_commands = group_settings[chat_id]["custom_commands"]
            if custom_commands:
                command_list = []
                # Sort commands alphabetically by trigger for consistent display
                sorted_commands = sorted(custom_commands.items())
                for trigger, response in sorted_commands:
                     # Truncate long responses for display
                     display_response = response[:70] + "..." if len(response) > 70 else response
                     command_list.append(f"• `{trigger}`: {display_response}")

                list_text = "\n".join(command_list)
                # Split message if too long
                if len(list_text) > 4000: # Approx limit
                     chunk_size = 1500
                     chunks = [list_text[i:i+chunk_size] for i in range(0, len(list_text), chunk_size)]
                     message.reply_text("📄 **الأوامر المضافة في هذا القروب (الجزء 1):**\n" + chunks[0], parse_mode="Markdown", quote=True)
                     for i, chunk in enumerate(chunks[1:], start=2):
                          message.reply_text(f"📄 **الأوامر المضافة في هذا القروب (الجزء {i}):**\n" + chunk, parse_mode="Markdown", quote=True)
                else:
                    message.reply_text("📄 **الأوامر المضافة في هذا القروب:**\n" + list_text, parse_mode="Markdown", quote=True)
            else:
                message.reply_text("ℹ️ **لا توجد أوامر مضافة خاصة بهذا القروب.**", quote=True)
        else:
            message.reply_text("ℹ️ **لا توجد أوامر مضافة خاصة بهذا القروب.**", quote=True)


# ✅ أمر /start الفلاوي (في الخاص) ✅
@app.on_message(filters.command("start") & filters.private & filters.incoming)
def start_command(client, message):
    user_name = message.from_user.first_name # اسم المستخدم
    try:
         bot_username = client.get_me().username # معرف البوت
    except Exception:
         bot_username = "my_bot" # Fallback

    # 🌟 أزرار الانلاين: زر المطور + زر إضافة البوت + زر قناة البوت
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 أضفني لقروبك", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("👨‍💻 المطوّر", url="https://t.me/rnp_e")],
        [InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{bot_channel_username}")] # Use bot_channel_username variable
    ])

    # 🌟 رسالة الترحيب الفلاوية باللهجة السعودية/الخليجية
    welcome_text = f"""هلااااااا والله يا {user_name} 👋😎
🌟 شرفت بوت {bot_name_arabic} الأسطوري!
🔹 إذا تبي حماية وكنترول كامل، ضيفني قروبك ولا عليك من شي 🔥
🔹 إذا عندك أي مشكلة أو اقتراح، مطوّري **@rnp_e** موجود ما يقصر 💪
📢 تابع قناة البوت للمستجدات هنا: **@{bot_channel_username}**

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