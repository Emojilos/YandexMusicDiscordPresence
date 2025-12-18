#!/bin/bash

# Yandex Music Discord Rich Presence Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -z "$DISCORD_CLIENT_ID" ]; then
    echo "❌ Ошибка: переменная окружения DISCORD_CLIENT_ID не установлена"
    echo ""
    echo "Установите её командой:"
    echo "  export DISCORD_CLIENT_ID=\"ваш_client_id\""
    echo ""
    echo "Или добавьте в ~/.zshrc:"
    echo "  export DISCORD_CLIENT_ID=\"ваш_client_id\""
    exit 1
fi

if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Сервер уже запущен на порту 8080"
    echo "Остановите его перед запуском нового экземпляра"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Ошибка: Python3 не найден"
    exit 1
fi

if ! python3 -c "import pypresence" 2>/dev/null; then
    echo "⚠️  Зависимости не установлены. Устанавливаю..."
    pip3 install -r requirements.txt
fi

echo "🚀 Запускаю Yandex Music Discord Rich Presence сервер..."
echo "📡 Сервер будет доступен на http://localhost:8080"
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

python3 server.py

