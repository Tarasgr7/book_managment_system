FROM python:3.12-slim


# Встановлюємо робочу директорію
WORKDIR /app 

# Копіюємо файл залежностей
COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Копіюємо весь код додатку
COPY . /app

# Вказуємо команду запуску
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
