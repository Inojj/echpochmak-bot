# Используем официальный образ Python с необходимой версией
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем необходимые пакеты Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота в контейнер
COPY echpochmak_bot.py .

# Создаём директорию для базы данных
RUN mkdir /app/data

# Определяем команду для запуска бота
CMD ["python", "echpochmak_bot.py"]
