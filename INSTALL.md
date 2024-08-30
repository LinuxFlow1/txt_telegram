# Установка и настройка для Termux

Следующие команды помогут вам настроить Termux для работы с этим проектом:

```bash
# Обновление пакетов Termux
pkg update && pkg upgrade

# Установка Python и PyPy3
pkg install python pypy python2 pypy2 python3 pypy3

# Установка pip для Python и PyPy3
python -m ensurepip --upgrade
pypy3 -m ensurepip --upgrade

# Установка основных инструментов разработки
pkg install git build-essential clang libffi openssl

# Установка Telethon и других зависимостей
pypy3 -m pip install telethon

# замените
 в файле main.py строки api_id и api_hash свои данные!

# как узнать данные api_id и api_hash?

для этого перейдите на сайт my.telegram.org создайте свое приложение (введите любое название приложения) после появится ваши данные!
если не поняли найдите туториал в YouTube.
