from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import datetime
import random
import json
import os

import os
TOKEN = os.getenv("BOT_TOKEN")

# Файл для сохранения данных
DATA_FILE = "user_data.json"

# Загрузка данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение данных в файл
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загружаем данные при старте
user_data = load_data()

def main_menu():
    return ReplyKeyboardMarkup([
        ['📝 Новая запись', '📊 Статистика'],
        ['🎭 Паттерны', '📚 Воспоминания'],
        ['🌿 Гербарий', '🎵 Саундтрек']
    ], resize_keyboard=True)

# Детектор эмоций
def detect_emotions(text):
    emotions_map = {
        'радость': ['рад', 'счастлив', 'весел', 'ура', 'хорошо', 'отлично', 'прекрасно', 'люблю', 'нравится'],
        'грусть': ['грустн', 'печал', 'тоск', 'плохо', 'обид', 'жаль', 'плач', 'слез'],
        'тревога': ['тревог', 'волнен', 'боюсь', 'страх', 'нерв', 'пережив', 'опасен', 'паник'],
        'спокойствие': ['споко', 'мир', 'тих', 'умиротворен', 'расслабл', 'безмятеж'],
        'гнев': ['зло', 'гнев', 'раздраж', 'бесит', 'ярост', 'злюсь', 'ненависть'],
        'гордость': ['горд', 'горжусь', 'победа', 'успех', 'достиг', 'молодец'],
        'любовь': ['любл', 'обожаю', 'симпатия', 'привязан', 'дорог', 'мил'],
        'удивление': ['удивл', 'неожидан', 'сюрприз', 'вот это да', 'невероятн'],
        'благодарность': ['спасибо', 'благодарн', 'признател', 'ценю'],
        'надежда': ['надежда', 'верю', 'ожидаю', 'мечта', 'хочу']
    }
    
    detected = []
    text_lower = text.lower()
    for emotion, keywords in emotions_map.items():
        if any(keyword in text_lower for keyword in keywords):
            detected.append(emotion)
    
    return detected if detected else ['неопределено']

# Команда /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user.first_name,
            'entries': [],
            'emotions_collected': set(),
            'registration_date': datetime.datetime.now().strftime("%d.%m.%Y"),
            'level': 1
        }
        save_data(user_data)
    
    await update.message.reply_text(
        f"🖋 *Чернильное пятно оживает...*\n\n"
        f"Приветствую, {user.first_name}! Я — Архивариус Эмоций.\n"
        f"Хранитель твоих мыслей и чувств.\n\n"
        f"*Твой свиток начат {user_data[user_id]['registration_date']}*\n"
        f"Выбери действие:",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# Команда /help
async def help_command(update: Update, context: CallbackContext):
    help_text = """
📖 *Свиток знаний Архивариуса*

*Основные команды:*
/start - Начать работу с Архивариусом
/help - Помощь и инструкции
/record - Создать новую запись
/stats - Показать статистику
/pattern - Найти паттерны в настроениях
/memory - Случайное воспоминание
/herobarium - Мой гербарий эмоций
/soundtrack - Саундтрек недели
/chaos - Архивный произвол
/profile - Мой профиль
/reset - Начать заново

*Или используй кнопки меню!*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Команда /record
async def record_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🖋 *Пергамент и чернила готовы!*\n\n"
        "Опиши свои мысли и эмоции...",
        parse_mode='Markdown'
    )

# Команда /stats
async def stats_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data or not user_data[user_id]['entries']:
        await update.message.reply_text("📊 *Архив пуст*\n\nСоздай первую запись!", parse_mode='Markdown')
        return
    
    user = user_data[user_id]
    entries = user['entries']
    
    # Анализ эмоций
    emotion_count = {}
    for entry in entries:
        for emotion in entry.get('emotions', []):
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
    
    total_entries = len(entries)
    total_days = len(set(entry['date'] for entry in entries))
    most_common_emotion = max(emotion_count.items(), key=lambda x: x[1]) if emotion_count else ('нет данных', 0)
    
    stats_text = f"""
📈 *Статистика восприятия*

📖 **Общая картина:**
Записей в архиве: {total_entries}
Дней активности: {total_days}
Уровень осознанности: {user['level']}

🎭 **Эмоциональный ландшафт:**
Всего эмоций: {len(user['emotions_collected'])}
Самая частая: {most_common_emotion[0]} ({most_common_emotion[1]} раз)

💫 *Продолжаем исследовать!*
    """
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Команда /pattern
async def pattern_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data or len(user_data[user_id]['entries']) < 5:
        await update.message.reply_text(
            "🔍 *Нужно больше данных!*\n\n"
            "Создай хотя бы 5 записей для поиска паттернов.",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(
        "🔍 *Анализирую узоры в твоем эмоциональном полотне...*\n\n"
        "Пока паттерны только начинают проявляться.\n"
        "Продолжай вести записи для более глубоких инсайтов! 🧩",
        parse_mode='Markdown'
    )

# Команда /memory
async def memory_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data or not user_data[user_id]['entries']:
        await update.message.reply_text("📜 *Архив пуст*\n\nВернись с первыми записями!", parse_mode='Markdown')
        return
    
    entries = user_data[user_id]['entries']
    memory = random.choice(entries)
    
    memory_text = f"""
📜 *Достаю случайный свиток...*

*«{memory['text']}»*

⏰ *{memory['date']} {memory['time']}*
💫 *Эмоции:* {', '.join(memory.get('emotions', ['неопределены']))}

*Этот момент был важен?*
    """
    await update.message.reply_text(memory_text, parse_mode='Markdown')

# Команда /herobarium
async def herobarium_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            'name': update.effective_user.first_name,
            'entries': [],
            'emotions_collected': set(),
            'registration_date': datetime.datetime.now().strftime("%d.%m.%Y"),
            'level': 1
        }
    
    emotions = user_data[user_id]['emotions_collected']
    emotion_count = len(emotions)
    
    herobarium_text = f"""
🌸 *Твой Гербарий Эмоций*

🌿 **Собрано эмоций:** {emotion_count}/15

{', '.join(f'• {emotion}' for emotion in emotions) if emotions else '• Коллекция пуста'}

🎯 **Цель:** Собери все 15 основных эмоций!
💫 *Каждая новая запись приближает к цели*
    """
    await update.message.reply_text(herobarium_text, parse_mode='Markdown')

# Команда /soundtrack
async def soundtrack_command(update: Update, context: CallbackContext):
    soundtracks = [
        "🎵 Саундтрек спокойствия\nhttps://music.yandex.ru/track/38274614?utm_source=web&utm_medium=copy_link",
        "🎶 Для поднятия настроения\nhttps://music.yandex.ru/track/72875163?utm_source=web&utm_medium=copy_link",
        "🎧 Атмосферные звуки\nhttps://music.yandex.ru/track/128072878?utm_source=web&utm_medium=copy_link",
        "🎼 Классика для медитации\nhttps://music.yandex.ru/track/132292476?utm_source=web&utm_medium=copy_link"
    ]
    
    await update.message.reply_text(
        random.choice(soundtracks) + "\n\nНаслаждайся! 🎧"
    )
# Команда /chaos
async def chaos_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data or not user_data[user_id]['entries']:
        await update.message.reply_text("🌀 *Архив пуст!*\n\nСоздай хаос из записей!", parse_mode='Markdown')
        return
    
    entries = user_data[user_id]['entries']
    
    # Берем случайную запись и немного "хаоса"
    memory = random.choice(entries)
    chaos_phrases = [
        "А этот момент ты помнишь?",
        "Вот это внезапно!",
        "Случайность? Не думаю...",
        "Вселенная шепчет тебе...",
        "Забытый фрагмент твоей истории"
    ]
    
    chaos_text = f"""
🌀 *Архивный произвол активирован!*

*«{memory['text']}»*

⏰ *Из глубины архива*
💫 {random.choice(chaos_phrases)}
    """
    await update.message.reply_text(chaos_text, parse_mode='Markdown')

# Команда /profile
async def profile_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user = update.effective_user
    
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user.first_name,
            'entries': [],
            'emotions_collected': set(),
            'registration_date': datetime.datetime.now().strftime("%d.%m.%Y"),
            'level': 1
        }
    
    user_data_entry = user_data[user_id]
    entries_count = len(user_data_entry['entries'])
    emotions_count = len(user_data_entry['emotions_collected'])
    
    profile_text = f"""
👤 *Твой профиль*

📛 Имя: {user.first_name}
📅 В архиве с: {user_data_entry['registration_date']}
📖 Записей: {entries_count}
🌿 Эмоций собрано: {emotions_count}
🎯 Уровень: {user_data_entry['level']}

💫 *Продолжай самопознание!*
    """
    await update.message.reply_text(profile_text, parse_mode='Markdown')

# Команда /reset
async def reset_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id in user_data:
        del user_data[user_id]
        save_data(user_data)
    
    await update.message.reply_text(
        "🔄 *Архив очищен!*\n\n"
        "Ты начинаешь с чистого листа.\n"
        "Используй /start для начала новой истории.",
        parse_mode='Markdown'
    )

# Обработка обычных сообщений (записей)
async def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # Инициализация пользователя если нужно
    if user_id not in user_data:
        user_data[user_id] = {
            'name': update.effective_user.first_name,
            'entries': [],
            'emotions_collected': set(),
            'registration_date': datetime.datetime.now().strftime("%d.%m.%Y"),
            'level': 1
        }
    
    # Обработка кнопок меню
    if text == '📝 Новая запись':
        await update.message.reply_text(
            "🖋 *Пергамент и чернила готовы!*\n\n"
            "Опиши свои мысли и эмоции...",
            parse_mode='Markdown'
        )
    elif text == '📊 Статистика':
        await stats_command(update, context)
    elif text == '🎭 Паттерны':
        await pattern_command(update, context)
    elif text == '📚 Воспоминания':
        await memory_command(update, context)
    elif text == '🌿 Гербарий':
        await herobarium_command(update, context)
    elif text == '🎵 Саундтрек':
        await soundtrack_command(update, context)
    else:
        # Сохраняем запись
        emotions = detect_emotions(text)
        entry = {
            'text': text,
            'time': datetime.datetime.now().strftime("%H:%M"),
            'date': datetime.datetime.now().strftime("%d.%m.%Y"),
            'emotions': emotions
        }
        
        user_data[user_id]['entries'].append(entry)
        user_data[user_id]['emotions_collected'].update(emotions)
        
        # Повышаем уровень при достижении порогов
        entries_count = len(user_data[user_id]['entries'])
        if entries_count >= 20:
            user_data[user_id]['level'] = 3
        elif entries_count >= 10:
            user_data[user_id]['level'] = 2
        
        save_data(user_data)
        
        await update.message.reply_text(
            f"💫 *Запись сохранена под символом '{random.choice(['Крылатый ключ', 'Сияющий свиток', 'Вечный пергамент'])}'*\n\n"
            f"*Обнаружены эмоции:* {', '.join(emotions) if emotions else 'пока не определил'}\n"
            f"*Всего записей:* {len(user_data[user_id]['entries'])}\n"
            f"*Уровень:* {user_data[user_id]['level']}\n\n"
            f"Продолжаем исследовать? 🗺️",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем все команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("record", record_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("pattern", pattern_command))
    application.add_handler(CommandHandler("memory", memory_command))
    application.add_handler(CommandHandler("herobarium", herobarium_command))
    application.add_handler(CommandHandler("soundtrack", soundtrack_command))
    application.add_handler(CommandHandler("chaos", chaos_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Обработчик обычных сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ БОТ ЗАПУЩЕН! Архивариус Эмоций готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    main()
