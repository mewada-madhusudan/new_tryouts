# ============================================================
# PROMPTS 6–10 OF 20
# ============================================================


# ============================================================
# PROMPT 6 — Mailbox page: shell + email list panel
# ============================================================

Open src/pages/Mailbox.tsx and replace it entirely.

IMPORTANT: The Mailbox page does NOT use the Header component.
It builds its own inline header — exactly as the Stitch HTML shows.
The Stitch mailbox body is:
  <body class="bg-background text-on-background font-body text-body
    antialiased flex h-screen overflow-hidden">

Since AppLayout already provides the outer flex wrapper and the
sidebar offset, the Mailbox page root element must be:
  <div className="flex-1 flex flex-col h-screen overflow-hidden">

The inline header from Stitch mailbox screen:
  <header class="docked full-width top-0 h-[56px] border-b
    border-[#E5E7EB] bg-surface-container-lowest flex justify-between
    items-center px-6 z-10 shrink-0">
    Left: <span class="font-page-title text-page-title text-on-surface">
            Mailbox</span>
    Right: notifications button + user avatar block (same as Header.tsx)
    Avatar: bg-primary-container text-on-primary-container with letter "U"

The main workspace from Stitch:
  <main class="flex-1 flex overflow-hidden bg-background">

Email list panel from Stitch:
  <div class="w-[320px] shrink-0 border-r border-outline-variant
    bg-surface-container-lowest flex flex-col h-full">

Filter buttons from Stitch (All = active, Unread = inactive):
  Active:   class="px-3 py-1 rounded-full bg-primary-container
              text-on-primary-container text-meta font-meta font-medium"
  Inactive: class="px-3 py-1 rounded-full bg-surface-variant
              text-on-surface-variant text-meta font-meta font-medium
              hover:bg-surface-container-highest transition-colors"

Search input from Stitch:
  <div class="relative">
    <span class="material-symbols-outlined absolute left-3 top-1/2
      -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
    <input class="w-full h-[36px] pl-9 pr-3 rounded-lg border
      border-outline-variant bg-surface focus:border-primary
      focus:ring-1 focus:ring-primary outline-none text-body
      font-body transition-all" placeholder="Search emails..."
      type="text"/>
  </div>

Email list rows from Stitch — there are two states:

SELECTED/UNREAD row:
  <div class="p-4 border-b border-outline-variant bg-[#EEF1FF]
    border-l-[3px] border-l-primary cursor-pointer">
  Avatar: bg-tertiary-container text-on-tertiary-container
  Sender: class="font-semibold text-on-surface text-[14px]"
  Time:   class="text-meta font-meta text-primary font-medium"
  Subject: class="font-medium text-on-surface text-[13px] mb-1
             line-clamp-1 text-primary"
  Preview: class="text-on-surface-variant text-meta font-meta line-clamp-2"

READ row:
  <div class="p-4 border-b border-outline-variant bg-surface-container-lowest
    hover:bg-surface-container-low transition-colors cursor-pointer
    border-l-[3px] border-l-transparent">
  Avatar colors vary: bg-secondary-container text-on-secondary-container
                   or bg-surface-dim text-on-surface
  Sender: class="text-on-surface text-[14px]" (no font-semibold)
  Time:   class="text-meta font-meta text-on-surface-variant"
  Subject: class="text-on-surface text-[13px] mb-1 line-clamp-1"
  Preview: class="text-secondary text-meta font-meta line-clamp-2"

Avatar shared structure:
  <div class="w-8 h-8 rounded-full flex items-center justify-center
    text-meta font-bold {avatarClass}">{initials}</div>

Row inner structure from Stitch:
  <div class="flex justify-between items-start mb-1">
    <div class="flex items-center gap-2">
      {avatar} {sender}
    </div>
    {time}
  </div>
  <div class="pl-10">
    {subject h4}
    {preview p}
  </div>

Use this exact data array for the 3 emails:

```tsx
const EMAILS = [
  {
    id: '1', initials: 'SJ',
    avatarClass: 'bg-tertiary-container text-on-tertiary-container',
    sender: 'Sarah Jenkins', isUnread: true,
    subject: 'Q3 Marketing Report Review',
    preview: 'Hi team, I have attached the latest numbers for the Q3 campaign. We saw a significant increase in engagement...',
    time: '10:42 AM',
  },
  {
    id: '2', initials: 'MR',
    avatarClass: 'bg-secondary-container text-on-secondary-container',
    sender: 'Mark Roberts', isUnread: false,
    subject: 'Client Onboarding Process Updates',
    preview: 'Please review the attached PDF for the new workflow. We need to implement these changes by next week...',
    time: 'Yesterday',
  },
  {
    id: '3', initials: 'IT',
    avatarClass: 'bg-surface-dim text-on-surface',
    sender: 'IT Support', isUnread: false,
    subject: 'Scheduled Maintenance Warning',
    preview: 'The servers will be down for routine maintenance this Saturday from 2AM to 4AM EST.',
    time: 'Oct 12',
  },
]
```

Write the full Mailbox component with useState for:
  - filter: 'All' | 'Unread'  (default 'All')
  - selectedId: string        (default '1')
  - search: string            (default '')

This prompt covers only the LEFT panel and header.
Leave the email viewer panel as:
  <div className="flex-1 bg-surface-container-lowest h-full">
    {/* viewer — added in Prompt 7 */}
  </div>


# ============================================================
# PROMPT 7 — Mailbox page: email viewer panel
# ============================================================

Open src/pages/Mailbox.tsx.
Fill in the email viewer panel div (the right side of main).

Email viewer panel wrapper from Stitch:
  <div class="flex-1 flex flex-col bg-surface-container-lowest
    h-full overflow-hidden">

Toolbar from Stitch (sits at top of viewer):
  <div class="h-[56px] border-b border-outline-variant flex items-center
    px-6 gap-4 shrink-0 bg-surface-container-lowest">

  Reply button:
    class="flex items-center gap-2 h-[36px] px-3 rounded
      text-on-surface-variant hover:bg-surface-container-high
      transition-colors"
    icon: reply   label: Reply

  Forward button: same class, icon: forward, label: Forward

  Divider:
    <div class="w-[1px] h-[24px] bg-outline-variant mx-2"></div>

  Archive button: same class as Reply, icon: archive, label: Archive

  Delete button (note: different color, ml-auto):
    class="flex items-center gap-2 h-[36px] px-3 rounded
      text-error hover:bg-error-container transition-colors ml-auto"
    icon: delete   label: Delete

  All button labels use:
    class="font-section-label text-section-label"

Email content area from Stitch:
  <div class="flex-1 overflow-y-auto p-lg">
    <div class="max-w-3xl mx-auto">

Subject heading:
  <h2 class="font-page-title text-[24px] font-bold text-on-surface mb-6">
    {selected.subject}</h2>

Sender metadata block:
  <div class="flex items-start justify-between mb-8 pb-6
    border-b border-outline-variant">
    <div class="flex items-center gap-4">
      Avatar (large): w-12 h-12 rounded-full, same avatarClass
      <div>
        <div class="font-semibold text-on-surface text-[16px]">
          {sender}
          <span class="text-on-surface-variant font-normal text-sm ml-1">
            &lt;sender@company.com&gt;</span>
        </div>
        <div class="text-on-surface-variant text-sm mt-1">
          To: Marketing Team, Executive Board</div>
      </div>
    </div>
    <div class="text-on-surface-variant text-sm">Oct 14, 2023, {time}</div>
  </div>

Email body:
  <div class="prose prose-sm max-w-none text-on-surface leading-relaxed
    text-body font-body space-y-4">
    <p>Hi team,</p>
    <p>{selected.preview}</p>
    <p>Please review the attached deck before our 2 PM sync tomorrow.</p>
    <p>Best regards,<br/>{selected.sender}</p>
  </div>

Attachment section:
  <div class="mt-8 pt-6 border-t border-outline-variant">
    <h3 class="font-section-label text-section-label
      text-on-surface-variant mb-4 uppercase">Attachments (1)</h3>
    <div class="flex items-center gap-3 p-3 border border-outline-variant
      rounded-lg w-max hover:bg-surface-container-lowest cursor-pointer
      transition-colors">
      <div class="w-10 h-10 rounded bg-error-container text-error
        flex items-center justify-center">
        <span class="material-symbols-outlined"
          style="font-variation-settings: 'FILL' 1;">picture_as_pdf</span>
      </div>
      <div>
        <div class="font-medium text-sm text-on-surface">
          Q3_Marketing_Report_Final.pdf</div>
        <div class="text-xs text-on-surface-variant mt-0.5">2.4 MB</div>
      </div>
    </div>
  </div>

The `selected` object is EMAILS.find(e => e.id === selectedId) ?? EMAILS[0].
The icon in the attachment uses style={{ fontVariationSettings: "'FILL' 1" }}.

After this prompt the Mailbox page should be complete and match
the Stitch design exactly. Do not add any extra elements.


# ============================================================
# PROMPT 8 — ScheduledTask page
# ============================================================

Open src/pages/ScheduledTask.tsx and replace it entirely.

This page uses the Header component with title="Scheduled Task".

Root element:
  <div className="flex-1 flex flex-col overflow-hidden">

After Header, the main area from Stitch:
  <main class="flex-1 overflow-y-auto p-4 md:p-lg bg-surface">
    <div class="max-w-6xl mx-auto space-y-6">

Page header row from Stitch:
  <div class="flex flex-col sm:flex-row sm:items-center
    justify-between gap-4">
    <h2 class="font-page-title text-page-title text-on-surface">
      Task List</h2>
    <button class="h-[36px] px-4 bg-primary text-on-primary rounded
      font-medium text-sm flex items-center justify-center gap-2
      hover:bg-primary-container transition-colors shadow-sm">
      <span class="material-symbols-outlined text-[18px]">add</span>
      New Task
    </button>

The card container from Stitch:
  <div class="bg-surface-container-lowest rounded-xl border
    border-outline-variant shadow-[0_4px_24px_rgba(0,0,0,0.02)]
    overflow-hidden">

Filter tabs from Stitch — note these are UNDERLINE tabs, not pills:
  All (active):
    class="py-4 text-sm font-medium text-primary border-b-2 border-primary"
  Enabled/Disabled (inactive):
    class="py-4 text-sm font-medium text-on-surface-variant
      hover:text-on-surface transition-colors border-b-2 border-transparent"
  Tab wrapper:
    class="border-b border-outline-variant px-6 flex items-center gap-6
      bg-surface-container-lowest"

Task rows wrapper:
  <div class="divide-y divide-outline-variant">

Each ENABLED task row from Stitch:
  <div class="p-6 flex flex-col lg:flex-row lg:items-center
    justify-between gap-4 hover:bg-surface-container-low/30
    transition-colors">
  (no opacity-75)

Each DISABLED task row from Stitch adds: opacity-75

Left side of row:
  <div class="flex items-start gap-4 flex-1">
    icon div (enabled):   class="w-10 h-10 rounded bg-primary/10
                            flex items-center justify-center text-primary shrink-0"
    icon div (disabled):  class="w-10 h-10 rounded bg-surface-variant
                            flex items-center justify-center
                            text-on-surface-variant shrink-0"
    <div>
      <h3 class="font-semibold text-on-surface text-base">{name}</h3>
      <p class="font-meta text-meta text-on-surface-variant mt-1">
        Last run: {lastRun}</p>
    </div>

Right side of row:
  <div class="flex items-center flex-wrap gap-4 lg:justify-end">

Schedule badge:
  <span class="px-3 py-1 bg-surface-container-high text-on-surface
    font-meta text-meta rounded-full whitespace-nowrap
    flex items-center gap-1">
    <span class="material-symbols-outlined text-[14px]">schedule</span>
    {schedule}
  </span>

Toggle ENABLED from Stitch:
  <div class="w-10 h-6 bg-primary rounded-full relative cursor-pointer
    shadow-inner">
    <div class="absolute right-1 top-1 w-4 h-4 bg-white rounded-full
      shadow-sm"></div>
  </div>

Toggle DISABLED from Stitch:
  <div class="w-10 h-6 bg-surface-variant rounded-full relative
    cursor-pointer shadow-inner border border-outline-variant/50">
    <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full
      shadow-sm"></div>
  </div>

Buttons:
  View (both):
    class="h-[36px] px-4 bg-surface-container-lowest border
      border-outline-variant text-primary rounded font-medium text-sm
      hover:bg-surface-container-low transition-colors shadow-sm"

  Run ENABLED:
    class="h-[36px] px-4 bg-primary text-on-primary rounded font-medium
      text-sm hover:bg-primary-container transition-colors shadow-sm"

  Run DISABLED:
    class="h-[36px] px-4 bg-surface-variant text-on-surface-variant
      rounded font-medium text-sm cursor-not-allowed shadow-sm"
    attribute: disabled

Use these 4 tasks:
```tsx
const TASKS = [
  { id: '1', name: 'Sync CRM Data',          icon: 'sync',
    iconClass: 'bg-primary/10 text-primary',
    lastRun: '4 minutes ago',  schedule: 'Every 15 min',    enabled: true  },
  { id: '2', name: 'Daily Digest Summary',   icon: 'summarize',
    iconClass: 'bg-tertiary-container/10 text-tertiary',
    lastRun: '2 hours ago',    schedule: 'Daily at 8:00 AM', enabled: true },
  { id: '3', name: 'Weekly Database Backup', icon: 'database',
    iconClass: 'bg-surface-variant text-on-surface-variant',
    lastRun: '5 days ago',     schedule: 'Weekly on Sun',   enabled: false },
  { id: '4', name: 'Purge Old Logs',         icon: 'delete_sweep',
    iconClass: 'bg-surface-variant text-on-surface-variant',
    lastRun: '1 month ago',    schedule: 'Monthly on 1st',  enabled: false },
]
```

State:
  - activeFilter: 'All' | 'Enabled' | 'Disabled'  (default 'All')
  - tasks: Task[]  (initialized from TASKS above)

Toggle handler: flip task.enabled in state.
  // TODO: axios.patch(`/api/tasks/${id}/toggle`)

New Task button: useNavigate() → navigate('/new-task')

After writing, also open src/pages/AllTasks.tsx and write:
  export { default } from './ScheduledTask'


# ============================================================
# PROMPT 9 — ImportExport page: shell + Import tab
# ============================================================

Open src/pages/ImportExport.tsx and replace it entirely.

This page uses Header component with title="Import/Export".

Root: <div className="flex-1 flex flex-col overflow-hidden">

Main area from Stitch import screen:
  <main class="flex-1 p-lg overflow-y-auto">
    <div class="max-w-[640px] mx-auto w-full pt-8">

Page heading block from Stitch:
  <div class="mb-6">
    <h1 class="font-page-title text-page-title text-on-surface mb-2">
      Import Data</h1>
    <p class="font-body text-body text-on-surface-variant">
      Upload your tasks and mailbox configurations via JSON or CSV.</p>
  </div>

Import info banner from Stitch:
  <div class="bg-primary-container/10 border border-primary-container/20
    rounded-lg p-md mb-xl flex items-start gap-3">
    <span class="material-symbols-outlined text-primary-container mt-0.5">
      info</span>
    <div class="flex-1">
      <p class="font-body text-body text-on-surface-variant mb-1">
        Upload a JSON/CSV to quickly populate your workspace with
        existing data structures.</p>
      <a class="font-section-label text-section-label
        text-primary-container hover:underline inline-flex
        items-center gap-1" href="#">
        Download template
        <span class="material-symbols-outlined text-[16px]">
          arrow_forward</span>
      </a>
    </div>
  </div>

Sub-nav tabs from Stitch (Import active, Export inactive):
  wrapper: class="flex border-b border-surface-variant mb-lg"

  Import (active):
    class="px-4 py-2 border-b-2 border-primary-container
      text-primary-container font-section-label text-section-label"

  Export (inactive):
    class="px-4 py-2 border-b-2 border-transparent
      text-on-surface-variant hover:text-on-surface
      font-section-label text-section-label"

Upload card from Stitch:
  <div class="bg-surface-container-lowest rounded-xl border
    border-surface-variant p-lg shadow-[0_4px_8px_rgba(0,0,0,0.04)] mb-xl">

Drop zone from Stitch:
  <div class="border-2 border-dashed border-[#CBD5E1] bg-[#F8FAFC]
    rounded-lg p-8 flex flex-col items-center justify-center
    text-center transition-colors hover:bg-surface-container-lowest
    hover:border-primary-container cursor-pointer group h-64">

  Icon circle:
    class="w-12 h-12 rounded-full bg-primary-container/10 flex
      items-center justify-center mb-4 group-hover:scale-110
      transition-transform"
    icon class: "material-symbols-outlined text-primary-container text-[28px]"
    icon name: cloud_upload

  Heading: class="font-body text-body font-medium text-on-surface mb-1"
    text: "Drag & drop your file here"

  Sub text: class="font-meta text-meta text-on-surface-variant mb-4"
    text: "or click to browse from your computer"

  Format chip:
    class="bg-surface-variant text-on-surface-variant px-3 py-1
      rounded-full font-meta text-meta"
    text: "Accepted: .xlsx"

Drag-hover state: change border to border-primary-container and
  bg to bg-primary-container/5 via isDragging state.

File selected state: show filename + size + a "Remove" link
  in text-error instead of the default drop zone content.

Import button from Stitch (disabled state shown):
  <button class="w-full h-[36px] bg-surface-variant
    text-on-surface-variant font-section-label text-section-label
    rounded flex items-center justify-center cursor-not-allowed
    opacity-70 transition-colors">
    Import Data
  </button>

When file IS selected, button becomes:
  class="w-full h-[36px] bg-primary text-on-primary
    font-section-label text-section-label rounded flex items-center
    justify-center hover:bg-primary-container transition-colors"

State needed:
  - tab: 'Import' | 'Export'  (default 'Import')
  - file: File | null          (default null)
  - isDragging: boolean        (default false)

Use a hidden <input type="file" accept=".xlsx" ref={fileRef} />
and trigger it on drop zone click.
Handle onDragOver, onDragLeave, onDrop events on the drop zone div.

This prompt covers the Import tab only.
Leave the Export tab content as: {tab === 'Export' && <div>Export — next prompt</div>}


# ============================================================
# PROMPT 10 — ImportExport page: Export tab
# ============================================================

Open src/pages/ImportExport.tsx.
Find the placeholder: {tab === 'Export' && <div>Export — next prompt</div>}
Replace it with the full Export tab content.

Also update the page heading to be dynamic:
  h1 text: tab === 'Import' ? 'Import Data' : 'Export Data'
  p text:  tab === 'Import'
    ? 'Upload your tasks and mailbox configurations via JSON or CSV.'
    : 'Export your configurations and data logs for external backup or migration.'

Also replace the info banner to be conditional:
  Import banner (already written in Prompt 9) shows when tab === 'Import'
  Export banner (below) shows when tab === 'Export'

Export info banner from Stitch:
  <div class="bg-tertiary-fixed border border-tertiary-fixed-dim
    rounded-lg p-4 mb-6 flex items-start gap-3">
    <span class="material-symbols-outlined text-on-tertiary-fixed-variant
      mt-0.5">info</span>
    <div>
      <p class="font-body text-body text-on-tertiary-fixed">
        Export your configurations and data logs for external backup
        or migration.</p>
      <p class="font-meta text-meta text-on-tertiary-fixed-variant mt-1">
        Last exported: 2 days ago</p>
    </div>
  </div>

Export options card from Stitch:
  <div class="bg-surface-container-lowest border
    border-surface-container-highest rounded-xl p-lg
    shadow-[0_4px_8px_rgba(0,0,0,0.04)]">
    <h3 class="font-section-label text-section-label text-on-surface
      mb-6 uppercase tracking-wider">Export Settings</h3>

FORMAT segmented control from Stitch:
  Label: <label class="block font-meta text-meta
    text-on-surface-variant mb-2">FORMAT</label>
  Wrapper: <div class="flex p-1 bg-surface-container-low border
    border-surface-container-highest rounded-lg">

  Active format button:
    class="flex-1 py-1.5 px-3 bg-surface-container-lowest shadow-sm
      rounded text-primary font-body text-body font-medium
      transition-colors text-center border border-outline-variant"

  Inactive format button:
    class="flex-1 py-1.5 px-3 text-on-surface-variant
      hover:text-on-surface font-body text-body transition-colors
      text-center"

  Options: JSON (default active), CSV, Excel

DATE RANGE from Stitch:
  Label: class="block font-meta text-meta text-on-surface-variant mb-2"
    text: DATE RANGE
  Grid: class="grid grid-cols-2 gap-4"
  Each item:
    Sub-label: class="block font-meta text-meta text-outline mb-1"
    Input: class="w-full h-[36px] bg-surface-container-lowest border
      border-[#E5E7EB] rounded-lg px-3 font-body text-body text-on-surface
      focus:outline-none focus:border-primary focus:ring-2
      focus:ring-primary/20 transition-all appearance-none"
      type="date"

INCLUDE checkboxes from Stitch (custom styled — NOT native checkbox):
  Label: class="block font-meta text-meta text-on-surface-variant mb-3"
    text: INCLUDE
  Each checkbox row:
    wrapper: class="flex items-center gap-3 cursor-pointer group"
    The actual input is hidden: class="peer sr-only" type="checkbox"
    Custom box:
      class="w-4 h-4 rounded border flex items-center justify-center
        transition-colors"
      When checked:   add "bg-primary border-primary"
      When unchecked: add "border-[#E5E7EB] bg-surface-container-lowest"
    Checkmark inside box (only visible when checked):
      <span class="material-symbols-outlined text-white text-[12px]">
        check</span>
    Text:
      class="font-body text-body text-on-surface
        group-hover:text-primary transition-colors"

  Three options (tasks=true, logs=true, rules=false by default):
    "Task definitions"
    "Execution logs"
    "Email rules"

  Implement with React state: { tasks: true, logs: true, rules: false }
  Use controlled pattern — no actual checkbox, just toggle state on click.

Action button from Stitch:
  wrapper: class="mt-6 pt-6 border-t border-surface-container-highest"
  <button class="w-full h-[36px] bg-primary hover:bg-primary-container
    text-white font-body text-body font-medium rounded-lg flex
    items-center justify-center gap-2 transition-colors">
    <span>Export & Download</span>
    <span class="material-symbols-outlined text-[18px]">download</span>
  </button>

State to add:
  - format: string  (default 'JSON')
  - include: { tasks: boolean; logs: boolean; rules: boolean }
    default: { tasks: true, logs: true, rules: false }
