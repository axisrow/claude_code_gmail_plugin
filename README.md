# Gmail Analyzer

Анализ входящих писем Gmail с помощью Claude AI. Получает письма через gcloud ADC, `gws` CLI или `google-api-python-client`, отправляет Claude на анализ — важность, резюме, требуется ли ответ. При указании флага `--tag` Claude также предлагает пользовательские теги (с подтверждением).

## Установка

### 1. Python-зависимости

```bash
pip install -r requirements.txt
```

### 2. Авторизация Gmail (один из вариантов)

#### Вариант A: gcloud ADC

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

Проверьте, что всё работает:

```bash
gws gmail +triage --max 3
```

#### Вариант C: credentials.json

1. Создайте OAuth Client ID в [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Скачайте `credentials.json` в корень проекта
3. При первом запуске откроется браузер для авторизации

Программа автоматически выберет доступный бэкенд: gcloud ADC → gws CLI → credentials.json.

## Запуск

```bash
python main.py                          # только анализ (INBOX)
python main.py --tag                    # анализ + автотегирование
python main.py --tag --label CATEGORY_X # тегирование писем с конкретным тегом
python main.py --label CATEGORY_UPDATES # анализ писем с конкретным тегом
python main.py labels                   # показать все теги
python main.py labels create Имя        # создать пользовательский тег
python main.py labels delete Label_XX   # удалить пользовательский тег
```

Анализ загружает 10 последних писем, Claude оценивает важность, даёт резюме. С флагом `--tag` также предлагает теги — перед применением запрашивается подтверждение.

> **Переавторизация:** если ранее использовался scope `gmail.readonly`, нужно переавторизоваться с `gmail.modify`. Удалите `token.json` если существует.
