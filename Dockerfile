## Базовый образ для сборки
FROM python:3.9.10-slim as builder

WORKDIR /usr/src/app

# Запрещаем Python писать файлы .pyc на диск
ENV PYTHONDONTWRITEBYTECODE 1
# Запрещает Python буферизовать stdout и stderr
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y curl gnupg lsb-release

RUN curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list

# Устанавливаем зависимости
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc tzdata netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Проверка оформления кода
RUN pip install --upgrade pip
RUN pip install flake8
COPY . .
# RUN flake8 --ignore=W503,E501,F401 .

# Установка зависимостей
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


## СБОРКА
FROM python:3.9.10-slim

# Создаем не root пользователя для проекта
#RUN mkdir -p /home/app
#RUN adduser --system --group app

# Создаем необходимые директории
#ENV HOME=/home/app
#ENV APP_HOME=/home/app/src
ENV APP_HOME=/root/src
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Устанавливаем зависимости
RUN apt-get update && \
    apt-get install --no-install-recommends -y netcat tzdata redis-server
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

#RUN service redis-server status

ENV TZ="Europe/Moscow"

# Копируем файлы проекта
COPY . $APP_HOME

# Изменяем владельца файлов на app
#RUN chown -R app:app $APP_HOME

#RUN chmod -R 777 /etc/redis
#RUN chmod -R 777 /var/log/redis

# Переключаемся на пользователя app
#USER app

# Запускаем скрипт
#RUN redis-server /etc/redis/redis.conf
#CMD [ "redis-server", "/etc/redis/redis.conf", ";", "python", "/root/src/bot.py" ]
CMD [ "sh", "/root/src/bot.sh" ]
