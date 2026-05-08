# ============================================================
# FIX PROMPTS — Restore correct mailbox routing in mail_engine
#
# ROOT CAUSE: The rewrite used Graph API for both personal and
# shared mailboxes. This is wrong.
#
# CORRECT ARCHITECTURE (from the original src/ code):
#   Personal mailbox → Token.generate_token() (HTTPKerberosAuth)
#                    → Graph API proxy (/me/... endpoints)
#                    → src/helpers/fetch_token.py Token class
#
#   Shared mailbox  → get_exchange_account() (ExchangeCredentials)
#                    → exchangelib Account object
#                    → src/helpers/fetch_token.py ExchangeCredentials class
#                    → src/helpers/common.py get_exchange_account()
#
# TOKEN FILE STRUCTURE (src/helpers/fetch_token.py):
#   class Token:
#       @staticmethod
#       def generate_token() -> str:   # returns access token string
#           # uses HTTPKerberosAuth internally
#           # calls the corporate Graph API proxy
#
#   class ExchangeCredentials:
#       # used by get_exchange_account() in common.py
#       # provides credentials for exchangelib connectivity
#
# DO NOT touch src/ files. Read them, do not modify them.
# All fixes go into app/services/mail_engine/ only.
# ============================================================


# ============================================================
# FIX 1 — Rewrite auth.py to expose both auth methods correctly
# ============================================================

Open app/services/auth.py (or create it if it does not exist).
Replace the entire file with the following.

IMPORTANT: Read src/helpers/fetch_token.py BEFORE writing
any code in this file. The goal is to expose a clean wrapper
around the two existing classes — do not reimplement them.

```python
"""
app/services/auth.py

Thin wrappers around the existing auth classes in src/helpers/fetch_token.py.
Exposes two functions:
  get_graph_headers()    — for personal mailbox (Graph API via Kerberos)
  get_exchange_account() — for shared mailbox (exchangelib via EWS)

DO NOT reimplement Token or ExchangeCredentials here.
Import and call the originals from src/.
"""
import sys
import logging
from pathlib import Path
from functools import lru_cache

# Add src/ to path so we can import the existing helpers
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

logger = logging.getLogger(__name__)


def get_graph_headers() -> dict:
    """
    Get HTTP headers for Graph API calls (personal mailbox).

    Uses Token.generate_token() from src/helpers/fetch_token.py
    which authenticates via HTTPKerberosAuth against the
    corporate Graph API proxy.

    Returns:
        dict with 'Authorization' and 'Content-Type' headers
    """
    try:
        from helpers.fetch_token import Token
        access_token = Token.generate_token()
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
    except Exception as e:
        logger.error(f"Failed to generate Graph API token: {e}")
        raise


def get_exchange_account(mailbox_address: str):
    """
    Get an authenticated exchangelib Account object (shared mailbox).

    Uses get_exchange_account() from src/helpers/common.py which
    uses ExchangeCredentials from src/helpers/fetch_token.py.

    Args:
        mailbox_address: The shared mailbox email address

    Returns:
        exchangelib Account object ready for use
    """
    try:
        from helpers.common import get_exchange_account as _get_account
        account = _get_account(mailbox_address)
        return account
    except Exception as e:
        logger.error(f"Failed to connect to shared mailbox '{mailbox_address}': {e}")
        raise
```

After writing, run this quick smoke test (no server needed):

```python
# test_auth.py — run from project root
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

# Test 1: Graph API token (personal mailbox)
try:
    from app.services.auth import get_graph_headers
    headers = get_graph_headers()
    print("✓ Graph headers obtained:", list(headers.keys()))
except Exception as e:
    print(f"✗ Graph token failed: {e}")
    print("  This is expected if Kerberos is not available in this environment")

# Test 2: Exchange account (shared mailbox)
try:
    from app.services.auth import get_exchange_account
    # Use a real shared mailbox address from your .env to test
    from app.config import settings
    if settings.PERSONAL_MAILBOX:
        account = get_exchange_account(settings.PERSONAL_MAILBOX)
        print(f"✓ Exchange account obtained: {account.primary_smtp_address}")
    else:
        print("  Skipped — PERSONAL_MAILBOX not set in .env")
except Exception as e:
    print(f"✗ Exchange account failed: {e}")
    print("  Check that exchangelib is installed and EWS is reachable")
```

Run: python test_auth.py
Both tests should either succeed or fail with a network/Kerberos
error — NOT an ImportError or AttributeError.
Fix any ImportError before proceeding to FIX 2.


# ============================================================
# FIX 2 — Rewrite mail_engine/draft_mail.py with correct routing
# ============================================================

Open app/services/mail_engine/draft_mail.py.
Replace the ENTIRE file.

Read these files BEFORE writing any code:
  src/personal_routes/draft_mail.py   ← Graph API implementation
  src/shared_routes/draft_mail.py     ← exchangelib implementation

Your job is to merge both implementations into one file
with a single run() entry point that routes based on is_shared.

```python
"""
app/services/mail_engine/draft_mail.py

Draft/Send mail — reimplementation of:
  src/personal_routes/draft_mail.py  (Graph API, personal mailbox)
  src/shared_routes/draft_mail.py    (exchangelib, shared mailbox)

Routing:
  is_shared=False → _run_personal()  uses Graph API + Kerberos token
  is_shared=True  → _run_shared()    uses exchangelib + EWS
"""
import logging
import base64
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

GRAPH_PROXY_BASE = 'https://o365-graph-proxy-ms6.gaiacloud.jpmchase.net'


# ── Shared utilities ──────────────────────────────────────

def _apply_find_replace(text: str, pairs: list) -> str:
    """Apply find/replace pairs to text. Mirrors original logic."""
    for pair in pairs:
        find = pair.get('find', '') if isinstance(pair, dict) else ''
        replace = pair.get('replace', '') if isinstance(pair, dict) else ''
        if find:
            text = text.replace(find, replace)
    return text


def _read_body_file(body_path: str, find_replace_pairs: list) -> str:
    """
    Read email body from .docx or text file and apply find/replace.
    Read src/personal_routes/draft_mail.py to confirm how
    the original code reads the body file and apply the same approach.
    """
    path = Path(body_path)
    if not path.exists():
        raise FileNotFoundError(f"Body file not found: {body_path}")

    if path.suffix.lower() == '.docx':
        # Read docx — use python-docx
        from docx import Document
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        content = '\n'.join(f'<p>{p}</p>' for p in paragraphs)
    else:
        content = path.read_text(encoding='utf-8')

    return _apply_find_replace(content, find_replace_pairs)


def _resolve_attachments(folder: str, pattern: str) -> list:
    """Resolve attachment file paths from folder + wildcard pattern."""
    if not folder:
        return []
    folder_path = Path(folder)
    if not folder_path.exists():
        logger.warning(f"Attachment folder not found: {folder}")
        return []
    return sorted(folder_path.glob(pattern)) if pattern else []


# ── Personal mailbox path (Graph API) ────────────────────

def _run_personal(config: dict, mailbox: str) -> dict:
    """
    Send/draft mail via Graph API for personal mailbox.

    Read src/personal_routes/draft_mail.py carefully.
    Mirror its Graph API call structure EXACTLY.
    The only changes allowed:
      - Replace the Excel row dict access with config dict access
      - Replace any GUI/Qt code with logging calls
      - Keep the same API endpoints and payload structure
    """
    import httpx
    from app.services.auth import get_graph_headers

    headers = get_graph_headers()

    find_replace_pairs = config.get('find_replace_pairs', [])
    subject = _apply_find_replace(config.get('subject_line', ''), find_replace_pairs)
    to_list = [e.strip() for e in config.get('to_stakeholders', '').split(';') if e.strip()]
    cc_list = [e.strip() for e in config.get('cc_stakeholders', '').split(';') if e.strip()]
    body_path = config.get('email_body_path', '')
    draft_or_send = config.get('draft_or_send', 'draft').lower()
    voting_option = config.get('voting_option', '')

    # Read body
    body_html = _read_body_file(body_path, find_replace_pairs) if body_path else f'<p>{subject}</p>'

    # Resolve attachments
    attachments = _resolve_attachments(
        config.get('attachment_folder_path', ''),
        config.get('attachment_file_name', ''),
    )

    # Build message payload
    # NOTE: mirror the exact payload structure from
    # src/personal_routes/draft_mail.py — do not guess
    to_recipients = [{'emailAddress': {'address': e}} for e in to_list]
    cc_recipients = [{'emailAddress': {'address': e}} for e in cc_list]

    message = {
        'subject': subject,
        'body': {'contentType': 'HTML', 'content': body_html},
        'toRecipients': to_recipients,
        'ccRecipients': cc_recipients,
    }

    # Voting options
    if voting_option:
        options = [v.strip() for v in voting_option.split(';') if v.strip()]
        if options:
            message['singleValueExtendedProperties'] = [{
                'id': 'String 0x0076',
                'value': ';'.join(options),
            }]

    # Attachments
    if attachments:
        message['attachments'] = []
        for att in attachments:
            content = base64.b64encode(att.read_bytes()).decode('utf-8')
            message['attachments'].append({
                '@odata.type': '#microsoft.graph.fileAttachment',
                'name': att.name,
                'contentBytes': content,
            })

    # Send or draft
    base_url = f'{GRAPH_PROXY_BASE}/me'
    if draft_or_send == 'send':
        response = httpx.post(
            f'{base_url}/sendMail',
            headers=headers,
            json={'message': message},
            timeout=30.0,
            verify=False,
        )
        response.raise_for_status()
        logger.info(f"[personal] Email sent: '{subject}' to {len(to_list)} recipient(s)")
        return {'status': 'sent', 'subject': subject, 'recipients': len(to_list)}
    else:
        response = httpx.post(
            f'{base_url}/messages',
            headers=headers,
            json=message,
            timeout=30.0,
            verify=False,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"[personal] Draft created: '{subject}' id={data.get('id')}")
        return {'status': 'drafted', 'message_id': data.get('id'), 'subject': subject}


# ── Shared mailbox path (exchangelib) ────────────────────

def _run_shared(config: dict, mailbox: str) -> dict:
    """
    Send/draft mail via exchangelib for shared mailbox.

    Read src/shared_routes/draft_mail.py carefully.
    Mirror its exchangelib usage EXACTLY.
    The only changes allowed:
      - Replace the Excel row dict access with config dict access
      - Replace any GUI/Qt code with logging calls
      - Keep the same exchangelib objects and method calls
    """
    from app.services.auth import get_exchange_account

    account = get_exchange_account(mailbox)

    find_replace_pairs = config.get('find_replace_pairs', [])
    subject = _apply_find_replace(config.get('subject_line', ''), find_replace_pairs)
    to_list = [e.strip() for e in config.get('to_stakeholders', '').split(';') if e.strip()]
    cc_list = [e.strip() for e in config.get('cc_stakeholders', '').split(';') if e.strip()]
    body_path = config.get('email_body_path', '')
    draft_or_send = config.get('draft_or_send', 'draft').lower()

    body_html = _read_body_file(body_path, find_replace_pairs) if body_path else f'<p>{subject}</p>'

    attachments = _resolve_attachments(
        config.get('attachment_folder_path', ''),
        config.get('attachment_file_name', ''),
    )

    # Build exchangelib Message
    # NOTE: mirror the exact exchangelib usage from
    # src/shared_routes/draft_mail.py — do not guess.
    # Read that file and reproduce the same Message construction.
    # Common pattern (adjust based on what src/shared_routes/draft_mail.py uses):
    from exchangelib import Message, Mailbox, FileAttachment, HTMLBody

    to_recipients = [Mailbox(email_address=e) for e in to_list]
    cc_recipients = [Mailbox(email_address=e) for e in cc_list]

    msg = Message(
        account=account,
        subject=subject,
        body=HTMLBody(body_html),
        to_recipients=to_recipients,
        cc_recipients=cc_recipients,
    )

    # Attachments
    for att in attachments:
        msg.attach(FileAttachment(name=att.name, content=att.read_bytes()))

    if draft_or_send == 'send':
        msg.send()
        logger.info(f"[shared] Email sent: '{subject}' to {len(to_list)} recipient(s)")
        return {'status': 'sent', 'subject': subject, 'recipients': len(to_list)}
    else:
        msg.save(account.drafts)
        logger.info(f"[shared] Draft saved: '{subject}'")
        return {'status': 'drafted', 'subject': subject}


# ── Public entry point ────────────────────────────────────

def run(config: dict, is_shared: bool, mailbox: str) -> dict:
    """
    Route to the correct implementation based on is_shared.

    Args:
        config:     Task config dict from tasks.json
        is_shared:  False = personal mailbox (Graph API)
                    True  = shared mailbox (exchangelib)
        mailbox:    Mailbox address (used when is_shared=True)
    """
    if is_shared:
        logger.info(f"[draft_mail] Routing to exchangelib (shared: {mailbox})")
        return _run_shared(config, mailbox)
    else:
        logger.info(f"[draft_mail] Routing to Graph API (personal)")
        return _run_personal(config, mailbox)
```

CRITICAL STEP after writing:
Read src/shared_routes/draft_mail.py right now and check:
  1. Does it use Message(...).send() or a different method?
  2. Does it use HTMLBody or plain Body?
  3. Does it handle attachments differently?
  4. Does it use account.drafts or a different folder for drafts?

Update _run_shared() to exactly match what src/shared_routes/draft_mail.py does.
Only the Excel row → config dict mapping changes.
Everything else must be identical.


# ============================================================
# FIX 3 — Apply the same routing fix to reminder, track_mail,
#          and download_attachments
# ============================================================

For each of these three files, apply the SAME pattern as FIX 2.

For each file, do this in order:
  1. Read src/personal_routes/{module}.py
  2. Read src/shared_routes/{module}.py
  3. Open app/services/mail_engine/{module}.py
  4. Rewrite it with _run_personal() + _run_shared() + run()
  5. _run_personal uses get_graph_headers() from auth.py
  6. _run_shared uses get_exchange_account() from auth.py

--- app/services/mail_engine/reminder_mail.py ---

Read src/personal_routes/reminder.py and src/shared_routes/reminder.py.

The reminder module differs from draft in ONE way:
  - It uses reminder_body_path instead of email_body_path for body

Write it following the exact same structure as FIX 2.
Import _apply_find_replace, _read_body_file, _resolve_attachments
from draft_mail to avoid duplication:

```python
from app.services.mail_engine.draft_mail import (
    _apply_find_replace,
    _read_body_file,
    _resolve_attachments,
)
```

In _run_personal and _run_shared use:
  body_path = config.get('reminder_body_path', '') or config.get('email_body_path', '')

Everything else mirrors draft_mail exactly.
Entry point: run(config, is_shared, mailbox)

--- app/services/mail_engine/track_mail.py ---

Read src/personal_routes/track_mail.py and src/shared_routes/track_mail.py.

_run_personal uses Graph API:
  Endpoint: GET {GRAPH_PROXY_BASE}/me/mailFolders/{folder}/messages
  Filter by subject (partial or exact based on config)
  Filter by date range if start_date/end_date are set
  Download attachments if download_attachment=True
  Save emails if save_email=True

_run_shared uses exchangelib:
  Use account.inbox or the configured folder
  Filter messages by subject using Q objects or iteration
  Read src/shared_routes/track_mail.py to see EXACTLY how
  it queries and what it does with results — mirror it

IMPORTANT: Do NOT invent the exchangelib query logic.
Read src/shared_routes/track_mail.py and copy the pattern.

For saving email as PDF (personal only, Graph API):
  The Graph API does not export PDF directly.
  Read src/personal_routes/track_mail.py to see what it does
  and replicate that approach exactly.

Entry point: run(config, is_shared, mailbox)

--- app/services/mail_engine/download_attachments.py ---

Read src/personal_routes/download_attachments.py
and src/shared_routes/download_attachments.py.

_run_personal uses Graph API:
  GET /me/messages (filtered by subject)
  GET /me/messages/{id}/attachments
  Filter by file type if specified
  Extract zip if configured

_run_shared uses exchangelib:
  Mirror src/shared_routes/download_attachments.py exactly

Entry point: run(config, is_shared, mailbox)

After writing all three files, verify each one has:
  ✓ No import of Token or ExchangeCredentials directly
      (auth is handled via app/services/auth.py only)
  ✓ _run_personal() calls get_graph_headers()
  ✓ _run_shared() calls get_exchange_account()
  ✓ run() routes based on is_shared boolean
  ✓ No httpx calls inside _run_shared()
  ✓ No exchangelib imports inside _run_personal()


# ============================================================
# FIX 4 — Update executor.py to pass correct args + verify
# ============================================================

Open app/tasks/executor.py.

Step 1 — Update _call_draft to pass the right arguments.
The mail_engine run() function signature is:
  run(config: dict, is_shared: bool, mailbox: str) -> dict

Make sure the call is:
```python
def _call_draft(self, args: dict, is_shared: bool):
    if settings.USE_MAIL_ENGINE:
        from app.services.mail_engine.draft_mail import run
        config = self.task.get('config', {})
        mailbox = self.task.get('mailbox', '')
        self._log('INFO',
            f"Routing to {'exchangelib (shared)' if is_shared else 'Graph API (personal)'}"
        )
        result = run(config=config, is_shared=is_shared, mailbox=mailbox)
        self._log('INFO', f"Result: {result.get('status')} — {result}")
    else:
        # legacy src/workers/ path
        if is_shared:
            from shared_routes.draft_mail import main as run_draft
        else:
            from personal_routes.draft_mail import main as run_draft
        run_draft(args)
```

Do the same update for _call_reminder, _call_tracking, _call_download —
each should import from the corresponding mail_engine module
and pass (config=config, is_shared=is_shared, mailbox=mailbox).

Step 2 — Verify is_shared is being read correctly.
Find where _dispatch calls the _call_* methods.
Confirm the is_shared value comes from:
  is_shared = self.task.get('is_shared_mailbox', False)
NOT from the args dict or any other source.

Step 3 — Add a routing log line at the top of _dispatch:
```python
def _dispatch(self):
    task_type = self.task.get('task_type')
    is_shared = self.task.get('is_shared_mailbox', False)
    mailbox = self.task.get('mailbox', '')

    self._log('INFO',
        f"Dispatch: task_type={task_type} | "
        f"mailbox_type={'shared (exchangelib)' if is_shared else 'personal (Graph API)'} | "
        f"mailbox={mailbox or '(personal default)'}"
    )
    ...
```

This log line means every task run will clearly show
which path was taken — making future debugging easy.

Step 4 — Run the full verification test.

Write this test at project root: test_routing.py

```python
"""
Routing verification test.
Confirms personal → Graph API and shared → exchangelib.
Does NOT actually send emails — just verifies the code path.
Run: python test_routing.py
"""
import sys
from pathlib import Path
sys.path.insert(0, 'src')

PERSONAL_TASK = {
    'id': 'verify-personal',
    'process_name': 'Routing Test (Personal)',
    'task_type': 'draft_send',
    'is_shared_mailbox': False,
    'mailbox': '',
    'log_output_folder': 'data/test-logs',
    'need_to_process': True,
    'enabled': True,
    'config': {
        'subject_line': 'Test Subject',
        'to_stakeholders': 'test@company.com',
        'cc_stakeholders': '',
        'attachment_folder_path': '',
        'attachment_file_name': '',
        'email_body_path': '',
        'draft_or_send': 'draft',
        'find_replace_pairs': [],
        'voting_option': '',
    }
}

SHARED_TASK = {
    **PERSONAL_TASK,
    'id': 'verify-shared',
    'process_name': 'Routing Test (Shared)',
    'is_shared_mailbox': True,
    'mailbox': 'shared-inbox@company.com',  # replace with a real shared mailbox
}

from app.tasks.executor import TaskExecutor

print("=== Personal mailbox routing test ===")
executor = TaskExecutor(PERSONAL_TASK, log_dir='data/test-logs')
result = executor.run()
for entry in result['entries']:
    print(f"  [{entry['level']}] {entry['message']}")

routing_msg_personal = next(
    (e['message'] for e in result['entries'] if 'Graph API (personal)' in e['message']),
    None
)
if routing_msg_personal:
    print(f"\n✓ PASS: Personal task correctly routed to Graph API")
else:
    print(f"\n✗ FAIL: Personal task did NOT route to Graph API — check executor._dispatch")

print()
print("=== Shared mailbox routing test ===")
executor2 = TaskExecutor(SHARED_TASK, log_dir='data/test-logs')
result2 = executor2.run()
for entry in result2['entries']:
    print(f"  [{entry['level']}] {entry['message']}")

routing_msg_shared = next(
    (e['message'] for e in result2['entries'] if 'exchangelib (shared)' in e['message']),
    None
)
if routing_msg_shared:
    print(f"\n✓ PASS: Shared task correctly routed to exchangelib")
else:
    print(f"\n✗ FAIL: Shared task did NOT route to exchangelib — check executor._dispatch")
```

Run: python test_routing.py

Expected output:
  ✓ PASS: Personal task correctly routed to Graph API
  ✓ PASS: Shared task correctly routed to exchangelib

If either test fails with an ImportError:
  → The import path in auth.py is wrong. Re-read FIX 1.

If either test fails with "did NOT route":
  → The is_shared_mailbox field in the task dict is not
    being read correctly. Re-read Step 2 of this prompt.

If either test fails with a network/auth error:
  → The routing is CORRECT. The failure is environmental
    (Kerberos not available, EWS unreachable in this shell).
    This is acceptable — the important thing is the routing
    log line appears correctly.
