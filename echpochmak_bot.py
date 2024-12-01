import os
import logging
import sqlite3
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatMember

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Путь к базе данных
DB_PATH = os.path.join('data', 'mentions.db')

# Список всех форм слова "эчпочмак"
ECHPOCHMAK_FORMS = [
    'эчпочмак', 'эчпочмака', 'эчпочмаку', 'эчпочмаком', 'эчпочмаке',
    'эчпочмаки', 'эчпочмаков', 'эчпочмакам', 'эчпочмаками', 'эчпочмаках'
]

# Список всех форм слова "учпочмак"
UCHPOCHMAK_FORMS = [
    'учпочмак', 'учпочмака', 'учпочмаку', 'учпочмаком', 'учпочмаке',
    'учпочмаки', 'учпочмаков', 'учпочмакам', 'учпочмаками', 'учпочмаках'
]

# Объединённый список всех форм
ALL_FORMS = set(ECHPOCHMAK_FORMS + UCHPOCHMAK_FORMS)


# Функции для работы с базой данных
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS mentions (chat_id INTEGER PRIMARY KEY, count INTEGER)')
    conn.commit()
    conn.close()


def get_mention_count(chat_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT count FROM mentions WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def increment_mention_count(chat_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO mentions (chat_id, count) VALUES (?, 0)', (chat_id,))
    cursor.execute('UPDATE mentions SET count = count + 1 WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()


# Функция для проверки прав администратора
def is_user_admin(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    member = context.bot.get_chat_member(chat_id, user_id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]


def start(update, context):
    update.message.reply_text('Привет! Я отслеживаю упоминания слов "эчпочмак" и "учпочмак" в этом чате.')


def count_mentions(update, context):
    message_text = update.message.text.lower()
    chat_id = update.effective_chat.id

    # Разбиваем сообщение на слова
    words = re.findall(r'\b\w+\b', message_text)

    # Проверяем наличие ключевых слов
    for word in words:
        if word in ALL_FORMS:
            increment_mention_count(chat_id)
            break  # Можно выйти из цикла после первого найденного слова


def get_count(update, context):
    chat_id = update.effective_chat.id
    current_count = get_mention_count(chat_id)
    update.message.reply_text(f'В этом чате слова "эчпочмак" и "учпочмак" были упомянуты {current_count} раз(а).')


def main():
    # Инициализация базы данных
    init_db()

    # Получение токена из переменной окружения
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logging.error('Переменная окружения TELEGRAM_BOT_TOKEN не установлена')
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('echpochmak', get_count))

    # Обработчик сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, count_mentions))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
