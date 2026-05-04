# ============================================================
# PROMPTS 11–15 OF 20
# ============================================================


# ============================================================
# PROMPT 11 — Logs page: stat cards + filter row + table
# ============================================================

Open src/pages/Logs.tsx and replace it entirely.

This page uses Header component with title="Logs".

Root: <div className="flex-1 flex flex-col overflow-hidden">

Main area from Stitch:
  <main class="flex-1 p-lg flex flex-col gap-lg overflow-y-auto
    bg-surface">

Page heading:
  <div>
    <h2 class="font-page-title text-page-title text-on-surface">
      Execution Logs</h2>
    <p class="font-body text-body text-on-surface-variant mt-1">
      Review the outcomes of your automated tasks.</p>
  </div>

STAT STRIP — grid of 3 cards from Stitch:
  wrapper: class="grid grid-cols-1 md:grid-cols-3 gap-lg"

  Each card:
    class="bg-surface-container-lowest border border-outline-variant
      rounded-xl p-lg flex items-center justify-between
      shadow-sm shadow-black/5"

  Label inside:
    class="font-section-label text-section-label text-on-surface-variant
      uppercase tracking-wider mb-2"

  Number inside:
    Total + Successful: class="font-page-title text-[32px] leading-tight
                          font-bold text-on-surface"
    Failed:             class="font-page-title text-[32px] leading-tight
                          font-bold text-error"

  Icon circle — Total:
    class="w-12 h-12 rounded-full bg-primary/10 flex items-center
      justify-center text-primary"
    icon: monitoring  style: fontVariationSettings: "'FILL' 1", fontSize: '24px'

  Icon circle — Successful:
    class="w-12 h-12 rounded-full bg-primary-container/20 flex items-center
      justify-center text-primary-container"
    icon: check_circle  same style

  Icon circle — Failed:
    class="w-12 h-12 rounded-full bg-error/10 flex items-center
      justify-center text-error"
    icon: error  same style

FILTER ROW from Stitch:
  wrapper: class="flex flex-col md:flex-row md:items-center
    justify-between gap-md bg-surface-container-lowest p-md
    rounded-xl border border-outline-variant"

  Filter pills — PILL style (not underline):
    Active:
      class="font-meta text-meta font-medium px-4 py-1.5 rounded-full
        bg-primary text-on-primary"
    Inactive:
      class="bg-surface-container hover:bg-surface-container-high
        text-on-surface-variant font-meta text-meta font-medium
        px-4 py-1.5 rounded-full border border-outline-variant/50"
    Options: All, Success, Failed, Skipped

  Right side of filter row:
    Search input:
      wrapper: class="relative"
      icon: class="material-symbols-outlined absolute left-3 top-1/2
        -translate-y-1/2 text-outline text-[18px]"  icon: search
      input: class="h-[36px] pl-9 pr-4 w-64 bg-surface-container-lowest
        border border-outline-variant rounded-lg text-body font-body
        text-on-surface placeholder:text-outline focus:outline-none
        focus:border-primary focus:ring-2 focus:ring-primary/20
        transition-all"
        placeholder: "Search logs..."

    Export button:
      class="h-[36px] px-4 bg-surface-container-lowest border
        border-outline-variant text-primary font-body text-body
        font-medium rounded-lg hover:bg-surface-container transition-colors
        flex items-center gap-2"
      icon: download  label: Export Logs

LOG TABLE from Stitch:
  outer: class="bg-surface-container-lowest rounded-xl border
    border-outline-variant overflow-hidden shadow-sm shadow-black/5
    flex-1 flex flex-col"

  Table: class="w-full text-left border-collapse"

  thead row: class="bg-surface-container-low border-b border-outline-variant"
  th cells:  class="py-3 px-6 font-section-label text-section-label
               text-on-surface-variant"
  Columns: Task Name | Timestamp | Duration | Status | (empty — for action)
  Last th (action): add text-right

  tbody: class="font-body text-body text-on-surface divide-y
    divide-outline-variant"

  SUCCESS row:
    class="transition-colors hover:bg-surface-container
      border-l-4 border-l-transparent"

  FAILED row:
    class="bg-error-container/20 border-l-4 border-l-error
      hover:bg-error-container/30 transition-colors"

  td cells: class="py-3 px-6"
  First td (Task Name): add "font-medium pl-5"
  Timestamp td: class="py-3 px-6 font-mono text-mono text-on-surface-variant"
  Duration td:  class="py-3 px-6 font-mono text-mono text-on-surface-variant"

  View Log button:
    class="text-primary hover:text-primary-container font-medium
      text-[13px] hover:underline"
    onClick: opens drawer with that log's data

StatusBadge component — write as a separate function inside the file:
  Success: wrap=bg-primary-container/10 text-primary  dot=bg-primary
  Failed:  wrap=bg-error/10 text-error               dot=bg-error
  Skipped: wrap=bg-surface-container text-on-surface-variant  dot=bg-outline
  Structure:
    <span class="inline-flex items-center gap-1 font-meta text-meta
      px-2.5 py-0.5 rounded-full font-medium {wrap}">
      <span class="w-1.5 h-1.5 rounded-full {dot}"></span>
      {status}
    </span>

PAGINATION from Stitch:
  wrapper: class="bg-surface-container-lowest border-t
    border-outline-variant px-6 py-4 flex items-center
    justify-between mt-auto"
  Left text: class="font-meta text-meta text-on-surface-variant"
    "Showing 1 to {filtered.length} of {LOGS.length} entries"
  Page buttons:
    Active page:   class="w-8 h-8 flex items-center justify-center
                     rounded bg-primary text-on-primary font-meta
                     text-meta font-medium"
    Inactive page: class="w-8 h-8 flex items-center justify-center
                     rounded border border-outline-variant
                     text-on-surface-variant hover:bg-surface-container
                     transition-colors font-meta text-meta font-medium"
    Prev/Next:     class="w-8 h-8 flex items-center justify-center
                     rounded border border-outline-variant
                     text-on-surface-variant hover:bg-surface-container"
                   icons: chevron_left / chevron_right
    Ellipsis:      <span class="text-outline mx-1">...</span>
  Show pages: prev | 1(active) | 2 | 3 | ... | 15 | next

Use this mock data:
```tsx
const LOGS = [
  { id:'1',  taskName:'Invoice Flagging Rule',        timestamp:'2023-10-27 14:32:01', duration:'1.2s',   status:'Success' as const },
  { id:'2',  taskName:'Daily Sync: CRM to Mailchimp', timestamp:'2023-10-27 14:30:00', duration:'45.0s',  status:'Failed'  as const },
  { id:'3',  taskName:'Lead Triage Automation',       timestamp:'2023-10-27 14:15:22', duration:'0.8s',   status:'Success' as const },
  { id:'4',  taskName:'Weekly Report Generator',      timestamp:'2023-10-27 13:00:05', duration:'3.4s',   status:'Success' as const },
  { id:'5',  taskName:'Database Backup: EU-West',     timestamp:'2023-10-27 12:00:00', duration:'120.5s', status:'Failed'  as const },
  { id:'6',  taskName:'Invoice Flagging Rule',        timestamp:'2023-10-27 11:32:01', duration:'1.1s',   status:'Success' as const },
  { id:'7',  taskName:'New User Onboarding Drip',     timestamp:'2023-10-27 10:45:12', duration:'0.4s',   status:'Success' as const },
  { id:'8',  taskName:'Lead Triage Automation',       timestamp:'2023-10-27 09:15:22', duration:'0.9s',   status:'Success' as const },
  { id:'9',  taskName:'Daily Sync: CRM to Mailchimp', timestamp:'2023-10-26 14:30:00', duration:'42.1s',  status:'Success' as const },
  { id:'10', taskName:'Invoice Flagging Rule',        timestamp:'2023-10-26 14:32:01', duration:'1.0s',   status:'Success' as const },
]
type LogStatus = 'Success' | 'Failed' | 'Skipped'
```

State:
  - filter: 'All' | 'Success' | 'Failed' | 'Skipped'  (default 'All')
  - search: string  (default '')
  - drawer: typeof LOGS[0] | null  (default null)

Derived:
  total      = LOGS.length
  successful = LOGS.filter(l => l.status === 'Success').length
  failed     = LOGS.filter(l => l.status === 'Failed').length
  filtered   = apply filter + search

Leave drawer as {drawer && <div>drawer — next prompt</div>}


# ============================================================
# PROMPT 12 — Logs page: log drawer
# ============================================================

Open src/pages/Logs.tsx.
Find: {drawer && <div>drawer — next prompt</div>}
Replace with the full drawer implementation.

Log drawer from Stitch — it slides in from the right:
  Overlay: <div class="fixed inset-0 bg-black/30 z-40"
    onClick={() => setDrawer(null)} />

  Drawer panel:
    class="fixed inset-y-0 right-0 w-[480px] bg-inverse-surface
      z-50 flex flex-col shadow-xl"

  Drawer header:
    class="flex items-center justify-between px-6 py-4
      border-b border-white/10"
    Left:
      <div>
        <h3 class="text-inverse-on-surface font-semibold text-base">
          {drawer.taskName}</h3>
        <p class="text-inverse-on-surface/60 font-mono text-mono mt-0.5">
          {drawer.timestamp}</p>
      </div>
    Right — close button:
      class="text-inverse-on-surface/60 hover:text-inverse-on-surface
        transition-colors"
      icon: close

  Log output area:
    class="flex-1 overflow-y-auto p-lg"
    Inner pre: class="font-mono text-mono space-y-1 whitespace-pre-wrap"

  Log line colors from Stitch:
    INFO lines:    class="text-inverse-on-surface/70"
    ERROR lines:   class="text-error-container"
    SUCCESS lines: class="text-primary-fixed"

  Show these hardcoded log lines:
    [INFO]  Starting task: {drawer.taskName}
    [INFO]  Connecting to mailbox...
    [INFO]  Connection established
    if drawer.status === 'Failed':
      [ERROR] Task failed — connection timeout after {drawer.duration}
    else:
      [SUCCESS] Task completed in {drawer.duration}

The drawer renders outside the main div, directly inside the
outermost return fragment alongside the flex-1 div.
Use a React fragment: <> <div className="flex-1..."> ... </div>
{drawer && (...)} </>


# ============================================================
# PROMPT 13 — NewTask page: shell + left column
# ============================================================

Open src/pages/NewTask.tsx and replace it entirely.

IMPORTANT: The NewTask page has a DIFFERENT background color from
all other pages. From Stitch: bg-[#F4F5F7] (NOT bg-surface/bg-background).

Root element:
  <div className="flex-1 flex flex-col min-h-screen bg-[#F4F5F7]">

The NewTask page does NOT use the Header component.
It has its own sticky top bar from Stitch:
  <header class="flex items-center justify-between px-8 py-3
    sticky top-0 bg-[#F4F5F7] h-16 border-b border-gray-200 z-40">

    Left side:
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-gray-200 rounded-lg transition-colors">
          <span class="material-symbols-outlined text-gray-500">
            arrow_back</span>
        </button>
        <h2 class="font-page-title text-page-title text-gray-900">
          New Task</h2>
      </div>

    Right side:
      <div class="flex items-center gap-3">
        <button class="px-4 py-2 border border-gray-300 bg-white
          rounded-lg font-medium text-gray-700 hover:bg-gray-50
          transition-colors">Cancel</button>
        <button class="px-4 py-2 bg-[#4F6BFF] text-white rounded-lg
          font-medium hover:bg-[#3D55CC] transition-colors shadow-sm">
          Save Task</button>
      </div>

Form layout wrapper from Stitch:
  <div class="max-w-[1100px] mx-auto px-8 py-10 flex gap-10
    items-start">

LEFT COLUMN from Stitch:
  <div class="w-[300px] sticky top-28 space-y-6">

Task type selector card from Stitch:
  <div class="bg-white rounded-xl border border-gray-200
    overflow-hidden shadow-sm">
    <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
      <span class="font-section-label text-section-label
        text-gray-400 uppercase">TASK TYPE</span>
    </div>
    <div class="divide-y divide-gray-100">

Each option row:
  SELECTED:
    class="p-4 bg-primary-container/5 border-l-4 border-primary
      cursor-pointer flex items-start gap-3"
  UNSELECTED:
    class="p-4 hover:bg-gray-50 cursor-pointer flex items-start
      gap-3 transition-colors"
    (no border-l or transparent border-l)

  Icon box per type:
    Draft/Send:  class="w-8 h-8 rounded-lg bg-primary-container/10
                   flex items-center justify-center text-primary"
                 icon: drafts
    Reminder:    class="w-8 h-8 rounded-lg bg-teal-50 flex items-center
                   justify-center text-teal-600"
                 icon: notification_important
    Tracking:    class="w-8 h-8 rounded-lg bg-amber-50 flex items-center
                   justify-center text-amber-600"
                 icon: track_changes
    Download:    class="w-8 h-8 rounded-lg bg-rose-50 flex items-center
                   justify-center text-rose-600"
                 icon: download

  Label: class="text-sm font-semibold text-gray-900 leading-tight"
  Desc:  class="text-xs text-gray-500 mt-0.5"

  Labels + descriptions:
    Draft / Send Mail  → "Compose & send emails"
    Reminder Mail      → "Automated follow-ups"
    Email Tracking     → "Monitor & save emails"
    Download           → "Download attachments"

Jump nav from Stitch:
  <nav class="space-y-1">
  Active link:
    class="flex items-center px-4 py-2 text-primary font-semibold
      border-l-2 border-primary"
  Inactive link:
    class="flex items-center px-4 py-2 text-gray-500
      hover:text-gray-900 border-l-2 border-transparent
      transition-all"
  All links are <a href="#section-id"> anchor links.

Show these jump nav links based on taskType:
  Always:  Basic Info (#basic-info)
  Draft/Reminder: Recipients | Email Content | Attachments | Find & Replace
  Tracking/Download: Email Filter | Save Email | Attachments & Downloads
  Tracking only (extra): Tracking Config (between Email Filter and Save Email)

State for this prompt:
  type TaskType = 'draft' | 'reminder' | 'tracking' | 'download'
  const [taskType, setTaskType] = useState<TaskType>('draft')

Right column placeholder:
  <div className="flex-1 space-y-8 max-w-[760px]">
    {/* form sections — next prompts */}
  </div>

Sticky bottom save bar from Stitch:
  <div class="fixed bottom-0 left-[260px] right-0 bg-white
    border-t border-gray-200 py-4 px-12 flex items-center
    justify-between z-50">
    <div class="flex items-center gap-4">
      <p class="text-xs text-gray-500">
        * All fields marked with asterisk are required</p>
      <div class="h-4 w-px bg-gray-200"></div>
      <p class="text-xs text-gray-400 italic flex items-center gap-1">
        <span class="material-symbols-outlined text-[14px]">
          cloud_done</span>
        Draft auto-saved at 14:32:05
      </p>
    </div>
    <div class="flex items-center gap-4">
      <button class="px-6 py-2 border border-gray-300 bg-white
        rounded-lg font-medium text-gray-700 hover:bg-gray-50
        transition-colors">Cancel</button>
      <button class="px-10 py-2 bg-[#4F6BFF] text-white rounded-lg
        font-bold hover:bg-[#3D55CC] transition-colors
        shadow-lg shadow-primary/20">Save Task</button>
    </div>
  </div>

Also add pb-32 to the form layout wrapper div so content is not
hidden behind the sticky bottom bar.


# ============================================================
# PROMPT 14 — NewTask page: Basic Info + Recipients +
#             Email Content sections
# ============================================================

Open src/pages/NewTask.tsx.
Find the right column placeholder comment and replace with the
first three form sections.

Add this state (using useReducer for the whole form):

```tsx
interface FormState {
  processName: string; needToProcess: boolean
  schedule: string; isSharedMailbox: 'Y' | 'N'; mailbox: string
  logPath: string; to: string; cc: string; subject: string
  bodySource: 'excel' | 'docx'; bodyPath: string
  draftOrSend: 'draft' | 'send'; votingOption: string
  reminderBodyPath: string
  attachmentFolder: string; attachmentFileName: string
  findReplace: Array<{ find: string; replace: string }>
  partialSubject: boolean; screeningFolder: string
  startDate: string; endDate: string; dueDate: string
  toTracking: string; saveEmail: boolean; saveBoth: string
  saveAs: string; downloadAttachment: boolean
  allOrSpecific: string; fileType: string; extractZip: boolean
}
const init: FormState = {
  processName:'', needToProcess:true, schedule:'every15',
  isSharedMailbox:'N', mailbox:'', logPath:'',
  to:'', cc:'', subject:'', bodySource:'docx', bodyPath:'',
  draftOrSend:'draft', votingOption:'', reminderBodyPath:'',
  attachmentFolder:'', attachmentFileName:'',
  findReplace:[{find:'{{DATE}}',replace:'Monday, 5 May'},{find:'',replace:''}],
  partialSubject:false, screeningFolder:'', startDate:'', endDate:'',
  dueDate:'', toTracking:'', saveEmail:false, saveBoth:'both',
  saveAs:'pdf', downloadAttachment:false, allOrSpecific:'all',
  fileType:'', extractZip:false,
}
function reducer(s: FormState, p: Partial<FormState>): FormState {
  return { ...s, ...p }
}
const [form, update] = useReducer(reducer, init)
```

Also add these derived booleans:
  const isDraftOrReminder = taskType === 'draft' || taskType === 'reminder'
  const isTrackingOrDownload = taskType === 'tracking' || taskType === 'download'

SECTION 1 — Basic Info from Stitch:
  <section class="bg-white rounded-xl p-8 border border-gray-200
    shadow-sm scroll-mt-24" id="basic-info">

  Section header row from Stitch:
    <div class="flex justify-between items-start mb-6">
      <h3 class="font-page-title text-gray-900">Basic Info</h3>
      Enable workflow toggle (right side)
    </div>

  Toggle from Stitch (used throughout form):
    ON:  <button class="relative inline-flex h-6 w-11 items-center
           rounded-full bg-primary">
           <span class="translate-x-6 inline-block h-4 w-4 transform
             rounded-full bg-white transition"></span>
         </button>
    OFF: same button but bg-gray-300 and translate-x-1

  Form fields wrapper: class="grid grid-cols-1 gap-6"

  Process Name field:
    <label class="block text-sm font-medium text-gray-700 mb-1.5">
      Process Name *</label>
    <input class="w-full h-9 rounded-lg border-gray-300 focus:ring-2
      focus:ring-primary/20 focus:border-primary transition-all
      text-body" placeholder="e.g. Daily Sales Report Automation"
      type="text"/>

  Schedule segmented control from Stitch:
    <label class="block text-sm font-medium text-gray-700 mb-2.5">
      Schedule</label>
    <div class="inline-flex p-1 bg-gray-100 rounded-lg w-full">
    Active option:
      class="flex-1 px-3 py-1.5 text-xs font-semibold bg-white
        rounded-md shadow-sm text-gray-900"
    Inactive option:
      class="flex-1 px-3 py-1.5 text-xs font-medium text-gray-500
        hover:text-gray-700"
    Options: Every 15 min (every15) | Every 1 hour (every1h) |
             Daily at time (daily) | Ad hoc (adhoc)
    When daily is selected, show a time input below:
      class="mt-2 h-9 rounded-lg border-gray-300 focus:ring-2
        focus:ring-primary/20 focus:border-primary text-body"
      type="time"

  Need to Process toggle row:
    <div class="flex justify-between items-center">
      <label class="block text-sm font-medium text-gray-700">
        Need to Process</label>
      {toggle}
    </div>

  Is Shared Mailbox + Mailbox grouped block from Stitch:
    <div class="bg-[#F8FAFC] border-l-4 border-[#4F6BFF] p-4
      rounded-r-lg space-y-4">

    Is Shared Mailbox:
      <label class="block text-sm font-medium text-gray-700 mb-1.5">
        Is Shared Mailbox</label>
      <div class="inline-flex p-1 bg-gray-200 rounded-lg">
      Active:   class="px-4 py-1 text-xs font-semibold bg-white
                  rounded shadow-sm text-gray-900"
      Inactive: class="px-4 py-1 text-xs font-medium text-gray-500
                  hover:text-gray-700"
      Options: Y | N (default N)

    Mailbox input — has mail icon prefix from Stitch:
      <label class="block text-sm font-medium text-gray-700 mb-1.5">
        Mailbox</label>
      <div class="relative">
        <span class="material-symbols-outlined absolute left-3 top-1/2
          -translate-y-1/2 text-gray-400 text-lg">mail</span>
        <input class="w-full h-9 pl-10 rounded-lg border-gray-300
          focus:ring-2 focus:ring-primary/20 focus:border-primary
          text-body"
          placeholder={form.isSharedMailbox==='Y'
            ? 'finance@company.com' : 'your.name@company.com'}
          type="email"/>
      </div>

  Log Output Folder Path — has folder icon prefix from Stitch:
    <label class="block text-sm font-medium text-gray-700 mb-1.5">
      Log Output Folder Path</label>
    <div class="relative">
      <span class="material-symbols-outlined absolute left-3 top-1/2
        -translate-y-1/2 text-gray-400 text-lg">folder</span>
      <input class="w-full h-9 pl-10 rounded-lg border-gray-300
        focus:ring-2 focus:ring-primary/20 focus:border-primary
        text-body" placeholder="C:\Automation\Logs" type="text"/>
    </div>

SECTION 2 — Recipients (show only when isDraftOrReminder):
  <section class="bg-white rounded-xl p-8 border border-gray-200
    shadow-sm scroll-mt-24" id="recipients">
  Heading: same h3 style, text "Recipients"
  TO textarea (required *):
    class="w-full rounded-lg border-gray-300 focus:ring-2
      focus:ring-primary/20 focus:border-primary text-body"
    rows={2} placeholder="Enter recipient email addresses,
      separated by semicolon..."
  CC textarea (not required):
    same class, rows={2}, placeholder "Enter CC addresses..."

SECTION 3 — Email Content (show only when isDraftOrReminder):
  <section class="bg-white rounded-xl p-8 border border-gray-200
    shadow-sm scroll-mt-24" id="email-content">
  Heading: "Email Content"

  Subject field (required *): standard input

  Body Source radio group from Stitch:
    <label class="block text-sm font-medium text-gray-700">
      Body Source</label>
    <div class="flex gap-6">
    Each radio:
      <label class="flex items-center gap-2 cursor-pointer">
        <input class="text-primary focus:ring-primary"
          name="body-source" type="radio"
          checked={form.bodySource === value}
          onChange={() => update({ bodySource: value })}/>
        <span class="text-sm text-gray-700">{label}</span>
      </label>
    Options: Direct Input (docx) | File Path (.html, .txt) (excel)

  Email Body Path — file upload area from Stitch:
    <div class="p-4 bg-gray-50 border border-dashed border-gray-300
      rounded-lg text-center cursor-pointer hover:bg-gray-100
      transition-colors">
      <span class="material-symbols-outlined text-gray-400 mb-2">
        upload_file</span>
      <p class="text-sm text-gray-600">
        Click to select body template or drag file here</p>
    </div>

  Draft/Send mode block from Stitch:
    When draftOrSend === 'send' — amber warning block:
      <div class="flex items-center justify-between p-4 bg-amber-50
        rounded-lg border border-amber-200">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-amber-600">
            warning</span>
          <div>
            <p class="text-sm font-semibold text-amber-900">
              Task Mode: Send Immediately</p>
            <p class="text-xs text-amber-700">
              Warning: Emails will be sent directly without manual review.</p>
          </div>
        </div>
        <button class="px-3 py-1.5 bg-amber-600 text-white text-xs
          font-semibold rounded-md"
          onClick={() => update({ draftOrSend: 'draft' })}>
          Change to Draft</button>
      </div>
    When draftOrSend === 'draft' — show segmented control to switch modes.

  Reminder body path (show only when taskType === 'reminder'):
    Wrap in: <div class="border-l-4 border-primary pl-4 space-y-2">
    Label: "Reminder Email Body Path (.docx)"
    Same file upload area style as Email Body Path above

  Voting Options:
    Standard input, placeholder "Approve; Reject; Maybe"
    Hint below: class="mt-1 text-xs text-gray-500"
      "Leave blank if not needed"


# ============================================================
# PROMPT 15 — NewTask page: Attachments + Find & Replace +
#             Tracking/Download sections
# ============================================================

Open src/pages/NewTask.tsx.
Add the remaining form sections inside the right column,
after the Email Content section.

SECTION 4 — Attachments (show only when isDraftOrReminder):
  <section class="bg-white rounded-xl p-8 border border-gray-200
    shadow-sm scroll-mt-24" id="attachments">
  Heading: "Attachments"
  Grid wrapper: class="grid grid-cols-2 gap-6"

  Folder Path (col-span-2) — has folder_open icon prefix:
    <div class="col-span-2">
    <label ...>Folder Path</label>
    <div class="relative">
      <span class="material-symbols-outlined absolute left-3 top-1/2
        -translate-y-1/2 text-gray-400 text-lg">folder_open</span>
      <input class="w-full h-9 pl-10 rounded-lg border-gray-300
        focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
        placeholder="C:\Exports\DailyReports"/>
    </div>

  File Name / Wildcard (col-span-2):
    Standard input, placeholder "report_*.pdf"
    Hint: class="mt-2 text-xs text-gray-500"
      "Hint: Use * as a wildcard for dynamic dates or IDs
       (e.g., report_*.pdf will attach all PDFs in the folder)."

SECTION 5 — Find & Replace (show only when isDraftOrReminder):
  <section class="bg-white rounded-xl p-8 border border-gray-200
    shadow-sm scroll-mt-24" id="find-replace">

  Header row from Stitch:
    <div class="flex justify-between items-center mb-6">
      <h3 class="font-page-title text-gray-900">Find & Replace</h3>
      <span class="text-xs text-gray-500 italic">
        Dynamic data variables for template injection</span>
    </div>

  Pairs list: class="space-y-3"
  Each pair row from Stitch:
    <div class="flex gap-3 items-center">
      <div class="flex-1 flex gap-2">
        Find input:
          class="flex-1 h-9 rounded-lg border-gray-300 bg-gray-50
            font-mono text-xs"
          placeholder="{{VARIABLE_NAME}}"
        Arrow:
          <div class="flex items-center text-gray-400">
            <span class="material-symbols-outlined">arrow_forward</span>
          </div>
        Replace input:
          class="flex-1 h-9 rounded-lg border-gray-300 text-sm"
          placeholder="Replacement Text"
      </div>
      Delete button:
        class="p-1.5 text-gray-400 hover:text-error transition-colors"
        icon: delete
        onClick: remove this pair from array
    </div>

  Add replacement link from Stitch:
    <button class="mt-6 flex items-center gap-2 text-primary
      font-semibold text-sm hover:underline">
      <span class="material-symbols-outlined text-sm">add</span>
      Add replacement
    </button>
  Disabled/hidden when findReplace.length >= 5.

SECTION 6 — Email Filter (show only when isTrackingOrDownload):
  id="email-filter"
  Heading: "Email Filter"
  Fields:
    Subject Line (required): standard input, placeholder "Invoice Q3 2024"
    Partial Subject toggle:
      same toggle pattern, label "Allow partial subject matching"
    Screening Mailbox Folder: standard input, placeholder "Inbox\Finance"
    Start Date: <input type="date" class="w-full h-9 rounded-lg
                  border-gray-300 text-body">
    End Date:   same as Start Date

  Wrap Start/End in: class="grid grid-cols-2 gap-4"

SECTION 7 — Tracking Config (show only when taskType === 'tracking'):
  id="tracking-config"
  Heading: "Tracking Config"
  Fields:
    Due Date: date input (same style)
    TO: Stakeholders: textarea rows={2}

SECTION 8 — Save Email (show only when isTrackingOrDownload):
  id="save-email"
  Heading: "Save Email"
  Fields:
    Save Email toggle (master): label "Save Email"
    When saveEmail is true, show indented sub-fields:
      Wrap in: <div class="pl-4 space-y-4 border-l-2 border-gray-200 mt-2">
      Save scope radio: "Both" | "Specific only"
        same radio style as Body Source
      Save as segmented: "PDF" | ".msg"
        same segmented style as Schedule

SECTION 9 — Attachments & Downloads (show only when isTrackingOrDownload):
  id="downloads"
  Heading: "Attachments & Downloads"
  Fields:
    Download Attachment toggle (master): label "Download Attachment"
    When downloadAttachment is true, show:
      Scope radio: "All attachments" | "Specific only"
      Attachment File Type: standard input, placeholder ".xlsx, .pdf, .zip"
      If Zip, Extract All toggle: label "If Zip, Extract All"

After completing all sections, verify:
  1. Switching taskType in left column shows/hides correct sections
  2. All toggle handlers correctly update form state
  3. Find & Replace add/remove works correctly
  4. The sticky bottom bar stays fixed at bottom-0 left-[260px]
  5. No TypeScript errors
