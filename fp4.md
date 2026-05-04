# ============================================================
# PROMPTS 16–20 OF 20
# ============================================================


# ============================================================
# PROMPT 16 — Zustand stores (task, log, mailbox)
# ============================================================

Write the three Zustand stores. These stores hold server data
and will replace the mock arrays in the pages once the backend
is running. For now they coexist with mock data — pages use
mock data directly but import the store hooks so they are ready.

--- src/store/taskStore.ts ---

```ts
import { create } from 'zustand'
import client from '../api/client'

export interface Task {
  id: string
  name: string
  icon: string
  iconClass: string
  lastRun: string
  schedule: string
  enabled: boolean
  taskType: 'draft' | 'reminder' | 'tracking' | 'download'
}

interface TaskStore {
  tasks: Task[]
  loading: boolean
  error: string | null
  fetchTasks: (filter?: 'all' | 'scheduled') => Promise<void>
  toggleTask: (id: string) => Promise<void>
  runTask: (id: string) => Promise<{ runId: string }>
  createTask: (payload: Record<string, unknown>) => Promise<void>
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async (filter = 'all') => {
    set({ loading: true, error: null })
    try {
      const { data } = await client.get('/tasks', { params: { type: filter } })
      set({ tasks: data, loading: false })
    } catch (e) {
      set({ error: String(e), loading: false })
    }
  },

  toggleTask: async (id: string) => {
    // Optimistic update
    set({
      tasks: get().tasks.map((t) =>
        t.id === id ? { ...t, enabled: !t.enabled } : t
      ),
    })
    try {
      await client.patch(`/tasks/${id}/toggle`)
    } catch {
      // Revert on failure
      await get().fetchTasks()
    }
  },

  runTask: async (id: string) => {
    const { data } = await client.post(`/tasks/${id}/run`)
    return data
  },

  createTask: async (payload) => {
    await client.post('/tasks', payload)
    await get().fetchTasks()
  },
}))
```

--- src/store/logStore.ts ---

```ts
import { create } from 'zustand'
import client from '../api/client'

export interface LogEntry {
  id: string
  taskName: string
  timestamp: string
  duration: string
  status: 'Success' | 'Failed' | 'Skipped'
}

export interface LogSummary {
  total: number
  successful: number
  failed: number
}

interface LogStore {
  logs: LogEntry[]
  summary: LogSummary
  loading: boolean
  fetchLogs: (params?: {
    status?: string
    search?: string
    page?: number
  }) => Promise<void>
  fetchSummary: () => Promise<void>
}

export const useLogStore = create<LogStore>((set) => ({
  logs: [],
  summary: { total: 0, successful: 0, failed: 0 },
  loading: false,

  fetchLogs: async (params = {}) => {
    set({ loading: true })
    try {
      const { data } = await client.get('/logs', { params })
      set({ logs: data, loading: false })
    } catch {
      set({ loading: false })
    }
  },

  fetchSummary: async () => {
    try {
      const { data } = await client.get('/logs/summary')
      set({ summary: data })
    } catch {
      // silent — page will show 0s
    }
  },
}))
```

--- src/store/mailboxStore.ts ---

```ts
import { create } from 'zustand'
import client from '../api/client'

export interface Email {
  id: string
  initials: string
  avatarClass: string
  sender: string
  subject: string
  preview: string
  time: string
  isUnread: boolean
  body?: string
}

interface MailboxStore {
  emails: Email[]
  selectedId: string | null
  filter: 'all' | 'unread'
  loading: boolean
  fetchEmails: (filter: 'all' | 'unread') => Promise<void>
  selectEmail: (id: string) => void
  setFilter: (filter: 'all' | 'unread') => void
}

export const useMailboxStore = create<MailboxStore>((set) => ({
  emails: [],
  selectedId: null,
  filter: 'all',
  loading: false,

  fetchEmails: async (filter) => {
    set({ loading: true, filter })
    try {
      const { data } = await client.get('/mailbox/emails', {
        params: { filter },
      })
      set({ emails: data, loading: false })
    } catch {
      set({ loading: false })
    }
  },

  selectEmail: (id) => set({ selectedId: id }),
  setFilter: (filter) => set({ filter }),
}))
```


# ============================================================
# PROMPT 17 — Wire stores into ScheduledTask + Logs pages
# ============================================================

The pages currently use hardcoded mock data arrays.
In this prompt we wire the Zustand stores so the pages
will fetch from the API when it is available, but fall
back gracefully to mock data when the API is offline.

--- ScheduledTask.tsx ---

Add these imports at the top:
  import { useTaskStore } from '../store/taskStore'

Add this inside the component (after existing useState):
  const { fetchTasks } = useTaskStore()

Add a useEffect to attempt a fetch on mount:
  useEffect(() => {
    fetchTasks('scheduled').catch(() => {
      // API offline — page keeps showing TASKS mock data
    })
  }, [])

Update the toggle handler to also call the store:
  const toggle = async (id: string) => {
    // Update local mock state (immediate UI feedback)
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, enabled: !t.enabled } : t))
    )
    // Also attempt real API call via store
    try {
      await useTaskStore.getState().toggleTask(id)
    } catch {
      // ignore if API offline
    }
  }

Update the Run button handler:
  const handleRun = async (id: string) => {
    try {
      await useTaskStore.getState().runTask(id)
      // TODO: show a toast "Task triggered"
    } catch {
      // ignore if API offline
    }
  }

Add onClick={handleRun(task.id)} to the Run button.
Add onClick={() => navigate('/new-task')} to the New Task button.

--- Logs.tsx ---

Add these imports:
  import { useLogStore } from '../store/logStore'

Inside component:
  const { fetchLogs, fetchSummary } = useLogStore()

  useEffect(() => {
    fetchLogs().catch(() => {})
    fetchSummary().catch(() => {})
  }, [])

The page continues to use the local LOGS mock array and
local stat calculations — the store wiring just prepares
for when the API comes online.


# ============================================================
# PROMPT 18 — NewTask: form submission + validation
# ============================================================

Open src/pages/NewTask.tsx.

Add form validation and submission logic.

Step 1 — Add a validation function:

```tsx
function validate(form: FormState, taskType: TaskType): string[] {
  const errors: string[] = []
  if (!form.processName.trim())
    errors.push('Process Name is required')
  if (!form.mailbox.trim())
    errors.push('Mailbox is required')
  if (!form.logPath.trim())
    errors.push('Log Output Folder Path is required')
  if ((taskType === 'draft' || taskType === 'reminder') && !form.to.trim())
    errors.push('TO recipients are required')
  if ((taskType === 'draft' || taskType === 'reminder') && !form.subject.trim())
    errors.push('Subject is required')
  if ((taskType === 'tracking' || taskType === 'download') && !form.subject.trim())
    errors.push('Subject Line is required')
  return errors
}
```

Step 2 — Add state for validation errors and submission:
  const [errors, setErrors] = useState<string[]>([])
  const [saving, setSaving] = useState(false)

Step 3 — Add handleSave function:
```tsx
const handleSave = async () => {
  const errs = validate(form, taskType)
  if (errs.length > 0) {
    setErrors(errs)
    return
  }
  setErrors([])
  setSaving(true)
  const payload = {
    task_type: taskType,
    process_name: form.processName,
    schedule_type: form.schedule,
    need_to_process: form.needToProcess,
    is_shared_mailbox: form.isSharedMailbox === 'Y',
    mailbox: form.mailbox,
    log_output_folder: form.logPath,
    config: {
      subject_line: form.subject,
      to_stakeholders: form.to,
      cc_stakeholders: form.cc,
      attachment_folder_path: form.attachmentFolder,
      attachment_file_name: form.attachmentFileName,
      email_body_source: form.bodySource,
      email_body_path: form.bodyPath,
      draft_or_send: form.draftOrSend,
      reminder_body_path: form.reminderBodyPath,
      find_replace_pairs: form.findReplace.filter(p => p.find),
      voting_option: form.votingOption,
      partial_subject: form.partialSubject,
      screening_folder: form.screeningFolder,
      start_date: form.startDate,
      end_date: form.endDate,
      due_date: form.dueDate,
      to_tracking: form.toTracking,
      save_email: form.saveEmail,
      save_both: form.saveBoth,
      save_as: form.saveAs,
      download_attachment: form.downloadAttachment,
      all_or_specific: form.allOrSpecific,
      file_type: form.fileType,
      extract_zip: form.extractZip,
    },
  }
  try {
    await useTaskStore.getState().createTask(payload)
    navigate('/scheduled')
  } catch {
    setErrors(['Failed to save task. Please check your connection.'])
  } finally {
    setSaving(false)
  }
}
```

Step 4 — Wire handleSave to both Save Task buttons
(the one in the top header and the one in the sticky bottom bar).

Step 5 — Show validation errors.
Add this block immediately below the top header bar
(between the header and the form layout div):
  {errors.length > 0 && (
    <div className="mx-8 mt-4 p-4 bg-error-container/20 border
      border-error/30 rounded-lg">
      <ul className="list-disc list-inside space-y-1">
        {errors.map((e, i) => (
          <li key={i} className="text-sm text-error">{e}</li>
        ))}
      </ul>
    </div>
  )}

Step 6 — Show loading state on Save Task button:
  When saving is true:
    Replace button text with:
      <span class="material-symbols-outlined animate-spin text-[18px]">
        progress_activity</span>
      Saving...
    And disable the button.

Step 7 — Wire Cancel buttons to navigate(-1).

Step 8 — Import useTaskStore and useNavigate at the top of the file.


# ============================================================
# PROMPT 19 — Final visual pass: fix any remaining issues
# ============================================================

Open each page file and check the following items.
Fix any that are wrong. Do NOT change anything that is already
correct.

CHECKLIST — Run through each item:

1. Tailwind config
   Open tailwind.config.ts.
   Confirm content array is:
     ['./index.html', './src/**/*.{ts,tsx}']
   Confirm all color keys use quotes (they are multi-word with hyphens).
   Confirm fontSize entries are arrays with a second element object.
   If anything is wrong, fix it.

2. index.css
   Confirm it has exactly:
     @tailwind base;
     @tailwind components;
     @tailwind utilities;
     .material-symbols-outlined {
       font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
     }
   Nothing else. No other CSS rules.

3. Sidebar
   Navigate to /mailbox. Confirm sidebar background is dark navy (#1E1F2E).
   Confirm the Mailbox nav item has:
     - white text
     - left border in #4F6BFF
     - bg-[#4F6BFF]/10 background
     - mail icon with FILL 1 style + text-[#4F6BFF] color
   Confirm all other items are #A0A3B1 and get white on hover.

4. Header
   Confirm page title is text-[#4F6BFF] on desktop, NOT text-on-surface.
   Confirm height is exactly h-[56px].
   Confirm border-b border-[#E5E7EB].

5. Mailbox page
   Confirm outer div is: flex-1 flex flex-col h-screen overflow-hidden
   Confirm main is: flex-1 flex overflow-hidden bg-background
   Confirm email list panel is: w-[320px] shrink-0 border-r border-outline-variant
   Confirm selected email row has: bg-[#EEF1FF] border-l-[3px] border-l-primary
   Confirm unselected rows have: border-l-[3px] border-l-transparent
   Confirm attachment icon has style fontVariationSettings: "'FILL' 1"

6. ScheduledTask page
   Confirm main has: bg-surface (NOT bg-background)
   Confirm card has: shadow-[0_4px_24px_rgba(0,0,0,0.02)]
   Confirm enabled toggle: bg-primary, dot at right-1
   Confirm disabled toggle: bg-surface-variant border-outline-variant/50,
     dot at left-1
   Confirm disabled row has: opacity-75
   Confirm disabled Run button has: disabled attribute AND cursor-not-allowed

7. ImportExport page
   Confirm drop zone has: border-2 border-dashed border-[#CBD5E1] bg-[#F8FAFC]
   Confirm drop zone height is h-64
   Confirm import button in disabled state has:
     bg-surface-variant text-on-surface-variant cursor-not-allowed opacity-70
   Confirm export banner uses: bg-tertiary-fixed border-tertiary-fixed-dim
   Confirm checkbox uses custom styled box (NOT native checkbox appearance)

8. Logs page
   Confirm stat card numbers: total+successful = text-on-surface,
     failed = text-error
   Confirm filter pills use PILL style (rounded-full), NOT underline tabs
   Confirm failed rows have: bg-error-container/20 border-l-4 border-l-error
   Confirm log drawer background: bg-inverse-surface
   Confirm drawer INFO lines: text-inverse-on-surface/70
   Confirm drawer SUCCESS lines: text-primary-fixed
   Confirm drawer ERROR lines: text-error-container

9. NewTask page
   Confirm body background: bg-[#F4F5F7]
   Confirm sticky top bar background: bg-[#F4F5F7] (same as page)
   Confirm sticky bottom bar: left-[260px] (accounts for sidebar)
   Confirm "Is Shared Mailbox" + "Mailbox" are in:
     bg-[#F8FAFC] border-l-4 border-[#4F6BFF] p-4 rounded-r-lg
   Confirm Save Task button: bg-[#4F6BFF] hover:bg-[#3D55CC]
     shadow-lg shadow-primary/20

10. Run `npm run dev` and visually verify each page against the
    Stitch designs. List any visual discrepancies found.


# ============================================================
# PROMPT 20 — Connect to backend + final wiring
# ============================================================

This is the final prompt. It wires the frontend to the live
Python FastAPI backend.

Step 1 — Update src/api/client.ts with better error handling:

```ts
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default client
```

Step 2 — Add a health check on app startup.
Open src/App.tsx. Add a useEffect at the top of the App component:

```tsx
useEffect(() => {
  client.get('/health')
    .then(() => console.log('Backend connected'))
    .catch(() => console.warn('Backend offline — using mock data'))
}, [])
```

Import client from './api/client'.

Step 3 — Add the Import/Export API calls.
Open src/pages/ImportExport.tsx.

For the Import submit button onClick handler:
```tsx
const handleImport = async () => {
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const { data } = await client.post('/import/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        const pct = Math.round((e.loaded * 100) / (e.total ?? 1))
        setProgress(pct)
      },
    })
    setImportResult({
      success: true,
      message: `Import successful — ${data.imported} tasks loaded`,
    })
    setFile(null)
  } catch (e) {
    setImportResult({ success: false, message: 'Import failed. Check file format.' })
  } finally {
    setProgress(0)
  }
}
```

Add state: progress: number (0-100), importResult: {success,message}|null

Show a progress bar when progress > 0:
  <div class="w-full bg-surface-container h-1.5 rounded-full mt-3">
    <div class="bg-primary h-1.5 rounded-full transition-all"
      style={{ width: `${progress}%` }}></div>
  </div>

Show result banner after import:
  Success: class="p-3 bg-primary-container/10 border
    border-primary-container/20 rounded-lg text-sm
    text-on-surface-variant flex items-center gap-2"
    icon: check_circle (green — text-primary-container)
  Failure: same structure but error colors

For Export submit button onClick:
```tsx
const handleExport = async () => {
  const { data } = await client.post('/export', {
    format: format.toLowerCase(),
    include_tasks: include.tasks,
    include_logs: include.logs,
    include_rules: include.rules,
  }, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `export.${format === 'Excel' ? 'xlsx' : format.toLowerCase()}`
  a.click()
  URL.revokeObjectURL(url)
}
```

Step 4 — Download template link wiring.
In the import info banner, update the "Download template" href to:
  onClick={(e) => {
    e.preventDefault()
    window.open(
      `${import.meta.env.VITE_API_BASE_URL}/import/template`,
      '_blank'
    )
  }}

Step 5 — Logs export button wiring.
In src/pages/Logs.tsx, add onClick to Export Logs button:
```tsx
const handleExportLogs = async () => {
  const { data } = await client.get('/logs/export', {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(new Blob([data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'execution_logs.json'
  a.click()
  URL.revokeObjectURL(url)
}
```

Step 6 — Final run.
  npm run dev

Verify these API integrations by checking browser Network tab:
  ✓ GET /api/health called on load
  ✓ Navigating to /scheduled triggers GET /api/tasks?type=scheduled
    (even if it returns 503 — the request should be made)
  ✓ Clicking a task toggle triggers PATCH /api/tasks/{id}/toggle
  ✓ Clicking Run triggers POST /api/tasks/{id}/run
  ✓ Navigating to /logs triggers GET /api/logs and GET /api/logs/summary
  ✓ Saving a new task triggers POST /api/tasks
  ✓ Import submit triggers POST /api/import/upload
  ✓ Export submit triggers POST /api/export

If the backend is offline, all pages continue to show mock data
with no crashes. The health check log in the console tells you
whether the backend is reachable.

You now have a complete frontend that:
  - Exactly matches all 6 Stitch screen designs
  - Uses all the correct Tailwind color tokens from Stitch
  - Has real Zustand state management
  - Is wired to the FastAPI backend endpoints
  - Degrades gracefully when the backend is offline
