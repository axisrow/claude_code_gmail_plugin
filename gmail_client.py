"""Gmail client с тремя бэкендами: ADC (приоритет), gws CLI, credentials.json (fallback)."""

import base64
import json
import os
import re
import subprocess
import time
from collections import Counter


# ── Общие утилиты ──


def _decode_body(payload):
    """Extract plain text body from email payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    elif mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            result = _decode_body(part)
            if result:
                return result

    return ""


def _get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _build_email_dict(msg_data, headers, payload):
    body = _decode_body(payload)
    if len(body) > 2000:
        body = body[:2000] + "\n... [обрезано]"
    return {
        "id": msg_data.get("id", ""),
        "labelIds": msg_data.get("labelIds", []),
        "subject": _get_header(headers, "Subject") or "(без темы)",
        "from": _get_header(headers, "From") or "(неизвестен)",
        "date": _get_header(headers, "Date") or "(дата неизвестна)",
        "body": body.strip() or "(пустое письмо)",
    }


# ── gws CLI бэкенд ──


def _try_gws():
    """Проверяет доступность gws CLI и авторизацию."""
    try:
        result = subprocess.run(
            ["gws", "gmail", "+triage", "--max", "1", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _run_gws(*args):
    """Run a gws command and return parsed JSON output."""
    cmd = ["gws", *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "gws CLI не найден. Установите: npm install -g @googleworkspace/cli"
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip()
        if "auth" in stderr.lower() or "login" in stderr.lower():
            raise RuntimeError(
                "gws не авторизован. Выполните: gws auth login -s gmail"
            )
        raise RuntimeError(f"Ошибка gws: {stderr or e.stdout.strip()}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()


def get_emails_via_gws(max_results=10, label_ids=None):
    """Получение писем через gws CLI."""
    if label_ids is None:
        label_ids = ["INBOX"]
    params = json.dumps({
        "userId": "me",
        "maxResults": max_results,
        "labelIds": label_ids,
    })
    list_data = _run_gws("gmail", "users", "messages", "list", "--params", params)

    messages = list_data.get("messages", []) if isinstance(list_data, dict) else []
    emails = []

    for msg in messages:
        msg_id = msg["id"]
        get_params = json.dumps({"userId": "me", "id": msg_id, "format": "full"})
        msg_data = _run_gws("gmail", "users", "messages", "get", "--params", get_params)

        if not isinstance(msg_data, dict):
            continue

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])
        emails.append(_build_email_dict(msg_data, headers, payload))

    return emails


# ── ADC бэкенд (gcloud Application Default Credentials) ──


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def _try_adc():
    """Проверяет доступность Application Default Credentials."""
    try:
        from google.auth import default
        creds, _ = default(scopes=SCOPES)
        return creds
    except Exception:
        return None


# ── google-api-python-client бэкенд (credentials.json) ──


TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def _has_credentials():
    """Проверяет наличие credentials.json для Google API."""
    return os.path.exists(CREDENTIALS_PATH)


def _authenticate():
    """Авторизация через credentials.json (legacy OAuth flow)."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


def get_emails_via_api(max_results=10, creds=None, label_ids=None):
    """Получение писем через google-api-python-client."""
    from googleapiclient.discovery import build

    if creds is None:
        creds = _authenticate()
    service = build("gmail", "v1", credentials=creds)

    if label_ids is None:
        label_ids = ["INBOX"]

    result = service.users().messages().list(
        userId="me", maxResults=max_results, labelIds=label_ids
    ).execute()

    messages = result.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])
        emails.append(_build_email_dict(msg_data, headers, payload))

    return emails


# ── Общий service хелпер ──


def _get_service(creds=None):
    """Получить Gmail API service (переиспользуемый хелпер)."""
    from googleapiclient.discovery import build

    if creds is None:
        creds = _try_adc()
    if creds is None:
        if _has_credentials():
            creds = _authenticate()
        else:
            raise RuntimeError("Нет доступных credentials для Gmail API.")
    return build("gmail", "v1", credentials=creds)


# ── Управление тегами (labels) ──


def get_labels():
    """Список всех тегов. Returns: [{"id": ..., "name": ..., "type": ...}]"""
    service = _get_service()
    result = service.users().labels().list(userId="me").execute()
    labels = result.get("labels", [])
    return [{"id": lb["id"], "name": lb["name"], "type": lb.get("type", "")} for lb in labels]


def create_label(name):
    """Создать пользовательский тег. Returns: {"id": ..., "name": ...}"""
    service = _get_service()
    body = {
        "name": name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    result = service.users().labels().create(userId="me", body=body).execute()
    return {"id": result["id"], "name": result["name"]}


def delete_label(label_id):
    """Удалить пользовательский тег."""
    service = _get_service()
    service.users().labels().delete(userId="me", id=label_id).execute()


def modify_message_labels(message_id, add_label_ids=None, remove_label_ids=None):
    """Добавить/убрать теги у письма."""
    service = _get_service()
    body = {}
    if add_label_ids:
        body["addLabelIds"] = add_label_ids
    if remove_label_ids:
        body["removeLabelIds"] = remove_label_ids
    service.users().messages().modify(userId="me", id=message_id, body=body).execute()


# ── Публичный API ──


def _extract_email(from_header):
    """Извлечь email-адрес из заголовка From."""
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1).lower()
    # Если нет угловых скобок, вернуть как есть (trimmed)
    return from_header.strip().lower()


def get_top_senders(max_results=5000, query="category:promotions OR category:updates -is:starred -is:important"):
    """Собрать топ отправителей через Batch API. Returns: Counter {email: count}."""
    service = _get_service()

    # 1. Собираем все ID через пагинацию
    message_ids = []
    page_token = None
    while len(message_ids) < max_results:
        page_size = min(500, max_results - len(message_ids))
        result = service.users().messages().list(
            userId="me", q=query, maxResults=page_size, pageToken=page_token
        ).execute()
        messages = result.get("messages", [])
        if not messages:
            break
        message_ids.extend(msg["id"] for msg in messages)
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if not message_ids:
        return Counter()

    print(f"Найдено {len(message_ids)} писем. Загрузка отправителей...")

    # 2. Batch API — до 100 запросов за batch, с retry при ошибках
    sender_counter = Counter()
    failed_ids = []

    def _run_batch(ids_to_fetch):
        """Выполнить batch-запросы, вернуть список ID с ошибками."""
        batch_errors = []
        for batch_start in range(0, len(ids_to_fetch), 100):
            batch_ids = ids_to_fetch[batch_start:batch_start + 100]
            batch = service.new_batch_http_request()

            def _callback(request_id, response, exception, _mid=None):
                if exception:
                    batch_errors.append(_mid)
                    return
                headers = response.get("payload", {}).get("headers", [])
                from_header = _get_header(headers, "From")
                if from_header:
                    sender_counter[_extract_email(from_header)] += 1

            for msg_id in batch_ids:
                batch.add(
                    service.users().messages().get(
                        userId="me", id=msg_id, format="metadata", metadataHeaders=["From"]
                    ),
                    callback=lambda rid, resp, exc, mid=msg_id: _callback(rid, resp, exc, _mid=mid),
                )

            batch.execute()

            done = min(batch_start + 100, len(ids_to_fetch))
            print(f"  {done}/{len(ids_to_fetch)}", end="\r")
            time.sleep(0.1)  # пауза между батчами для rate limiting

        print()
        return batch_errors

    failed_ids = _run_batch(message_ids)

    # Retry неудачных запросов (до 2 попыток)
    for attempt in range(2):
        if not failed_ids:
            break
        print(f"  Повтор {len(failed_ids)} неудачных запросов (попытка {attempt + 1})...")
        time.sleep(2)
        failed_ids = _run_batch(failed_ids)

    if failed_ids:
        print(f"  ({len(failed_ids)} писем не удалось загрузить)")

    return sender_counter


def get_subjects_by_senders(senders, max_per_sender=10, query_base="category:promotions OR category:updates"):
    """Получить темы писем для каждого отправителя. Returns: {email: [subject, ...]}."""
    service = _get_service()

    # Фаза 1: собираем message_id для каждого отправителя
    msg_id_to_sender = {}
    for i, sender in enumerate(senders, 1):
        query = f"from:{sender} ({query_base})"
        try:
            result = service.users().messages().list(
                userId="me", q=query, maxResults=max_per_sender
            ).execute()
        except Exception:
            continue
        for msg in result.get("messages", []):
            msg_id_to_sender[msg["id"]] = sender
        if i % 10 == 0:
            print(f"  Сбор ID: {i}/{len(senders)}", end="\r")
            time.sleep(0.05)

    print(f"  Сбор ID: {len(senders)}/{len(senders)} — найдено {len(msg_id_to_sender)} писем")

    if not msg_id_to_sender:
        return {}

    # Фаза 2: batch-загрузка тем
    subjects = {sender: [] for sender in senders}
    all_ids = list(msg_id_to_sender.keys())
    failed_ids = []

    def _run_batch(ids_to_fetch):
        batch_errors = []
        for batch_start in range(0, len(ids_to_fetch), 100):
            batch_ids = ids_to_fetch[batch_start:batch_start + 100]
            batch = service.new_batch_http_request()

            def _callback(request_id, response, exception, _mid=None):
                if exception:
                    batch_errors.append(_mid)
                    return
                headers = response.get("payload", {}).get("headers", [])
                subj = _get_header(headers, "Subject") or "(без темы)"
                sender = msg_id_to_sender.get(_mid)
                if sender:
                    subjects[sender].append(subj)

            for msg_id in batch_ids:
                batch.add(
                    service.users().messages().get(
                        userId="me", id=msg_id, format="metadata", metadataHeaders=["Subject"]
                    ),
                    callback=lambda rid, resp, exc, mid=msg_id: _callback(rid, resp, exc, _mid=mid),
                )

            batch.execute()
            done = min(batch_start + 100, len(ids_to_fetch))
            print(f"  Загрузка тем: {done}/{len(ids_to_fetch)}", end="\r")
            time.sleep(0.1)

        print()
        return batch_errors

    failed_ids = _run_batch(all_ids)

    for attempt in range(2):
        if not failed_ids:
            break
        print(f"  Повтор {len(failed_ids)} неудачных запросов (попытка {attempt + 1})...")
        time.sleep(2)
        failed_ids = _run_batch(failed_ids)

    return {k: v for k, v in subjects.items() if v}


def label_messages_from_senders(label_id, senders, query_base="category:promotions OR category:updates"):
    """Пометить все письма от указанных отправителей заданным тегом. Returns: {sender: count}."""
    service = _get_service()
    results = {}

    for sender in senders:
        query = f"from:{sender} ({query_base})"
        message_ids = []
        page_token = None

        # Собираем все ID через пагинацию
        while True:
            resp = service.users().messages().list(
                userId="me", q=query, maxResults=500, pageToken=page_token
            ).execute()
            messages = resp.get("messages", [])
            if not messages:
                break
            message_ids.extend(msg["id"] for msg in messages)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        if not message_ids:
            results[sender] = 0
            continue

        # Batch modify по 100
        for batch_start in range(0, len(message_ids), 100):
            batch_ids = message_ids[batch_start:batch_start + 100]
            service.users().messages().batchModify(
                userId="me",
                body={"ids": batch_ids, "addLabelIds": [label_id]},
            ).execute()

        results[sender] = len(message_ids)

    return results


def label_messages_by_query(label_id, query):
    """Пометить все письма по произвольному Gmail search query. Returns: int (кол-во помеченных)."""
    service = _get_service()
    message_ids = []
    page_token = None

    while True:
        resp = service.users().messages().list(
            userId="me", q=query, maxResults=500, pageToken=page_token
        ).execute()
        messages = resp.get("messages", [])
        if not messages:
            break
        message_ids.extend(msg["id"] for msg in messages)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    if not message_ids:
        return 0

    # Batch modify по 100
    for batch_start in range(0, len(message_ids), 100):
        batch_ids = message_ids[batch_start:batch_start + 100]
        service.users().messages().batchModify(
            userId="me",
            body={"ids": batch_ids, "addLabelIds": [label_id]},
        ).execute()
        done = min(batch_start + 100, len(message_ids))
        print(f"  {done}/{len(message_ids)}", end="\r")

    print()
    return len(message_ids)


def get_emails(max_results=10, label_ids=None):
    """Получить письма: ADC → gws CLI → credentials.json → ошибка."""
    adc_creds = _try_adc()
    if adc_creds:
        print("Используется бэкенд: gcloud ADC")
        return get_emails_via_api(max_results, creds=adc_creds, label_ids=label_ids)

    if _try_gws():
        print("Используется бэкенд: gws CLI")
        return get_emails_via_gws(max_results, label_ids=label_ids)

    if _has_credentials():
        print("Используется бэкенд: credentials.json (OAuth)")
        return get_emails_via_api(max_results, label_ids=label_ids)

    raise RuntimeError(
        "Не удалось подключиться к Gmail. Настройте один из вариантов:\n"
        "  1) gcloud ADC: gcloud auth application-default login "
        "--client-id-file=client_secret.json "
        "--scopes=https://www.googleapis.com/auth/cloud-platform,"
        "https://www.googleapis.com/auth/gmail.modify\n"
        "  2) gws CLI: npm install -g @googleworkspace/cli && gws auth login -s gmail\n"
        "  3) credentials.json: создайте OAuth Client ID в GCP Console, "
        "скачайте credentials.json в корень проекта"
    )
