# ============================================================
# NEW FEATURE PROMPTS — Part 2 of 2
# FA1-FA2: Consolidation frontend
# FB1-FB2: Calendar event frontend
# FC1:     Multi-job run frontend
# R1-R5:   src/ rewrite into app/services/mail_engine/
# ============================================================


# ============================================================
# FA1 — Consolidation: NewTask form section
# ============================================================

Open src/pages/NewTask.tsx.

This prompt adds a "Response Consolidation" toggle section
that appears ONLY when taskType === 'tracking'.
It goes inside SECTION 8 (Save Email section), added AFTER it
as a new SECTION 8b.

Step 1 — Add consolidation fields to FormState interface:
```tsx
// Add these to the FormState interface
consolidationEnabled: boolean
consolidationInputFolder: string
consolidationOutputPath: string
consolidationFilePattern: string
consolidationAddSource: boolean
```

Add to the init object in the reducer:
```tsx
consolidationEnabled: false,
consolidationInputFolder: '',
consolidationOutputPath: '',
consolidationFilePattern: '*.xlsx',
consolidationAddSource: true,
```

Step 2 — Add the new section inside the right column,
after the Save Email section, inside {isTrackingOrDownload && ...}
but MORE specifically only when taskType === 'tracking':

```tsx
{taskType === 'tracking' && (
  <section
    id="consolidation"
    className="bg-white rounded-xl border border-gray-200 shadow-sm scroll-mt-24"
  >
    {/* Section header */}
    <div className="px-8 py-6 border-b border-gray-100">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="font-page-title text-gray-900">Response Consolidation</h3>
          <p className="text-xs text-gray-500 mt-1">
            Merge all reply attachments (same Excel format) into one output file
          </p>
        </div>
        {/* Master toggle — same style as other toggles in form */}
        <button
          type="button"
          onClick={() => update({ consolidationEnabled: !form.consolidationEnabled })}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            form.consolidationEnabled ? 'bg-primary' : 'bg-gray-300'
          }`}
        >
          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            form.consolidationEnabled ? 'translate-x-6' : 'translate-x-1'
          }`} />
        </button>
      </div>
    </div>

    {/* Consolidation fields — shown only when enabled */}
    {form.consolidationEnabled && (
      <div className="px-8 py-6 space-y-6">

        {/* Explanation info banner */}
        <div className="bg-primary-container/10 border border-primary-container/20 rounded-lg p-4 flex items-start gap-3">
          <span className="material-symbols-outlined text-primary-container mt-0.5">info</span>
          <p className="text-sm text-on-surface-variant">
            After tracking completes, all attachment files matching the pattern
            will be merged into a single Excel file. Files must share the same
            column headers.
          </p>
        </div>

        {/* Input folder */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Response Attachments Folder
            <span className="text-error ml-0.5">*</span>
          </label>
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">folder_open</span>
            <input
              type="text"
              value={form.consolidationInputFolder}
              onChange={(e) => update({ consolidationInputFolder: e.target.value })}
              className="w-full h-9 pl-10 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
              placeholder="C:\Tracking\Responses"
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Folder where tracking saves the attachment files
          </p>
        </div>

        {/* File pattern */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">File Pattern</label>
          <input
            type="text"
            value={form.consolidationFilePattern}
            onChange={(e) => update({ consolidationFilePattern: e.target.value })}
            className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono text-sm"
            placeholder="*.xlsx"
          />
          <p className="mt-1 text-xs text-gray-500">
            Glob pattern — use *.xlsx for all Excel files
          </p>
        </div>

        {/* Output path */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Merged Output File Path
            <span className="text-error ml-0.5">*</span>
          </label>
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">save</span>
            <input
              type="text"
              value={form.consolidationOutputPath}
              onChange={(e) => update({ consolidationOutputPath: e.target.value })}
              className="w-full h-9 pl-10 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
              placeholder="C:\Output\consolidated_responses.xlsx"
            />
          </div>
        </div>

        {/* Add source column toggle */}
        <div className="flex justify-between items-center py-3 border-t border-gray-100">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Add "Source File" column
            </label>
            <p className="text-xs text-gray-500 mt-0.5">
              Adds a column showing which file each row came from
            </p>
          </div>
          <button
            type="button"
            onClick={() => update({ consolidationAddSource: !form.consolidationAddSource })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              form.consolidationAddSource ? 'bg-primary' : 'bg-gray-300'
            }`}
          >
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              form.consolidationAddSource ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </button>
        </div>

      </div>
    )}
  </section>
)}
```

Step 3 — Add "Consolidation" to the jump nav.
In the left column jump nav, inside the {taskType === 'tracking' && ...} block,
add after the Save Email link:
```tsx
<a href="#consolidation"
  className="flex items-center px-4 py-2 text-gray-500 hover:text-gray-900 border-l-2 border-transparent text-sm">
  Response Consolidation
</a>
```

Step 4 — Include consolidation fields in the handleSave payload.
In the handleSave function, inside the config object, add:
```tsx
consolidation: {
  enabled: form.consolidationEnabled,
  input_folder: form.consolidationInputFolder,
  output_path: form.consolidationOutputPath,
  file_pattern: form.consolidationFilePattern,
  add_source_column: form.consolidationAddSource,
},
```


# ============================================================
# FA2 — Consolidation: results view in Logs drawer
# ============================================================

Open src/pages/Logs.tsx.

When a log entry belongs to an email_tracking task and
contains consolidation results in its entries, show them
in the log drawer in a structured summary section.

Step 1 — Update the log drawer to detect consolidation entries.
In the drawer content area (the <pre> block), replace the
hardcoded log lines with dynamic rendering:

```tsx
{/* Log drawer content — replace static lines */}
<div className="flex-1 overflow-y-auto p-lg space-y-4">

  {/* Raw log lines */}
  <pre className="font-mono text-mono whitespace-pre-wrap space-y-1">
    {/* These come from GET /api/logs/:run_id entries array */}
    {/* For now render mock lines — replace with real data when wired */}
    {drawer.status === 'Failed' ? (
      <>
        <div className="text-inverse-on-surface/70">[INFO]  Starting task: {drawer.taskName}</div>
        <div className="text-inverse-on-surface/70">[INFO]  Connecting to mailbox...</div>
        <div className="text-error-container">[ERROR] Task failed — {drawer.duration}</div>
      </>
    ) : (
      <>
        <div className="text-inverse-on-surface/70">[INFO]  Starting task: {drawer.taskName}</div>
        <div className="text-inverse-on-surface/70">[INFO]  Connecting to mailbox...</div>
        <div className="text-inverse-on-surface/70">[INFO]  Connection established</div>
        <div className="text-primary-fixed">[SUCCESS] Task completed in {drawer.duration}</div>
      </>
    )}
  </pre>

  {/* Consolidation summary — show when task is tracking type */}
  {/* In real implementation check drawer.taskType === 'email_tracking' */}
  {drawer.status === 'Success' && (
    <div className="border border-white/10 rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-white/5 border-b border-white/10">
        <p className="text-inverse-on-surface font-medium text-sm flex items-center gap-2">
          <span className="material-symbols-outlined text-[16px]"
            style={{ fontVariationSettings: "'FILL' 1" }}>
            table_merge_cells
          </span>
          Consolidation Result
        </p>
      </div>
      <div className="p-4 space-y-2">
        {/* Mock consolidation result — replace with real data */}
        <div className="flex justify-between items-center">
          <span className="text-inverse-on-surface/70 text-xs">Rows merged</span>
          <span className="text-primary-fixed font-mono text-xs font-bold">42</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-inverse-on-surface/70 text-xs">Source files</span>
          <span className="text-inverse-on-surface font-mono text-xs">8 files</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-inverse-on-surface/70 text-xs">Output path</span>
          <span className="text-inverse-on-surface/60 font-mono text-xs truncate max-w-[220px]">
            C:\Output\consolidated.xlsx
          </span>
        </div>
      </div>
    </div>
  )}

</div>
```

Note: The consolidation summary data will come from the
log entries when the full log is fetched from GET /api/logs/:run_id.
The executor writes consolidation output into the entries array.
When API is wired, parse entries to find lines containing
"Consolidated" to extract the numbers.


# ============================================================
# FB1 — Calendar Events: NewTask type + form sections
# ============================================================

Open src/pages/NewTask.tsx.

Step 1 — Add 'calendar' to the TaskType type and TASK_TYPES array.

```tsx
// Add to the type
type TaskType = 'draft' | 'reminder' | 'tracking' | 'download' | 'calendar'

// Add to TASK_TYPES array (after download)
{
  id: 'calendar' as TaskType,
  label: 'Calendar Event',
  desc: 'Book Outlook meetings',
  icon: 'calendar_month',
  iconClass: 'bg-violet-50 flex items-center justify-center text-violet-600',
}
```

Step 2 — Add calendar fields to FormState interface:
```tsx
// Calendar fields
calendarMode: 'single' | 'separate'
calendarSubject: string
calendarBody: string
calendarTimezone: string
calendarLocation: string
calendarIsOnline: boolean
calendarReminderMinutes: number
// Single mode
calendarStartDt: string
calendarEndDt: string
calendarAttendees: string    // semicolon-separated emails
// Separate mode
calendarSchedule: Array<{
  email: string
  startDt: string
  endDt: string
  location: string
}>
```

Add to init:
```tsx
calendarMode: 'single',
calendarSubject: '',
calendarBody: '',
calendarTimezone: 'GMT Standard Time',
calendarLocation: '',
calendarIsOnline: false,
calendarReminderMinutes: 15,
calendarStartDt: '',
calendarEndDt: '',
calendarAttendees: '',
calendarSchedule: [{ email: '', startDt: '', endDt: '', location: '' }],
```

Step 3 — Add the Calendar form sections.
Inside the right column, add a conditional block:
{taskType === 'calendar' && (...)}

Inside it, write these sections:

SECTION A — Event Details:
```tsx
<section id="event-details" className="bg-white rounded-xl p-8 border border-gray-200 shadow-sm scroll-mt-24">
  <h3 className="font-page-title text-gray-900 mb-6">Event Details</h3>
  <div className="space-y-6">

    {/* Subject */}
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        Event Subject <span className="text-error ml-0.5">*</span>
      </label>
      <input type="text" value={form.calendarSubject}
        onChange={(e) => update({ calendarSubject: e.target.value })}
        className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
        placeholder="Q4 Review Meeting" />
    </div>

    {/* Body / Description */}
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
      <textarea value={form.calendarBody}
        onChange={(e) => update({ calendarBody: e.target.value })}
        className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
        rows={3} placeholder="Meeting agenda, dial-in links, etc." />
    </div>

    {/* Location + Online toggle side by side */}
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Location</label>
        <input type="text" value={form.calendarLocation}
          onChange={(e) => update({ calendarLocation: e.target.value })}
          className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
          placeholder="Conference Room A" />
      </div>
      <div className="flex items-end pb-1">
        <div className="flex justify-between items-center w-full">
          <label className="text-sm font-medium text-gray-700">Teams meeting</label>
          <button type="button"
            onClick={() => update({ calendarIsOnline: !form.calendarIsOnline })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              form.calendarIsOnline ? 'bg-primary' : 'bg-gray-300'
            }`}>
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              form.calendarIsOnline ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </button>
        </div>
      </div>
    </div>

    {/* Timezone + Reminder side by side */}
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Timezone</label>
        <select value={form.calendarTimezone}
          onChange={(e) => update({ calendarTimezone: e.target.value })}
          className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body bg-white">
          <option value="GMT Standard Time">GMT Standard Time</option>
          <option value="Eastern Standard Time">Eastern Standard Time</option>
          <option value="Central Standard Time">Central Standard Time</option>
          <option value="Mountain Standard Time">Mountain Standard Time</option>
          <option value="Pacific Standard Time">Pacific Standard Time</option>
          <option value="India Standard Time">India Standard Time</option>
          <option value="Singapore Standard Time">Singapore Standard Time</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Reminder (minutes before)
        </label>
        <input type="number" value={form.calendarReminderMinutes}
          onChange={(e) => update({ calendarReminderMinutes: parseInt(e.target.value) || 15 })}
          className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
          min={0} max={10080} />
      </div>
    </div>

  </div>
</section>
```

SECTION B — Scheduling Mode + Attendees:
```tsx
<section id="attendees" className="bg-white rounded-xl p-8 border border-gray-200 shadow-sm scroll-mt-24">
  <div className="flex justify-between items-start mb-6">
    <div>
      <h3 className="font-page-title text-gray-900">Attendees & Schedule</h3>
      <p className="text-xs text-gray-500 mt-1">
        Choose to create one event for everyone, or separate events per person
      </p>
    </div>
  </div>

  {/* Mode selector — large option cards */}
  <div className="grid grid-cols-2 gap-4 mb-6">
    {[
      {
        value: 'single' as const,
        label: 'Single event',
        desc: 'One event for all attendees at the same time',
        icon: 'group',
      },
      {
        value: 'separate' as const,
        label: 'Separate events',
        desc: 'Individual events with different times per person',
        icon: 'calendar_view_day',
      },
    ].map((mode) => (
      <div
        key={mode.value}
        onClick={() => update({ calendarMode: mode.value })}
        className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
          form.calendarMode === mode.value
            ? 'border-primary bg-primary-container/5'
            : 'border-gray-200 hover:border-gray-300'
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <span className={`material-symbols-outlined text-[18px] ${
            form.calendarMode === mode.value ? 'text-primary' : 'text-gray-400'
          }`}>{mode.icon}</span>
          <span className={`text-sm font-semibold ${
            form.calendarMode === mode.value ? 'text-primary' : 'text-gray-700'
          }`}>{mode.label}</span>
        </div>
        <p className="text-xs text-gray-500 pl-6">{mode.desc}</p>
      </div>
    ))}
  </div>

  {/* SINGLE MODE */}
  {form.calendarMode === 'single' && (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Attendees <span className="text-error ml-0.5">*</span>
        </label>
        <textarea value={form.calendarAttendees}
          onChange={(e) => update({ calendarAttendees: e.target.value })}
          className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body"
          rows={3}
          placeholder="alice@company.com; bob@company.com; charlie@company.com" />
        <p className="mt-1 text-xs text-gray-500">Separate addresses with semicolons</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Start <span className="text-error ml-0.5">*</span>
          </label>
          <input type="datetime-local" value={form.calendarStartDt}
            onChange={(e) => update({ calendarStartDt: e.target.value })}
            className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            End <span className="text-error ml-0.5">*</span>
          </label>
          <input type="datetime-local" value={form.calendarEndDt}
            onChange={(e) => update({ calendarEndDt: e.target.value })}
            className="w-full h-9 rounded-lg border-gray-300 focus:ring-2 focus:ring-primary/20 focus:border-primary text-body" />
        </div>
      </div>
    </div>
  )}

  {/* SEPARATE MODE */}
  {form.calendarMode === 'separate' && (
    <div className="space-y-3">
      <p className="text-xs text-gray-500 mb-2">
        Add one row per person with their individual time slot
      </p>
      {form.calendarSchedule.map((entry, i) => (
        <div key={i} className="grid grid-cols-[1fr_1fr_1fr_auto] gap-2 items-center p-3 bg-gray-50 rounded-lg">
          <input type="email" value={entry.email}
            onChange={(e) => {
              const next = [...form.calendarSchedule]
              next[i] = { ...next[i], email: e.target.value }
              update({ calendarSchedule: next })
            }}
            className="h-8 rounded border-gray-300 text-sm focus:ring-1 focus:ring-primary/20 focus:border-primary"
            placeholder="email@company.com" />
          <input type="datetime-local" value={entry.startDt}
            onChange={(e) => {
              const next = [...form.calendarSchedule]
              next[i] = { ...next[i], startDt: e.target.value }
              update({ calendarSchedule: next })
            }}
            className="h-8 rounded border-gray-300 text-xs focus:ring-1 focus:ring-primary/20 focus:border-primary" />
          <input type="datetime-local" value={entry.endDt}
            onChange={(e) => {
              const next = [...form.calendarSchedule]
              next[i] = { ...next[i], endDt: e.target.value }
              update({ calendarSchedule: next })
            }}
            className="h-8 rounded border-gray-300 text-xs focus:ring-1 focus:ring-primary/20 focus:border-primary" />
          <button
            onClick={() => update({ calendarSchedule: form.calendarSchedule.filter((_, j) => j !== i) })}
            className="p-1 text-gray-400 hover:text-error transition-colors">
            <span className="material-symbols-outlined text-[18px]">delete</span>
          </button>
        </div>
      ))}
      <button
        onClick={() => update({
          calendarSchedule: [
            ...form.calendarSchedule,
            { email: '', startDt: '', endDt: '', location: '' }
          ]
        })}
        className="mt-2 flex items-center gap-2 text-primary font-semibold text-sm hover:underline">
        <span className="material-symbols-outlined text-sm">add</span>
        Add person
      </button>
    </div>
  )}
</section>
```

Step 4 — Add jump nav links for calendar task type:
In the left column nav, add a new condition block:
```tsx
{taskType === 'calendar' && (
  <>
    <a href="#event-details" className="...active link style...">Event Details</a>
    <a href="#attendees"     className="...inactive link style...">Attendees & Schedule</a>
  </>
)}
```

Step 5 — Add calendar payload to handleSave:
```tsx
// Inside the payload.config object, add:
...(taskType === 'calendar' && {
  event_mode: form.calendarMode,
  subject: form.calendarSubject,
  body_content: form.calendarBody,
  timezone: form.calendarTimezone,
  location: form.calendarLocation,
  is_online: form.calendarIsOnline,
  reminder_minutes: form.calendarReminderMinutes,
  // Single mode
  start_dt: form.calendarStartDt,
  end_dt: form.calendarEndDt,
  attendees: form.calendarAttendees.split(';').map(e => e.trim()).filter(Boolean),
  // Separate mode
  attendee_schedule: form.calendarSchedule.filter(s => s.email),
}),
```


# ============================================================
# FB2 — Calendar Events: preview modal before save
# ============================================================

Open src/pages/NewTask.tsx.

Add a preview step for calendar tasks so the user can see
exactly what events will be created before saving.

Step 1 — Add preview state:
```tsx
const [showCalendarPreview, setShowCalendarPreview] = useState(false)
const [calendarPreviewData, setCalendarPreviewData] = useState<any[]>([])
const [calendarPreviewLoading, setCalendarPreviewLoading] = useState(false)
```

Step 2 — Add fetchCalendarPreview function:
```tsx
const fetchCalendarPreview = async () => {
  setCalendarPreviewLoading(true)
  try {
    const config = {
      event_mode: form.calendarMode,
      subject: form.calendarSubject,
      body_content: form.calendarBody,
      timezone: form.calendarTimezone,
      location: form.calendarLocation,
      is_online: form.calendarIsOnline,
      reminder_minutes: form.calendarReminderMinutes,
      start_dt: form.calendarStartDt,
      end_dt: form.calendarEndDt,
      attendees: form.calendarAttendees.split(';').map(e => e.trim()).filter(Boolean),
      attendee_schedule: form.calendarSchedule.filter(s => s.email),
    }
    const { data } = await client.post('/tasks/calendar/preview', config)
    setCalendarPreviewData(data.events)
    setShowCalendarPreview(true)
  } catch {
    // If API offline, show local preview
    const localEvents = form.calendarMode === 'single'
      ? [{ subject: form.calendarSubject, attendees: form.calendarAttendees.split(';'), start_dt: form.calendarStartDt, end_dt: form.calendarEndDt }]
      : form.calendarSchedule.map(s => ({ subject: form.calendarSubject, attendee: s.email, start_dt: s.startDt, end_dt: s.endDt }))
    setCalendarPreviewData(localEvents)
    setShowCalendarPreview(true)
  } finally {
    setCalendarPreviewLoading(false)
  }
}
```

Step 3 — Show "Preview Events" button for calendar task type.
In the sticky bottom bar, when taskType === 'calendar',
replace the Save Task button with two buttons:

```tsx
{taskType === 'calendar' ? (
  <>
    <button
      onClick={fetchCalendarPreview}
      disabled={calendarPreviewLoading}
      className="px-6 py-2 border border-[#4F6BFF] text-[#4F6BFF] rounded-lg font-medium hover:bg-[#4F6BFF]/5 transition-colors"
    >
      {calendarPreviewLoading ? 'Loading...' : 'Preview Events'}
    </button>
    <button
      onClick={handleSave}
      className="px-10 py-2 bg-[#4F6BFF] text-white rounded-lg font-bold hover:bg-[#3D55CC] transition-colors shadow-lg shadow-primary/20"
    >
      Save & Schedule
    </button>
  </>
) : (
  <button onClick={handleSave} className="...existing save button...">
    Save Task
  </button>
)}
```

Step 4 — Add the preview modal.
Use a fixed overlay (faux-viewport pattern — no position:fixed for modals):

```tsx
{showCalendarPreview && (
  <div style={{
    position: 'fixed', inset: 0,
    background: 'rgba(0,0,0,0.45)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    zIndex: 60,
  }}>
    <div className="bg-white rounded-2xl shadow-xl w-[600px] max-h-[80vh] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <div>
          <h3 className="text-base font-semibold text-gray-900">
            Events to be created
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {calendarPreviewData.length} event{calendarPreviewData.length !== 1 ? 's' : ''} •
            {form.calendarMode === 'single' ? ' Single event for all' : ' Separate events per person'}
          </p>
        </div>
        <button onClick={() => setShowCalendarPreview(false)}
          className="text-gray-400 hover:text-gray-600">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>
      {/* Event list */}
      <div className="flex-1 overflow-y-auto p-6 space-y-3">
        {calendarPreviewData.map((event, i) => (
          <div key={i}
            className="p-4 border border-gray-200 rounded-xl bg-gray-50 space-y-2">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-[#4F6BFF]"
                style={{ fontVariationSettings: "'FILL' 1" }}>
                calendar_month
              </span>
              <span className="font-semibold text-sm text-gray-900">{event.subject}</span>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 pl-6">
              <div className="text-xs text-gray-500">
                {event.attendee
                  ? <span>{event.attendee}</span>
                  : <span>{(event.attendees || []).join(', ')}</span>
                }
              </div>
              <div className="text-xs text-gray-500">
                {event.start_dt} → {event.end_dt}
              </div>
              {event.location && (
                <div className="text-xs text-gray-400 col-span-2">{event.location}</div>
              )}
            </div>
          </div>
        ))}
      </div>
      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
        <button onClick={() => setShowCalendarPreview(false)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
          Back to edit
        </button>
        <button
          onClick={async () => { setShowCalendarPreview(false); await handleSave() }}
          className="px-6 py-2 bg-[#4F6BFF] text-white rounded-lg font-semibold text-sm hover:bg-[#3D55CC]">
          Confirm & Save
        </button>
      </div>
    </div>
  </div>
)}
```


# ============================================================
# FC1 — Multi-job Run: checkbox selection + bulk run UI
# ============================================================

Open src/pages/ScheduledTask.tsx.

This prompt adds multi-select checkboxes to the task list
and a "Run Selected" action bar that appears when tasks are selected.

Step 1 — Add selection state:
```tsx
const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
const [bulkRunMode, setBulkRunMode] = useState<'parallel' | 'sequential'>('parallel')
const [bulkRunning, setBulkRunning] = useState(false)
const [bulkResult, setBulkResult] = useState<any | null>(null)

const toggleSelect = (id: string) => {
  setSelectedIds(prev => {
    const next = new Set(prev)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    return next
  })
}

const selectAll = () => {
  const enabledIds = filteredTasks.filter(t => t.enabled).map(t => t.id)
  setSelectedIds(new Set(enabledIds))
}

const clearSelection = () => setSelectedIds(new Set())

const handleBulkRun = async () => {
  if (selectedIds.size === 0) return
  setBulkRunning(true)
  setBulkResult(null)
  try {
    const { data } = await client.post('/tasks/bulk-run', {
      task_ids: Array.from(selectedIds),
      run_mode: bulkRunMode,
    })
    setBulkResult(data)
    clearSelection()
  } catch (e) {
    setBulkResult({ error: 'Failed to trigger bulk run' })
  } finally {
    setBulkRunning(false)
  }
}
```

Step 2 — Add a checkbox column to each task row.
In the task row div, add a checkbox as the FIRST element
inside the left flex container:

```tsx
{/* Checkbox — appears before the icon+name block */}
<div className="flex items-start gap-4 flex-1">

  {/* Checkbox */}
  <div className="pt-0.5 shrink-0">
    <div
      onClick={() => task.enabled && toggleSelect(task.id)}
      className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors cursor-pointer ${
        selectedIds.has(task.id)
          ? 'bg-primary border-primary'
          : task.enabled
            ? 'border-outline-variant hover:border-primary'
            : 'border-outline-variant/40 cursor-not-allowed opacity-40'
      }`}
    >
      {selectedIds.has(task.id) && (
        <span className="material-symbols-outlined text-white text-[14px]"
          style={{ fontVariationSettings: "'FILL' 1" }}>
          check
        </span>
      )}
    </div>
  </div>

  {/* existing icon + name block unchanged */}
  <div className={`w-10 h-10 rounded flex items-center justify-center shrink-0 ${task.iconClass}`}>
    <span className="material-symbols-outlined">{task.icon}</span>
  </div>
  <div>
    <h3 className="font-semibold text-on-surface text-base">{task.name}</h3>
    <p className="font-meta text-meta text-on-surface-variant mt-1">Last run: {task.lastRun}</p>
  </div>
</div>
```

Step 3 — Add a "Select all" link next to filter tabs.
Inside the filter tabs bar div, after the filter tab buttons, add:

```tsx
<div className="ml-auto flex items-center gap-4 pr-2">
  {selectedIds.size > 0 ? (
    <button onClick={clearSelection}
      className="text-xs text-on-surface-variant hover:text-on-surface transition-colors">
      Clear ({selectedIds.size})
    </button>
  ) : (
    <button onClick={selectAll}
      className="text-xs text-primary hover:underline">
      Select enabled
    </button>
  )}
</div>
```

Step 4 — Add the "Run Selected" action bar.
This bar slides up from the bottom when selectedIds.size > 0.
Place it OUTSIDE and AFTER the main card div, still inside <main>:

```tsx
{/* Bulk run action bar — slides up when items selected */}
{selectedIds.size > 0 && (
  <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 flex items-center justify-between gap-4 shadow-lg animate-in fade-in slide-in-from-bottom-2 duration-200">

    {/* Left: count + mode selector */}
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
          <span className="text-white text-xs font-bold">{selectedIds.size}</span>
        </div>
        <span className="font-body text-body text-on-surface font-medium">
          task{selectedIds.size !== 1 ? 's' : ''} selected
        </span>
      </div>

      {/* Run mode toggle */}
      <div className="flex p-1 bg-surface-container rounded-lg border border-outline-variant">
        {[
          { value: 'parallel'   as const, label: 'Parallel',   icon: 'dynamic_feed' },
          { value: 'sequential' as const, label: 'Sequential', icon: 'linear_scale' },
        ].map((mode) => (
          <button
            key={mode.value}
            onClick={() => setBulkRunMode(mode.value)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors ${
              bulkRunMode === mode.value
                ? 'bg-surface-container-lowest text-primary shadow-sm border border-outline-variant'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[14px]">{mode.icon}</span>
            {mode.label}
          </button>
        ))}
      </div>

      {/* Mode explanation */}
      <p className="text-xs text-on-surface-variant hidden lg:block">
        {bulkRunMode === 'parallel'
          ? 'All tasks start simultaneously'
          : 'Tasks run one after another in order'}
      </p>
    </div>

    {/* Right: Run + Cancel */}
    <div className="flex items-center gap-3">
      <button
        onClick={clearSelection}
        className="h-[36px] px-4 border border-outline-variant bg-surface-container-lowest text-on-surface-variant rounded font-medium text-sm hover:bg-surface-container transition-colors"
      >
        Cancel
      </button>
      <button
        onClick={handleBulkRun}
        disabled={bulkRunning}
        className={`h-[36px] px-6 rounded font-medium text-sm flex items-center gap-2 transition-colors shadow-sm ${
          bulkRunning
            ? 'bg-surface-variant text-on-surface-variant cursor-not-allowed'
            : 'bg-primary text-on-primary hover:bg-primary-container'
        }`}
      >
        {bulkRunning ? (
          <>
            <span className="material-symbols-outlined text-[16px] animate-spin">
              progress_activity
            </span>
            Running...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-[16px]">play_arrow</span>
            Run {selectedIds.size} task{selectedIds.size !== 1 ? 's' : ''}
          </>
        )}
      </button>
    </div>
  </div>
)}

{/* Bulk run result banner */}
{bulkResult && !bulkResult.error && (
  <div className="bg-primary-container/10 border border-primary-container/20 rounded-xl p-4 flex items-center justify-between">
    <div className="flex items-center gap-3">
      <span className="material-symbols-outlined text-primary-container"
        style={{ fontVariationSettings: "'FILL' 1" }}>
        check_circle
      </span>
      <div>
        <p className="font-medium text-on-surface text-sm">
          {bulkResult.triggered} task{bulkResult.triggered !== 1 ? 's' : ''} triggered
          {bulkResult.failed > 0 ? `, ${bulkResult.failed} failed` : ''}
        </p>
        <p className="text-xs text-on-surface-variant mt-0.5">
          Mode: {bulkResult.run_mode} — check Logs for results
        </p>
      </div>
    </div>
    <button onClick={() => setBulkResult(null)}
      className="text-on-surface-variant hover:text-on-surface">
      <span className="material-symbols-outlined">close</span>
    </button>
  </div>
)}

{bulkResult?.error && (
  <div className="bg-error-container/20 border border-error/20 rounded-xl p-4 flex items-center gap-3">
    <span className="material-symbols-outlined text-error">error</span>
    <p className="text-sm text-error">{bulkResult.error}</p>
    <button onClick={() => setBulkResult(null)} className="ml-auto text-error">
      <span className="material-symbols-outlined">close</span>
    </button>
  </div>
)}
```

Import client from '../api/client' at the top of the file.

After writing, verify:
  ✓ Checkboxes appear on all task rows
  ✓ Disabled tasks have greyed-out, non-clickable checkboxes
  ✓ "Select enabled" selects only enabled tasks
  ✓ Action bar appears/disappears smoothly based on selection
  ✓ Parallel/Sequential toggle updates mode
  ✓ Run button shows spinner when running
  ✓ Result banner appears after run completes
  ✓ AllTasks page (which re-exports ScheduledTask) gets these features too


# ============================================================
# R1 — src/ Rewrite: create mail_engine folder + draft_mail
# ============================================================

CONTEXT: The goal is to rewrite the logic in src/ into
app/services/mail_engine/ — pure Python, no GUI, no Excel
dependency, using the Graph API proxy. Once verified,
src/ can be deleted. The executor will switch from calling
src/workers/ to calling app/services/mail_engine/.

DO NOT delete src/ yet. Run old and new in parallel first.

Step 1 — Create app/services/mail_engine/__init__.py:
```python
"""
Mail Engine — reimplementation of src/ worker logic.
No GUI dependencies. No Excel row format.
Uses Graph API proxy for all mailbox operations.
"""
```

Step 2 — Read src/workers/draft_mail.py and
src/personal_routes/draft_mail.py and src/shared_routes/draft_mail.py
carefully. Understand:
  - What Graph API calls they make
  - How they build the email (subject, body, to, cc, attachments)
  - How they handle find/replace
  - How they handle draft vs send
  - How they handle voting options
  - How they handle attachments from folder path + wildcard

Step 3 — Write app/services/mail_engine/draft_mail.py:
```python
"""
Draft/Send Mail Engine
Replaces: src/workers/draft_mail.py
          src/personal_routes/draft_mail.py
          src/shared_routes/draft_mail.py

No GUI imports. No Excel row format.
Receives a clean Python dict — not a spreadsheet row.
"""
import logging
import re
from pathlib import Path
from typing import Optional
import httpx
import base64

logger = logging.getLogger(__name__)
GRAPH_PROXY_BASE = 'https://o365-graph-proxy-ms6.gaiacloud.jpmchase.net'


def _get_headers() -> dict:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))
    from helpers.fetch_token import fetch_token
    token = fetch_token()
    return token if isinstance(token, dict) else {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def _apply_find_replace(text: str, pairs: list[dict]) -> str:
    """Apply all find/replace pairs to the given text."""
    for pair in pairs:
        find = pair.get('find', '')
        replace = pair.get('replace', '')
        if find:
            text = text.replace(find, replace)
    return text


def _read_body(body_path: str, find_replace_pairs: list[dict]) -> str:
    """
    Read email body from a .docx or .html/.txt file.
    Apply find/replace pairs after reading.
    Returns HTML string.
    """
    path = Path(body_path)
    if not path.exists():
        raise FileNotFoundError(f"Email body file not found: {body_path}")

    if path.suffix.lower() == '.docx':
        try:
            from docx import Document
            doc = Document(str(path))
            html_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    html_parts.append(f'<p>{para.text}</p>')
            content = '\n'.join(html_parts)
        except ImportError:
            raise ImportError("python-docx is required. Run: pip install python-docx")
    else:
        content = path.read_text(encoding='utf-8')

    return _apply_find_replace(content, find_replace_pairs)


def _get_attachment_files(folder_path: str, file_pattern: str) -> list[Path]:
    """Resolve attachments from folder + wildcard pattern."""
    folder = Path(folder_path)
    if not folder.exists():
        logger.warning(f"Attachment folder not found: {folder_path}")
        return []
    return sorted(folder.glob(file_pattern)) if file_pattern else []


def _build_email_payload(
    subject: str,
    body_html: str,
    to_list: list[str],
    cc_list: list[str],
    attachments: list[Path],
    voting_options: Optional[str] = None,
) -> dict:
    """Build the Graph API message payload."""
    to_recipients = [
        {'emailAddress': {'address': e.strip()}}
        for e in to_list if e.strip()
    ]
    cc_recipients = [
        {'emailAddress': {'address': e.strip()}}
        for e in cc_list if e.strip()
    ]

    message = {
        'subject': subject,
        'body': {'contentType': 'HTML', 'content': body_html},
        'toRecipients': to_recipients,
        'ccRecipients': cc_recipients,
    }

    if voting_options:
        options = [v.strip() for v in voting_options.split(';') if v.strip()]
        if options:
            message['singleValueExtendedProperties'] = [{
                'id': 'String 0x0076',
                'value': ';'.join(options),
            }]

    if attachments:
        message['attachments'] = []
        for att in attachments:
            try:
                content = base64.b64encode(att.read_bytes()).decode('utf-8')
                message['attachments'].append({
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': att.name,
                    'contentBytes': content,
                })
            except Exception as e:
                logger.warning(f"Could not attach {att.name}: {e}")

    return message


def run(config: dict, is_shared: bool, mailbox: str) -> dict:
    """
    Main entry point for draft/send mail.

    Args:
        config:     Task config dict (from tasks.json)
        is_shared:  True = shared mailbox, False = personal
        mailbox:    Mailbox address (used when is_shared=True)

    Returns:
        Dict with status, message_id, and details
    """
    headers = _get_headers()

    # Parse config
    subject = _apply_find_replace(
        config.get('subject_line', ''),
        config.get('find_replace_pairs', [])
    )
    to_list = [e.strip() for e in config.get('to_stakeholders', '').split(';') if e.strip()]
    cc_list = [e.strip() for e in config.get('cc_stakeholders', '').split(';') if e.strip()]
    body_path = config.get('email_body_path', '')
    draft_or_send = config.get('draft_or_send', 'draft').lower()
    voting_option = config.get('voting_option', '')
    attachment_folder = config.get('attachment_folder_path', '')
    attachment_pattern = config.get('attachment_file_name', '')
    find_replace_pairs = config.get('find_replace_pairs', [])

    # Read body
    if body_path:
        body_html = _read_body(body_path, find_replace_pairs)
    else:
        body_html = f'<p>{subject}</p>'
        logger.warning("No body path provided — using subject as body")

    # Resolve attachments
    attachments = _get_attachment_files(attachment_folder, attachment_pattern) if attachment_folder else []
    logger.info(f"Attachments: {len(attachments)} file(s) from {attachment_folder}")

    # Build message
    message = _build_email_payload(subject, body_html, to_list, cc_list, attachments, voting_option)

    # Choose endpoint
    if is_shared:
        base_url = f'{GRAPH_PROXY_BASE}/users/{mailbox}'
    else:
        base_url = f'{GRAPH_PROXY_BASE}/me'

    if draft_or_send == 'send':
        url = f'{base_url}/sendMail'
        response = httpx.post(url, headers=headers, json={'message': message}, timeout=30.0, verify=False)
        response.raise_for_status()
        logger.info(f"Email sent: '{subject}' to {len(to_list)} recipient(s)")
        return {'status': 'sent', 'subject': subject, 'recipients': len(to_list)}
    else:
        url = f'{base_url}/messages'
        response = httpx.post(url, headers=headers, json=message, timeout=30.0, verify=False)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Draft created: '{subject}' — id={data.get('id')}")
        return {'status': 'drafted', 'message_id': data.get('id'), 'subject': subject}
```

Add python-docx to requirements.txt.


# ============================================================
# R2 — src/ Rewrite: reminder_mail + track_mail + download
# ============================================================

Using the same pattern as R1, write these three files.
Read the corresponding src/ files first each time.

--- app/services/mail_engine/reminder_mail.py ---

Read src/workers/reminder.py first.
The reminder module is similar to draft but:
  - Reads reminder_body_path instead of email_body_path
  - May need to find an existing draft by subject and update it
  - Or simply sends a new email using the reminder body

Write the module with a run(config, is_shared, mailbox) signature.
Import _get_headers, _read_body, _apply_find_replace from draft_mail
to avoid duplication:
  from app.services.mail_engine.draft_mail import (
      _get_headers, _read_body, _apply_find_replace,
      _build_email_payload, _get_attachment_files
  )

Use the reminder_body_path field for the body.
Same send/draft logic as draft_mail.

--- app/services/mail_engine/track_mail.py ---

Read src/workers/track_mail.py first.
This module:
  - Searches a mailbox folder for emails matching subject criteria
  - Optionally saves emails as PDF or .msg
  - Optionally downloads attachments

Write with run(config, is_shared, mailbox) signature.

Key Graph API calls to use:
  Search emails by subject:
    GET {base_url}/mailFolders/{folder}/messages?$filter=contains(subject,'{subject}')
    or for partial: ?$filter=contains(subject,'{subject}')
    or for exact: ?$filter=subject eq '{subject}'

  For date range add:
    &$filter=receivedDateTime ge {start_dt} and receivedDateTime le {end_dt}

  Save email as PDF: Graph API does not directly export as PDF.
    Save the email body HTML and attachments locally instead.
    For .msg format: save the raw MIME content.

  Download attachments:
    GET {base_url}/messages/{message_id}/attachments

--- app/services/mail_engine/download_attachments.py ---

Read src/workers/download_attachments.py first.
Similar to track_mail but focused on downloading attachments.
Supports:
  - All attachments or specific file type filter
  - ZIP extraction if the attachment is a zip file

Write with run(config, is_shared, mailbox) signature.

For ZIP extraction use Python's built-in zipfile module:
  import zipfile
  if extract_zip and att_path.suffix.lower() == '.zip':
      with zipfile.ZipFile(att_path) as z:
          z.extractall(att_path.parent)


# ============================================================
# R3 — src/ Rewrite: update executor to use mail_engine
# ============================================================

Open app/tasks/executor.py.

Update the _dispatch method to try mail_engine first,
and fall back to src/workers/ if mail_engine fails or
if a feature flag is set.

Step 1 — Add a USE_MAIL_ENGINE flag to app/config.py:
```python
USE_MAIL_ENGINE: bool = True   # Set False to use legacy src/workers/
```
Add to .env.example:
  USE_MAIL_ENGINE=true

Step 2 — Update _call_draft:
```python
def _call_draft(self, args: dict, is_shared: bool):
    from app.config import settings
    if settings.USE_MAIL_ENGINE:
        self._log('INFO', 'Using mail_engine (new implementation)')
        from app.services.mail_engine.draft_mail import run
        config = self.task.get('config', {})
        mailbox = self.task.get('mailbox', '')
        result = run(config, is_shared, mailbox)
        self._log('INFO', f"Result: {result}")
    else:
        self._log('INFO', 'Using legacy src/workers/ (old implementation)')
        if is_shared:
            from shared_routes.draft_mail import main as run_draft
        else:
            from personal_routes.draft_mail import main as run_draft
        run_draft(args)
```

Do the same for _call_reminder, _call_tracking, _call_download —
each routes to the corresponding mail_engine module when
USE_MAIL_ENGINE=True.

Step 3 — Test by setting USE_MAIL_ENGINE=true in .env
and running a draft task. Confirm the mail_engine code path
is used (you will see "Using mail_engine" in the logs).

Step 4 — Set USE_MAIL_ENGINE=false temporarily to verify
the legacy path still works. This gives you a safe rollback.


# ============================================================
# R4 — src/ Rewrite: integration test both paths
# ============================================================

Write a test script at the project root: test_engine_switch.py

```python
"""
Integration test — runs the same task through both paths
and compares the log outputs.
Run with: python test_engine_switch.py
"""
import json
from pathlib import Path

TEST_TASK = {
    'id': 'test-001',
    'process_name': 'Engine Comparison Test',
    'task_type': 'draft_send',
    'is_shared_mailbox': False,
    'mailbox': 'test@company.com',
    'log_output_folder': str(Path('data/test-logs')),
    'need_to_process': True,
    'enabled': True,
    'config': {
        'subject_line': 'Test Email [Engine Comparison]',
        'to_stakeholders': 'test@company.com',
        'cc_stakeholders': '',
        'attachment_folder_path': '',
        'attachment_file_name': '',
        'email_body_path': '',        # leave empty to test no-body path
        'draft_or_send': 'draft',
        'find_replace_pairs': [],
        'voting_option': '',
    }
}

def run_with_engine(use_mail_engine: bool):
    import os
    os.environ['USE_MAIL_ENGINE'] = str(use_mail_engine).lower()
    # Force reload of settings
    import importlib
    import app.config
    importlib.reload(app.config)

    from app.tasks.executor import TaskExecutor
    executor = TaskExecutor(TEST_TASK, log_dir='data/test-logs')
    result = executor.run()
    return result

print("=== Testing with USE_MAIL_ENGINE=true ===")
result_new = run_with_engine(True)
print(f"Status: {result_new['status']}")
for entry in result_new['entries']:
    print(f"  [{entry['level']}] {entry['message']}")

print()
print("=== Testing with USE_MAIL_ENGINE=false ===")
result_old = run_with_engine(False)
print(f"Status: {result_old['status']}")
for entry in result_old['entries']:
    print(f"  [{entry['level']}] {entry['message']}")

print()
print("Both paths completed. Compare the outputs above.")
print("If mail_engine path shows 'sent'/'drafted' and legacy shows")
print("the same — the rewrite is working correctly.")
```

Run it:
  python test_engine_switch.py

When both paths produce the same outcome (even if it's a
controlled failure because Graph API is unreachable), the
rewrite is confirmed working and you can proceed to R5.


# ============================================================
# R5 — src/ Rewrite: cleanup and final switch
# ============================================================

This is the final step. Only run this after:
  ✓ R1–R4 are complete
  ✓ test_engine_switch.py runs without crashing on both paths
  ✓ USE_MAIL_ENGINE=true has been running in production for
    at least a few successful task runs

Step 1 — Set USE_MAIL_ENGINE=true permanently in .env.
Confirm it is not overridden anywhere else.

Step 2 — Remove the legacy fallback from executor.py.
In each _call_* method, remove the else branch:
```python
def _call_draft(self, args: dict, is_shared: bool):
    # Legacy fallback removed — mail_engine only
    from app.services.mail_engine.draft_mail import run
    config = self.task.get('config', {})
    mailbox = self.task.get('mailbox', '')
    result = run(config, is_shared, mailbox)
    self._log('INFO', f"Result: {result}")
```
Do this for all four _call_* methods.

Step 3 — Remove the USE_MAIL_ENGINE flag.
Remove from config.py, from .env, from .env.example.

Step 4 — Remove sys.path.insert(0, src/) from all files
in app/services/mail_engine/*.py — they no longer need
to import from src/helpers/.

Instead, move the fetch_token.py logic INTO app/services/auth.py:
Read src/helpers/fetch_token.py one more time and rewrite it
cleanly in app/services/auth.py with:
  - No GUI imports
  - A single function: get_auth_headers() -> dict
  - The same authentication flow as the original

Then update all mail_engine files to import from:
  from app.services.auth import get_auth_headers

Step 5 — Copy common.py utilities.
Read src/helpers/common.py. For any utility function that
the mail_engine modules use, copy it into:
  app/services/mail_engine/utils.py
Name it properly, add type hints, remove any GUI references.

Step 6 — Delete src/ folder.
Only after all tests pass:
  rm -rf src/

Step 7 — Run the full test suite:
  python test_engine_switch.py  (expect: fails gracefully — no legacy path)
  uvicorn app.main:app --reload --port 8000
  curl http://localhost:8000/api/health
  # Trigger a test task and verify the log shows mail_engine path
