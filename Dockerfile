# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда для запуска бота
CMD ["python", "main.py"]