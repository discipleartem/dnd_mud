#!/bin/bash
# Init для integrated terminal: обычный bashrc + тихое .venv + цветной PS1.
# --init-file заменяет загрузку ~/.bashrc, поэтому подключаем его явно.

if [ -f "$HOME/.bashrc" ]; then
    # shellcheck source=/dev/null
    source "$HOME/.bashrc"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    # activate не должен трогать PS1 — оформление задаём сами
    export VIRTUAL_ENV_DISABLE_PROMPT=1
    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/.venv/bin/activate"

    # (.venv) зелёный · user@host синий · путь жёлтый
    PS1='\[\033[32m\](.venv)\[\033[0m\] \[\033[34m\]\u@\h\[\033[0m\]:\[\033[33m\]\w\[\033[0m\]\$ '
fi
