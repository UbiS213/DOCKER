FROM python:3.11-slim

WORKDIR /app

# Создаём системную группу и пользователя без пароля и домашней папки
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /bin/false appuser

# Копируем и устанавливаем зависимости (от root — это нормально на этапе сборки)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Меняем владельца файлов приложения на appuser
RUN chown -R appuser:appgroup /app

# Переключаемся на non-root пользователя для всех следующих инструкций
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
