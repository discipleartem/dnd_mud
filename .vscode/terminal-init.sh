#!/bin/bash
# Активация виртуального окружения .venv для терминала VS Code

# Определяем путь к корню проекта (директория выше .vscode)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    
    # Стилизация приглашения через переменные цветов
    GREEN=$'\033[32m'
    BLUE=$'\033[34m'
    YELLOW=$'\033[33m'
    RESET=$'\033[0m'
    
    # Устанавливаем PS1 с цветами напрямую
    export PS1="${GREEN}(.venv)${RESET} ${BLUE}tomas@cooffee:${RESET}${YELLOW}~/WORK/dnd_mud${RESET}$ "
fi
