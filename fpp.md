Frontend (React) — 10 Prompts

F1 — Project scaffold & design system

I am building a React frontend for an Outlook email automation tool called "Your Personal Assistant". Set up a new React project using Vite + React 18. Install and configure: Tailwind CSS, React Router v6, Axios, and Zustand for state management.
Create the base folder structure:
src/
  components/    (shared UI components)
  pages/         (one file per screen)
  store/         (Zustand slices)
  hooks/         (custom hooks)
  utils/         (helpers)
  api/           (axios instance + endpoint functions)
In tailwind.config.js, define these design tokens as custom values — do not change them later, all components must use these:

Colors: primary #4F6BFF, sidebar bg #1E1F2E, page bg #F4F5F7, text primary #111827, text muted #6B7280, border #E5E7EB, success #22C55E, error #EF4444, warning #F59E0B
Border radius: card 12px, button/input 8px, badge 999px
Font: Inter (import from Google Fonts in index.html)

Create a base Axios instance in src/api/client.js pointing to http://localhost:8000/api with a default Content-Type: application/json header.
Do not build any UI yet. Only scaffold, config, and folder structure.


F2 — Shell layout: sidebar + header

Using the project scaffolded in F1, build the persistent shell layout that wraps every screen.
Create src/components/Layout/Sidebar.jsx. It must be a fixed 220px wide dark navy (#1E1F2E) sidebar with:

Top: app logo square (#4F6BFF bg, white "PA" text) + "Your Personal Assistant" title + "Outlook Automation" subtitle
Nav items (in order): Mailbox (mail), New Task (add_circle), All Tasks (checklist), Scheduled Task (schedule), Import/Export (import_export with expand chevron), Logs (receipt_long)
Bottom: Settings (settings)
Use React Router NavLink for each item. Active item: white text + 3px left #4F6BFF border + rgba(255,255,255,0.05) background. Inactive: #A0A3B1 text, hover white.
Use Material Symbols Outlined icons (load via CDN in index.html).

Create src/components/Layout/Header.jsx. It is a sticky 56px top bar (white bg, bottom border #E5E7EB) showing:

Left: current page title (passed as prop)
Right: notification bell icon + user avatar circle (initials, #4F6BFF bg)

Create src/components/Layout/AppLayout.jsx that composes sidebar + header + a <main> content area with margin-left: 220px and padding: 24px. Use React Router <Outlet /> for child pages.
Wire up React Router in App.jsx with AppLayout as the root route. Add placeholder routes for all 6 pages. No page content yet.


F3 — Shared UI component library

Build the reusable component library in src/components/ui/. These components must be used by all pages — never write inline one-off versions. Build exactly these:

Button.jsx — props: variant (primary/secondary/danger), size (sm/md/lg), disabled, loading (shows spinner), onClick, children. Primary: #4F6BFF bg white text. Secondary: white bg #E5E7EB border. Danger: #EF4444.
Input.jsx — props: label, placeholder, value, onChange, error (shows red helper text below), required (shows red asterisk), suffix (icon button slot on the right), hint.
Toggle.jsx — pill toggle switch. Props: label, value, onChange. On = #22C55E, Off = #D1D5DB.
SegmentedControl.jsx — props: options (array of {label, value}), value, onChange. Selected option: #4F6BFF bg white text. Unselected: white bg gray text.
Badge.jsx — props: variant (success/error/warning/info/neutral), children. Pill shaped, semantic colors.
Card.jsx — white bg, 12px radius, 1px solid #E5E7EB border, 20px padding. Props: title, description, children.
SectionLabel.jsx — 11px uppercase muted label, 0.05em letter spacing.

Each component is self-contained with no external dependencies beyond React and Tailwind. Export all from src/components/ui/index.js.


F4 — Mailbox page

Build src/pages/Mailbox.jsx. This page has three panels side by side inside AppLayout:
Panel 1 — Filter bar (full width top):
Two pill tabs: "All" and "Unread" using SegmentedControl. A search input on the right.
Panel 2 — Email list (320px wide, scrollable, white card):
Fetch emails from GET /api/mailbox/emails?filter=all|unread using Axios. While loading show 5 skeleton rows (gray animated pulse). Each email row shows: sender initials avatar (colored circle), sender name (bold), subject (14px), preview snippet (12px muted, truncated), timestamp (right-aligned 12px). Unread emails: 3px left #4F6BFF border. Selected row: #EEF1FF bg. Clicking a row sets it as selected in local state.
Panel 3 — Email viewer (flex remaining width, white card):
If no email selected: centered empty state — envelope icon + "Select an email to read" in muted text.
If email selected: show subject as h2, From/To/Date metadata row in muted text, full email body in 15px text. Toolbar at top: Reply, Forward, Archive, Delete as icon buttons.
Use a Zustand slice src/store/mailboxStore.js with state: emails, selectedEmail, filter, loading. No mock data — connect to real API endpoints. If API is unreachable, show an error banner.


F5 — All Tasks & Scheduled Task pages

Build two pages that share the same task list component.
Create src/components/TaskList/TaskRow.jsx. A single white card row (56px height) showing:

Task name (bold) + "Last run: X ago" in 12px muted below
Schedule badge (muted pill: "Every 15 min", "Daily at 8:00", etc.)
Task type badge using Badge component (color per type: blue=Draft, teal=Reminder, amber=Tracking, coral=Download)
Toggle switch (enabled/disabled) — on change calls PATCH /api/tasks/:id/toggle
"View" secondary button — navigates to task detail
"Run" primary button — calls POST /api/tasks/:id/run, disabled if task is disabled

Create src/components/TaskList/TaskListContainer.jsx — accepts a filter prop. Fetches from GET /api/tasks?type=all|scheduled. Shows filter tabs (All / Enabled / Disabled) and a summary strip (X total · X enabled · X disabled). "+ New Task" button top right navigates to /new-task.
src/pages/AllTasks.jsx — uses TaskListContainer with filter="all".
src/pages/ScheduledTask.jsx — uses TaskListContainer with filter="scheduled" (only tasks with a non-adhoc schedule).
Use Zustand slice src/store/taskStore.js with state: tasks, loading, error. Fetch on mount, update toggle state optimistically.


F6 — New Task page (single form)

Build src/pages/NewTask.jsx — the single-form task creation page.
Two-column layout:
Left column (280px, sticky): Task type selector card (4 options: Draft/Send Mail, Reminder Mail, Email Tracking, Download). Selected type stored in local state, controls which form sections are visible on the right.
Below task type selector: jump nav links to each visible section (use smooth scroll to anchor IDs).
Right column (scrollable): stacked Card sections. Show/hide sections based on selected task type using conditional rendering with smooth CSS transition (max-height + opacity).
Sections to build (use components from F3):

Basic Info (all types): Process Name (required), Schedule (SegmentedControl: Every 15 min / Every 1 hour / Daily at time / Ad hoc — Daily reveals a time picker), Is Shared Mailbox (SegmentedControl: Y/N — default N), Mailbox (text input — placeholder changes based on Is Shared Mailbox value), Log Output Folder Path (Input with folder icon suffix), Need to Process (Toggle)
Recipients (Draft/Reminder): TO textarea, CC textarea
Email Content (Draft/Reminder): Subject Line, Email Body Source (SegmentedControl: Excel/Docx), Email Body Path, Draft/Send toggle (Send shows amber warning chip), Voting Options, Reminder Body Path (Reminder only — indigo left border subsection)
Attachments (Draft/Reminder): Folder Path, File Name
Find & Replace (Draft/Reminder): Dynamic repeating rows (Find → Replace with), max 5 pairs, "+ Add" link, "× remove" per row
Email Filter (Tracking/Download): Subject Line, Partial Match toggle, Screening Folder, Start Date, End Date
Tracking Config (Tracking only): Due Date (amber warning if past), TO stakeholders
Save Email (Tracking/Download): master toggle, Save Both/Specific radio, PDF/.msg SegmentedControl
Attachments & Downloads (Tracking/Download): Download toggle, All/Specific radio, File Type input, Extract Zip toggle

Form state managed with useReducer. On save: POST /api/tasks with full form payload. Show validation inline on blur. Sticky bottom bar with Cancel + Save Task button.


F7 — Import / Export page

Build src/pages/ImportExport.jsx. Two sub-views toggled by a SegmentedControl tab at the top: "Import" and "Export".
Import view:

Info banner (indigo-tinted card with left border): explains accepted formats. "Download template →" link calls GET /api/import/template to download the Excel template.
Drop zone card: dashed border area, cloud icon, "Drag & drop your file here" text, "or Browse Files" link. Accept .xlsx only. On file select, show file name chip with × remove. Use the HTML drag-and-drop API — no external library.
On submit: POST /api/import/upload with multipart/form-data. Show a progress bar during upload (use onUploadProgress from Axios). On success: green banner "Import successful — X tasks loaded." On error: red banner with error message.

Export view:

Info banner (amber-tinted): "Last exported: X days ago" loaded from GET /api/export/meta.
Options form: Format SegmentedControl (JSON / Excel), Date range (Start + End date inputs), Checkboxes for scope: Task definitions / Execution logs / Email rules — all checked by default.
Estimated file size: fetched from GET /api/export/estimate on option change (debounced 400ms).
On submit: POST /api/export — response is a file blob, trigger browser download using a dynamic <a> tag.

No Zustand for this page — use local useState. Loading and error states on both actions.


F8 — Logs page

Build src/pages/Logs.jsx.
Top stat strip: 3 metric cards side by side — Total Runs (blue), Successful (green), Failed (red). Fetched from GET /api/logs/summary.
Filter bar: Pill tabs (All / Success / Failed / Skipped), date range inputs (Start/End), search input for task name, "Export Logs" outlined button (triggers GET /api/logs/export file download).
Log table (white card): columns — Task Name | Timestamp | Duration | Status badge | "View Log" button. Fetch from GET /api/logs?status=&start=&end=&search=&page=. Failed rows: #FFF5F5 row background + 3px red left border.
Timestamp column: show relative time ("2 minutes ago") as primary, absolute as tooltip on hover. Duration in monospace font.
"View Log" button: Opens a right-side drawer (slides in from right, 480px wide, overlay). Drawer shows: task name + run timestamp as header, then raw log output in a dark (#0F172A bg) monospace scrollable pre block with syntax coloring (green for success lines, red for error lines, white for info). Fetch log content from GET /api/logs/:id.
Pagination: "Showing X–Y of Z" text + Prev/Next buttons. Page size 15.
Use Zustand slice src/store/logStore.js. All filters update the URL query string (use React Router useSearchParams) so the filtered view is shareable/bookmarkable.


F9 — Global state, error handling & notifications

Wire up app-wide concerns that every page relies on.
Zustand src/store/appStore.js: Global state for: currentUser (name, initials, email), notifications (array of {id, type, message, timestamp}), sidebarCollapsed (boolean).
Notification toast system: Create src/components/ui/Toast.jsx and src/components/ui/ToastContainer.jsx. Toasts appear top-right, stack vertically, auto-dismiss after 4 seconds, support manual dismiss. Variants: success (green), error (red), warning (amber), info (blue). Expose a useToast() hook that any component can call: toast.success("Task saved"), toast.error("Upload failed").
Axios interceptors in src/api/client.js:

Request interceptor: attach auth token from localStorage if present.
Response interceptor: on 401 redirect to /login. On 5xx auto-show an error toast via the toast store. On network error show "Cannot reach server — check your connection."

Error boundary: Create src/components/ErrorBoundary.jsx wrapping the entire app. On crash: show a centered card with error message + "Reload" button.
Loading states: Create src/components/ui/Skeleton.jsx — a gray animated pulse block that accepts width and height props. Use this everywhere data is loading instead of spinners.
Empty states: Create src/components/ui/EmptyState.jsx — accepts icon, title, description, optional action button. Use across Mailbox (no email selected), Tasks (no tasks yet), Logs (no logs).


F10 — Environment config, routing guards & final wiring

Final frontend integration pass.
Environment config: Create .env.development with VITE_API_BASE_URL=http://localhost:8000/api and .env.production with the production URL. Update src/api/client.js to use import.meta.env.VITE_API_BASE_URL.
React Router setup (final): Define all routes in src/router.jsx:
/                → redirect to /mailbox
/mailbox         → Mailbox
/new-task        → NewTask
/tasks           → AllTasks
/scheduled       → ScheduledTask
/import-export   → ImportExport
/logs            → Logs
Wrap all routes in AppLayout. Add a 404 catch-all route showing EmptyState with "Page not found".
Page titles: Each page updates document.title to "PageName — Your Personal Assistant" using a useDocumentTitle(title) custom hook in src/hooks/useDocumentTitle.js.
API health check: On app load (in App.jsx useEffect), call GET /api/health. If it fails, show a full-screen banner: "Backend is offline — some features may not work." with a retry button.
Final check: Confirm every page imports only from src/components/ui/index.js for UI primitives, uses Zustand for shared state, uses Axios from src/api/client.js for all HTTP calls, and uses React Router for all navigation. No direct fetch() calls anywhere.
