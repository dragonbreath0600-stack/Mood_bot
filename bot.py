import telebot
from telebot import types
from database import Database
import analyzer

TOKEN = '8793567629:AAHUQz4lv1zi6TzZ5amfGse-NAmfq3h4mRc'
bot = telebot.TeleBot(TOKEN)
db = Database()

user_state = {}

def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Записать день"), types.KeyboardButton("Статистика"))
    markup.add(types.KeyboardButton("История"), types.KeyboardButton("Настройки"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    db.add_user(message.from_user.id)
    bot.send_message(message.chat.id,
        "Привет! Я помогу отслеживать твое настроение и продуктивность.\n\n"
        "/add — записать день\n"
        "/stats — статистика\n"
        "/history — история\n"
        "/settings — настройки\n"
        "/clear — очистить данные\n"
        "/help — справка",
        reply_markup=main_markup())

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id,
        "Каждый день записывай:\n- Настроение (1-5)\n- Часы работы/учебы\n- Часы сна\n\nПотом смотри статистику и инсайты.")

@bot.message_handler(commands=['add'])
def add_entry(message):
    markup = types.InlineKeyboardMarkup(row_width=5)
    markup.add(*[types.InlineKeyboardButton(str(i), callback_data=f'mood_{i}') for i in range(1, 6)])
    bot.send_message(message.chat.id, "Оцени свое настроение от 1 до 5, где 1 — ужасно, 5 — отлично.", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("За неделю", callback_data='stats_week'),
        types.InlineKeyboardButton("За месяц", callback_data='stats_month'),
        types.InlineKeyboardButton("Мои инсайты", callback_data='stats_insights'),
        types.InlineKeyboardButton("График", callback_data='stats_chart')
    )
    bot.send_message(message.chat.id, "Что хочешь узнать?", reply_markup=markup)

@bot.message_handler(commands=['history'])
def history_cmd(message):
    rows = db.get_entries(message.from_user.id, 7)
    if not rows:
        bot.send_message(message.chat.id, "Записей пока нет.")
        return
    text = "Последние записи:\n\n"
    for r in rows:
        text += f"{r[0]} | Настроение: {r[1]} | Работа: {r[2]}ч | Сон: {r[3]}ч"
        if r[4]:
            text += f" | {r[4]}"
        text += "\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['settings'])
def settings_cmd(message):
    user_state[message.from_user.id] = 'settings_reminder'
    bot.send_message(message.chat.id, "Введите время напоминания в формате ЧЧ:ММ (например, 21:00):")

@bot.message_handler(commands=['clear'])
def clear_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Да, удалить", callback_data='clear_yes'),
        types.InlineKeyboardButton("Отмена", callback_data='clear_no')
    )
    bot.send_message(message.chat.id, "Удалить все твои данные?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id

    if call.data.startswith('mood_'):
        user_state[uid] = {'step': 'work', 'mood': int(call.data.split('_')[1])}
        markup = types.InlineKeyboardMarkup(row_width=5)
        markup.add(*[types.InlineKeyboardButton(f"{h}ч", callback_data=f'work_{h}') for h in [0.5, 1, 2, 4]])
        markup.add(types.InlineKeyboardButton("Другое", callback_data='work_other'))
        bot.edit_message_text("Сколько часов потратил на работу/учебу?", cid, mid, reply_markup=markup)

    elif call.data.startswith('work_'):
        if uid not in user_state or not isinstance(user_state.get(uid), dict):
            bot.answer_callback_query(call.id, "Начни заново — нажми /add")
            return
        val = call.data.split('_')[1]
        if val == 'other':
            user_state[uid]['step'] = 'work_input'
            bot.edit_message_text("Введи количество часов работы/учебы:", cid, mid)
        else:
            user_state[uid]['work'] = float(val)
            user_state[uid]['step'] = 'sleep'
            markup = types.InlineKeyboardMarkup(row_width=5)
            markup.add(*[types.InlineKeyboardButton(f"{h}ч", callback_data=f'sleep_{h}') for h in [6, 7, 8, 9]])
            markup.add(types.InlineKeyboardButton("Другое", callback_data='sleep_other'))
            bot.edit_message_text("Сколько часов спал?", cid, mid, reply_markup=markup)

    elif call.data.startswith('sleep_'):
        if uid not in user_state or not isinstance(user_state.get(uid), dict):
            bot.answer_callback_query(call.id, "Начни заново — нажми /add")
            return
        val = call.data.split('_')[1]
        if val == 'other':
            user_state[uid]['step'] = 'sleep_input'
            bot.edit_message_text("Введи количество часов сна:", cid, mid)
        else:
            user_state[uid]['sleep'] = float(val)
            user_state[uid]['step'] = 'comment'
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Пропустить", callback_data='skip_comment'))
            bot.edit_message_text("Добавь комментарий или нажми Пропустить:", cid, mid, reply_markup=markup)

    elif call.data == 'skip_comment':
        state = user_state.pop(uid, {})
        db.add_entry(uid, state.get('mood'), state.get('work'), state.get('sleep'))
        bot.edit_message_text("Записано! Хорошего дня.", cid, mid)

    elif call.data.startswith('stats_'):
        period = call.data.split('_')[1]
        if period == 'week':
            text = analyzer.weekly_stats(db, uid)
            bot.send_message(cid, text)
        elif period == 'month':
            text = analyzer.monthly_stats(db, uid)
            bot.send_message(cid, text)
        elif period == 'insights':
            text = analyzer.insights(db, uid)
            bot.send_message(cid, text)
        elif period == 'chart':
            buf = analyzer.build_chart(db, uid)
            if buf:
                bot.send_photo(cid, buf)
            else:
                bot.send_message(cid, "Недостаточно данных для графика.")

    elif call.data == 'clear_yes':
        db.clear_user_data(uid)
        bot.edit_message_text("Данные удалены.", cid, mid)

    elif call.data == 'clear_no':
        bot.edit_message_text("Отменено.", cid, mid)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    uid = message.from_user.id
    state = user_state.get(uid)
    text = message.text

    if text == "Записать день":
        add_entry(message)
    elif text == "Статистика":
        stats_cmd(message)
    elif text == "История":
        history_cmd(message)
    elif text == "Настройки":
        settings_cmd(message)
    elif isinstance(state, dict) and state.get('step') in ('work_input', 'sleep_input'):
        try:
            val = float(text.replace(',', '.'))
            if state['step'] == 'work_input':
                user_state[uid]['work'] = val
                user_state[uid]['step'] = 'sleep'
                markup = types.InlineKeyboardMarkup(row_width=5)
                markup.add(*[types.InlineKeyboardButton(f"{h}ч", callback_data=f'sleep_{h}') for h in [6, 7, 8, 9]])
                markup.add(types.InlineKeyboardButton("Другое", callback_data='sleep_other'))
                bot.send_message(message.chat.id, "Сколько часов спал?", reply_markup=markup)
            else:
                user_state[uid]['sleep'] = val
                user_state[uid]['step'] = 'comment'
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Пропустить", callback_data='skip_comment'))
                bot.send_message(message.chat.id, "Добавь комментарий или нажми Пропустить:", reply_markup=markup)
        except ValueError:
            bot.send_message(message.chat.id, "Введи число.")
    elif isinstance(state, dict) and state.get('step') == 'comment':
        s = user_state.pop(uid, {})
        db.add_entry(uid, s.get('mood'), s.get('work'), s.get('sleep'), text)
        bot.send_message(message.chat.id, "Записано! Хорошего дня.")
    elif state == 'settings_reminder':
        db.set_reminder(uid, text)
        user_state.pop(uid, None)
        bot.send_message(message.chat.id, f"Время напоминания установлено: {text}")

if __name__ == '__main__':
    print('Бот запущен')
    bot.polling()
