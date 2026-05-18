# ============================================================
# RULES RUN FIXES — Frontend + Backend
# 4 prompts:
#   FX-B1: Update mailbox_service to support date range filter
#   FX-B2: Replace /rules/run POST with SSE stream endpoint
#   FX-F1: Update Rules.tsx processing state to use SSE
#   FX-F2: Remove all "AI" wording throughout the UI
#
# WHAT IS BEING FIXED:
#   1. Steps show static dummy numbers that never update
#   2. "AI" / "Sending to AI" language used throughout
#   3. /rules/run fetches ALL emails then filters in Python
#      — wasteful, should filter at the mailbox API level
#   4. /rules/run is a plain POST — blocks until fully done
#      so the frontend fakes progress with hardcoded steps
#      — replace with SSE so steps update in real time
# ============================================================


# ============================================================
# FX-B1 — Update mailbox_service.get_emails to accept date range
# ============================================================

Open app/services/mailbox_service.py.

Find the get_emails() function. It currently builds a
$filter param only for 'unread'. Update it to also
accept start_date and end_date and pass them directly
to the Graph API $filter so the mailbox API does the
filtering — not Python.

Update the function signature:

```python
def get_emails(
    is_shared: bool,
    mailbox: str,
    filter_type: str = 'all',
    limit: int = 50,
    start_date: str = '',    # ← ADD: 'YYYY-MM-DD' or empty
    end_date: str = '',      # ← ADD: 'YYYY-MM-DD' or empty
) -> list[dict]:
```

Update the $filter construction inside the function.
Find where params['$filter'] is set and replace with:

```python
filters = []

# Existing unread filter
if filter_type == 'unread':
    filters.append('isRead eq false')

# Date range — pass directly to Graph API
# Graph API uses ISO 8601 datetime format for receivedDateTime
if start_date:
    filters.append(f"receivedDateTime ge {start_date}T00:00:00Z")
if end_date:
    filters.append(f"receivedDateTime le {end_date}T23:59:59Z")

if filters:
    params['$filter'] = ' and '.join(filters)
```

This means the Graph API returns only emails in the date
range — no separate Python filtering step needed at all.

The exchangelib path (shared mailbox) also needs updating.
Find where exchangelib queries the inbox and add a filter:

```python
# For exchangelib (shared mailbox), add date filter:
from exchangelib import Q
from datetime import datetime

qs = account.inbox.filter(
    received_time__gte=datetime.strptime(start_date, '%Y-%m-%d')
    if start_date else None
)
# Only apply if start_date is set, otherwise use all
```

Read the existing exchangelib query in _run_shared and
apply the same pattern — adjust to match the actual
query method used in the existing code.

After updating, remove the separate date-filtering step
from app/routers/rules.py (the list comprehension that
filters emails by timestamp). It is no longer needed
because get_emails() now returns only emails in range.

Open app/routers/rules.py and in the /rules/run endpoint
(which will be replaced in FX-B2 anyway) and /dry-run,
remove these lines:

```python
# REMOVE THIS BLOCK — no longer needed:
filtered_emails = [
    e for e in all_emails
    if e.get('timestamp', '')[:10] >= body.start_date
    and e.get('timestamp', '')[:10] <= body.end_date
]
```

Replace with:
```python
# get_emails now returns only in-range emails directly
filtered_emails = all_emails   # already filtered by date at source
```

Also update the RunRulesRequest model in app/models/rule.py.
The start_date and end_date are now passed to get_emails
not used for Python filtering, so add a note:

```python
class RunRulesRequest(BaseModel):
    start_date:  str    # YYYY-MM-DD — passed to mailbox API filter
    end_date:    str    # YYYY-MM-DD — passed to mailbox API filter
    rules:       List[RuleDefinition]
    is_shared:   bool = False
    mailbox:     str  = ''
```


# ============================================================
# FX-B2 — Replace /rules/run POST with SSE stream endpoint
# ============================================================

Open app/routers/rules.py.

RENAME the existing @router.post('') endpoint to
_run_rules_sync() — keep it as a private function,
it will be called from inside the SSE generator.

ADD a new SSE streaming endpoint that yields real-time
progress events as each step completes:

```python
import json
import asyncio
from fastapi.responses import StreamingResponse
from app.services.rules_service import run_rules
from app.services.mailbox_service import get_emails, move_email
from app.config import settings


def _sse(event: str, data: dict) -> str:
    """Format one SSE message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _run_rules_stream(body_dict: dict):
    """
    SSE generator for /rules/run/stream.
    Yields progress events as each step completes.

    Steps (no "AI" language anywhere):
      1. fetch       — fetching emails from mailbox
      2. analyse     — sending to rules engine
      3. move        — moving emails to folders

    Each step event:
      { stepId, status, detail }
      status: 'active' | 'done' | 'error'
      detail: human readable result e.g. "47 emails fetched"
    """
    try:
        rules      = body_dict.get('rules', [])
        start_date = body_dict.get('start_date', '')
        end_date   = body_dict.get('end_date', '')
        is_shared  = body_dict.get('is_shared', False)
        mailbox    = body_dict.get('mailbox', '') or settings.PERSONAL_MAILBOX

        # ── STEP 1: Fetch emails ──────────────────────────────
        yield _sse('progress', {
            'stepId': 'fetch',
            'status': 'active',
            'detail': f'Fetching emails from {start_date} to {end_date}...',
        })

        try:
            emails = get_emails(
                is_shared=is_shared,
                mailbox=mailbox,
                filter_type='all',
                limit=500,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            yield _sse('progress', {
                'stepId': 'fetch',
                'status': 'error',
                'detail': f'Failed to fetch emails: {str(e)}',
            })
            yield _sse('error_event', {'message': str(e)})
            return

        email_count = len(emails)
        yield _sse('progress', {
            'stepId': 'fetch',
            'status': 'done',
            'detail': f'{email_count} email{"s" if email_count != 1 else ""} fetched',
        })

        await asyncio.sleep(0.05)

        if not emails:
            yield _sse('complete', {
                'total_emails':    0,
                'emails_in_range': 0,
                'moved': 0, 'no_match': 0, 'errors': 0,
                'results': [],
            })
            return

        # ── STEP 2: Run rules engine ──────────────────────────
        yield _sse('progress', {
            'stepId': 'analyse',
            'status': 'active',
            'detail': f'Applying {len(rules)} rule{"s" if len(rules) != 1 else ""} to {email_count} email{"s" if email_count != 1 else ""}...',
        })

        try:
            decisions = run_rules(rules=rules, emails=emails)
        except Exception as e:
            yield _sse('progress', {
                'stepId': 'analyse',
                'status': 'error',
                'detail': f'Rules engine failed: {str(e)}',
            })
            yield _sse('error_event', {'message': str(e)})
            return

        matched   = sum(1 for d in decisions if d.get('status') == 'moved')
        unmatched = sum(1 for d in decisions if d.get('status') != 'moved')

        yield _sse('progress', {
            'stepId': 'analyse',
            'status': 'done',
            'detail': f'{matched} matched, {unmatched} unmatched',
        })

        await asyncio.sleep(0.05)

        # ── STEP 3: Move emails ───────────────────────────────
        yield _sse('progress', {
            'stepId': 'move',
            'status': 'active',
            'detail': f'Moving {matched} email{"s" if matched != 1 else ""} to folders...',
        })

        email_map = {e['id']: e for e in emails}
        results   = []
        error_count = 0

        for decision in decisions:
            email_id  = decision.get('email_id', '')
            email     = email_map.get(email_id, {})
            status    = decision.get('status', 'no_match')
            error_msg = None

            if status == 'moved' and decision.get('folder'):
                try:
                    move_email(
                        is_shared=is_shared,
                        mailbox=mailbox,
                        email_id=email_id,
                        destination_folder=decision['folder'],
                    )
                except Exception as e:
                    error_msg   = str(e)
                    status      = 'error'
                    error_count += 1

            results.append({
                'emailId':         email_id,
                'subject':         email.get('subject', ''),
                'from':            email.get('sender_email', ''),
                'matchedRuleId':   decision.get('rule_id', ''),
                'matchedRuleName': decision.get('rule_name', ''),
                'folder':          decision.get('folder', ''),
                'confidence':      decision.get('confidence', 'low'),
                'reasoning':       decision.get('reasoning', ''),
                'status':          status,
                'errorMessage':    error_msg,
            })

        moved_count = sum(1 for r in results if r['status'] == 'moved')

        yield _sse('progress', {
            'stepId': 'move',
            'status': 'done' if error_count == 0 else 'done',
            'detail': (
                f'{moved_count} moved successfully'
                if error_count == 0
                else f'{moved_count} moved, {error_count} failed'
            ),
        })

        # Update match counts in rules store
        try:
            from app.services.rules_store import update_match_count
            tally: dict[str, int] = {}
            for r in results:
                rid = r.get('matchedRuleId', '')
                if rid and r['status'] == 'moved':
                    tally[rid] = tally.get(rid, 0) + 1
            for rid, count in tally.items():
                update_match_count(rid, count)
        except Exception as e:
            pass   # non-critical — don't fail the run

        # ── FINAL: complete event ─────────────────────────────
        yield _sse('complete', {
            'total_emails':    email_count,
            'emails_in_range': email_count,
            'moved':           moved_count,
            'no_match':        sum(1 for r in results if r['status'] == 'no_match'),
            'errors':          error_count,
            'results':         results,
        })

    except Exception as e:
        yield _sse('error_event', {'message': f'Unexpected error: {str(e)}'})


@router.get('/run/stream')
async def run_rules_stream(
    start_date: str,
    end_date:   str,
    rules_json: str,     # JSON-encoded list of rule dicts
    is_shared:  bool  = False,
    mailbox:    str   = '',
):
    """
    SSE endpoint for running rules with live progress.

    Frontend connects with EventSource:
      new EventSource('/api/rules/run/stream?start_date=...&rules_json=...')

    Streams three progress events then a complete event.
    No "AI" language in any event data.
    """
    import json as _json
    try:
        rules = _json.loads(rules_json)
    except Exception:
        rules = []

    body_dict = {
        'start_date': start_date,
        'end_date':   end_date,
        'rules':      rules,
        'is_shared':  is_shared,
        'mailbox':    mailbox,
    }

    return StreamingResponse(
        _run_rules_stream(body_dict),
        media_type='text/event-stream',
        headers={
            'Cache-Control':               'no-cache',
            'X-Accel-Buffering':           'no',
            'Access-Control-Allow-Origin': '*',
        },
    )
```

NOTE on GET vs POST for SSE:
EventSource only supports GET requests. The rule data
(rules_json) is passed as a query param as a JSON-encoded
string. The frontend encodes it with JSON.stringify() +
encodeURIComponent() before building the URL.

If rules_json is very long (many rules with long instructions),
consider using a POST-then-stream pattern:
  POST /api/rules/run/prepare → returns a session_token
  GET  /api/rules/run/stream?token=session_token
This avoids URL length limits. For now implement the simple
GET version — add the POST pattern later if needed.

Keep the original @router.post('/run') endpoint as-is
for non-SSE clients (curl testing, dry-run reference).
Do NOT remove it.


# ============================================================
# FX-F1 — Update Rules.tsx processing state to use SSE
# ============================================================

Open src/pages/Rules.tsx.

--- STEP 1: Update state ---

Replace the existing runStatus useState and steps array
with SSE-aware state:

REMOVE all of:
```tsx
// Remove these entirely:
const [runStatus, setRunStatus] = useState<RuleStatus>('idle')
// And the static steps array in R-F3 processing state
```

ADD:
```tsx
type RunPhase = 'idle' | 'running' | 'done' | 'error'

interface ProgressStep {
  id:     'fetch' | 'analyse' | 'move'
  label:  string
  status: 'pending' | 'active' | 'done' | 'error'
  detail: string
}

const [runPhase, setRunPhase] = useState<RunPhase>('idle')
const [runError, setRunError] = useState<string | null>(null)
const [steps, setSteps] = useState<ProgressStep[]>([
  { id: 'fetch',   label: 'Fetching emails from mailbox', status: 'pending', detail: '' },
  { id: 'analyse', label: 'Running rules',                status: 'pending', detail: '' },
  { id: 'move',    label: 'Moving emails to folders',     status: 'pending', detail: '' },
])
const esRef = useRef<EventSource | null>(null)
```

--- STEP 2: Replace handleRunRules with SSE version ---

REMOVE the existing handleRunRules function entirely.
REPLACE with:

```tsx
const handleRunRules = () => {
  const activeRules = rules.filter(r => r.enabled)
  if (activeRules.length === 0) return

  // Reset state
  setRunPhase('running')
  setRunError(null)
  setResults([])
  setSteps([
    { id: 'fetch',   label: 'Fetching emails from mailbox', status: 'pending', detail: '' },
    { id: 'analyse', label: 'Running rules',                status: 'pending', detail: '' },
    { id: 'move',    label: 'Moving emails to folders',     status: 'pending', detail: '' },
  ])

  // Build SSE URL — rules passed as JSON query param
  const rulesJson = encodeURIComponent(JSON.stringify(
    activeRules.map(r => ({ id: r.id, name: r.name, instruction: r.instruction }))
  ))
  const url = [
    `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'}`,
    `/rules/run/stream`,
    `?start_date=${startDate}`,
    `&end_date=${endDate}`,
    `&rules_json=${rulesJson}`,
  ].join('')

  // Open SSE connection
  const es = new EventSource(url)
  esRef.current = es

  // Progress events — update individual step in real time
  es.addEventListener('progress', (e: MessageEvent) => {
    const data = JSON.parse(e.data) as {
      stepId: 'fetch' | 'analyse' | 'move'
      status: 'active' | 'done' | 'error'
      detail: string
    }
    setSteps(prev => prev.map(step =>
      step.id === data.stepId
        ? { ...step, status: data.status, detail: data.detail }
        : step
    ))
  })

  // Complete event — run finished, show results
  es.addEventListener('complete', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    setResults(data.results ?? [])
    setRunPhase('done')
    es.close()
    esRef.current = null
    fetchRules()   // refresh match counts
  })

  // Error event from backend
  es.addEventListener('error_event', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    setRunError(data.message)
    setRunPhase('error')
    es.close()
    esRef.current = null
  })

  // Network / connection error
  es.onerror = () => {
    setRunError('Connection to server lost')
    setRunPhase('error')
    es.close()
    esRef.current = null
  }
}

// Cancel — close the SSE connection
const handleCancelRun = () => {
  if (esRef.current) {
    esRef.current.close()
    esRef.current = null
  }
  setRunPhase('idle')
  setRunError(null)
  setSteps([
    { id: 'fetch',   label: 'Fetching emails from mailbox', status: 'pending', detail: '' },
    { id: 'analyse', label: 'Running rules',                status: 'pending', detail: '' },
    { id: 'move',    label: 'Moving emails to folders',     status: 'pending', detail: '' },
  ])
}

// Cleanup on unmount
useEffect(() => {
  return () => { esRef.current?.close() }
}, [])
```

Add useRef import at the top of the file if not present:
  import { useState, useEffect, useRef } from 'react'

--- STEP 3: Update run panel button ---

Find the Cancel / Run button in the right column run panel.
Update the condition from runStatus === 'processing'
to runPhase === 'running', and wire cancel:

```tsx
{runPhase === 'running' ? (
  <button
    onClick={handleCancelRun}
    className="w-full border border-outline-variant bg-white text-on-surface-variant py-3 rounded-lg flex items-center justify-center gap-2 font-semibold hover:bg-surface-container transition-all"
  >
    <span className="material-symbols-outlined">close</span>
    <span>Cancel</span>
  </button>
) : (
  <button
    onClick={handleRunRules}
    className="w-full bg-primary text-white py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-primary-container transition-all font-semibold shadow-lg shadow-primary/20"
  >
    <span className="material-symbols-outlined"
      style={{ fontVariationSettings: "'FILL' 1" }}>
      auto_awesome
    </span>
    <span>Run All Rules</span>
  </button>
)}
```

Also disable date inputs when runPhase === 'running':
  disabled={runPhase === 'running'}

--- STEP 4: Update processing state body ---

In R-F3 the processing state renders static steps.
Replace that entire processing state section with
live steps driven from the SSE events:

```tsx
{/* Show when runPhase === 'running' OR when done/error
    so results area updates progressively */}
{(runPhase === 'running' || runPhase === 'done' || runPhase === 'error') && (

  <section className="bg-surface-container-lowest rounded-xl border border-outline-variant p-lg shadow-sm space-y-4">

    {/* Header row */}
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        {runPhase === 'running' && (
          <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
        )}
        {runPhase === 'done' && (
          <span className="material-symbols-outlined text-emerald-500 text-[18px]"
            style={{ fontVariationSettings: "'FILL' 1" }}>
            check_circle
          </span>
        )}
        {runPhase === 'error' && (
          <span className="material-symbols-outlined text-error text-[18px]"
            style={{ fontVariationSettings: "'FILL' 1" }}>
            error
          </span>
        )}
        <p className="text-body font-semibold text-on-surface">
          {runPhase === 'running' ? 'Processing...' :
           runPhase === 'done'    ? 'Completed' :
           'Failed'}
        </p>
      </div>
    </div>

    {/* Live steps — driven by SSE events */}
    <div className="space-y-2">
      {steps.map((step) => (
        <div
          key={step.id}
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
            step.status === 'active' ? 'bg-primary/5' : ''
          } ${step.status === 'pending' ? 'opacity-40' : ''}`}
        >
          {/* Status icon */}
          {step.status === 'done' && (
            <span className="material-symbols-outlined text-emerald-500 text-[18px] shrink-0"
              style={{ fontVariationSettings: "'FILL' 1" }}>
              check_circle
            </span>
          )}
          {step.status === 'active' && (
            <div className="w-[18px] h-[18px] border-2 border-primary border-t-transparent rounded-full animate-spin shrink-0" />
          )}
          {step.status === 'pending' && (
            <span className="material-symbols-outlined text-outline text-[18px] shrink-0">
              radio_button_unchecked
            </span>
          )}
          {step.status === 'error' && (
            <span className="material-symbols-outlined text-error text-[18px] shrink-0"
              style={{ fontVariationSettings: "'FILL' 1" }}>
              cancel
            </span>
          )}

          {/* Label */}
          <span className={`text-body flex-1 ${
            step.status === 'active' ? 'font-medium text-primary' :
            step.status === 'done'   ? 'text-on-surface' :
            step.status === 'error'  ? 'text-error' :
            'text-on-surface-variant'
          }`}>
            {step.label}
          </span>

          {/* Live detail — updates from SSE */}
          {step.detail && (
            <span className={`text-meta ml-auto shrink-0 font-mono ${
              step.status === 'active' ? 'text-primary bg-primary/5 px-2 py-0.5 rounded' :
              step.status === 'done'   ? 'text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded' :
              step.status === 'error'  ? 'text-error' :
              'text-outline'
            }`}>
              {step.detail}
            </span>
          )}
        </div>
      ))}
    </div>

    {/* Error message */}
    {runPhase === 'error' && runError && (
      <div className="bg-error-container/20 border border-error/20 rounded-lg px-4 py-3">
        <p className="text-meta text-error">{runError}</p>
        <button
          onClick={() => { setRunPhase('idle'); setRunError(null) }}
          className="text-meta text-primary hover:underline mt-1"
        >
          Dismiss
        </button>
      </div>
    )}

  </section>
)}
```

Remove the "What the AI is seeing" collapsible block
from the processing state entirely — it references AI.

--- STEP 5: Update result state condition ---

Find every place that checks runStatus === 'done'
and replace with runPhase === 'done'.

Find every place that checks runStatus === 'processing'
and replace with runPhase === 'running'.

Find every place that checks runStatus === 'idle'
and replace with runPhase === 'idle'.


# ============================================================
# FX-F2 — Remove all "AI" wording from the entire frontend
# ============================================================

Search the entire src/ directory for the word "AI" (case
sensitive and case insensitive) and replace as follows.
Run this search:
  grep -rn "\bAI\b\|Artificial Intelligence\|ai is\|sending to ai\|what the ai" src/ --include="*.tsx" --include="*.ts"

Make these replacements everywhere found:

  "AI is reading your emails..."
    → "Processing your emails..."

  "Sending {n} rules to AI..."
    → "Running {n} rules against emails..."

  "Summarising with AI..."
    → "Generating summary..."

  "What the AI is seeing"
    → "What the engine is using"

  "Analysing with LLM..."
    → "Matching rules..."

  "AI reasoning"
    → "Why this matched"

  "View AI reasoning"
    → "View reasoning"

  "AI Suggestion"
    → "Suggestion"

  "this may take a moment (AI)"
    → "this may take a moment"

  Any button or label containing "AI":
    Remove the word and keep the action description

Also check these specific files:
  src/pages/Rules.tsx
  src/components/DigestModal/DigestModal.tsx
  src/components/DryRunModal/DryRunModal.tsx
  src/pages/Dashboard.tsx

In DigestModal.tsx specifically, the step label
"Summarising with AI..." must become:
  "Generating summary..."

The Generate Digest button label "Generate Digest" is fine
— no AI word there. Keep it.

The auto_awesome icon is fine — it is a visual element
not a text label.

After replacing, run:
  grep -rn "\bAI\b" src/ --include="*.tsx" --include="*.ts"

Expected: zero results.


# ============================================================
# VERIFICATION
# ============================================================

With backend running, open the Rules page and click
"Run All Rules". Confirm:

STEP LABELS (no AI wording, no static numbers):
  ✓ Step 1 shows: "Fetching emails from mailbox"
    then updates to real count e.g. "47 emails fetched"
  ✓ Step 2 shows: "Running rules"
    active detail: "Applying 3 rules to 47 emails..."
    done detail:   "28 matched, 19 unmatched"
  ✓ Step 3 shows: "Moving emails to folders"
    active detail: "Moving 28 emails to folders..."
    done detail:   "28 moved successfully"

LIVE UPDATES:
  ✓ Steps transition from pending → active → done
    in real time as SSE events arrive
  ✓ Detail text updates with real numbers from backend
  ✓ No step is hardcoded — all driven by SSE events

CANCEL:
  ✓ Clicking Cancel closes SSE connection immediately
  ✓ Steps reset to pending
  ✓ Run button reappears

ERROR HANDLING:
  ✓ If mailbox fetch fails, step 1 shows error state
    with the actual error message
  ✓ If rules engine fails, step 2 shows error state
  ✓ Dismiss button clears the error and resets to idle

NO AI WORDING:
  ✓ No "AI" text anywhere in the processing state
  ✓ No "AI" text in step labels or detail values
  ✓ "Why this matched" instead of "AI reasoning"
  ✓ "Processing your emails..." not "AI is reading..."
