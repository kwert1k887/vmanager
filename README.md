# vmanager

CLI-утилита для управления виртуальными машинами через VMmanager API.

## Возможности

- Список виртуальных машин с подробной информацией
- Создание новых ВМ (поиск/создание аккаунта, выбор узла, назначение IP)
- Просмотр IP-адресов и их статуса

## Установка

```bash
pip install requests python-dotenv
```

## Настройка

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

```
VM_BASE_URL=https://your-hosting-panel.com
VM_EMAIL=admin@example.com
VM_PASSWORD=your_password
```

## Запуск

```bash
python main.py
```

## Структура

```
vmanager/
├── main.py       # Точка входа, CLI-меню
├── client.py     # VMClient — API клиент
├── config.py     # Загрузка конфигурации из .env
├── .env.example  # Пример конфигурации
└── .gitignore
```
