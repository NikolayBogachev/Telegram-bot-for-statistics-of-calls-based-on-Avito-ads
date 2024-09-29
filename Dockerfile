# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY database/ /app/database/
COPY TG/ /app/TG/
COPY .env /app/
COPY config.py /app/
COPY main_bot.py /app/

# Установка переменной окружения
ENV PYTHONUNBUFFERED=1

# Команда для запуска бота
CMD ["python", "main_bot.py"]