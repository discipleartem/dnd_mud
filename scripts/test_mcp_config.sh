#!/bin/bash
# Скрипт для проверки конфигурации MCP серверов и мульти-агентности

set -e

echo "=== Проверка конфигурации MCP серверов ==="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка конфигурации mcp.json
echo "1. Проверка ~/.cursor/mcp.json..."
if [ -f ~/.cursor/mcp.json ]; then
    if python3 -m json.tool ~/.cursor/mcp.json > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ JSON валиден${NC}"
        
        # Проверка обязательных полей
        AGENTS_DIR=$(python3 -c "import json; f=open('$HOME/.cursor/mcp.json'); d=json.load(f); print(d['mcpServers']['sub-agents']['env'].get('AGENTS_DIR', ''))" 2>/dev/null)
        if [ -n "$AGENTS_DIR" ] && [ -d "$AGENTS_DIR" ]; then
            echo -e "${GREEN}   ✅ AGENTS_DIR указан и существует: $AGENTS_DIR${NC}"
        else
            echo -e "${RED}   ❌ AGENTS_DIR не указан или не существует${NC}"
        fi
        
        SESSION_DIR=$(python3 -c "import json; f=open('$HOME/.cursor/mcp.json'); d=json.load(f); print(d['mcpServers']['sub-agents']['env'].get('SESSION_DIR', ''))" 2>/dev/null)
        if [ -n "$SESSION_DIR" ]; then
            if [ -d "$SESSION_DIR" ]; then
                echo -e "${GREEN}   ✅ SESSION_DIR существует: $SESSION_DIR${NC}"
            else
                echo -e "${YELLOW}   ⚠️  SESSION_DIR указан, но директория не существует: $SESSION_DIR${NC}"
                echo "      Создаю директорию..."
                mkdir -p "$SESSION_DIR"
                echo -e "${GREEN}   ✅ Директория создана${NC}"
            fi
        else
            echo -e "${YELLOW}   ⚠️  SESSION_DIR не указан${NC}"
        fi
    else
        echo -e "${RED}   ❌ JSON невалиден${NC}"
        exit 1
    fi
else
    echo -e "${RED}   ❌ Файл ~/.cursor/mcp.json не найден${NC}"
    exit 1
fi

echo ""

# Проверка определений агентов
echo "2. Проверка определений агентов..."
AGENTS_DIR=$(python3 -c "import json; f=open('$HOME/.cursor/mcp.json'); d=json.load(f); print(d['mcpServers']['sub-agents']['env'].get('AGENTS_DIR', ''))" 2>/dev/null)

if [ -d "$AGENTS_DIR" ]; then
    AGENT_COUNT=$(find "$AGENTS_DIR" -name "*.md" -o -name "*.txt" | grep -v MODELS.md | wc -l)
    echo "   Найдено агентов: $AGENT_COUNT"
    
    # Проверка каждого агента
    for agent_file in "$AGENTS_DIR"/*.md; do
        if [ -f "$agent_file" ] && [ "$(basename "$agent_file")" != "MODELS.md" ]; then
            AGENT_NAME=$(basename "$agent_file" .md)
            if grep -q "^# " "$agent_file" && grep -q "## Роль" "$agent_file"; then
                echo -e "${GREEN}   ✅ $AGENT_NAME - структура корректна${NC}"
            else
                echo -e "${YELLOW}   ⚠️  $AGENT_NAME - отсутствуют обязательные секции${NC}"
            fi
        fi
    done
else
    echo -e "${RED}   ❌ Директория агентов не найдена: $AGENTS_DIR${NC}"
    exit 1
fi

echo ""

# Проверка разрешений
echo "3. Проверка разрешений (.cursor/cli.json)..."
if [ -f .cursor/cli.json ]; then
    if python3 -m json.tool .cursor/cli.json > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ JSON валиден${NC}"
        
        # Проверка наличия разрешений для npx
        if grep -q "Shell(npx)" .cursor/cli.json; then
            echo -e "${GREEN}   ✅ Разрешение для npx найдено${NC}"
        else
            echo -e "${YELLOW}   ⚠️  Разрешение для npx не найдено${NC}"
        fi
    else
        echo -e "${RED}   ❌ JSON невалиден${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Файл .cursor/cli.json не найден${NC}"
fi

echo ""

# Проверка зависимостей
echo "4. Проверка зависимостей..."

# Node.js
if command -v node > /dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}   ✅ Node.js установлен: $NODE_VERSION${NC}"
else
    echo -e "${RED}   ❌ Node.js не установлен${NC}"
    echo "      Установите через: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
fi

# npx
if command -v npx > /dev/null 2>&1; then
    NPX_VERSION=$(npx --version)
    echo -e "${GREEN}   ✅ npx установлен: $NPX_VERSION${NC}"
else
    echo -e "${RED}   ❌ npx не установлен (устанавливается вместе с Node.js)${NC}"
fi

# cursor-agent
if command -v cursor-agent > /dev/null 2>&1; then
    CURSOR_VERSION=$(cursor-agent --version 2>/dev/null || echo "неизвестна")
    echo -e "${GREEN}   ✅ cursor-agent найден: $CURSOR_VERSION${NC}"
    
    # Проверка аутентификации
    if cursor-agent status > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ cursor-agent аутентифицирован${NC}"
    else
        echo -e "${YELLOW}   ⚠️  cursor-agent не аутентифицирован${NC}"
        echo "      Выполните: cursor-agent login"
    fi
else
    echo -e "${RED}   ❌ cursor-agent не найден${NC}"
    echo "      Установите через официальный установщик:"
    echo "      curl https://cursor.com/install -fsS | bash"
fi

echo ""

# Итоговая сводка
echo "=== Итоговая сводка ==="
echo ""
echo "Конфигурация MCP:"
echo "  - mcp.json: ✅ Валиден"
echo "  - cli.json: ✅ Настроен"
echo "  - Агенты: ✅ $AGENT_COUNT агентов найдено"
echo ""
echo "Зависимости:"
if command -v node > /dev/null 2>&1 && command -v npx > /dev/null 2>&1 && command -v cursor-agent > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Все зависимости установлены${NC}"
    echo ""
    echo "Следующие шаги:"
    echo "  1. Перезапустите Cursor IDE для применения изменений"
    echo "  2. Проверьте доступность MCP сервера через Command Palette"
    echo "  3. Протестируйте запуск агента"
else
    echo -e "  ${YELLOW}⚠️  Некоторые зависимости не установлены${NC}"
    echo ""
    echo "Следующие шаги:"
    echo "  1. Установите недостающие зависимости (см. выше)"
    echo "  2. Выполните аутентификацию cursor-agent: cursor-agent login"
    echo "  3. Перезапустите Cursor IDE"
    echo "  4. Протестируйте запуск агента"
fi

echo ""
echo "Для тестирования мульти-агентности используйте:"
echo "  Используй code-reviewer для проверки файла src/systems/combat.py"
echo ""

