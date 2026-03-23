# Gmail Analyzer — Claude Code Plugin

> [Русская версия](README.ru.md)

A Claude Code plugin that extends Gmail MCP with 5-category email classification, auto-tagging, search, and label management. Also includes a standalone CLI (`main.py`).

## Plugin Installation

### 1. Clone and copy skills

```bash
git clone https://github.com/axisrow/claude_code_gmail_plugin.git
cd claude_code_gmail_plugin
cp -r skills/* ~/.claude/skills/
mkdir -p ~/.claude/scripts/gmail-analyzer
cp scripts/*.py gmail_client.py ~/.claude/scripts/gmail-analyzer/
```

### 2. Install dependencies

```bash
pip install -r requirements.txt            # Google API libs
```

For the standalone CLI (`main.py`):
```bash
pip install -r requirements-sdk.txt        # + claude-agent-sdk, openpyxl
```

### 3. Gmail Authorization (pick one)

The client auto-selects an available backend: gcloud ADC → gws CLI → credentials.json.

#### Option A: gcloud ADC (recommended)

1. Install [gcloud CLI](https://cloud.google.com/sdk/docs/install):

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

   Open a **new terminal** after installation.

2. Initialize gcloud:
   ```bash
   gcloud init
   ```

3. Create an OAuth Client ID in [Google Cloud Console](https://console.cloud.google.com/apis/credentials), download it as `client_secret.json` into the project root.

4. Authenticate:
   ```bash
   gcloud auth application-default login \
     --client-id-file=client_secret.json \
     --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/gmail.modify
   ```

#### Option B: gws CLI

```bash
npm install -g @googleworkspace/cli
gws auth setup
gws auth login -s gmail
```

Verify: `gws gmail +triage --max 3`

#### Option C: credentials.json

1. Create an OAuth Client ID in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Download `credentials.json` into the project root
3. A browser window will open for authorization on first run

## Plugin Skills

Once installed, 4 skills are available:

| Skill | Command | Description |
|---|---|---|
| Email Analysis | `/analyze-emails` | 5-category classification (Personal, Newsletter, Important, Noise, Spam) |
| Search | `/search-emails <query>` | Gmail query syntax search (`from:`, `subject:`, `newer_than:`) |
| Labels | `/manage-labels` | List, create, delete labels |
| Auto-tag | `/auto-tag` | Analyze + suggest tags + confirm + apply |

Skills use Gmail MCP for reading and scripts from `scripts/` for writing (applying labels).

## Standalone CLI (optional, requires requirements-sdk.txt)

`main.py` runs independently from Claude Code via Claude Agent SDK:

```bash
python main.py                          # analysis only (INBOX)
python main.py --tag                    # analysis + auto-tagging
python main.py --tag --label CATEGORY_X # tag emails with a specific label
python main.py --label CATEGORY_UPDATES # analyze emails with a specific label
python main.py top [N]                  # top-N newsletter senders
python main.py mark <Label_ID> <emails> # label emails from specific senders
python main.py mark-query <Label_ID> <q># label emails by Gmail query
python main.py analyze-senders [N]      # sender analysis by sector (Excel)
python main.py labels                   # show all labels
python main.py labels create Name       # create a custom label
python main.py labels delete Label_XX   # delete a custom label
```

> **Important:** `main.py` cannot be run inside a Claude Code session (nested sessions are not allowed). Use a regular terminal.

> **Re-authorization:** if you previously used the `gmail.readonly` scope, delete `token.json` and re-authorize with `gmail.modify`.
