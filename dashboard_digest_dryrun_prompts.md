# ============================================================
# DASHBOARD + DRY RUN + DAILY DIGEST PROMPTS
# 8 prompts total:
#
# FRONTEND:
#   D-F1: Add Dashboard to router + sidebar nav item
#   D-F2: Dashboard.tsx — page layout + stats + activity
#   D-F3: DryRunModal.tsx — processing + results states
#   D-F4: DigestModal.tsx — running state with SSE progress
#   D-F5: DigestModal.tsx — completed state (digest content)
#
# BACKEND:
#   D-B1: SSE endpoint for digest progress streaming
#   D-B2: Digest generation service (LLM + enterprise invoke)
#   D-B3: Dry run endpoint (rules without moving emails)
#   D-B4: Dashboard summary endpoint
#
# SOURCE: All 4 Stitch HTML files read in full.
# Sidebar and Header are NOT touched — only add Dashboard
# to the nav array in Sidebar.tsx.
# ============================================================


# ============================================================
# D-F1 — Add Dashboard to Sidebar + Router
# ============================================================

Open src/components/Layout/Sidebar.tsx.
Find the NAV_ITEMS array. Add Dashboard as the FIRST item:

```ts
const NAV_ITEMS = [
  { label: 'Dashboard',      icon: 'dashboard',   to: '/dashboard'     }, // ← ADD FIRST
  { label: 'Mailbox',        icon: 'mail',        to: '/mailbox'       },
  { label: 'New Task',       icon: 'add_task',    to: '/new-task'      },
  { label: 'All Tasks',      icon: 'list_alt',    to: '/tasks'         },
  { label: 'Scheduled Task', icon: 'schedule',    to: '/scheduled'     },
  { label: 'Import/Export',  icon: 'swap_horiz',  to: '/import-export' },
  { label: 'Rules',          icon: 'rule',        to: '/rules'         },
  { label: 'Logs',           icon: 'terminal',    to: '/logs'          },
]
```

That is the ONLY change to Sidebar.tsx.

Open src/App.tsx. Add the dashboard route as the default:
```tsx
import Dashboard from './pages/Dashboard'

// Inside Routes — add before all other routes:
<Route index element={<Navigate to="/dashboard" replace />} />
<Route path="/dashboard" element={<Dashboard />} />
```

Also update the existing index redirect from /mailbox to /dashboard.

Create src/pages/Dashboard.tsx placeholder:
```tsx
export default function Dashboard() {
  return <div className="p-8 text-on-surface">Dashboard — coming soon</div>
}
```

Run npm run dev. Confirm:
  ✓ Dashboard appears FIRST in the sidebar
  ✓ Navigating to / redirects to /dashboard
  ✓ Dashboard nav item shows dashboard icon active state
  ✓ All other nav items unchanged


# ============================================================
# D-F2 — Dashboard.tsx: full page layout
# ============================================================

Open src/pages/Dashboard.tsx and replace entirely.

This page uses the existing Header component with title="Dashboard".

Root: <div className="flex-1 flex flex-col overflow-hidden">

--- STATE ---

```tsx
const [showDigestModal, setShowDigestModal] = useState(false)
const [showDryRunModal, setShowDryRunModal] = useState(false)
```

--- MAIN ---

```tsx
<main className="flex-1 overflow-y-auto p-lg bg-background">
  <div className="max-w-6xl mx-auto">
```

--- WELCOME ROW (from dashboard.html exactly) ---

```tsx
<div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-xl gap-4">
  <div>
    <span className="font-meta text-meta text-outline mb-1 block">
      {new Date().toLocaleDateString('en-GB', {
        weekday: 'long', day: '2-digit', month: 'long', year: 'numeric'
      })}
    </span>
    <h1 className="font-page-title text-page-title text-on-surface text-2xl mb-1">
      Good morning, Username
    </h1>
    <p className="font-body text-body text-on-surface-variant">
      Here's your automation overview for today.
    </p>
  </div>
  <button
    onClick={() => setShowDigestModal(true)}
    className="h-10 px-6 bg-primary text-white font-medium rounded-lg flex items-center gap-2 shadow-lg shadow-primary/20 hover:bg-primary-container transition-all active:scale-95"
  >
    <span className="material-symbols-outlined text-[20px]"
      style={{ fontVariationSettings: "'FILL' 1" }}>
      auto_awesome
    </span>
    Generate Digest
  </button>
</div>
```

--- STATS STRIP (from dashboard.html — 4 tiles, lg:grid-cols-4) ---

```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter mb-xl">
  {[
    { label: 'Total Rules', value: '34', valueClass: 'text-on-surface', pulse: false },
    { label: 'Total Tasks', value: '142', valueClass: 'text-on-surface', pulse: false },
    { label: 'Tasks run',   value: '7',   valueClass: 'text-on-surface', pulse: false },
    { label: 'Errors',      value: '2',   valueClass: 'text-error',      pulse: true  },
  ].map((stat) => (
    <div
      key={stat.label}
      className="bg-white p-lg rounded-xl border border-outline-variant flex flex-col gap-1 hover:border-primary transition-colors relative"
    >
      {stat.pulse && (
        <div className="absolute top-4 right-4 w-2 h-2 bg-error rounded-full animate-pulse shadow-[0_0_8px_rgba(186,26,26,0.6)]" />
      )}
      <span className="font-section-label text-section-label text-outline uppercase">
        {stat.label}
      </span>
      <span className={`text-3xl font-bold leading-tight ${stat.valueClass}`}>
        {stat.value}
      </span>
    </div>
  ))}
</div>
```

--- DASHBOARD GRID (from dashboard.html — grid-cols-12) ---

```tsx
<div className="grid grid-cols-12 gap-gutter">

  {/* LEFT col-span-7 */}
  <div className="col-span-12 lg:col-span-7 flex flex-col gap-gutter">

    {/* RECENT ACTIVITY CARD — from dashboard.html exactly */}
    <div className="bg-white rounded-xl border border-outline-variant overflow-hidden">
      <div className="p-lg border-b border-outline-variant">
        <span className="font-section-label text-section-label text-outline uppercase">
          Recent Activity
        </span>
      </div>
      <div className="divide-y divide-outline-variant/50">
        {[
          { icon: 'check_circle', iconBg: 'bg-green-100 text-green-700',
            title: 'Daily Digest completed', sub: 'Outlook Mailbox • 2m ago',  status: 'SUCCESS', statusClass: 'text-outline' },
          { icon: 'settings_suggest', iconBg: 'bg-blue-100 text-blue-700',
            title: 'Rules ran',             sub: 'Global Trigger • 15m ago',  status: 'RAN',     statusClass: 'text-outline' },
          { icon: 'error', iconBg: 'bg-red-100 text-red-700',
            title: 'Invoice Flagging error',sub: 'Accounting Folder • 45m ago',status: 'FAILED',  statusClass: 'text-error'   },
          { icon: 'check_circle', iconBg: 'bg-green-100 text-green-700',
            title: 'SABS tracker success',  sub: 'Workflow Sync • 1h ago',    status: 'SUCCESS', statusClass: 'text-outline' },
          { icon: 'download', iconBg: 'bg-gray-100 text-gray-700',
            title: 'Attachment download info', sub: 'OneDrive • 2h ago',      status: 'INFO',    statusClass: 'text-outline' },
          { icon: 'warning', iconBg: 'bg-amber-100 text-amber-700',
            title: 'Weekly Backup warning', sub: 'System • 3h ago',           status: 'WARNING', statusClass: 'text-amber-600'},
        ].map((row, i) => (
          <div key={i} className="px-lg py-md flex items-center justify-between hover:bg-surface-container-low transition-colors">
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${row.iconBg}`}>
                <span className="material-symbols-outlined text-[18px]">{row.icon}</span>
              </div>
              <div>
                <p className="font-body text-body font-medium">{row.title}</p>
                <p className="font-meta text-meta text-on-surface-variant">{row.sub}</p>
              </div>
            </div>
            <span className={`font-mono text-mono ${row.statusClass}`}>{row.status}</span>
          </div>
        ))}
      </div>
    </div>
  </div>

  {/* RIGHT col-span-5 */}
  <div className="col-span-12 lg:col-span-5 flex flex-col gap-gutter">

    {/* SCHEDULED NEXT CARD — from dashboard.html exactly */}
    <div className="bg-white rounded-xl border border-outline-variant">
      <div className="p-lg border-b border-outline-variant flex justify-between items-center">
        <span className="font-section-label text-section-label text-outline uppercase">
          Scheduled Next
        </span>
        <span className="material-symbols-outlined text-outline text-sm">event</span>
      </div>
      <div className="p-lg flex flex-col gap-4">
        {[
          { name: 'Sync CRM Data',  sub: 'Sales Force Integration',    when: 'In 6m'    },
          { name: 'Daily Digest',   sub: 'Automated Summary Report',   when: 'Tomorrow' },
          { name: 'Purge Logs',     sub: 'Maintenance Task',           when: 'In 18d'   },
        ].map((task, i) => (
          <div key={i} className="flex items-center justify-between p-md bg-surface-container-lowest rounded-lg border border-outline-variant">
            <div className="flex flex-col">
              <span className="font-body text-body font-semibold">{task.name}</span>
              <span className="font-meta text-meta text-on-surface-variant">{task.sub}</span>
            </div>
            <span className="px-3 py-1 bg-secondary-container text-on-secondary-container text-xs rounded-full font-medium">
              {task.when}
            </span>
          </div>
        ))}
      </div>
    </div>

  </div>
</div>
```

--- MODALS (rendered at bottom of return, outside main) ---

```tsx
{showDigestModal && (
  <DigestModal onClose={() => setShowDigestModal(false)} />
)}
{showDryRunModal && (
  <DryRunModal onClose={() => setShowDryRunModal(false)} />
)}
```

Import DigestModal and DryRunModal at the top (create empty
placeholder files for both before running — filled in D-F3/D-F4).


# ============================================================
# D-F3 — DryRunModal.tsx
# ============================================================

Create src/components/DryRunModal/DryRunModal.tsx

Taken DIRECTLY from dry_run.html.

--- TYPES ---

```tsx
interface DryRunResult {
  emailId: string
  subject: string
  from: string
  matchedRuleName: string
  folder: string
  status: 'would_move' | 'no_match'
}

interface DryRunSummary {
  analysed: number
  toMove: number
  noMatch: number
  rulesApplied: number
  ruleBreakdown: Array<{ name: string; folder: string; count: number }>
  results: DryRunResult[]
}
```

--- STATE ---

```tsx
const [phase, setPhase] = useState<'processing' | 'results'>('processing')
const [summary, setSummary] = useState<DryRunSummary | null>(null)
const [resultFilter, setResultFilter] = useState<'all'|'would_move'|'no_match'>('all')
```

On mount, call the backend:
```tsx
useEffect(() => {
  client.post('/rules/dry-run', {
    start_date: startDate,
    end_date: endDate,
    rules: activeRules,
  })
  .then(({ data }) => {
    setSummary(data)
    setPhase('results')
  })
  .catch(console.error)
}, [])
```

--- OVERLAY + CONTAINER (from dry_run.html) ---

```tsx
<>
  <div className="fixed inset-0 z-40 bg-black/40 backdrop-blur-[2px]"
    onClick={onClose} />
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div className="w-full max-w-[720px] bg-[#F4F5F7] rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
```

--- MODAL HEADER (from dry_run.html) ---

```tsx
<header className="bg-white px-lg py-md border-b border-outline-variant flex items-center justify-between">
  <div className="flex items-center gap-md">
    <div className="w-10 h-10 bg-tertiary-fixed rounded-full flex items-center justify-center text-tertiary">
      <span className="material-symbols-outlined text-[24px]">science</span>
    </div>
    <div>
      <h2 className="font-page-title text-page-title text-on-surface">Dry Run Preview</h2>
      <p className="font-meta text-meta text-on-surface-variant">No emails will be moved</p>
    </div>
  </div>
  <div className="flex items-center gap-3">
    {phase === 'results' && (
      <button
        onClick={handleRunForReal}
        className="h-9 px-4 bg-primary text-on-primary rounded-lg text-body font-medium hover:bg-primary-container transition-colors shadow-sm flex items-center gap-2"
      >
        <span className="material-symbols-outlined text-[18px]"
          style={{ fontVariationSettings: "'FILL' 1" }}>
          auto_awesome
        </span>
        Run for Real
      </button>
    )}
    <button onClick={onClose}
      className="w-8 h-8 flex items-center justify-center text-secondary hover:bg-surface-container-high rounded-full transition-colors">
      <span className="material-symbols-outlined">close</span>
    </button>
  </div>
</header>
```

--- PROCESSING STATE BODY ---

When phase === 'processing', show a centered loading card:
```tsx
<div className="flex-1 flex items-center justify-center p-xl">
  <div className="w-full max-w-[400px] bg-white rounded-xl border border-outline-variant p-xl flex flex-col items-center text-center shadow-sm">
    {/* Spinning animation — from daily_digest_running.html */}
    <div className="relative w-20 h-20 mb-6 flex items-center justify-center">
      <div className="absolute inset-0 border-4 border-primary/10 rounded-full" />
      <div className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin" />
      <div className="relative bg-primary-container/10 w-14 h-14 rounded-full flex items-center justify-center text-primary">
        <span className="material-symbols-outlined text-[32px]">science</span>
      </div>
    </div>
    <h3 className="font-body text-gray-900 font-semibold mb-6">Simulating rule matching...</h3>
    <p className="font-meta text-on-surface-variant mb-4">
      No emails will be moved during this preview
    </p>
  </div>
</div>
```

--- RESULTS STATE BODY (from dry_run.html exactly) ---

When phase === 'results' && summary:
```tsx
<div className="flex-1 overflow-y-auto p-lg space-y-lg">

  {/* Summary strip — grid-cols-4 from dry_run.html */}
  <div className="grid grid-cols-4 gap-md">
    {[
      { label: 'Analysed', value: summary.analysed,     valueClass: 'text-on-surface'          },
      { label: 'To Move',  value: summary.toMove,       valueClass: 'text-primary'             },
      { label: 'No Match', value: summary.noMatch,      valueClass: 'text-on-surface-variant'  },
      { label: 'Applied',  value: summary.rulesApplied, valueClass: 'text-on-surface'          },
    ].map((tile) => (
      <div key={tile.label} className="bg-white p-md rounded-xl border border-outline-variant shadow-sm text-center">
        <p className="text-meta font-meta text-on-surface-variant uppercase tracking-wide">
          {tile.label}
        </p>
        <p className={`font-page-title text-page-title mt-xs ${tile.valueClass}`}>
          {tile.value}
        </p>
      </div>
    ))}
  </div>

  {/* Rule breakdown — from dry_run.html */}
  <div className="bg-white rounded-xl border border-outline-variant shadow-sm overflow-hidden">
    <div className="px-lg py-md border-b border-outline-variant bg-surface-container-low">
      <h3 className="font-section-label text-section-label text-on-surface">Rule Matches</h3>
    </div>
    <div className="divide-y divide-outline-variant">
      {summary.ruleBreakdown.map((rule, i) => (
        <div key={i} className="px-lg py-md flex items-center justify-between">
          <div className="flex items-center gap-md">
            <span className="material-symbols-outlined text-primary">filter_list</span>
            <span className="font-body text-body font-medium">{rule.name}</span>
          </div>
          <div className="flex items-center gap-lg">
            <span className="font-mono text-mono bg-surface-container rounded px-sm py-[2px] text-on-secondary-container">
              {rule.folder}
            </span>
            <span className="text-meta font-meta text-on-surface-variant">
              {rule.count} emails
            </span>
          </div>
        </div>
      ))}
    </div>
  </div>

  {/* Filter pills + results list */}
  <div className="bg-white rounded-xl border border-outline-variant overflow-hidden shadow-sm">
    <div className="px-lg py-3 border-b border-outline-variant bg-surface-container-low/40 flex gap-2">
      {(['all', 'would_move', 'no_match'] as const).map(f => (
        <button key={f} onClick={() => setResultFilter(f)}
          className={`text-meta font-meta font-medium px-3 py-1 rounded-full transition-colors ${
            resultFilter === f
              ? 'bg-primary text-on-primary'
              : 'bg-surface-container text-on-surface-variant border border-outline-variant/50'
          }`}>
          {f === 'all' ? `All ${summary.results.length}` :
           f === 'would_move' ? `Would move ${summary.toMove}` :
           `No match ${summary.noMatch}`}
        </button>
      ))}
    </div>
    <div className="divide-y divide-outline-variant max-h-[280px] overflow-y-auto">
      {summary.results
        .filter(r => resultFilter === 'all' || r.status === resultFilter)
        .map(result => (
          <div key={result.emailId}
            className={`px-lg py-3 flex items-center gap-3 border-l-4 ${
              result.status === 'would_move'
                ? 'border-l-emerald-400'
                : 'border-l-outline-variant bg-surface-container/20'
            }`}>
            <div className="flex-1 min-w-0">
              <p className="font-body font-medium text-on-surface truncate">{result.subject}</p>
              <p className="font-meta text-on-surface-variant">{result.from}</p>
            </div>
            {result.status === 'would_move' ? (
              <div className="flex items-center gap-2 shrink-0">
                <span className="material-symbols-outlined text-primary text-[14px]">arrow_forward</span>
                <span className="font-mono text-mono bg-surface-container-high text-on-surface-variant px-2 py-0.5 rounded text-xs">
                  {result.folder}
                </span>
              </div>
            ) : (
              <span className="text-meta text-outline italic shrink-0">Stay in Inbox</span>
            )}
          </div>
        ))}
    </div>
  </div>
</div>
```

--- MODAL FOOTER (from dry_run.html) ---

```tsx
<footer className="bg-white px-lg py-md border-t border-outline-variant flex items-center justify-between">
  <div className="bg-surface-container px-sm py-xs rounded flex items-center gap-xs border border-outline-variant">
    <span className="text-[10px] font-mono font-bold text-on-surface-variant">ESC</span>
    <span className="text-meta font-meta text-on-surface-variant">to close</span>
  </div>
  {phase === 'results' && (
    <div className="flex gap-3">
      <button onClick={onClose}
        className="h-9 px-4 border border-outline-variant bg-white text-on-surface-variant rounded-lg text-body font-medium hover:bg-surface-container">
        Close
      </button>
      <button onClick={handleRunForReal}
        className="h-9 px-6 bg-primary text-white rounded-lg text-body font-medium shadow-sm hover:bg-primary-container">
        Run for Real
      </button>
    </div>
  )}
</footer>
```

Esc key handler: same pattern as TaskViewModal.
Export as default. Props: { onClose, activeRules, startDate, endDate }.


# ============================================================
# D-F4 — DigestModal.tsx: running state with SSE
# ============================================================

Create src/components/DigestModal/DigestModal.tsx

This is the most important prompt — the running state uses
Server-Sent Events (SSE) to receive live progress updates
from the backend as the digest is generated.

--- TYPES ---

```tsx
type DigestPhase = 'running' | 'done' | 'error'

interface ProgressStep {
  id: string
  label: string
  status: 'done' | 'active' | 'pending'
  detail?: string
}

interface DigestContent {
  atAGlance: {
    highPriority: number
    meetingInvites: number
    followUps: number
    others: number
  }
  sections: Array<{
    type: 'high_priority' | 'follow_ups' | 'meeting_invites'
    items: Array<{ sender: string; summary: string }>
  }>
  date: string
}
```

--- STATE ---

```tsx
const [phase, setPhase]         = useState<DigestPhase>('running')
const [steps, setSteps]         = useState<ProgressStep[]>([
  { id: 'fetch',    label: '47 emails',           status: 'pending' },
  { id: 'summarise',label: 'Summarising with AI...', status: 'pending' },
  { id: 'format',   label: 'Formatting digest',   status: 'pending' },
])
const [digest, setDigest]       = useState<DigestContent | null>(null)
const [error, setError]         = useState<string | null>(null)
const eventSourceRef            = useRef<EventSource | null>(null)
```

--- SSE CONNECTION (the key part) ---

Connect to the backend SSE endpoint on mount:

```tsx
useEffect(() => {
  // Open SSE connection to backend
  const es = new EventSource(
    `${import.meta.env.VITE_API_BASE_URL}/digest/stream`
  )
  eventSourceRef.current = es

  // Handle progress events from backend
  es.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data)
    // data: { stepId, status, detail }
    setSteps(prev => prev.map(step =>
      step.id === data.stepId
        ? { ...step, status: data.status, detail: data.detail }
        : step
    ))
  })

  // Handle completion — backend sends the full digest
  es.addEventListener('complete', (e) => {
    const data = JSON.parse(e.data)
    setDigest(data.digest)
    setPhase('done')
    es.close()
  })

  // Handle errors
  es.addEventListener('error_event', (e) => {
    const data = JSON.parse((e as MessageEvent).data)
    setError(data.message)
    setPhase('error')
    es.close()
  })

  es.onerror = () => {
    setError('Connection to server lost')
    setPhase('error')
    es.close()
  }

  // Cleanup on unmount
  return () => {
    es.close()
  }
}, [])
```

--- MODAL CONTAINER (from daily_digest_running.html) ---

```tsx
<>
  <div className="fixed inset-0 z-40 bg-black/40 backdrop-blur-[2px]"
    onClick={onClose} />
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div className="w-full max-w-[640px] bg-[#F4F5F7] rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-white/20">
```

--- MODAL HEADER (from daily_digest_running.html) ---

```tsx
<header className="bg-white px-lg py-md flex items-center justify-between border-b border-[#E5E7EB]">
  <div className="flex items-center gap-3">
    <div className="text-primary-container">
      <span className="material-symbols-outlined text-[24px]">auto_awesome</span>
    </div>
    <div>
      <h2 className="font-page-title text-page-title text-on-surface">Daily Digest</h2>
      <p className="font-meta text-meta text-on-surface-variant">
        {phase === 'running' ? 'Generating...' : new Date().toLocaleDateString()}
      </p>
    </div>
  </div>
  <button onClick={onClose}
    className="w-8 h-8 flex items-center justify-center text-secondary hover:bg-surface-container-high rounded-full">
    <span className="material-symbols-outlined">close</span>
  </button>
</header>
```

--- RUNNING STATE BODY (from daily_digest_running.html exactly) ---

When phase === 'running':
```tsx
<div className="p-xl flex flex-col items-center">
  <div className="w-full max-w-[400px] bg-white rounded-xl border border-[#E5E7EB] p-xl flex flex-col items-center text-center shadow-sm">

    {/* Spinning animation — from daily_digest_running.html */}
    <div className="relative w-20 h-20 mb-6 flex items-center justify-center">
      <div className="absolute inset-0 border-4 border-primary/10 rounded-full" />
      <div className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"
        style={{ animationDuration: '3s' }} />
      <div className="relative bg-primary-container/10 w-14 h-14 rounded-full flex items-center justify-center text-primary"
        style={{ animation: 'pulse 2s ease-in-out infinite' }}>
        <span className="material-symbols-outlined text-[32px]">auto_awesome</span>
      </div>
    </div>

    <h3 className="font-body text-gray-900 font-semibold mb-6">
      Generating your digest...
    </h3>

    {/* Progress steps — driven by SSE events */}
    <div className="w-full space-y-4 text-left">
      {steps.map((step) => (
        <div key={step.id} className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {step.status === 'done' && (
              <span className="material-symbols-outlined text-green-500 text-[18px]">
                check_circle
              </span>
            )}
            {step.status === 'active' && (
              <div className="w-[18px] h-[18px] border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
            )}
            {step.status === 'pending' && (
              <span className="material-symbols-outlined text-gray-400 text-[18px]">
                radio_button_unchecked
              </span>
            )}
            <span className={`text-body ${
              step.status === 'active'  ? 'text-gray-900 font-medium' :
              step.status === 'done'    ? 'text-gray-600' :
              'text-gray-500'
            }`}>
              {step.label}
            </span>
          </div>
          <span className={`text-meta font-mono px-2 py-0.5 rounded ${
            step.status === 'done'   ? 'text-green-600 bg-green-50'  :
            step.status === 'active' ? 'text-primary bg-primary/5'   :
            'text-gray-400'
          }`}>
            {step.status === 'done'   ? 'DONE'    :
             step.status === 'active' ? 'ACTIVE'  :
             'PENDING'}
          </span>
        </div>
      ))}
    </div>
  </div>
</div>
```

--- ERROR STATE BODY ---

When phase === 'error':
```tsx
<div className="flex-1 flex items-center justify-center p-xl">
  <div className="text-center space-y-3">
    <span className="material-symbols-outlined text-error text-[48px]"
      style={{ fontVariationSettings: "'FILL' 1" }}>
      error
    </span>
    <p className="font-body font-semibold text-on-surface">Generation failed</p>
    <p className="font-meta text-on-surface-variant">{error}</p>
    <button onClick={onClose}
      className="h-9 px-4 border border-outline-variant rounded-lg text-body font-medium hover:bg-surface-container mt-2">
      Close
    </button>
  </div>
</div>
```

--- MODAL FOOTER (from daily_digest_running.html) ---

```tsx
<footer className="px-lg py-md bg-white border-t border-[#E5E7EB] flex items-center justify-between">
  <div className="flex items-center gap-2 px-2 py-1 bg-gray-100 rounded-md">
    <span className="text-mono text-[10px] font-bold text-gray-500 uppercase tracking-wider">Esc</span>
    <span className="text-meta text-gray-500">to close</span>
  </div>
  {phase === 'running' && (
    <p className="text-meta text-on-surface-variant">
      This may take a moment...
    </p>
  )}
</footer>
```

Add to index.css if not present:
```css
@keyframes pulse-soft {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(0.95); }
}
```

Props: { onClose: () => void }
Export as default.
The completed digest content is shown in D-F5 below.


# ============================================================
# D-F5 — DigestModal.tsx: completed state (digest content)
# ============================================================

Open src/components/DigestModal/DigestModal.tsx.
Add the 'done' phase rendering inside the existing modal body.

When phase === 'done' && digest, show the full digest content.
This replaces the running state body entirely.

--- DONE STATE BODY (from daily_digest_completed.html exactly) ---

```tsx
<div className="p-lg space-y-lg max-h-[70vh] overflow-y-auto">

  {/* SECTION A — At a Glance (from completed HTML) */}
  <section>
    <h3 className="font-section-label text-section-label text-outline uppercase mb-md">
      At a Glance
    </h3>
    <div className="flex flex-wrap gap-2">
      <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-outline-variant shadow-sm hover:border-error/20 transition-colors">
        <span className="material-symbols-outlined text-error text-[18px]">priority_high</span>
        <span className="font-mono text-sm font-bold">{digest.atAGlance.highPriority}</span>
        <span className="font-meta text-[11px] text-on-surface-variant">High Priority</span>
      </div>
      <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-outline-variant shadow-sm hover:border-primary/20 transition-colors">
        <span className="material-symbols-outlined text-primary text-[18px]">calendar_today</span>
        <span className="font-mono text-sm font-bold">{digest.atAGlance.meetingInvites}</span>
        <span className="font-meta text-[11px] text-on-surface-variant">Meeting Invites</span>
      </div>
      <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-outline-variant shadow-sm hover:border-tertiary/20 transition-colors">
        <span className="material-symbols-outlined text-tertiary text-[18px]">flag</span>
        <span className="font-mono text-sm font-bold">{digest.atAGlance.followUps}</span>
        <span className="font-meta text-[11px] text-on-surface-variant">Follow-ups</span>
      </div>
      <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-outline-variant shadow-sm">
        <span className="material-symbols-outlined text-outline text-[18px]">more_horiz</span>
        <span className="font-mono text-sm font-bold">{digest.atAGlance.others}</span>
        <span className="font-meta text-[11px] text-on-surface-variant">Others</span>
      </div>
    </div>
  </section>

  {/* CONTENT SECTIONS — from daily_digest_completed.html */}
  {digest.sections.map((section, si) => {
    const configs = {
      high_priority:   { label: 'High Priority',   labelClass: 'text-error',    borderColor: 'bg-error'    },
      follow_ups:      { label: 'Follow Ups',       labelClass: 'text-tertiary', borderColor: 'bg-tertiary' },
      meeting_invites: { label: 'Meeting Invites',  labelClass: 'text-primary',  borderColor: 'bg-primary'  },
    }
    const cfg = configs[section.type]
    return (
      <section key={si} className="bg-white border border-outline-variant rounded-xl overflow-hidden shadow-sm">
        <header className="px-md py-sm bg-surface-container-low border-b border-outline-variant flex items-center justify-between">
          <h4 className={`font-section-label text-section-label font-bold uppercase ${cfg.labelClass}`}>
            {cfg.label}
          </h4>
          <button className="flex items-center gap-1 text-[11px] font-bold text-outline hover:text-on-surface transition-colors">
            <span className="material-symbols-outlined text-[14px]">content_copy</span>
            COPY TEXT
          </button>
        </header>
        <div className="p-md space-y-md">
          {section.items.map((item, ii) => (
            <div key={ii} className="flex gap-md">
              <div className={`w-1 ${cfg.borderColor} rounded-full shrink-0`} />
              <div>
                <p className="font-body text-body font-bold text-on-surface">{item.sender}</p>
                <p className="font-body text-body text-on-surface-variant">{item.summary}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    )
  })}
</div>
```

Also update the modal footer for done phase:

```tsx
{/* In modal footer, add done-phase actions */}
{phase === 'done' && (
  <div className="flex gap-3">
    <button
      onClick={() => {/* TODO: copy digest text */}}
      className="h-9 px-4 border border-outline-variant bg-white text-on-surface-variant rounded-lg text-body font-medium hover:bg-surface-container flex items-center gap-2"
    >
      <span className="material-symbols-outlined text-[16px]">content_copy</span>
      Copy
    </button>
    <button
      onClick={() => {/* TODO: POST /digest/send-to-inbox */}}
      className="h-9 px-4 bg-primary text-white rounded-lg text-body font-medium hover:bg-primary-container shadow-sm flex items-center gap-2"
    >
      <span className="material-symbols-outlined text-[16px]"
        style={{ fontVariationSettings: "'FILL' 1" }}>
        send
      </span>
      Send to Inbox
    </button>
  </div>
)}
```

After writing, verify:
  ✓ SSE connection opens on DigestModal mount
  ✓ Steps update in real time as SSE events arrive
  ✓ When 'complete' event fires, digest content replaces spinner
  ✓ EventSource is closed on modal unmount (cleanup)
  ✓ Error state shows if SSE connection fails
  ✓ Esc key closes modal and closes EventSource


# ============================================================
# D-B1 — Backend: SSE endpoint for digest progress
# ============================================================

Create app/routers/digest.py

Server-Sent Events (SSE) stream progress events to the
frontend DigestModal as the digest is being generated.

```python
"""
app/routers/digest.py

GET  /api/digest/stream  — SSE endpoint, streams progress
POST /api/digest/send    — send completed digest to inbox
"""
import json
import logging
import asyncio
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix='/digest', tags=['digest'])
logger = logging.getLogger(__name__)


def _sse_event(event: str, data: dict) -> str:
    """Format a single SSE message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _generate_digest_stream():
    """
    Generator that:
      1. Yields SSE progress events as each step completes
      2. Calls the enterprise LLM to generate the digest
      3. Yields the final 'complete' event with digest content

    The frontend DigestModal listens to these events via
    EventSource and updates the progress steps in real time.
    """
    try:
        # Step 1: fetch emails
        yield _sse_event('progress', {
            'stepId': 'fetch',
            'status': 'active',
            'detail': 'Fetching emails...'
        })

        from app.services.mailbox_service import get_emails
        from app.config import settings

        emails = get_emails(
            is_shared=False,
            mailbox=settings.PERSONAL_MAILBOX,
            filter_type='all',
            limit=200,
        )

        today = datetime.utcnow().date().isoformat()
        todays_emails = [
            e for e in emails
            if e.get('timestamp', '')[:10] == today
        ]

        yield _sse_event('progress', {
            'stepId': 'fetch',
            'status': 'done',
            'detail': f'{len(todays_emails)} emails'
        })

        await asyncio.sleep(0.1)

        # Step 2: call enterprise LLM
        yield _sse_event('progress', {
            'stepId': 'summarise',
            'status': 'active',
            'detail': 'Calling AI...'
        })

        from app.services.digest_service import generate_digest
        digest_content = generate_digest(todays_emails)

        yield _sse_event('progress', {
            'stepId': 'summarise',
            'status': 'done',
            'detail': 'Done'
        })

        await asyncio.sleep(0.1)

        # Step 3: format
        yield _sse_event('progress', {
            'stepId': 'format',
            'status': 'active',
            'detail': 'Formatting...'
        })

        await asyncio.sleep(0.2)

        yield _sse_event('progress', {
            'stepId': 'format',
            'status': 'done',
            'detail': 'Done'
        })

        # Final: send complete event with digest
        yield _sse_event('complete', {
            'digest': digest_content,
        })

    except Exception as e:
        logger.error(f"Digest generation failed: {e}")
        yield _sse_event('error_event', {
            'message': str(e)
        })


@router.get('/stream')
async def stream_digest():
    """
    SSE endpoint — frontend connects with EventSource.
    Streams: progress events → complete event with digest content.
    """
    return StreamingResponse(
        _generate_digest_stream(),
        media_type='text/event-stream',
        headers={
            'Cache-Control':               'no-cache',
            'X-Accel-Buffering':           'no',
            'Access-Control-Allow-Origin': '*',
        },
    )
```

Register in app/main.py:
```python
from app.routers.digest import router as digest_router
app.include_router(digest_router, prefix='/api')
```

IMPORTANT — CORS for SSE:
EventSource does not send custom headers, so the CORS
middleware must allow the frontend origin for SSE.
Confirm app/main.py CORS middleware includes:
  allow_origins=['http://localhost:5173']
  allow_credentials=True

Test the SSE endpoint manually:
  curl -N http://localhost:8000/api/digest/stream

Expected output (lines streaming with delay):
  event: progress
  data: {"stepId": "fetch", "status": "active", "detail": "Fetching emails..."}

  event: progress
  data: {"stepId": "fetch", "status": "done", "detail": "47 emails"}

  event: progress
  data: {"stepId": "summarise", "status": "active", "detail": "Calling AI..."}
  ...
  event: complete
  data: {"digest": {...}}


# ============================================================
# D-B2 — Backend: Digest generation service
# ============================================================

Create app/services/digest_service.py

```python
"""
app/services/digest_service.py

Calls the enterprise LLM (invoke + archive) to generate
a structured daily digest from today's emails.

Uses the same _call_llm pattern as rules_service.py:
  1. Get token (existing function)
  2. Call /invoke with prompt
  3. Extract response + conversation_id
  4. Call /archive to clean up
  5. Parse JSON response
"""
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
logger = logging.getLogger(__name__)


DIGEST_SYSTEM_PROMPT = """You are an executive email assistant.
Analyse the emails provided and generate a structured daily digest.

Classify each email into one of:
  high_priority   - requires urgent action or response today
  follow_ups      - needs a reply but not urgent
  meeting_invites - calendar invites or meeting requests
  others          - newsletters, FYI, no action needed

Return ONLY a valid JSON object with this exact structure.
No markdown, no preamble, no explanation outside the JSON:

{
  "atAGlance": {
    "highPriority": <count>,
    "meetingInvites": <count>,
    "followUps": <count>,
    "others": <count>
  },
  "sections": [
    {
      "type": "high_priority",
      "items": [
        { "sender": "<name>", "summary": "<one sentence summary>" }
      ]
    },
    {
      "type": "follow_ups",
      "items": [...]
    },
    {
      "type": "meeting_invites",
      "items": [...]
    }
  ],
  "date": "<today's date as DD MMM YYYY>"
}

Only include sections that have at least one item.
Keep summaries to one concise sentence each.
"""


def _build_email_block(emails: list[dict]) -> str:
    """Format emails for the LLM prompt."""
    lines = []
    for e in emails:
        lines.append(
            f"From: {e.get('sender_name', '')} <{e.get('sender_email', '')}>\n"
            f"Subject: {e.get('subject', '')}\n"
            f"Preview: {e.get('preview', '')[:200]}\n---"
        )
    return '\n'.join(lines)


def _call_llm(prompt: str) -> str:
    """
    Call enterprise LLM using existing invoke + archive functions.
    Read the existing LLM integration files before filling this in.
    Pattern: token → invoke → extract (response + conv_id) → archive → return text

    Replace the template below with actual function calls:
    """
    # token    = get_llm_access_token()          ← existing function
    # response = invoke_llm(prompt, token)        ← existing function
    # conv_id  = response['conversation_id']      ← actual field name
    # text     = response['response']             ← actual field name
    # archive_conversation(conv_id, token)        ← existing function
    # return text
    raise NotImplementedError(
        "Fill in _call_llm() using existing LLM functions. "
        "See rules_service.py for the same pattern."
    )


def generate_digest(emails: list[dict]) -> dict:
    """
    Generate a structured digest from today's emails.

    Args:
        emails: list of email dicts from mailbox_service

    Returns:
        digest dict matching the DigestContent TypeScript interface
    """
    if not emails:
        return {
            'atAGlance': {
                'highPriority': 0,
                'meetingInvites': 0,
                'followUps': 0,
                'others': 0,
            },
            'sections': [],
            'date': '',
        }

    email_block = _build_email_block(emails)
    full_prompt = f"{DIGEST_SYSTEM_PROMPT}\n\nEmails:\n{email_block}"

    logger.info(f"Calling enterprise LLM for digest: {len(emails)} emails")

    response_text = _call_llm(full_prompt)

    # Strip markdown fences if present
    cleaned = response_text.strip()
    if cleaned.startswith('```'):
        cleaned = cleaned.split('\n', 1)[1].rsplit('```', 1)[0].strip()

    try:
        digest = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON for digest: {e}")
        raise ValueError(f"LLM did not return valid JSON: {e}")

    logger.info("Digest generated successfully")
    return digest
```

NOTE: Fill in `_call_llm()` using the same enterprise
functions you used in rules_service.py. The pattern is
identical — only the prompt content changes.


# ============================================================
# D-B3 — Backend: Dry run endpoint
# ============================================================

Open app/routers/rules.py.
Add a dry-run endpoint that runs all rule matching logic
but NEVER calls move_email(). Returns what WOULD happen.

```python
@router.post('/dry-run')
def dry_run_rules(body: RunRulesRequest):
    """
    Exactly like /run but skips the move_email() step.
    Returns a preview of what would happen if run for real.
    """
    if not body.rules:
        raise HTTPException(status_code=400, detail='No rules provided')

    # Fetch + filter emails (same as /run)
    try:
        mailbox = body.mailbox or settings.PERSONAL_MAILBOX
        all_emails = get_emails(
            is_shared=body.is_shared,
            mailbox=mailbox,
            filter_type='all',
            limit=200,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot fetch emails: {str(e)}")

    from datetime import timedelta
    try:
        start_dt = datetime.strptime(body.start_date, '%Y-%m-%d')
        end_dt   = datetime.strptime(body.end_date,   '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid date format')

    filtered = [
        e for e in all_emails
        if e.get('timestamp', '')[:10] >= body.start_date
        and e.get('timestamp', '')[:10] <= body.end_date
    ]

    if not filtered:
        return {
            'analysed': len(all_emails),
            'toMove': 0, 'noMatch': 0,
            'rulesApplied': len(body.rules),
            'ruleBreakdown': [],
            'results': [],
        }

    # Call LLM (same as /run)
    rules_dicts = [r.dict() for r in body.rules]
    try:
        from app.services.rules_service import run_rules
        decisions = run_rules(rules=rules_dicts, emails=filtered)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM failed: {str(e)}")

    # Build results — NO move_email() call here
    email_map   = {e['id']: e for e in filtered}
    results     = []
    folder_tally: dict[str, dict] = {}

    for decision in decisions:
        email    = email_map.get(decision.get('email_id', ''), {})
        status   = 'would_move' if decision.get('status') == 'moved' else 'no_match'
        folder   = decision.get('folder', '')
        rule_name= decision.get('rule_name', '')

        # Tally per rule for breakdown
        if status == 'would_move' and rule_name:
            if rule_name not in folder_tally:
                folder_tally[rule_name] = {'folder': folder, 'count': 0}
            folder_tally[rule_name]['count'] += 1

        results.append({
            'emailId':         decision.get('email_id', ''),
            'subject':         email.get('subject', ''),
            'from':            email.get('sender_email', ''),
            'matchedRuleName': rule_name,
            'folder':          folder,
            'status':          status,
        })

    return {
        'analysed':      len(filtered),
        'toMove':        sum(1 for r in results if r['status'] == 'would_move'),
        'noMatch':       sum(1 for r in results if r['status'] == 'no_match'),
        'rulesApplied':  len(body.rules),
        'ruleBreakdown': [
            {'name': name, 'folder': v['folder'], 'count': v['count']}
            for name, v in folder_tally.items()
        ],
        'results': results,
    }
```


# ============================================================
# D-B4 — Backend: Dashboard summary endpoint
# ============================================================

Open app/routers/tasks.py (or create app/routers/dashboard.py).
Add a summary endpoint the Dashboard stats strip calls on mount.

```python
# In a new app/routers/dashboard.py:
from fastapi import APIRouter
from datetime import datetime
from app.services.task_store import load_tasks
from app.services.log_service import get_summary, list_logs

router = APIRouter(prefix='/dashboard', tags=['dashboard'])

@router.get('/summary')
def dashboard_summary():
    """
    Returns counts for the Dashboard stats strip.
    Called once on Dashboard mount.
    """
    tasks    = load_tasks()
    log_sum  = get_summary()
    recent   = list_logs(page=1, page_size=6)

    total_rules   = 0   # TODO: count from rules store when implemented
    total_tasks   = len(tasks)
    tasks_run     = log_sum.get('total', 0)
    error_count   = log_sum.get('failed', 0)

    return {
        'totalRules':  total_rules,
        'totalTasks':  total_tasks,
        'tasksRun':    tasks_run,
        'errors':      error_count,
        'recentLogs':  recent.get('logs', []),
        'updatedAt':   datetime.utcnow().isoformat(),
    }
```

Register in app/main.py:
```python
from app.routers.dashboard import router as dashboard_router
app.include_router(dashboard_router, prefix='/api')
```

In Dashboard.tsx, add a useEffect on mount:
```tsx
useEffect(() => {
  client.get('/dashboard/summary').then(({ data }) => {
    // Update the stats strip values from real data
    // For now the mock values in the component are fine
    // Replace them with: data.totalRules, data.totalTasks, etc.
    console.log('Dashboard summary:', data)
  }).catch(() => {
    // API offline — mock data stays visible
  })
}, [])
```

Test:
  curl http://localhost:8000/api/dashboard/summary
  Expected: JSON with totalTasks, tasksRun, errors, recentLogs
