# =========================================
# STANDFADE FACEIT BOT
# Python 3.11+
# pip install pyTelegramBotAPI
# =========================================

import telebot
from telebot import types
import random
import time

# =========================================
# TOKEN
# =========================================

TOKEN = "8818405158:AAHWwdPc3qLRXjWvO4eOFQf-0L4MSaA80Ow"

bot = telebot.TeleBot(TOKEN)

# =========================================
# CONFIG
# =========================================

MAPS = [
    "Sandstone",
    "Province",
    "Zone 9",
    "Rust",
    "Sakura"
]

MODES = {
    "1x1": 2,
    "2x2": 4,
    "5x5": 10
}

START_ELO = 200
START_LEVEL = 1

ADMINS = [
    "fastukteamm",
    "b3bl1",
    "psiblades_ez"
]

# =========================================
# DATABASE
# =========================================

users = {}

queues = {
    "1x1": [],
    "2x2": [],
    "5x5": []
}

parties = {}

matches = {}

waiting_nick = []
waiting_gameid = []
waiting_username = []

waiting_warn = []
waiting_mute = []
waiting_broadcast = []

# =========================================
# CREATE USER
# =========================================

def create_user(user):

    if user.id not in users:

        users[user.id] = {
            "id": user.id,
            "tg_name": user.first_name,
            "telegram_username": "None",
            "game_name": "None",
            "game_id": "None",
            "elo": 0,
            "level": 0,
            "calibration": 0,
            "wins": 0,
            "loses": 0,
            "kills": 0,
            "deaths": 0,
            "warns": 0,
            "party": None,
            "muted": 0
        }

# =========================================
# ADMIN CHECK
# =========================================

def is_admin(user):

    if user.username is None:
        return False

    return user.username.lower() in [
        x.lower() for x in ADMINS
    ]

# =========================================
# HELPERS
# =========================================

def kd(user_id):

    data = users[user_id]

    deaths = data["deaths"]

    if deaths <= 0:
        deaths = 1

    return round(
        data["kills"] / deaths,
        2
    )

def wl(user_id):

    data = users[user_id]

    loses = data["loses"]

    if loses <= 0:
        loses = 1

    return round(
        data["wins"] / loses,
        2
    )

def main_menu():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row("🎮 Играть")
    kb.row("👤 Профиль", "📊 Топы")
    kb.row("👥 Пати")
    kb.row("🛠 Админ панель")

    return kb

def play_menu():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row("🎮 1x1", "🔥 2x2")
    kb.row("🏆 5x5")
    kb.row("⬅ Назад")

    return kb

def leave_button(mode):

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "❌ Выйти из лобби",
            callback_data=f"leave_{mode}"
        )
    )

    return kb

def lobby_text(mode, players):

    need = MODES[mode]

    text = f"""
🛡 Standfade
🎮 ЛОББИ {mode}

Игроков в лобби: {len(players)}/{need}

Игроки в лобби:
"""

    for player in players:

        calibration = users[
            player["id"]
        ]["calibration"]

        text += f"\n🔒 {player['name']} ({calibration}/5)"

    text += "\n\n🔥 Fastuk Faceit"

    return text

# =========================================
# START
# =========================================

@bot.message_handler(commands=["start"])
def start(message):

    create_user(message.from_user)

    waiting_nick.append(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "✍ Введи ник как в игре"
    )

# =========================================
# REGISTER NICK
# =========================================

@bot.message_handler(
    func=lambda m:
    m.from_user.id in waiting_nick
)
def register_nick(message):

    users[message.from_user.id][
        "game_name"
    ] = message.text

    waiting_nick.remove(
        message.from_user.id
    )

    waiting_gameid.append(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "🆔 Введи ID как в игре"
    )

# =========================================
# REGISTER GAME ID
# =========================================

@bot.message_handler(
    func=lambda m:
    m.from_user.id in waiting_gameid
)
def register_gameid(message):

    users[message.from_user.id][
        "game_id"
    ] = message.text

    waiting_gameid.remove(
        message.from_user.id
    )

    waiting_username.append(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "📱 Введи свой @username"
    )

# =========================================
# REGISTER USERNAME
# =========================================

@bot.message_handler(
    func=lambda m:
    m.from_user.id in waiting_username
)
def register_username(message):

    users[message.from_user.id][
        "telegram_username"
    ] = message.text

    waiting_username.remove(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        f"""
✅ Регистрация завершена

👤 Ник: {users[message.from_user.id]['game_name']}
🆔 ID: {users[message.from_user.id]['game_id']}
📱 Username: {message.text}
""",
        reply_markup=main_menu()
    )

# =========================================
# PLAY MENU
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "🎮 Играть"
)
def play(message):

    bot.send_message(
        message.chat.id,
        "🎮 Выбери режим",
        reply_markup=play_menu()
    )

@bot.message_handler(
    func=lambda m:
    m.text == "⬅ Назад"
)
def back(message):

    bot.send_message(
        message.chat.id,
        "🛡 Главное меню",
        reply_markup=main_menu()
    )

# =========================================
# PROFILE
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "👤 Профиль"
)
def profile(message):

    data = users[message.from_user.id]

    if data["calibration"] >= 5:

        elo_text = data["elo"]
        lvl_text = data["level"]

    else:

        elo_text = "🔒 Locked"
        lvl_text = "🔒 Locked"

    text = f"""
👤 ПРОФИЛЬ

🎮 Ник: {data['game_name']}
🆔 ID: {data['game_id']}
📱 Username: {data['telegram_username']}

🎯 KD: {kd(message.from_user.id)}
🏆 W/L: {wl(message.from_user.id)}

⚔ Побед: {data['wins']}
💀 Поражений: {data['loses']}

🔫 Убийств: {data['kills']}
☠ Смертей: {data['deaths']}

📈 Калибровка: {data['calibration']}/5

🏅 LVL: {lvl_text}
💎 ELO: {elo_text}

⚠ Варны: {data['warns']}
"""

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================
# TOPS
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "📊 Топы"
)
def tops(message):

    top = sorted(
        users.values(),
        key=lambda x: x["elo"],
        reverse=True
    )

    text = "🏆 ТОП ИГРОКОВ\n"

    pos = 1

    for user in top[:10]:

        text += f"\n{pos}. {user['game_name']} — {user['elo']} ELO"

        pos += 1

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================
# PARTY SYSTEM
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "👥 Пати"
)
def party_menu(message):

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "➕ Создать пати",
            callback_data="create_party"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "❌ Выйти из пати",
            callback_data="leave_party"
        )
    )

    bot.send_message(
        message.chat.id,
        "👥 PARTY SYSTEM",
        reply_markup=kb
    )

@bot.callback_query_handler(
    func=lambda c:
    c.data == "create_party"
)
def create_party(call):

    user_id = call.from_user.id

    if users[user_id]["party"] is not None:

        bot.answer_callback_query(
            call.id,
            "❌ Ты уже в пати"
        )

        return

    party_id = random.randint(
        10000,
        99999
    )

    parties[party_id] = {
        "leader": user_id,
        "players": [user_id]
    }

    users[user_id]["party"] = party_id

    bot.edit_message_text(
        f"""
👥 ПАТИ СОЗДАНО

🆔 PARTY ID: {party_id}

/party {party_id}
""",
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(
    func=lambda c:
    c.data == "leave_party"
)
def leave_party(call):

    user_id = call.from_user.id

    party_id = users[user_id]["party"]

    if party_id is None:
        return

    if party_id in parties:

        if user_id in parties[party_id]["players"]:

            parties[party_id]["players"].remove(
                user_id
            )

    users[user_id]["party"] = None

    bot.answer_callback_query(
        call.id,
        "❌ Ты вышел из пати"
    )

# =========================================
# JOIN PARTY
# =========================================

@bot.message_handler(commands=["party"])
def join_party(message):

    args = message.text.split()

    if len(args) < 2:
        return

    party_id = int(args[1])

    if party_id not in parties:

        bot.send_message(
            message.chat.id,
            "❌ Пати не найдено"
        )

        return

    parties[party_id]["players"].append(
        message.from_user.id
    )

    users[message.from_user.id]["party"] = party_id

    bot.send_message(
        message.chat.id,
        "✅ Ты вошёл в пати"
    )

# =========================================
# QUEUE
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text in [
        "🎮 1x1",
        "🔥 2x2",
        "🏆 5x5"
    ]
)
def queue(message):

    mode_map = {
        "🎮 1x1": "1x1",
        "🔥 2x2": "2x2",
        "🏆 5x5": "5x5"
    }

    mode = mode_map[message.text]

    players = queues[mode]

    for p in players:

        if p["id"] == message.from_user.id:

            bot.send_message(
                message.chat.id,
                "❌ Ты уже в лобби"
            )

            return

    players.append({
        "id": message.from_user.id,
        "name": users[
            message.from_user.id
        ]["game_name"]
    })

    text = lobby_text(
        mode,
        players
    )

    for player in players:

        bot.send_message(
            player["id"],
            text,
            reply_markup=leave_button(mode)
        )

    if len(players) >= MODES[mode]:

        match_players = players[
            :MODES[mode]
        ]

        queues[mode] = players[
            MODES[mode]:
        ]

        start_confirmation(
            mode,
            match_players
        )

# =========================================
# LEAVE LOBBY
# =========================================

@bot.callback_query_handler(
    func=lambda c:
    c.data.startswith("leave_")
)
def leave_lobby(call):

    mode = call.data.split("_")[1]

    user_id = call.from_user.id

    players = queues[mode]

    queues[mode] = [
        x for x in players
        if x["id"] != user_id
    ]

    bot.answer_callback_query(
        call.id,
        "❌ Ты вышел из лобби"
    )

# =========================================
# CONFIRM MATCH
# =========================================

def start_confirmation(mode, players):

    match_id = random.randint(
        1000,
        9999
    )

    matches[match_id] = {
        "mode": mode,
        "players": players,
        "confirmed": []
    }

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "✅ ПОДТВЕРДИТЬ",
            callback_data=f"confirm_{match_id}"
        )
    )

    for player in players:

        bot.send_message(
            player["id"],
            f"""
🔥 MATCH FOUND

🎮 Режим: {mode}

Нажми подтвердить
""",
            reply_markup=kb
        )

@bot.callback_query_handler(
    func=lambda c:
    c.data.startswith("confirm_")
)
def confirm(call):

    match_id = int(
        call.data.split("_")[1]
    )

    user_id = call.from_user.id

    data = matches[match_id]

    if user_id not in data["confirmed"]:

        data["confirmed"].append(
            user_id
        )

    current = len(
        data["confirmed"]
    )

    need = len(
        data["players"]
    )

    bot.answer_callback_query(
        call.id,
        f"{current}/{need}"
    )

    if current >= need:

        start_match(match_id)

# =========================================
# START MATCH
# =========================================

def start_match(match_id):

    data = matches[match_id]

    players = data["players"]

    captain1 = random.choice(players)

    captain2 = random.choice(
        [x for x in players if x != captain1]
    )

    final_map = random.choice(MAPS)

    text = f"""
🔥 ВСЕ ПОДТВЕРДИЛИ

👑 Капитан 1: {captain1['name']}
👑 Капитан 2: {captain2['name']}

🗺 Карта: {final_map}

🔑 Lobby: STAND-{random.randint(100000,999999)}
"""

    for player in players:

        bot.send_message(
            player["id"],
            text
        )

        if users[player["id"]]["calibration"] < 5:

            users[player["id"]]["calibration"] += 1

            if users[player["id"]]["calibration"] >= 5:

                users[player["id"]]["elo"] = START_ELO
                users[player["id"]]["level"] = START_LEVEL

# =========================================
# ADMIN PANEL
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "🛠 Админ панель"
)
def admin_panel(message):

    if not is_admin(message.from_user):

        bot.send_message(
            message.chat.id,
            "❌ Нет доступа"
        )

        return

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row("⚠ Варн")
    kb.row("🔇 Мут")
    kb.row("📢 Рассылка")
    kb.row("📊 Статистика")
    kb.row("⬅ Назад")

    bot.send_message(
        message.chat.id,
        "🛠 ADMIN PANEL",
        reply_markup=kb
    )

# =========================================
# ADMIN STATS
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "📊 Статистика"
)
def admin_stats(message):

    if not is_admin(message.from_user):
        return

    text = f"""
📊 СТАТИСТИКА

👥 Пользователей: {len(users)}

🎮 1x1: {len(queues['1x1'])}
🔥 2x2: {len(queues['2x2'])}
🏆 5x5: {len(queues['5x5'])}

👥 Пати: {len(parties)}
🎯 Матчи: {len(matches)}
"""

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================
# WARN
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "⚠ Варн"
)
def warn_panel(message):

    if not is_admin(message.from_user):
        return

    waiting_warn.append(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "🆔 Введи ID игрока"
    )

@bot.message_handler(
    func=lambda m:
    m.from_user.id in waiting_warn
)
def process_warn(message):

    try:

        user_id = int(message.text)

        if user_id not in users:

            bot.send_message(
                message.chat.id,
                "❌ Игрок не найден"
            )

            return

        users[user_id]["warns"] += 1

        bot.send_message(
            message.chat.id,
            "⚠ Варн выдан"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Ошибка"
        )

    waiting_warn.remove(
        message.from_user.id
    )

# =========================================
# MUTE
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "🔇 Мут"
)
def mute_panel(message):

    if not is_admin(message.from_user):
        return

    waiting_mute.append(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "Пример:\n123456789 30"
    )

@bot.message_handler(
    func=lambda m:
    m.from_user.id in waiting_mute
)
def process_mute(message):

    try:

        args = message.text.split()

        user_id = int(args[0])
        minutes = int(args[1])

        users[user_id]["muted"] = (
            time.time() + minutes * 60
        )

        bot.send_message(
            message.chat.id,
            f"🔇 Мут {minutes} минут"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Ошибка"
        )

    waiting_mute.remove(
        message.from_user.id
    )

# =========================================
# BROADCAST
# =========================================

@bot.message_handler(
    func=lambda m:
    m.text == "📢 Рассылка"
)
def broadcast_panel(message):

    if not is_admin(message.from_user):
        return

    waiting_broadcast.append(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "✍ Введи текст"
    )

@bot.message_handler(
    func=lambda m:
    m.from_user.id in waiting_broadcast
)
def process_broadcast(message):

    success = 0

    for user_id in users:

        try:

            bot.send_message(
                user_id,
                f"""
📢 РАССЫЛКА

{message.text}
"""
            )

            success += 1

        except:
            pass

    bot.send_message(
        message.chat.id,
        f"✅ Отправлено: {success}"
    )

    waiting_broadcast.remove(
        message.from_user.id
    )

# =========================================
# RUN
# =========================================

print("STANDFADE FACEIT STARTED")

bot.infinity_polling()
