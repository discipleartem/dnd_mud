# Установка и настройка проекта

## Требования

- Python 3.13+
- Node.js 20+ (для MCP серверов)
- cursor-agent CLI (для мульти-агентности)

## Установка Python зависимостей

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## Установка Node.js

### Через nvm (рекомендуется)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
```

### Проверка установки

```bash
node --version  # Должно быть v20.x.x
npm --version
npx --version
```

## Установка cursor-agent

```bash
# Установка через официальный установщик
curl https://cursor.com/install -fsS | bash

# Добавьте в PATH (если не добавлено автоматически)
export PATH="$HOME/.local/bin:$PATH"
# Или добавьте в ~/.bashrc:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Проверка установки
cursor-agent --version
```

## Настройка MCP серверов

См. [Настройка MCP и мульти-агентности](./mcp-setup.md)

## Проверка установки

```bash
# Запустите скрипт проверки конфигурации
./scripts/test_mcp_config.sh
```

## Следующие шаги

- [Аутентификация cursor-agent](./authentication.md)
- [Быстрый старт](./quick-start.md)
- [Документация по MCP](../mcp/README.md)

