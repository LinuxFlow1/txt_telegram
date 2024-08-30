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
