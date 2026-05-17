# ============================================================
# RULES CRUD — Backend + Frontend Integration
# 5 prompts total:
#
# BACKEND:
#   RU-B1: rules_store.py — JSON file persistence (mirrors task_store)
#   RU-B2: rule models update + full CRUD router
#
# FRONTEND:
#   RU-F1: useRulesStore.ts — Zustand store + API calls
#   RU-F2: Wire Rules.tsx to real API (replace mock state)
#   RU-F3: Wire DryRunModal + Dashboard to real rules data
#
# EXISTING CODE TO READ FIRST:
#   app/services/task_store.py   ← mirror this pattern exactly
#   app/models/rule.py           ← extend, don't replace
#   app/routers/rules.py         ← add CRUD alongside /run and /dry-run
#   src/pages/Rules.tsx          ← replace mock rules array with store
# ============================================================


# ============================================================
# RU-B1 — rules_store.py (mirrors task_store.py exactly)
# ============================================================

Read app/services/task_store.py before writing anything.
Understand its file-locking pattern, load/save functions,
and how it handles UUID generation and timestamps.

Then create app/services/rules_store.py mirroring that
pattern exactly — same file locking, same error handling,
same function signatures. Only the data shape differs.

```python
"""
app/services/rules_store.py

Persists rules to data/rules.json.
Mirrors app/services/task_store.py exactly.
Each rule is a plain English instruction the user wrote.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Optional

logger = logging.getLogger(__name__)

RULES_FILE = Path('data/rules.json')


def _ensure_file():
    """Create data/rules.json if it does not exist."""
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not RULES_FILE.exists():
        RULES_FILE.write_text(json.dumps([]))


def load_rules() -> list[dict]:
    """
    Load all rules from data/rules.json.
    Uses the same file-locking approach as task_store.py.
    Read task_store.py and apply the same locking pattern here.
    """
    _ensure_file()
    try:
        return json.loads(RULES_FILE.read_text())
    except Exception as e:
        logger.error(f"Failed to load rules: {e}")
        return []


def save_rules(rules: list[dict]):
    """
    Save rules list to data/rules.json.
    Uses same file-locking approach as task_store.py.
    """
    _ensure_file()
    RULES_FILE.write_text(json.dumps(rules, indent=2))


def get_rule_by_id(rule_id: str) -> Optional[dict]:
    """Return a single rule by id or None."""
    return next(
        (r for r in load_rules() if r.get('id') == rule_id),
        None
    )


def create_rule(data: dict) -> dict:
    """
    Create a new rule.
    Assigns id, created_at, updated_at, enabled=True,
    match_count=0 automatically.
    """
    rules = load_rules()
    rule = {
        'id':          str(uuid4()),
        'name':        data.get('name', '').strip(),
        'instruction': data.get('instruction', '').strip(),
        'enabled':     data.get('enabled', True),
        'match_count': 0,
        'last_run_at': None,
        'created_at':  datetime.utcnow().isoformat(),
        'updated_at':  datetime.utcnow().isoformat(),
    }
    rules.append(rule)
    save_rules(rules)
    logger.info(f"Rule created: {rule['id']} — '{rule['name']}'")
    return rule


def update_rule(rule_id: str, updates: dict) -> dict:
    """
    Partial update. Only provided fields are changed.
    updated_at is always refreshed.
    Raises ValueError if rule not found.
    """
    rules = load_rules()
    for i, rule in enumerate(rules):
        if rule.get('id') == rule_id:
            rules[i] = {
                **rule,
                **{k: v for k, v in updates.items()
                   if k not in ('id', 'created_at')},
                'updated_at': datetime.utcnow().isoformat(),
            }
            save_rules(rules)
            logger.info(f"Rule updated: {rule_id}")
            return rules[i]
    raise ValueError(f"Rule {rule_id} not found")


def toggle_rule(rule_id: str) -> dict:
    """Flip the enabled flag. Returns updated rule."""
    rule = get_rule_by_id(rule_id)
    if not rule:
        raise ValueError(f"Rule {rule_id} not found")
    return update_rule(rule_id, {'enabled': not rule['enabled']})


def delete_rule(rule_id: str) -> bool:
    """
    Delete a rule by id.
    Returns True if deleted, False if not found.
    """
    rules = load_rules()
    original_count = len(rules)
    rules = [r for r in rules if r.get('id') != rule_id]
    if len(rules) == original_count:
        return False
    save_rules(rules)
    logger.info(f"Rule deleted: {rule_id}")
    return True


def update_match_count(rule_id: str, count: int):
    """
    Update match_count and last_run_at after a rules run.
    Called by the rules router after each successful run.
    """
    try:
        update_rule(rule_id, {
            'match_count': count,
            'last_run_at': datetime.utcnow().isoformat(),
        })
    except ValueError:
        logger.warning(f"Could not update match count for rule {rule_id}")
```

After writing, create data/rules.json manually with
some sample rules so the frontend has data immediately:

```json
[
  {
    "id": "rule-001",
    "name": "SABS Team",
    "instruction": "If emails are from anyone in the SABS team (Sarah, Amir, Ben, or Sophie), move them to the SABS Team folder.",
    "enabled": true,
    "match_count": 42,
    "last_run_at": null,
    "created_at": "2025-05-01T09:00:00",
    "updated_at": "2025-05-01T09:00:00"
  },
  {
    "id": "rule-002",
    "name": "Pending Action",
    "instruction": "If an email requires me to take any action, complete a task, or respond urgently, move it to the Pending Action folder.",
    "enabled": true,
    "match_count": 15,
    "last_run_at": null,
    "created_at": "2025-05-01T09:00:00",
    "updated_at": "2025-05-01T09:00:00"
  },
  {
    "id": "rule-003",
    "name": "Newsletters",
    "instruction": "If the email is a newsletter, marketing message, or promotional content, move it to the Newsletters folder.",
    "enabled": true,
    "match_count": 128,
    "last_run_at": null,
    "created_at": "2025-05-01T09:00:00",
    "updated_at": "2025-05-01T09:00:00"
  },
  {
    "id": "rule-004",
    "name": "Finance Invoices",
    "instruction": "If the email contains an invoice, payment confirmation, or receipt, move it to Finance/Invoices.",
    "enabled": false,
    "match_count": 0,
    "last_run_at": null,
    "created_at": "2025-05-01T09:00:00",
    "updated_at": "2025-05-01T09:00:00"
  }
]
```


# ============================================================
# RU-B2 — Update rule models + add full CRUD to rules router
# ============================================================

Step 1 — Open app/models/rule.py and ADD these models.
Do NOT remove existing RuleDefinition or RunRulesRequest.

```python
# ADD to app/models/rule.py — do not replace existing content

class RuleCreate(BaseModel):
    """POST /api/rules — body for creating a new rule."""
    name:        str
    instruction: str
    enabled:     bool = True

    class Config:
        # Validate that name and instruction are not blank
        anystr_strip_whitespace = True

class RuleUpdate(BaseModel):
    """PATCH /api/rules/{id} — all fields optional."""
    name:        Optional[str] = None
    instruction: Optional[str] = None
    enabled:     Optional[bool] = None

class RuleResponse(BaseModel):
    """Shape returned to frontend for every rule."""
    id:          str
    name:        str
    instruction: str
    enabled:     bool
    match_count: int
    last_run_at: Optional[str]
    created_at:  str
    updated_at:  str
```

Step 2 — Open app/routers/rules.py.
ADD these CRUD endpoints ABOVE the existing /run endpoint.
Do NOT modify /run or /dry-run.

```python
# ADD these imports at the top of rules.py if not already present:
from app.models.rule import RuleCreate, RuleUpdate, RuleResponse
from app.services.rules_store import (
    load_rules, get_rule_by_id, create_rule,
    update_rule, toggle_rule, delete_rule,
)


# ── GET /api/rules ────────────────────────────────────────
@router.get('', response_model=list[RuleResponse])
def list_rules():
    """
    Fetch all rules.
    Frontend Rules.tsx calls this on mount to populate the list.
    """
    return load_rules()


# ── POST /api/rules ───────────────────────────────────────
@router.post('', response_model=RuleResponse, status_code=201)
def create_rule_endpoint(body: RuleCreate):
    """
    Create a new rule.
    Frontend calls this when user saves from the Add Rule form.
    Validates name and instruction are not blank.
    """
    if not body.name.strip():
        raise HTTPException(
            status_code=422,
            detail='Rule name cannot be empty'
        )
    if not body.instruction.strip():
        raise HTTPException(
            status_code=422,
            detail='Rule instruction cannot be empty'
        )
    return create_rule(body.dict())


# ── GET /api/rules/{rule_id} ──────────────────────────────
@router.get('/{rule_id}', response_model=RuleResponse)
def get_rule_endpoint(rule_id: str):
    """Fetch a single rule by id."""
    rule = get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail='Rule not found')
    return rule


# ── PATCH /api/rules/{rule_id} ────────────────────────────
@router.patch('/{rule_id}', response_model=RuleResponse)
def update_rule_endpoint(rule_id: str, body: RuleUpdate):
    """
    Partial update a rule (name, instruction, or enabled).
    Frontend calls this when user saves from the Edit Rule modal.
    Only fields present in body are updated.
    """
    rule = get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail='Rule not found')

    updates = body.dict(exclude_none=True)
    if not updates:
        return rule   # nothing to update

    # Validate if instruction or name are being updated
    if 'name' in updates and not updates['name'].strip():
        raise HTTPException(status_code=422, detail='Name cannot be empty')
    if 'instruction' in updates and not updates['instruction'].strip():
        raise HTTPException(status_code=422, detail='Instruction cannot be empty')

    try:
        return update_rule(rule_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── PATCH /api/rules/{rule_id}/toggle ────────────────────
@router.patch('/{rule_id}/toggle', response_model=RuleResponse)
def toggle_rule_endpoint(rule_id: str):
    """
    Flip enabled/disabled.
    Frontend calls this when user clicks the toggle on a rule row.
    Optimistic update on frontend — this confirms it.
    """
    try:
        return toggle_rule(rule_id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Rule not found')


# ── DELETE /api/rules/{rule_id} ───────────────────────────
@router.delete('/{rule_id}', status_code=204)
def delete_rule_endpoint(rule_id: str):
    """
    Delete a rule permanently.
    Frontend calls this after user confirms deletion.
    Returns 204 No Content on success.
    """
    deleted = delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Rule not found')
    # 204 returns no body
```

Step 3 — Update the /run endpoint in the same file to
write match counts back to rules_store after a run.

Find the existing /run endpoint. At the end, after
building the results list, add:

```python
    # Update match counts per rule in the store
    from app.services.rules_store import update_match_count
    tally: dict[str, int] = {}
    for r in results:
        rid = r.get('matchedRuleId', '')
        if rid and r.get('status') == 'moved':
            tally[rid] = tally.get(rid, 0) + 1
    for rid, count in tally.items():
        update_match_count(rid, count)
```

Step 4 — Test all endpoints:

```bash
# List rules (should return 4 sample rules from data/rules.json)
curl http://localhost:8000/api/rules

# Create a new rule
curl -X POST http://localhost:8000/api/rules \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Rule", "instruction": "Move test emails to Test folder."}'

# Get the new rule (replace ID with one returned above)
curl http://localhost:8000/api/rules/{id}

# Update instruction only
curl -X PATCH http://localhost:8000/api/rules/{id} \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Updated instruction."}'

# Toggle enabled/disabled
curl -X PATCH http://localhost:8000/api/rules/{id}/toggle

# Delete
curl -X DELETE http://localhost:8000/api/rules/{id}
# Expect: 204 No Content

# Confirm deleted
curl http://localhost:8000/api/rules/{id}
# Expect: 404
```

Expected responses:
  GET /api/rules         → array of 4 rules from data/rules.json
  POST /api/rules        → the created rule with id + timestamps
  PATCH /api/rules/{id}  → updated rule with new updated_at
  PATCH .../toggle       → rule with flipped enabled value
  DELETE /api/rules/{id} → 204 empty
  GET after delete       → 404


# ============================================================
# RU-F1 — src/store/rulesStore.ts (Zustand)
# ============================================================

Create src/store/rulesStore.ts.
This is the single source of truth for rules in the frontend.
All components read from and write to this store.

```ts
import { create } from 'zustand'
import client from '../api/client'

export interface Rule {
  id:          string
  name:        string
  instruction: string
  enabled:     boolean
  matchCount:  number
  lastRunAt:   string | null
  createdAt:   string
  updatedAt:   string
}

interface RulesStore {
  rules:   Rule[]
  loading: boolean
  error:   string | null

  // Actions
  fetchRules:   () => Promise<void>
  createRule:   (name: string, instruction: string) => Promise<Rule>
  updateRule:   (id: string, patch: Partial<Pick<Rule, 'name' | 'instruction' | 'enabled'>>) => Promise<Rule>
  toggleRule:   (id: string) => Promise<void>
  deleteRule:   (id: string) => Promise<void>
}

// Map API response (snake_case) to frontend (camelCase)
function toRule(raw: Record<string, unknown>): Rule {
  return {
    id:          raw.id as string,
    name:        raw.name as string,
    instruction: raw.instruction as string,
    enabled:     raw.enabled as boolean,
    matchCount:  (raw.match_count as number) ?? 0,
    lastRunAt:   (raw.last_run_at as string) ?? null,
    createdAt:   raw.created_at as string,
    updatedAt:   raw.updated_at as string,
  }
}

export const useRulesStore = create<RulesStore>((set, get) => ({
  rules:   [],
  loading: false,
  error:   null,

  fetchRules: async () => {
    set({ loading: true, error: null })
    try {
      const { data } = await client.get('/rules')
      set({ rules: data.map(toRule), loading: false })
    } catch (e) {
      set({ error: String(e), loading: false })
    }
  },

  createRule: async (name, instruction) => {
    const { data } = await client.post('/rules', { name, instruction })
    const rule = toRule(data)
    set({ rules: [...get().rules, rule] })
    return rule
  },

  updateRule: async (id, patch) => {
    // Optimistic update
    set({
      rules: get().rules.map(r =>
        r.id === id ? { ...r, ...patch } : r
      )
    })
    try {
      const { data } = await client.patch(`/rules/${id}`, {
        ...(patch.name        !== undefined && { name:        patch.name }),
        ...(patch.instruction !== undefined && { instruction: patch.instruction }),
        ...(patch.enabled     !== undefined && { enabled:     patch.enabled }),
      })
      const updated = toRule(data)
      set({ rules: get().rules.map(r => r.id === id ? updated : r) })
      return updated
    } catch (e) {
      // Revert on failure
      await get().fetchRules()
      throw e
    }
  },

  toggleRule: async (id) => {
    // Optimistic update
    set({
      rules: get().rules.map(r =>
        r.id === id ? { ...r, enabled: !r.enabled } : r
      )
    })
    try {
      const { data } = await client.patch(`/rules/${id}/toggle`)
      const updated = toRule(data)
      set({ rules: get().rules.map(r => r.id === id ? updated : r) })
    } catch (e) {
      // Revert on failure
      await get().fetchRules()
    }
  },

  deleteRule: async (id) => {
    // Optimistic removal
    set({ rules: get().rules.filter(r => r.id !== id) })
    try {
      await client.delete(`/rules/${id}`)
    } catch (e) {
      // Revert on failure
      await get().fetchRules()
      throw e
    }
  },
}))
```


# ============================================================
# RU-F2 — Wire Rules.tsx to real API via rulesStore
# ============================================================

Open src/pages/Rules.tsx.

Replace the mock rules useState array and all inline
CRUD handlers with the Zustand store. The UI markup
does NOT change — only the data source and handlers change.

Step 1 — Replace the mock rules state at the top:

REMOVE:
```tsx
const [rules, setRules] = useState<Rule[]>([
  { id: '1', name: 'SABS Team', enabled: true, matchCount: 42, ... },
  // ... other mock rules
])
```

ADD:
```tsx
import { useRulesStore } from '../store/rulesStore'

const {
  rules,
  loading,
  fetchRules,
  createRule,
  updateRule,
  toggleRule,
  deleteRule,
} = useRulesStore()
```

Step 2 — Fetch rules on mount:
```tsx
useEffect(() => {
  fetchRules()
}, [])
```

Step 3 — Show a loading skeleton while rules load.
In the rules card body, wrap the rule rows:
```tsx
{loading ? (
  // Show 3 skeleton rows while loading
  Array.from({ length: 3 }).map((_, i) => (
    <div key={i} className="flex items-start gap-md p-md animate-pulse">
      <div className="w-8 h-8 rounded-full bg-surface-container-high shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-surface-container-high rounded w-1/3" />
        <div className="h-10 bg-surface-container-high rounded w-full" />
        <div className="h-3 bg-surface-container-high rounded w-1/4" />
      </div>
    </div>
  ))
) : (
  // Existing rule rows map — unchanged markup
  rules.map((rule, index) => ( ... ))
)}
```

Step 4 — Wire the Add Rule form save button:

REMOVE the inline setRules call.
REPLACE with:
```tsx
const [addName, setAddName]           = useState('')
const [addInstruction, setAddInstruction] = useState('')
const [addSaving, setAddSaving]       = useState(false)
const [addError, setAddError]         = useState('')

const handleAddRule = async () => {
  if (!addName.trim())        { setAddError('Name is required'); return }
  if (!addInstruction.trim()) { setAddError('Instruction is required'); return }
  setAddSaving(true)
  setAddError('')
  try {
    await createRule(addName.trim(), addInstruction.trim())
    setAddName('')
    setAddInstruction('')
    setShowAddForm(false)
  } catch {
    setAddError('Failed to save rule. Please try again.')
  } finally {
    setAddSaving(false)
  }
}
```

In the Add Rule form JSX:
  - Bind name input:     value={addName} onChange={e => setAddName(e.target.value)}
  - Bind instruction:    value={addInstruction} onChange={e => setAddInstruction(e.target.value)}
  - Save button onClick: handleAddRule
  - Save button shows:   addSaving ? 'Saving...' : 'Save Rule'
  - Save button disabled: addSaving
  - Show addError below the textarea if set:
      {addError && <p className="text-meta text-error mt-1">{addError}</p>}

Step 5 — Wire the toggle:

REMOVE: setRules(prev => prev.map(...))
REPLACE onClick of the toggle div:
```tsx
onClick={() => toggleRule(rule.id)}
```

Step 6 — Wire the delete confirmation:

REMOVE: setRules(prev => prev.filter(...))
REPLACE the "Yes, delete" button onClick:
```tsx
onClick={async () => {
  await deleteRule(rule.id)
  setShowDeleteConfirm(null)
}}
```

Step 7 — Wire the Edit Rule modal save button:

In the edit modal save handler:
```tsx
const handleEditSave = async () => {
  if (!editingRule) return
  await updateRule(editingRule.id, {
    name:        editName,
    instruction: editInstruction,
  })
  setEditingRule(null)
}
```

Add state for the edit modal form fields:
```tsx
const [editName, setEditName]               = useState('')
const [editInstruction, setEditInstruction] = useState('')

// When editingRule changes, populate fields
useEffect(() => {
  if (editingRule) {
    setEditName(editingRule.name)
    setEditInstruction(editingRule.instruction)
  }
}, [editingRule])
```

Bind inputs in edit modal:
  name input:        value={editName} onChange={e => setEditName(e.target.value)}
  instruction textarea: value={editInstruction} onChange={e => setEditInstruction(e.target.value)}

Step 8 — Update handleRunRules to use store rules:

The handleRunRules function already reads from `rules`.
Since rules now comes from the store instead of useState,
this should work without changes. Confirm it reads:
  const activeRules = rules.filter(r => r.enabled)

Step 9 — Update the match count display in rule rows:

The matchCount field now comes from the API.
In each rule row meta section find the "X matches this week"
text and update it:
```tsx
<span className="text-meta text-on-surface-variant">
  {rule.matchCount} matches this week
</span>
```
This field is updated by the backend after each /run call
and refreshed when fetchRules() is called again.

Step 10 — After a successful run, refresh rules to get
updated match counts:

In handleRunRules, after setRunStatus('done'):
```tsx
setResults(data.results)
setRunStatus('done')
fetchRules()   // ← refresh to get updated match_count values
```


# ============================================================
# RU-F3 — Wire DryRunModal + Dashboard to real rules
# ============================================================

--- DryRunModal ---

Open src/components/DryRunModal/DryRunModal.tsx.

The DryRunModal needs the active rules list to send to
the backend. Instead of passing rules as a prop (which
would require drilling from Dashboard → Rules page → Modal),
read them directly from the store.

Add at the top of the component:
```tsx
import { useRulesStore } from '../../store/rulesStore'

const { rules } = useRulesStore()
const activeRules = rules.filter(r => r.enabled)
```

Remove the activeRules prop from the component's Props
interface and from wherever it is passed in Dashboard.tsx.

In the useEffect that calls the backend:
```tsx
useEffect(() => {
  if (activeRules.length === 0) {
    setPhase('results')
    setSummary({
      analysed: 0, toMove: 0, noMatch: 0,
      rulesApplied: 0, ruleBreakdown: [], results: [],
    })
    return
  }
  client.post('/rules/dry-run', {
    start_date:  startDate,
    end_date:    endDate,
    rules:       activeRules.map(r => ({
      id:          r.id,
      name:        r.name,
      instruction: r.instruction,
    })),
  })
  .then(({ data }) => {
    setSummary(data)
    setPhase('results')
  })
  .catch(e => {
    console.error('Dry run failed:', e)
    setPhase('results')
  })
}, [])
```

Also update the "Run for Real" button handler:
```tsx
const handleRunForReal = async () => {
  onClose()
  // Navigate to Rules page and trigger run
  // OR call /rules/run directly here
  // For now just close and let user go to Rules page
}
```

--- Dashboard.tsx ---

Open src/pages/Dashboard.tsx.

The Rules Health card on the dashboard shows rule names
and match counts. Wire it to the store so it shows real data.

Add at top of component:
```tsx
import { useRulesStore } from '../store/rulesStore'

const { rules, fetchRules } = useRulesStore()

useEffect(() => {
  fetchRules()
}, [])
```

In the Rules Health card, replace the hardcoded rule rows
with a map over the store rules:
```tsx
{rules.slice(0, 4).map((rule, i) => (
  <div
    key={rule.id}
    className={`flex items-center gap-3 px-3 py-2 rounded-lg bg-surface-container-low ${
      !rule.enabled ? 'opacity-60' : ''
    }`}
  >
    {/* Number circle */}
    <div className="w-6 h-6 bg-primary/10 text-primary text-xs font-bold rounded-full flex items-center justify-center">
      {i + 1}
    </div>
    {/* Rule name */}
    <span className="text-body font-medium text-on-surface flex-1 truncate">
      {rule.name}
    </span>
    {/* Match count */}
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
      rule.matchCount > 0
        ? 'bg-emerald-100 text-emerald-800'
        : 'bg-surface-container text-outline'
    }`}>
      {rule.matchCount > 0 ? `${rule.matchCount} today` : '0 today'}
    </span>
    {/* Status dot */}
    <div className={`w-2 h-2 rounded-full ${
      rule.enabled ? 'bg-emerald-500' : 'bg-outline'
    }`} />
  </div>
))}

{rules.length === 0 && !loading && (
  <p className="text-meta text-outline text-center py-4">
    No rules configured yet
  </p>
)}
```

Also update the Stats strip to show real rule count:
```tsx
// Replace hardcoded "34" for Total Rules with:
{ label: 'Total Rules', value: String(rules.length), ... }
// And active rules:
{ label: 'Active Rules', value: String(rules.filter(r => r.enabled).length), ... }
```

After writing all 5 prompts, verify end-to-end:

  BACKEND CHECKS:
  ✓ GET /api/rules returns the 4 rules from data/rules.json
  ✓ POST /api/rules creates a new rule and writes to file
  ✓ PATCH /api/rules/{id} updates name/instruction
  ✓ PATCH /api/rules/{id}/toggle flips enabled flag
  ✓ DELETE /api/rules/{id} removes from file, returns 204
  ✓ GET /api/rules after delete returns one fewer rule
  ✓ /run endpoint updates match_count in rules.json after run

  FRONTEND CHECKS:
  ✓ Rules.tsx fetches rules from API on mount
  ✓ Skeleton rows shown while loading
  ✓ Add Rule form POSTs and new rule appears in list
  ✓ Toggle calls PATCH .../toggle with optimistic update
  ✓ Delete calls DELETE with optimistic removal
  ✓ Edit modal PATCHes with updated name + instruction
  ✓ After Run All Rules, fetchRules() refreshes match counts
  ✓ Dashboard Rules Health card shows real rule names + counts
  ✓ DryRunModal reads active rules from store (no prop drilling)
  ✓ If API is offline, pages still show last loaded rules
