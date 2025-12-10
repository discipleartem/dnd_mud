#!/bin/bash
# Скрипт для аутентификации cursor-agent

set -e

echo "🔐 Аутентификация cursor-agent для MCP агентов"
echo ""

# Проверка установки cursor-agent
if ! command -v cursor-agent &> /dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v cursor-agent &> /dev/null; then
        echo "❌ cursor-agent не найден в PATH"
        echo "Убедитесь, что cursor-agent установлен:"
        echo "  curl https://cursor.com/install -fsS | bash"
        exit 1
    fi
fi

echo "✅ cursor-agent найден: $(which cursor-agent)"
echo "   Версия: $(cursor-agent --version)"
echo ""

# Проверка текущего статуса
echo "📋 Проверка текущего статуса аутентификации..."
STATUS=$(cursor-agent status 2>&1 | grep -i "logged\|not logged" || echo "unknown")

if echo "$STATUS" | grep -qi "logged"; then
    echo "✅ Уже аутентифицирован!"
    cursor-agent status
    exit 0
fi

echo "⚠️  Требуется аутентификация"
echo ""
echo "Выберите способ аутентификации:"
echo "1) Интерактивный login (откроет браузер)"
echo "2) Использование API ключа (вручную добавить в ~/.cursor/mcp.json)"
echo ""
read -p "Выберите вариант (1 или 2): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Запуск интерактивного login..."
        echo "   Откроется браузер для аутентификации"
        echo ""
        cursor-agent login
        echo ""
        echo "✅ Проверка статуса после login..."
        cursor-agent status
        ;;
    2)
        echo ""
        echo "📝 Для использования API ключа:"
        echo "1. Получите API ключ на https://cursor.com/settings"
        echo "2. Добавьте в ~/.cursor/mcp.json:"
        echo ""
        echo '   "env": {'
        echo '     "CURSOR_API_KEY": "ваш_api_ключ",'
        echo '     ...'
        echo '   }'
        echo ""
        echo "3. Перезапустите Cursor IDE"
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "✅ Готово! После аутентификации перезапустите Cursor IDE."

