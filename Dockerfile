# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .
# Для сети и отладки
RUN apt-get update && apt-get install -y curl iputils-ping && rm -rf /var/lib/apt/lists/*

# Запускаем uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]