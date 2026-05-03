F4 (revised) — Mailbox page

Build src/pages/Mailbox.jsx. Reference the Stitch design file for this screen.
Layout: Full height flex row. Three panels inside <main class="flex-1 p-lg flex flex-col gap-lg overflow-y-auto">.
Filter bar (top): Two pill tabs using this exact pattern from Stitch:
jsx// Active tab
<button className="rounded-full bg-primary-container text-on-primary-container text-meta font-meta font-medium px-4 py-1.5">All</button>
// Inactive tab
<button className="rounded-full bg-surface-variant text-on-surface-variant text-meta font-meta font-medium hover:bg-surface-container-highest transition-colors px-4 py-1.5">Unread</button>
Search input on the right: border border-outline-variant bg-surface-container-lowest rounded-lg.
Email list panel (320px, scrollable): Card: bg-surface-container-lowest border border-outline-variant rounded-xl. Each email row: sender avatar circle using Stitch's color pattern — rounded-full bg-tertiary-container text-on-tertiary-container or bg-secondary-container text-on-secondary-container alternating. Unread row: border-l-4 border-l-primary. Selected row: bg-primary/5. Hover: hover:bg-surface-container-low/30 transition-colors.
Email viewer panel (flex remaining): Card: same bg-surface-container-lowest border border-outline-variant rounded-xl. Empty state: centered material-symbols-outlined envelope icon + muted text-on-surface-variant text. Toolbar buttons: h-[36px] px-4 bg-surface-container-lowest border border-outline-variant text-primary rounded font-medium text-sm hover:bg-surface-container-low transition-colors shadow-sm.
Fetch from GET /api/mailbox/emails?filter=all|unread. Use Zustand slice src/store/mailboxStore.js. Show skeleton rows (gray animate-pulse blocks) while loading.


F5 (revised) — All Tasks & Scheduled Task pages

Build the task list pages using the exact component patterns from the Stitch scheduled_tasks_detailed design.
Container card: bg-surface-container-lowest rounded-xl border border-outline-variant shadow-[0_4px_24px_rgba(0,0,0,0.02)] overflow-hidden
Filter tabs (inside a border-b border-outline-variant px-6 bar):
jsx// Active
<button className="py-4 text-sm font-medium text-primary border-b-2 border-primary">All</button>
// Inactive
<button className="py-4 text-sm font-medium text-on-surface-variant hover:text-on-surface transition-colors border-b-2 border-transparent">Enabled</button>
Task row (divide-y divide-outline-variant list): Each row: p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:bg-surface-container-low/30 transition-colors. Disabled rows add opacity-75.

Left: icon square w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary + task name font-semibold text-on-surface text-base + last run font-meta text-meta text-on-surface-variant mt-1
Schedule badge: px-3 py-1 bg-surface-container-high text-on-surface font-meta text-meta rounded-full whitespace-nowrap flex items-center gap-1 with schedule material icon
Toggle (enabled): w-10 h-6 bg-primary rounded-full relative cursor-pointer shadow-inner with inner absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm
Toggle (disabled): same but bg-outline-variant
View button: h-[36px] px-4 bg-surface-container-lowest border border-outline-variant text-primary rounded font-medium text-sm hover:bg-surface-container-low transition-colors shadow-sm
Run button (active): h-[36px] px-4 bg-primary text-on-primary rounded font-medium text-sm hover:bg-primary-container transition-colors shadow-sm
Run button (disabled): h-[36px] px-4 bg-surface-variant text-on-surface-variant rounded font-medium text-sm cursor-not-allowed shadow-sm with disabled attribute

New Task button (top right): h-[36px] px-4 bg-primary text-on-primary rounded font-medium text-sm flex items-center gap-2 hover:bg-primary-container transition-colors shadow-sm with add material icon.
Toggle on change: PATCH /api/tasks/:id/toggle. Run button: POST /api/tasks/:id/run. Use Zustand taskStore. Optimistic toggle update.


F6 (revised) — New Task page

Build src/pages/NewTask.jsx as a single-form page. The Stitch new_task_creation_2 HTML file is your visual reference — match it exactly.
Page shell: bg-[#F4F5F7] body. Sticky header (h-16 bg-[#F4F5F7] border-b border-gray-200) with back arrow button + "New Task" title (font-page-title text-page-title text-gray-900) + Cancel/Save buttons.
Two-column layout: max-w-[1100px] mx-auto px-8 py-10 flex gap-10 items-start
Left column (w-[300px] sticky top-28): Task type selector card — bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm. Header: px-4 py-3 bg-gray-50 border-b border-gray-200 with TASK TYPE section label. Each option row: p-4 hover:bg-gray-50 cursor-pointer flex items-start gap-3 transition-colors divide-y divide-gray-100. Active row: bg-primary-container/5 border-l-4 border-primary. Icon square per type: Draft=bg-primary-container/10 text-primary, Reminder=bg-teal-50 text-teal-600, Tracking=bg-amber-50 text-amber-600, Download=bg-rose-50 text-rose-600.
Below selector: Jump nav card — same card style, JUMP TO label, anchor links that smooth-scroll to section IDs.
Right column (flex-1 space-y-6): Each section is bg-white rounded-xl border border-gray-200 shadow-sm p-6. Section title: text-base font-semibold text-on-surface mb-4. Show/hide sections based on selected task type using conditional rendering.
Form fields use these exact Stitch patterns:

Input: w-full h-[36px] border border-outline-variant rounded bg-surface-container-lowest px-3 text-body text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary
Textarea: same border/bg, no fixed height, resize-none
Label: block text-section-label font-medium text-on-surface-variant mb-1
Required asterisk: text-error ml-0.5
Segmented control: outer flex rounded border border-outline-variant overflow-hidden, active segment bg-primary text-on-primary, inactive bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container
Toggle row: label left + w-10 h-6 bg-primary rounded-full relative cursor-pointer shadow-inner right (same toggle pattern as F5)

Sections and their task type visibility:

Basic Info (all): Process Name*, Schedule (segmented: Every 15 min/Every 1 hour/Daily at time/Ad hoc — Daily reveals time input), Is Shared Mailbox (segmented: Y/N default N), Mailbox, Log Output Folder Path, Need to Process toggle
Recipients (Draft/Reminder): TO textarea*, CC textarea
Email Content (Draft/Reminder): Subject*, Body Source segmented, Body Path, Draft/Send segmented (Send shows amber warning bg-tertiary-fixed text-on-tertiary-fixed rounded px-3 py-2 text-sm), Voting Options
Reminder Body (Reminder only — subsection with border-l-4 border-primary pl-4): Reminder Body Path
Attachments (Draft/Reminder): Folder Path, File Name
Find & Replace (Draft/Reminder): dynamic rows flex gap-2 items-center with Find input + → + Replace input + × text-error remove button. + Add replacement link: text-primary text-sm font-medium. Max 5.
Email Filter (Tracking/Download): Subject*, Partial Match toggle, Screening Folder, Start Date, End Date
Tracking Config (Tracking only): Due Date (past date shows text-tertiary warning), TO stakeholders
Save Email (Tracking/Download): master toggle + conditional Save scope radio + PDF/.msg segmented
Attachments & Downloads (Tracking/Download): Download toggle + conditional scope radio + File Type + Extract Zip toggle

Sticky bottom bar: fixed bottom-0 left-[260px] right-0 bg-white border-t border-outline-variant px-8 py-4 flex justify-between items-center z-30. Left: text-meta text-on-surface-variant. Right: Cancel secondary + Save primary buttons.
Form state with useReducer. On save: POST /api/tasks. Inline validation on blur.


F7 (revised) — Import / Export page

Build src/pages/ImportExport.jsx. Reference Stitch files import_data_2 and export_data_2.
Page header: font-page-title text-page-title text-on-surface title. Sub-tab toggle at top using the Stitch pill pattern — "Import" active: bg-primary text-on-primary rounded-full px-4 py-1.5, inactive: bg-surface-container text-on-surface-variant rounded-full px-4 py-1.5 border border-outline-variant/50.
Import view:
Info banner: bg-primary-container/10 border border-primary/20 rounded-xl p-md flex gap-3. Icon: material-symbols-outlined text-primary-container (info). Text: font-body text-body text-on-surface-variant. "Download template →" link: text-primary font-medium hover:underline.
Upload card: bg-surface-container-lowest border border-outline-variant rounded-xl p-lg. Drop zone: border-2 border-dashed border-outline-variant rounded-xl bg-surface-container-low/50 flex flex-col items-center justify-center py-12 gap-3 transition-colors. On drag-hover: border-primary bg-primary/5. Cloud icon: material-symbols-outlined text-[48px] text-outline (cloud_upload). "or Browse Files": text-primary font-medium cursor-pointer hover:underline. Accepted formats chip: rounded-full font-meta text-meta bg-surface-container px-3 py-1.
File selected state: chip showing filename with × text-error remove button.
Submit: full-width primary button, disabled until file selected.
Upload via POST /api/import/upload multipart. Progress bar: bg-primary h-1.5 rounded-full transition-all. Success banner: same structure as info banner but bg-primary-container/20. Error: bg-error-container/20 border-error/20 text-error.
Export view:
Info banner: amber-tinted — bg-tertiary-fixed/30 border border-tertiary/20 rounded-xl p-md. "Last exported" in text-on-surface-variant font-meta.
Options card: bg-surface-container-lowest border border-outline-variant rounded-xl p-lg space-y-6. Section labels: font-section-label text-section-label text-on-surface-variant uppercase tracking-wider mb-2. Format segmented control, date inputs, checkboxes (accent-primary), estimated size in font-meta text-on-surface-variant.
Submit button: full-width primary. Triggers blob download.


F8 (revised) — Logs page

Build src/pages/Logs.jsx. Reference Stitch execution_logs_1 design exactly.
Stat strip (grid grid-cols-3 gap-lg): Each card — bg-surface-container-lowest border border-outline-variant rounded-xl p-lg flex items-center justify-between shadow-sm shadow-black/5:

Label: font-section-label text-section-label text-on-surface-variant uppercase tracking-wider mb-2
Number: font-page-title text-[32px] leading-tight font-bold text-on-surface (Failed uses text-error)
Icon circle: Total=w-12 h-12 rounded-full bg-primary/10 text-primary with monitoring icon, Success=bg-primary-container/20 text-primary-container with check_circle icon, Failed=bg-error/10 text-error with error icon. All icons: style="font-variation-settings: 'FILL' 1; font-size: 24px;"

Filter bar (flex items-center justify-between gap-md bg-surface-container-lowest p-md rounded-xl border border-outline-variant):

Pill tabs — active: bg-primary text-on-primary font-meta text-meta font-medium px-4 py-1.5 rounded-full, inactive: bg-surface-container hover:bg-surface-container-high text-on-surface-variant font-meta text-meta font-medium px-4 py-1.5 rounded-full border border-outline-variant/50
Search input with search material icon absolutely positioned left
"Export Logs" button: secondary style

Log table (bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden):

Table header: bg-surface-container row, font-section-label text-section-label text-on-surface-variant uppercase tracking-wider py-3 px-6
Success row: hover:bg-surface-container transition-colors border-l-4 border-l-transparent
Failed row: bg-error-container/20 border-l-4 border-l-error hover:bg-error-container/30 transition-colors
Timestamp + Duration cells: font-mono text-mono text-on-surface-variant
Success badge: inline-flex items-center gap-1 bg-primary-container/10 text-primary font-meta text-meta px-2.5 py-0.5 rounded-full font-medium with w-1.5 h-1.5 rounded-full bg-primary dot
Failed badge: same pattern with bg-error/10 text-error and bg-error dot
"View Log" button: text-primary hover:text-primary-container font-medium text-[13px] hover:underline

Log drawer (slides in from right, w-[480px]): fixed inset-y-0 right-0 bg-inverse-surface z-50 flex flex-col shadow-xl. Header: text-inverse-on-surface. Log output: flex-1 overflow-y-auto p-lg font-mono text-mono. Line colors — INFO: text-inverse-on-surface/70, ERROR: text-error-container, SUCCESS: text-primary-fixed.
All data from GET /api/logs. Filters update URL via useSearchParams. Zustand logStore. Page size 15 with prev/next pagination.
