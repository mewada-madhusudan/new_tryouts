# ============================================================
# PROMPTS 1–5 OF 20
# Your Personal Assistant — React TypeScript Frontend
# All class names are copied EXACTLY from Stitch HTML source.
# Do not paraphrase. Do not substitute. Copy exactly.
# ============================================================


# ============================================================
# PROMPT 1 — Vite + React TS scaffold, install dependencies
# ============================================================

Create a brand new React TypeScript project using Vite.
Run these commands exactly:

  npm create vite@latest personal-assistant -- --template react-ts
  cd personal-assistant
  npm install
  npm install react-router-dom axios zustand
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p

Then create this exact folder structure under src/
(create empty placeholder files — no content yet):

  src/
    components/
      Layout/
        Sidebar.tsx       ← empty
        Header.tsx        ← empty
        AppLayout.tsx     ← empty
    pages/
      Mailbox.tsx         ← empty
      NewTask.tsx         ← empty
      AllTasks.tsx        ← empty
      ScheduledTask.tsx   ← empty
      ImportExport.tsx    ← empty
      Logs.tsx            ← empty
    store/
      taskStore.ts        ← empty
      logStore.ts         ← empty
      mailboxStore.ts     ← empty
    api/
      client.ts           ← empty
    App.tsx               ← empty
    main.tsx              ← empty

Do not write any component code yet.
Only run commands and create the folder structure.
Confirm when done.


# ============================================================
# PROMPT 2 — tailwind.config.ts + index.css + index.html
# ============================================================

Step A — Replace the ENTIRE content of tailwind.config.ts
with exactly this. Do not change any value:

```ts
import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'inverse-surface':            '#2f3039',
        'surface-container-lowest':   '#ffffff',
        'tertiary':                   '#994200',
        'on-tertiary-fixed-variant':  '#773200',
        'surface-bright':             '#fbf8ff',
        'on-tertiary-fixed':          '#331200',
        'on-tertiary-container':      '#fffbff',
        'secondary-container':        '#e2e0f6',
        'secondary':                  '#5d5d6e',
        'on-primary-container':       '#fffbff',
        'on-secondary-container':     '#636375',
        'primary':                    '#2a49df',
        'background':                 '#fbf8ff',
        'surface':                    '#fbf8ff',
        'primary-container':          '#4965f9',
        'on-primary':                 '#ffffff',
        'on-primary-fixed-variant':   '#002fc9',
        'error':                      '#ba1a1a',
        'on-surface-variant':         '#444655',
        'on-secondary':               '#ffffff',
        'tertiary-fixed':             '#ffdbca',
        'surface-dim':                '#dad9e5',
        'tertiary-container':         '#bf5500',
        'surface-tint':               '#2d4ce2',
        'surface-variant':            '#e2e1ee',
        'error-container':            '#ffdad6',
        'surface-container-high':     '#e8e7f3',
        'tertiary-fixed-dim':         '#ffb68f',
        'inverse-primary':            '#bac3ff',
        'on-secondary-fixed-variant': '#454556',
        'on-tertiary':                '#ffffff',
        'on-error-container':         '#93000a',
        'on-surface':                 '#1a1b24',
        'secondary-fixed':            '#e2e0f6',
        'surface-container-highest':  '#e2e1ee',
        'outline-variant':            '#c5c5d8',
        'inverse-on-surface':         '#f1effc',
        'surface-container-low':      '#f4f2ff',
        'surface-container':          '#eeecf9',
        'on-error':                   '#ffffff',
        'primary-fixed':              '#dee0ff',
        'secondary-fixed-dim':        '#c5c5d9',
        'on-secondary-fixed':         '#191a29',
        'on-primary-fixed':           '#00105b',
        'primary-fixed-dim':          '#bac3ff',
        'on-background':              '#1a1b24',
        'outline':                    '#757687',
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg:      '0.5rem',
        xl:      '0.75rem',
        full:    '9999px',
      },
      spacing: {
        xs:            '4px',
        sm:            '8px',
        md:            '16px',
        lg:            '24px',
        xl:            '32px',
        base:          '4px',
        gutter:        '24px',
        'sidebar-width': '260px',
      },
      fontFamily: {
        mono:           ['JetBrains Mono', 'monospace'],
        body:           ['Inter', 'sans-serif'],
        'page-title':   ['Inter', 'sans-serif'],
        meta:           ['Inter', 'sans-serif'],
        'section-label':['Inter', 'sans-serif'],
      },
      fontSize: {
        mono:           ['13px', { lineHeight: '20px', fontWeight: '400' }],
        body:           ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'page-title':   ['20px', { lineHeight: '28px', letterSpacing: '-0.01em', fontWeight: '600' }],
        meta:           ['12px', { lineHeight: '16px', fontWeight: '400' }],
        'section-label':['13px', { lineHeight: '16px', letterSpacing: '0.05em', fontWeight: '500' }],
      },
    },
  },
  plugins: [],
} satisfies Config
```

Step B — Replace the ENTIRE content of src/index.css with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```

Step C — Replace the ENTIRE <head> section of index.html with:

```html
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Your Personal Assistant</title>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400&display=swap"
    rel="stylesheet"
  />
  <link
    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
    rel="stylesheet"
  />
  <script type="module" src="/src/main.tsx"></script>
</head>
```

Step D — Create a .env file in the project root:
  VITE_API_BASE_URL=http://localhost:8000/api

Do not write any component code yet. Confirm when done.


# ============================================================
# PROMPT 3 — Sidebar.tsx
# ============================================================

Open src/components/Layout/Sidebar.tsx and replace it entirely
with the code below. This is translated DIRECTLY from the Stitch
HTML. Do not change any class names, colors, or structure.

The sidebar from Stitch is:
  <nav class="fixed left-0 top-0 h-full w-sidebar-width
    bg-[#1E1F2E] border-r border-gray-800 flex flex-col
    py-6 z-20 hidden md:flex">

Active nav item from Stitch:
  class="text-white border-l-4 border-[#4F6BFF] bg-[#4F6BFF]/10
    flex items-center px-6 py-3 transition-all duration-200 gap-3"
  + icon has style="font-variation-settings: 'FILL' 1;"
  + icon color: text-[#4F6BFF]

Inactive nav item from Stitch:
  class="text-[#A0A3B1] flex items-center px-6 py-3
    transition-all hover:bg-white/5 hover:text-white group gap-3"
  + icon has class="opacity-70 group-hover:opacity-100 transition-opacity"

Nav items in order (label → icon name):
  Mailbox       → mail
  New Task      → add_task
  All Tasks     → list_alt
  Scheduled Task→ schedule
  Import/Export → swap_horiz
  Logs          → terminal

Settings at bottom (same inactive style).

Logo block from Stitch:
  <div class="px-6 mb-8 flex items-center gap-3">
    <div class="w-8 h-8 rounded bg-[#4F6BFF] flex items-center
      justify-center text-white font-bold text-sm">PA</div>
    <div>
      <h1 class="text-[13px] font-semibold text-white">
        Your Personal Assistant</h1>
      <p class="text-[11px] text-[#A0A3B1]">Outlook Automation</p>
    </div>
  </div>

Nav items wrapper from Stitch:
  <div class="flex-1 overflow-y-auto font-['Inter']
    text-[13px] font-semibold">

Settings wrapper from Stitch:
  <div class="mt-auto px-6 font-['Inter'] text-[13px] font-semibold">

Write the complete component now using NavLink from react-router-dom.
Use NavLink's isActive to switch between active and inactive class strings.
When isActive is true, add style={{ fontVariationSettings: "'FILL' 1" }}
to the icon span and add class text-[#4F6BFF] to the icon span.

```tsx
import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { label: 'Mailbox',         icon: 'mail',        to: '/mailbox'       },
  { label: 'New Task',        icon: 'add_task',    to: '/new-task'      },
  { label: 'All Tasks',       icon: 'list_alt',    to: '/tasks'         },
  { label: 'Scheduled Task',  icon: 'schedule',    to: '/scheduled'     },
  { label: 'Import/Export',   icon: 'swap_horiz',  to: '/import-export' },
  { label: 'Logs',            icon: 'terminal',    to: '/logs'          },
]

export default function Sidebar() {
  return (
    <nav className="fixed left-0 top-0 h-full w-[260px] bg-[#1E1F2E] border-r border-gray-800 flex flex-col py-6 z-20 hidden md:flex">

      {/* Logo — exact Stitch */}
      <div className="px-6 mb-8 flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-[#4F6BFF] flex items-center justify-center text-white font-bold text-sm">
          PA
        </div>
        <div>
          <h1 className="text-[13px] font-semibold text-white">Your Personal Assistant</h1>
          <p className="text-[11px] text-[#A0A3B1]">Outlook Automation</p>
        </div>
      </div>

      {/* Nav links — exact Stitch */}
      <div className="flex-1 overflow-y-auto font-['Inter'] text-[13px] font-semibold">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive
                ? 'text-white border-l-4 border-[#4F6BFF] bg-[#4F6BFF]/10 flex items-center px-6 py-3 transition-all duration-200 gap-3'
                : 'text-[#A0A3B1] flex items-center px-6 py-3 transition-all hover:bg-white/5 hover:text-white group gap-3'
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={`material-symbols-outlined text-[20px] ${isActive ? 'text-[#4F6BFF]' : 'opacity-70 group-hover:opacity-100 transition-opacity'}`}
                  style={isActive ? { fontVariationSettings: "'FILL' 1" } : undefined}
                >
                  {item.icon}
                </span>
                {item.label}
              </>
            )}
          </NavLink>
        ))}
      </div>

      {/* Settings — exact Stitch */}
      <div className="mt-auto px-6 font-['Inter'] text-[13px] font-semibold">
        <NavLink
          to="/settings"
          className="text-[#A0A3B1] flex items-center py-3 transition-all hover:bg-white/5 hover:text-white group gap-3"
        >
          <span className="material-symbols-outlined text-[20px] opacity-70 group-hover:opacity-100 transition-opacity">
            settings
          </span>
          Settings
        </NavLink>
      </div>

    </nav>
  )
}
```


# ============================================================
# PROMPT 4 — Header.tsx + AppLayout.tsx
# ============================================================

--- src/components/Layout/Header.tsx ---

The header from Stitch (scheduled tasks screen) is:
  <header class="bg-white dark:bg-gray-900 border-b border-[#E5E7EB]
    dark:border-gray-800 h-[56px] flex justify-between items-center
    px-6 w-full z-10 shrink-0">

Left side — desktop shows page title in:
  class="hidden md:block text-[#4F6BFF] font-['Inter']
    text-[20px] font-semibold"

Left side — mobile shows app name in:
  class="text-xl font-semibold text-gray-900 dark:text-white md:hidden"

Right side:
  Bell button:
    class="text-gray-500 dark:text-gray-400 hover:text-[#4F6BFF]
      transition-colors hover:scale-105 active:scale-95"
    icon: notifications

  User section:
    class="flex items-center gap-2 cursor-pointer"
    → <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
        Username</span>
    → avatar: w-8 h-8 rounded-full bg-gray-200 overflow-hidden
      with a person icon inside

Write this component accepting a `title: string` prop:

```tsx
interface HeaderProps {
  title: string
}

export default function Header({ title }: HeaderProps) {
  return (
    <header className="bg-white border-b border-[#E5E7EB] h-[56px] flex justify-between items-center px-6 w-full z-10 shrink-0">
      {/* Mobile title */}
      <div className="text-xl font-semibold text-gray-900 md:hidden">
        Your Personal Assistant
      </div>
      {/* Desktop page title — text-[#4F6BFF] exactly as Stitch */}
      <div className="hidden md:block text-[#4F6BFF] font-['Inter'] text-[20px] font-semibold">
        {title}
      </div>
      {/* Right side */}
      <div className="flex items-center gap-4">
        <button className="text-gray-500 hover:text-[#4F6BFF] transition-colors hover:scale-105 active:scale-95">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <div className="flex items-center gap-2 cursor-pointer">
          <span className="text-sm font-medium text-gray-700">Username</span>
          <div className="w-8 h-8 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center">
            <span className="material-symbols-outlined text-gray-500 text-[18px]">person</span>
          </div>
        </div>
      </div>
    </header>
  )
}
```

--- src/components/Layout/AppLayout.tsx ---

From Stitch the body wrapper is:
  <body class="bg-background font-body text-body
    text-on-background flex h-screen overflow-hidden">

The main content wrapper (next to sidebar) is:
  <div class="flex-1 flex flex-col md:ml-sidebar-width h-full">

Because we defined sidebar-width as a spacing token (260px),
use md:ml-[260px] explicitly to avoid any Tailwind JIT issues.

```tsx
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppLayout() {
  return (
    <div className="bg-background font-body text-body text-on-background flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col md:ml-[260px] h-full overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
```


# ============================================================
# PROMPT 5 — App.tsx + main.tsx + api/client.ts
# ============================================================

--- src/App.tsx ---

Set up all routes. Every page uses AppLayout as the shell.
All pages currently just render a placeholder div — that is fine,
they will be filled in subsequent prompts.

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout/AppLayout'
import Mailbox from './pages/Mailbox'
import NewTask from './pages/NewTask'
import AllTasks from './pages/AllTasks'
import ScheduledTask from './pages/ScheduledTask'
import ImportExport from './pages/ImportExport'
import Logs from './pages/Logs'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/mailbox" replace />} />
          <Route path="/mailbox"       element={<Mailbox />} />
          <Route path="/new-task"      element={<NewTask />} />
          <Route path="/tasks"         element={<AllTasks />} />
          <Route path="/scheduled"     element={<ScheduledTask />} />
          <Route path="/import-export" element={<ImportExport />} />
          <Route path="/logs"          element={<Logs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
```

--- src/main.tsx ---

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

--- src/api/client.ts ---

```ts
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
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

--- Placeholder pages ---

For each of these files, write ONLY a placeholder so the app compiles:
src/pages/Mailbox.tsx:
  export default function Mailbox() { return <div className="p-8 text-on-surface">Mailbox — coming soon</div> }

src/pages/NewTask.tsx:
  export default function NewTask() { return <div className="p-8 text-on-surface">New Task — coming soon</div> }

src/pages/AllTasks.tsx:
  export default function AllTasks() { return <div className="p-8 text-on-surface">All Tasks — coming soon</div> }

src/pages/ScheduledTask.tsx:
  export default function ScheduledTask() { return <div className="p-8 text-on-surface">Scheduled Task — coming soon</div> }

src/pages/ImportExport.tsx:
  export default function ImportExport() { return <div className="p-8 text-on-surface">Import/Export — coming soon</div> }

src/pages/Logs.tsx:
  export default function Logs() { return <div className="p-8 text-on-surface">Logs — coming soon</div> }

After writing all files, run:
  npm run dev

Open http://localhost:5173 and confirm:
  ✓ Dark navy sidebar appears on the left (260px wide)
  ✓ Active route has white text + blue left border + blue/10 background
  ✓ Inactive routes have #A0A3B1 text
  ✓ Header shows blue page title on desktop
  ✓ Page background is #fbf8ff (very light purple-white)
  ✓ No TypeScript errors in the terminal

Fix any errors before proceeding to Prompt 6.
