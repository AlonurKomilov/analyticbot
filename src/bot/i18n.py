"""Internationalization — English, Russian, Uzbek translations"""

from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Welcome / Start ───────────────────────────────────────────────
    "welcome": {
        "en": (
            "<b>Welcome to Analyticbot!</b> 🤖\n\n"
            "I analyze Telegram channels and groups — just send me a link "
            "and I'll generate a detailed PDF report.\n\n"
            "Tap a button below to get started."
        ),
        "ru": (
            "<b>Добро пожаловать в Analyticbot!</b> 🤖\n\n"
            "Я анализирую Telegram-каналы и группы — "
            "просто отправьте мне ссылку, и я создам подробный PDF-отчёт.\n\n"
            "Нажмите кнопку ниже, чтобы начать."
        ),
        "uz": (
            "<b>Analyticbot-ga xush kelibsiz!</b> 🤖\n\n"
            "Men Telegram kanal va guruhlarni tahlil qilaman — "
            "menga havola yuboring, batafsil PDF hisobot tayyorlayman.\n\n"
            "Boshlash uchun tugmani bosing."
        ),
    },
    # ── Help ──────────────────────────────────────────────────────────
    "help": {
        "en": (
            "<b>How to use:</b>\n\n"
            "1. Tap <b>📊 Analyze Channel</b> or send /analyze\n"
            "2. Paste a channel link or @username\n"
            "3. Wait while I fetch and analyze the data\n"
            "4. Receive a detailed PDF report\n\n"
            "<i>Analysis usually takes 30–60 seconds depending on channel size.</i>"
        ),
        "ru": (
            "<b>Как пользоваться:</b>\n\n"
            "1. Нажмите <b>📊 Анализ канала</b> или отправьте /analyze\n"
            "2. Вставьте ссылку на канал или @username\n"
            "3. Подождите, пока я соберу и проанализирую данные\n"
            "4. Получите подробный PDF-отчёт\n\n"
            "<i>Анализ обычно занимает 30–60 секунд.</i>"
        ),
        "uz": (
            "<b>Qanday foydalanish:</b>\n\n"
            "1. <b>📊 Kanalni tahlil qilish</b> tugmasini bosing yoki /analyze yuboring\n"
            "2. Kanal havolasini yoki @username yuboring\n"
            "3. Ma'lumotlarni yig'ib tahlil qilgunimcha kuting\n"
            "4. Batafsil PDF hisobotni oling\n\n"
            "<i>Tahlil odatda 30–60 soniya davom etadi.</i>"
        ),
    },
    # ── Buttons ───────────────────────────────────────────────────────
    "btn_analyze": {
        "en": "📊 Analyze Channel",
        "ru": "📊 Анализ канала",
        "uz": "📊 Kanalni tahlil qilish",
    },
    "btn_history": {
        "en": "📜 History",
        "ru": "📜 История",
        "uz": "📜 Tarix",
    },
    "btn_help": {
        "en": "ℹ️ Help",
        "ru": "ℹ️ Помощь",
        "uz": "ℹ️ Yordam",
    },
    "btn_analyze_another": {
        "en": "📊 Analyze Another",
        "ru": "📊 Анализ другого канала",
        "uz": "📊 Boshqa kanalni tahlil qilish",
    },
    "btn_my_history": {
        "en": "📜 My History",
        "ru": "📜 Мои анализы",
        "uz": "📜 Mening tarixim",
    },
    "btn_language": {
        "en": "🌐 Language",
        "ru": "🌐 Язык",
        "uz": "🌐 Til",
    },
    # ── Analyze flow ──────────────────────────────────────────────────
    "send_channel": {
        "en": (
            "Send me a channel link or @username to analyze.\n\n"
            "Examples:\n"
            "• <code>https://t.me/durov</code>\n"
            "• <code>@durov</code>\n"
            "• <code>durov</code>"
        ),
        "ru": (
            "Отправьте мне ссылку на канал или @username для анализа.\n\n"
            "Примеры:\n"
            "• <code>https://t.me/durov</code>\n"
            "• <code>@durov</code>\n"
            "• <code>durov</code>"
        ),
        "uz": (
            "Tahlil qilish uchun kanal havolasini yoki @username yuboring.\n\n"
            "Misollar:\n"
            "• <code>https://t.me/durov</code>\n"
            "• <code>@durov</code>\n"
            "• <code>durov</code>"
        ),
    },
    "already_running": {
        "en": "An analysis is already running. Please wait or /cancel first.",
        "ru": "Анализ уже выполняется. Подождите или сначала отправьте /cancel.",
        "uz": "Tahlil allaqachon ishlayapti. Kuting yoki avval /cancel yuboring.",
    },
    "nothing_to_cancel": {
        "en": "Nothing to cancel.",
        "ru": "Нечего отменять.",
        "uz": "Bekor qilish uchun hech narsa yo'q.",
    },
    "cancelled": {
        "en": "Cancelled. Send /analyze to start a new analysis.",
        "ru": "Отменено. Отправьте /analyze для нового анализа.",
        "uz": "Bekor qilindi. Yangi tahlil uchun /analyze yuboring.",
    },
    "invalid_channel": {
        "en": (
            "I couldn't recognize that as a channel link.\n"
            "Try formats like <code>@channel</code> or <code>https://t.me/channel</code>"
        ),
        "ru": (
            "Я не смог распознать это как ссылку на канал.\n"
            "Попробуйте формат <code>@channel</code> или <code>https://t.me/channel</code>"
        ),
        "uz": (
            "Buni kanal havolasi sifatida aniqlay olmadim.\n"
            "<code>@channel</code> yoki <code>https://t.me/channel</code> formatini sinab ko'ring"
        ),
    },
    "send_channel_prompt": {
        "en": "Please send a channel link or @username.",
        "ru": "Пожалуйста, отправьте ссылку на канал или @username.",
        "uz": "Iltimos, kanal havolasini yoki @username yuboring.",
    },
    # ── Progress ──────────────────────────────────────────────────────
    "analyzing": {
        "en": "⏳ <b>Analyzing @{username}</b>\n{stage}",
        "ru": "⏳ <b>Анализирую @{username}</b>\n{stage}",
        "uz": "⏳ <b>@{username} tahlil qilinmoqda</b>\n{stage}",
    },
    "progress_starting": {
        "en": "Starting...",
        "ru": "Начинаю...",
        "uz": "Boshlanmoqda...",
    },
    # ── Report summary ────────────────────────────────────────────────
    "report_title": {
        "en": "✅ <b>Analysis Complete</b>",
        "ru": "✅ <b>Анализ завершён</b>",
        "uz": "✅ <b>Tahlil yakunlandi</b>",
    },
    "channel_label": {
        "en": "Channel",
        "ru": "Канал",
        "uz": "Kanal",
    },
    "supergroup_label": {
        "en": "Supergroup",
        "ru": "Супергруппа",
        "uz": "Superguruh",
    },
    "type_channel": {
        "en": "Channel",
        "ru": "Канал",
        "uz": "Kanal",
    },
    "type_supergroup": {
        "en": "Supergroup",
        "ru": "Супергруппа",
        "uz": "Superguruh",
    },
    "members": {
        "en": "Members",
        "ru": "Подписчики",
        "uz": "A'zolar",
    },
    "period": {
        "en": "Period",
        "ru": "Период",
        "uz": "Davr",
    },
    "posts_analyzed": {
        "en": "posts analyzed",
        "ru": "постов проанализировано",
        "uz": "post tahlil qilindi",
    },
    "days": {
        "en": "days",
        "ru": "дн.",
        "uz": "kun",
    },
    # ── Activity status ───────────────────────────────────────────────
    "activity_active": {
        "en": "🟢 Active",
        "ru": "🟢 Активен",
        "uz": "🟢 Faol",
    },
    "activity_low": {
        "en": "🟡 Low activity",
        "ru": "🟡 Низкая активность",
        "uz": "🟡 Past faoliyat",
    },
    "activity_inactive": {
        "en": "🟠 Inactive",
        "ru": "🟠 Неактивен",
        "uz": "🟠 Faol emas",
    },
    "activity_dead": {
        "en": "🔴 Dead",
        "ru": "🔴 Мёртвый",
        "uz": "🔴 O'lik",
    },
    "status_label": {
        "en": "Status",
        "ru": "Статус",
        "uz": "Holat",
    },
    "last_post_ago": {
        "en": "Last post: {days} days ago",
        "ru": "Последний пост: {days} дн. назад",
        "uz": "Oxirgi post: {days} kun oldin",
    },
    "last_post_today": {
        "en": "Last post: today",
        "ru": "Последний пост: сегодня",
        "uz": "Oxirgi post: bugun",
    },
    "warn_stale_engagement": {
        "en": (
            "⚠️ <b>Note:</b> This channel hasn't posted in {days} days. "
            "Engagement metrics may be inflated because views accumulated over a long period "
            "with very few posts. Treat these numbers with caution."
        ),
        "ru": (
            "⚠️ <b>Внимание:</b> Канал не публиковал {days} дн. "
            "Метрики вовлечённости могут быть завышены, так как просмотры накапливались "
            "длительное время при малом количестве постов."
        ),
        "uz": (
            "⚠️ <b>Diqqat:</b> Kanal {days} kun davomida post joylamagan. "
            "Faollik ko'rsatkichlari shishirilgan bo'lishi mumkin, chunki ko'rishlar "
            "kam postlar bilan uzoq vaqt davomida to'plangan."
        ),
    },
    "warn_low_posts": {
        "en": (
            "⚠️ <b>Note:</b> Only {n} posts found across {days} days ({freq:.2f} posts/day). "
            "Statistics may not be representative of typical performance."
        ),
        "ru": (
            "⚠️ <b>Внимание:</b> Найдено только {n} постов за {days} дн. ({freq:.2f} пост/день). "
            "Статистика может не отражать типичную активность."
        ),
        "uz": (
            "⚠️ <b>Diqqat:</b> {days} kun davomida faqat {n} ta post topildi ({freq:.2f} post/kun). "
            "Statistika odatiy faoliyatni aks ettirmasligi mumkin."
        ),
    },
    "period_note": {
        "en": "📅 Period covers the {n} most recent posts, not the channel lifetime",
        "ru": "📅 Период охватывает {n} последних постов, а не всю историю канала",
        "uz": "📅 Davr kanal umri emas, oxirgi {n} ta postni qamrab oladi",
    },
    "section_reach": {
        "en": "📈 <b>Reach & Engagement</b>",
        "ru": "📈 <b>Охват и вовлечённость</b>",
        "uz": "📈 <b>Qamrov va faollik</b>",
    },
    "avg_views": {
        "en": "Avg views",
        "ru": "Ср. просмотры",
        "uz": "O'rt. ko'rishlar",
    },
    "median": {
        "en": "median",
        "ru": "медиана",
        "uz": "mediana",
    },
    "engagement_rate": {
        "en": "Engagement",
        "ru": "Вовлечённость",
        "uz": "Faollik",
    },
    "virality": {
        "en": "Virality",
        "ru": "Виральность",
        "uz": "Virallik",
    },
    "interaction": {
        "en": "Interaction",
        "ru": "Взаимодействие",
        "uz": "O'zaro ta'sir",
    },
    "section_activity": {
        "en": "📅 <b>Posting Activity</b>",
        "ru": "📅 <b>Активность</b>",
        "uz": "📅 <b>Faoliyat</b>",
    },
    "posts_per_day": {
        "en": "Posts/day",
        "ru": "Постов/день",
        "uz": "Post/kun",
    },
    "best_time": {
        "en": "Best time",
        "ru": "Лучшее время",
        "uz": "Eng yaxshi vaqt",
    },
    "best_day": {
        "en": "Best day",
        "ru": "Лучший день",
        "uz": "Eng yaxshi kun",
    },
    "section_content": {
        "en": "📎 <b>Content</b>",
        "ru": "📎 <b>Контент</b>",
        "uz": "📎 <b>Kontent</b>",
    },
    "top_type": {
        "en": "Top type",
        "ru": "Популярный тип",
        "uz": "Asosiy tur",
    },
    "with_links": {
        "en": "With links",
        "ru": "Со ссылками",
        "uz": "Havolali",
    },
    "full_report": {
        "en": "Full report attached below ⬇️",
        "ru": "Полный отчёт прикреплён ниже ⬇️",
        "uz": "To'liq hisobot quyida biriktirilgan ⬇️",
    },
    # ── Errors ────────────────────────────────────────────────────────
    "error_timeout": {
        "en": (
            "⏰ Analysis timed out. The channel may be too large or Telegram is slow.\n"
            "Try again later."
        ),
        "ru": (
            "⏰ Время анализа истекло. Канал может быть слишком большим.\n"
            "Попробуйте позже."
        ),
        "uz": (
            "⏰ Tahlil vaqti tugadi. Kanal juda katta bo'lishi mumkin.\n"
            "Keyinroq qayta urinib ko'ring."
        ),
    },
    "error_not_channel": {
        "en": "❌ That doesn't appear to be a channel or supergroup.",
        "ru": "❌ Это не похоже на канал или супергруппу.",
        "uz": "❌ Bu kanal yoki superguruhga o'xshamaydi.",
    },
    "error_invalid_link": {
        "en": "❌ Invalid channel link. Check the format and try again.",
        "ru": "❌ Неверная ссылка на канал. Проверьте формат и попробуйте снова.",
        "uz": "❌ Noto'g'ri kanal havolasi. Formatni tekshirib, qayta urinib ko'ring.",
    },
    "error_not_found": {
        "en": "❌ Channel not found. Make sure it exists and is public.",
        "ru": "❌ Канал не найден. Убедитесь, что он существует и является публичным.",
        "uz": "❌ Kanal topilmadi. Kanal mavjud va ochiq ekanligiga ishonch hosil qiling.",
    },
    "error_flood": {
        "en": "⚠️ Telegram rate limit hit. Please wait a few minutes and try again.",
        "ru": "⚠️ Превышен лимит запросов Telegram. Подождите несколько минут.",
        "uz": "⚠️ Telegram so'rovlar chegarasi. Bir necha daqiqa kuting.",
    },
    "error_generic": {
        "en": (
            "❌ Something went wrong during analysis.\n"
            "Make sure the channel exists and is public, then try again."
        ),
        "ru": (
            "❌ Произошла ошибка при анализе.\n"
            "Убедитесь, что канал существует и является публичным."
        ),
        "uz": (
            "❌ Tahlil paytida xatolik yuz berdi.\n"
            "Kanal mavjud va ochiq ekanligiga ishonch hosil qiling."
        ),
    },
    "error_pdf_not_found": {
        "en": "Report generated but PDF file not found. Please try again.",
        "ru": "Отчёт создан, но PDF-файл не найден. Попробуйте снова.",
        "uz": "Hisobot yaratildi, lekin PDF fayl topilmadi. Qayta urinib ko'ring.",
    },
    # ── History ───────────────────────────────────────────────────────
    "no_history": {
        "en": "You haven't run any analyses yet.",
        "ru": "У вас ещё нет анализов.",
        "uz": "Sizda hali tahlillar yo'q.",
    },
    "history_title": {
        "en": "<b>Your recent analyses:</b>\n",
        "ru": "<b>Ваши последние анализы:</b>\n",
        "uz": "<b>Oxirgi tahlillaringiz:</b>\n",
    },
    # ── Language ──────────────────────────────────────────────────────
    "choose_language": {
        "en": "🌐 Choose your language:",
        "ru": "🌐 Выберите язык:",
        "uz": "🌐 Tilni tanlang:",
    },
    "language_set": {
        "en": "Language set to English 🇬🇧",
        "ru": "Язык изменён на русский 🇷🇺",
        "uz": "Til o'zbek tiliga o'zgartirildi 🇺🇿",
    },
    # ── Weekdays ──────────────────────────────────────────────────────
    "weekday_0": {"en": "Monday", "ru": "Понедельник", "uz": "Dushanba"},
    "weekday_1": {"en": "Tuesday", "ru": "Вторник", "uz": "Seshanba"},
    "weekday_2": {"en": "Wednesday", "ru": "Среда", "uz": "Chorshanba"},
    "weekday_3": {"en": "Thursday", "ru": "Четверг", "uz": "Payshanba"},
    "weekday_4": {"en": "Friday", "ru": "Пятница", "uz": "Juma"},
    "weekday_5": {"en": "Saturday", "ru": "Суббота", "uz": "Shanba"},
    "weekday_6": {"en": "Sunday", "ru": "Воскресенье", "uz": "Yakshanba"},
    # ── Weekdays short ────────────────────────────────────────────────
    "weekday_short_0": {"en": "Mon", "ru": "Пн", "uz": "Du"},
    "weekday_short_1": {"en": "Tue", "ru": "Вт", "uz": "Se"},
    "weekday_short_2": {"en": "Wed", "ru": "Ср", "uz": "Ch"},
    "weekday_short_3": {"en": "Thu", "ru": "Чт", "uz": "Pa"},
    "weekday_short_4": {"en": "Fri", "ru": "Пт", "uz": "Ju"},
    "weekday_short_5": {"en": "Sat", "ru": "Сб", "uz": "Sh"},
    "weekday_short_6": {"en": "Sun", "ru": "Вс", "uz": "Ya"},
    # ── PDF report ────────────────────────────────────────────────────
    "pdf_title": {
        "en": "Channel Analytics Report",
        "ru": "Аналитический отчёт канала",
        "uz": "Kanal tahlili hisoboti",
    },
    "pdf_overview": {"en": "Overview", "ru": "Обзор", "uz": "Umumiy ko'rinish"},
    "pdf_status": {"en": "Status", "ru": "Статус", "uz": "Holat"},
    "pdf_last_post": {"en": "Last post", "ru": "Последний пост", "uz": "Oxirgi post"},
    "pdf_days_ago": {"en": "{days} days ago", "ru": "{days} дн. назад", "uz": "{days} kun oldin"},
    "pdf_today": {"en": "today", "ru": "сегодня", "uz": "bugun"},
    "pdf_activity_active": {"en": "Active", "ru": "Активен", "uz": "Faol"},
    "pdf_activity_low": {"en": "Low activity", "ru": "Низкая активность", "uz": "Past faoliyat"},
    "pdf_activity_inactive": {"en": "Inactive", "ru": "Неактивен", "uz": "Faol emas"},
    "pdf_activity_dead": {"en": "Dead", "ru": "Мёртвый", "uz": "O'lik"},
    "pdf_warn_stale": {
        "en": "⚠️ This channel hasn't posted in {days} days. Engagement metrics may be inflated because views accumulated over a long period with very few posts.",
        "ru": "⚠️ Канал не публиковал {days} дн. Метрики вовлечённости могут быть завышены — просмотры накапливались длительное время.",
        "uz": "⚠️ Kanal {days} kun davomida post joylamagan. Faollik ko'rsatkichlari oshirilgan bo'lishi mumkin.",
    },
    "pdf_warn_low_posts": {
        "en": "⚠️ Only {n} posts found across {days} days. Statistics may not be representative.",
        "ru": "⚠️ Найдено только {n} постов за {days} дн. Статистика может быть не показательной.",
        "uz": "⚠️ {days} kun davomida faqat {n} ta post topildi. Statistika ishonchli bo'lmasligi mumkin.",
    },
    "pdf_metric": {"en": "Metric", "ru": "Метрика", "uz": "Ko'rsatkich"},
    "pdf_value": {"en": "Value", "ru": "Значение", "uz": "Qiymat"},
    "pdf_type": {"en": "Type", "ru": "Тип", "uz": "Tur"},
    "pdf_members": {"en": "Members", "ru": "Подписчики", "uz": "A'zolar"},
    "pdf_posts_analyzed": {"en": "Posts analyzed", "ru": "Постов проанализировано", "uz": "Tahlil qilingan postlar"},
    "pdf_period": {"en": "Period", "ru": "Период", "uz": "Davr"},
    "pdf_total_views": {"en": "Total views", "ru": "Всего просмотров", "uz": "Jami ko'rishlar"},
    "pdf_avg_views": {"en": "Avg views/post", "ru": "Ср. просмотров/пост", "uz": "O'rt. ko'rishlar/post"},
    "pdf_median_views": {"en": "Median views/post", "ru": "Медиана просмотров/пост", "uz": "Mediana ko'rishlar/post"},
    "pdf_avg_engagement": {"en": "Avg engagement rate", "ru": "Ср. вовлечённость", "uz": "O'rt. faollik darajasi"},
    "pdf_avg_posts_day": {"en": "Avg posts/day", "ru": "Ср. постов/день", "uz": "O'rt. post/kun"},
    "pdf_engagement_breakdown": {"en": "Engagement Breakdown", "ru": "Разбор вовлечённости", "uz": "Faollik tafsiloti"},
    "pdf_what_it_means": {"en": "What it means", "ru": "Что это значит", "uz": "Bu nima degani"},
    "pdf_reach": {"en": "Reach", "ru": "Охват", "uz": "Qamrov"},
    "pdf_reach_desc": {
        "en": "Avg views as % of members — how many see each post",
        "ru": "Ср. просмотры в % от подписчиков — сколько видят каждый пост",
        "uz": "A'zolarning % ko'rishlar — har bir postni qancha kishi ko'radi",
    },
    "pdf_virality": {"en": "Virality Rate", "ru": "Виральность", "uz": "Virallik darajasi"},
    "pdf_virality_desc": {
        "en": "Forwards ÷ views — how shareable content is",
        "ru": "Пересылки ÷ просмотры — насколько контент распространяется",
        "uz": "Yo'naltirishlar ÷ ko'rishlar — kontent qanchalik tarqaladi",
    },
    "pdf_interaction": {"en": "Interaction Rate", "ru": "Взаимодействие", "uz": "O'zaro ta'sir"},
    "pdf_interaction_desc": {
        "en": "Reactions + replies ÷ views — audience activity",
        "ru": "Реакции + ответы ÷ просмотры — активность аудитории",
        "uz": "Reaksiyalar + javoblar ÷ ko'rishlar — auditoriya faolligi",
    },
    "pdf_avg_replies": {"en": "Avg replies/post", "ru": "Ср. ответов/пост", "uz": "O'rt. javoblar/post"},
    "pdf_avg_replies_desc": {
        "en": "Discussion level in comments",
        "ru": "Уровень обсуждения в комментариях",
        "uz": "Izohlar darajasi",
    },
    "pdf_posts_with_links": {"en": "Posts with links", "ru": "Посты со ссылками", "uz": "Havolali postlar"},
    "pdf_posts_with_links_desc": {
        "en": "How often posts include external links",
        "ru": "Как часто посты содержат внешние ссылки",
        "uz": "Postlarda tashqi havolalar qanchalik tez-tez bo'ladi",
    },
    "pdf_total": {"en": "Total", "ru": "Всего", "uz": "Jami"},
    "pdf_avg_per_post": {"en": "Avg per post", "ru": "Ср. на пост", "uz": "O'rt. post uchun"},
    "pdf_views": {"en": "Views", "ru": "Просмотры", "uz": "Ko'rishlar"},
    "pdf_forwards": {"en": "Forwards", "ru": "Пересылки", "uz": "Yo'naltirishlar"},
    "pdf_reactions": {"en": "Reactions", "ru": "Реакции", "uz": "Reaksiyalar"},
    "pdf_replies": {"en": "Replies", "ru": "Ответы", "uz": "Javoblar"},
    "pdf_views_trend": {"en": "Views Trend", "ru": "Динамика просмотров", "uz": "Ko'rishlar dinamikasi"},
    "pdf_posting_patterns": {"en": "Posting Patterns", "ru": "Паттерны публикаций", "uz": "Nashr qilish naqshlari"},
    "pdf_peak_hour": {"en": "Peak posting hour", "ru": "Пиковый час публикаций", "uz": "Eng ko'p nashr soati"},
    "pdf_peak_day": {"en": "Peak day", "ru": "Пиковый день", "uz": "Eng faol kun"},
    "pdf_content_mix": {"en": "Content Mix", "ru": "Типы контента", "uz": "Kontent turlari"},
    "pdf_top_posts": {"en": "Top Posts by Views", "ru": "Топ-посты по просмотрам", "uz": "Ko'rishlar bo'yicha top postlar"},
    "pdf_top_posts_er": {"en": "Top Posts by Engagement Rate", "ru": "Топ-посты по вовлечённости", "uz": "Faollik bo'yicha top postlar"},
    "pdf_post_id": {"en": "Post ID", "ru": "ID поста", "uz": "Post ID"},
    "pdf_fwd": {"en": "Fwd", "ru": "Пер.", "uz": "Yub."},
    "pdf_react": {"en": "React", "ru": "Реакц.", "uz": "Reaks."},
    "pdf_er_pct": {"en": "ER %", "ru": "ER %", "uz": "ER %"},
    "pdf_preview": {"en": "Preview", "ru": "Превью", "uz": "Ko'rib chiqish"},
    "pdf_generated": {"en": "Generated {date}", "ru": "Сформирован {date}", "uz": "Yaratilgan {date}"},
    "pdf_footer": {
        "en": "Generated by {bot_name} • www.t.me/{bot_name}",
        "ru": "Создано {bot_name} • www.t.me/{bot_name}",
        "uz": "{bot_name} tomonidan yaratilgan • www.t.me/{bot_name}",
    },
    "pdf_days": {"en": "days", "ru": "дн.", "uz": "kun"},
    "pdf_data_note": {
        "en": "Based on the most recent {n} posts ({date_from} – {date_to}, {days} days).",
        "ru": "На основе последних {n} постов ({date_from} – {date_to}, {days} дн.).",
        "uz": "Oxirgi {n} ta post asosida ({date_from} – {date_to}, {days} kun).",
    },
    "pdf_data_note_full": {
        "en": " This represents the channel's complete recent history.",
        "ru": " Это полная недавняя история канала.",
        "uz": " Bu kanalning to'liq yaqin tarixi.",
    },
    "pdf_data_note_partial": {
        "en": " This covers active posting history. For high-volume channels, older posts beyond this window are not included.",
        "ru": " Охватывает активную историю публикаций. Для каналов с высокой частотой старые посты за пределами этого окна не включены.",
        "uz": " Faol nashr tarixi qamrab olingan. Yuqori hajmli kanallar uchun ushbu oynadan tashqaridagi eski postlar kiritilmagan.",
    },
    "pdf_data_note_cached": {
        "en": "Cached result.",
        "ru": "Результат из кэша.",
        "uz": "Kesh natijasi.",
    },
    # ── Chart labels ──────────────────────────────────────────────────
    "chart_views_trend": {"en": "Daily Views Over Time", "ru": "Ежедневные просмотры", "uz": "Kunlik ko'rishlar"},
    "chart_views": {"en": "Views", "ru": "Просмотры", "uz": "Ko'rishlar"},
    "chart_posts": {"en": "Posts", "ru": "Посты", "uz": "Postlar"},
    "chart_top_posts": {"en": "Top 10 Posts by Views", "ru": "Топ-10 постов по просмотрам", "uz": "Ko'rishlar bo'yicha top-10 post"},
    "chart_hourly": {"en": "Posting Activity by Hour (UTC)", "ru": "Активность по часам (UTC)", "uz": "Soatlik faoliyat (UTC)"},
    "chart_hour": {"en": "Hour", "ru": "Час", "uz": "Soat"},
    "chart_weekday": {"en": "Posting Activity by Weekday", "ru": "Активность по дням недели", "uz": "Hafta kunlari bo'yicha faoliyat"},
    "chart_day": {"en": "Day", "ru": "День", "uz": "Kun"},
    "chart_content_mix": {"en": "Content Mix", "ru": "Типы контента", "uz": "Kontent turlari"},
    "chart_engagement": {"en": "Engagement Metrics", "ru": "Метрики вовлечённости", "uz": "Faollik ko'rsatkichlari"},
    "chart_reach_label": {"en": "Reach\n(views/member)", "ru": "Охват\n(просм./подп.)", "uz": "Qamrov\n(ko'rish/a'zo)"},
    "chart_virality_label": {"en": "Virality\n(fwd/views %)", "ru": "Виральность\n(пер./просм. %)", "uz": "Virallik\n(yub./ko'rish %)"},
    "chart_interaction_label": {"en": "Interaction\n(react/views %)", "ru": "Взаимодействие\n(реакц./просм. %)", "uz": "O'zaro ta'sir\n(reaks./ko'rish %)"},
    "chart_text": {"en": "Text", "ru": "Текст", "uz": "Matn"},
    "chart_photo": {"en": "Photo", "ru": "Фото", "uz": "Rasm"},
    "chart_video": {"en": "Video", "ru": "Видео", "uz": "Video"},
    "chart_document": {"en": "Document", "ru": "Документ", "uz": "Hujjat"},
    "chart_other": {"en": "Other", "ru": "Другое", "uz": "Boshqa"},
}

# ── Month names (1-indexed: month_1 = January) ──────────────────────────
_MONTHS_FULL: dict[str, list[str]] = {
    "en": ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "ru": ["", "января", "февраля", "марта", "апреля", "мая", "июня",
           "июля", "августа", "сентября", "октября", "ноября", "декабря"],
    "uz": ["", "yanvar", "fevral", "mart", "aprel", "may", "iyun",
           "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"],
}

_MONTHS_SHORT: dict[str, list[str]] = {
    "en": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "ru": ["", "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
           "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
    "uz": ["", "Yan", "Fev", "Mar", "Apr", "May", "Iyn",
           "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"],
}


def format_date(dt, lang: str) -> str:
    """Format a datetime as a human-readable localized date.

    EN: August 17, 2024
    RU: 17 августа 2024
    UZ: 17-avgust 2024
    """
    months = _MONTHS_FULL.get(lang, _MONTHS_FULL["en"])
    m = months[dt.month]
    if lang == "en":
        return f"{m} {dt.day}, {dt.year}"
    if lang == "ru":
        return f"{dt.day} {m} {dt.year}"
    # uz
    return f"{dt.day}-{m} {dt.year}"


def format_date_short(dt, lang: str) -> str:
    """Short month + day for chart axes: 'Jan 15', 'Янв 15', 'Yan 15'."""
    months = _MONTHS_SHORT.get(lang, _MONTHS_SHORT["en"])
    return f"{months[dt.month]} {dt.day:02d}"


# In-memory per-user language store (user_id → lang code)
_user_languages: dict[int, str] = {}
DEFAULT_LANG = "en"


def get_lang(user_id: int | None) -> str:
    """Get language for a user, defaulting to English."""
    if user_id is None:
        return DEFAULT_LANG
    return _user_languages.get(user_id, DEFAULT_LANG)


def set_lang(user_id: int, lang: str) -> None:
    """Set language for a user."""
    if lang not in ("en", "ru", "uz"):
        lang = DEFAULT_LANG
    _user_languages[user_id] = lang


def t(key: str, lang: str, **kwargs: object) -> str:
    """Get translated string. Falls back to English if key/lang missing."""
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get("en", f"[{key}]")
    if kwargs:
        text = text.format(**kwargs)
    return text
