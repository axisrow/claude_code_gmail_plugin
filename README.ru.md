# Gmail Analyzer — Claude Code Plugin

> [English version](README.md)

Плагин для Claude Code, расширяющий Gmail MCP: 5-категорийная классификация писем, авто-тегирование, поиск, управление метками. Также включает standalone CLI (`main.py`).

## Установка плагина

### 1. Клонировать и скопировать скиллы

```bash
git clone https://github.com/axisrow/claude_code_gmail_plugin.git
cd claude_code_gmail_plugin
cp -r skills/* ~/.claude/skills/
mkdir -p ~/.claude/scripts/gmail-analyzer
cp scripts/*.py gmail_client.py ~/.claude/scripts/gmail-analyzer/
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt            # Google API libs
```

Для standalone CLI (`main.py`) дополнительно:
```bash
pip install -r requirements-sdk.txt        # + claude-agent-sdk, openpyxl
```

### 3. Авторизация Gmail (один из вариантов)

Программа автоматически выберет доступный бэкенд: gcloud ADC → gws CLI → credentials.json.

#### Вариант A: gcloud ADC (рекомендуется)

1. Установите [gcloud CLI](https://cloud.google.com/sdk/docs/install):

   **macOS (Apple Silicon):**
   ```bash
   curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-darwin-arm.tar.gz
   tar -xf google-cloud-cli-darwin-arm.tar.gz
   ./google-cloud-sdk/install.sh
   ```

   **macOS (Intel):**
   ```bash
   curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-darwin-x86_64.tar.gz
   tar -xf google-cloud-cli-darwin-x86_64.tar.gz
   ./google-cloud-sdk/install.sh
   ```

   После установки откройте **новый терминал**.

2. Инициализируйте gcloud:
   ```bash
   gcloud init
   ```

3. Создайте OAuth Client ID в [Google Cloud Console](https://console.cloud.google.com/apis/credentials), скачайте как `client_secret.json` в корень проекта.

4. Авторизуйтесь:
   ```bash
   gcloud auth application-default login \
     --client-id-file=client_secret.json \
     --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/gmail.modify
   ```

#### Вариант B: gws CLI

```bash
npm install -g @googleworkspace/cli
gws auth setup
gws auth login -s gmail
```

Проверьте: `gws gmail +triage --max 3`

#### Вариант C: credentials.json

1. Создайте OAuth Client ID в [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Скачайте `credentials.json` в корень проекта
3. При первом запуске откроется браузер для авторизации

## Скиллы плагина

После подключения доступны 4 скилла:

| Скилл | Команда | Описание |
|---|---|---|
| Анализ почты | `/analyze-emails` | 5-категорийная классификация (Личное, Рассылка, Важное, Шум, Мусор) |
| Поиск | `/search-emails <query>` | Поиск по Gmail query syntax (`from:`, `subject:`, `newer_than:`) |
| Метки | `/manage-labels` | Список, создание, удаление меток |
| Авто-теги | `/auto-tag` | Анализ + предложение тегов + подтверждение + применение |

Скиллы используют Gmail MCP для чтения и скрипты из `scripts/` для записи (применение меток).

## Standalone CLI (optional, требует requirements-sdk.txt)

`main.py` работает отдельно от Claude Code через Claude Agent SDK:

```bash
python main.py                          # только анализ (INBOX)
python main.py --tag                    # анализ + автотегирование
python main.py --tag --label CATEGORY_X # тегирование писем с конкретным тегом
python main.py --label CATEGORY_UPDATES # анализ писем с конкретным тегом
python main.py top [N]                  # топ-N отправителей рассылок
python main.py mark <Label_ID> <emails> # пометить письма от отправителей
python main.py mark-query <Label_ID> <q># пометить письма по Gmail query
python main.py analyze-senders [N]      # анализ отправителей по секторам (Excel)
python main.py labels                   # показать все теги
python main.py labels create Имя        # создать пользовательский тег
python main.py labels delete Label_XX   # удалить пользовательский тег
```

> **Важно:** `main.py` нельзя запускать внутри сессии Claude Code (вложенные сессии запрещены). Используйте обычный терминал.

> **Переавторизация:** если ранее использовался scope `gmail.readonly`, удалите `token.json` и авторизуйтесь заново с `gmail.modify`.
