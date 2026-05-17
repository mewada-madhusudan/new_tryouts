# ============================================================
# BACKEND OFFLINE / CONNECTING SCREENS — Frontend Only
# 3 prompts:
#   OF-1: BackendStatus context + health check hook
#   OF-2: ConnectingScreen + OfflineScreen components
#   OF-3: Wire into AppLayout — replace page content when offline
#
# BACKEND: No changes needed.
#   GET /api/health already exists from B10.
#   These prompts are purely frontend.
#
# SOURCE: offline.html + Connecting.html read in full.
# Class names copied exactly from both files.
# ============================================================


# ============================================================
# OF-1 — BackendStatus context + useHealthCheck hook
# ============================================================

Create src/context/BackendStatusContext.tsx

This context is the single source of truth for whether the
backend is reachable. Every page reads from it. When offline,
AppLayout swaps the page content for OfflineScreen.
When checking on first load, it shows ConnectingScreen.

```tsx
import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import client from '../api/client'

type BackendStatus = 'checking' | 'online' | 'offline'

interface BackendStatusValue {
  status:       BackendStatus
  lastChecked:  string | null     // ISO string of last check time
  attempts:     number            // how many failed attempts in a row
  errorCode:    string | null     // e.g. "ECONNREFUSED", "TIMEOUT", "500"
  retry:        () => void        // manual retry trigger
}

const BackendStatusContext = createContext<BackendStatusValue>({
  status:      'checking',
  lastChecked: null,
  attempts:    0,
  errorCode:   null,
  retry:       () => {},
})

export function useBackendStatus() {
  return useContext(BackendStatusContext)
}

const HEALTH_URL    = `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'}/health`
const RETRY_INTERVAL_MS = 10_000   // auto-retry every 10 seconds when offline
const TIMEOUT_MS        = 5_000    // consider offline after 5s no response

export function BackendStatusProvider({ children }: { children: React.ReactNode }) {
  const [status,      setStatus]      = useState<BackendStatus>('checking')
  const [lastChecked, setLastChecked] = useState<string | null>(null)
  const [attempts,    setAttempts]    = useState(0)
  const [errorCode,   setErrorCode]   = useState<string | null>(null)
  const retryTimerRef                 = useRef<ReturnType<typeof setInterval> | null>(null)
  const countdownRef                  = useRef<ReturnType<typeof setInterval> | null>(null)

  // Countdown state for the "Auto-retry in Xs" chip
  const [countdown, setCountdown]     = useState(10)

  const check = useCallback(async () => {
    setStatus('checking')
    const controller = new AbortController()
    const timeoutId  = setTimeout(() => controller.abort(), TIMEOUT_MS)

    try {
      await client.get('/health', { signal: controller.signal })
      clearTimeout(timeoutId)
      setStatus('online')
      setAttempts(0)
      setErrorCode(null)
      setLastChecked(new Date().toLocaleString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
      }))
      // Clear auto-retry when back online
      if (retryTimerRef.current) clearInterval(retryTimerRef.current)
    } catch (err: unknown) {
      clearTimeout(timeoutId)
      setStatus('offline')
      setAttempts(prev => prev + 1)
      setLastChecked(new Date().toLocaleString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
      }))

      // Determine error code from the error object
      const message = (err as Error).message ?? ''
      if (message.includes('aborted') || message.includes('timeout')) {
        setErrorCode('TIMEOUT')
      } else if (message.includes('Network') || message.includes('fetch')) {
        setErrorCode('ECONNREFUSED')
      } else if (message.includes('500')) {
        setErrorCode('SERVER_ERROR')
      } else {
        setErrorCode('ECONNREFUSED')
      }

      // Start countdown for auto-retry
      setCountdown(10)
      if (countdownRef.current) clearInterval(countdownRef.current)
      countdownRef.current = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            if (countdownRef.current) clearInterval(countdownRef.current)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
  }, [])

  // Run check on mount
  useEffect(() => {
    check()
  }, [check])

  // Auto-retry every RETRY_INTERVAL_MS when offline
  useEffect(() => {
    if (status === 'offline') {
      if (retryTimerRef.current) clearInterval(retryTimerRef.current)
      retryTimerRef.current = setInterval(check, RETRY_INTERVAL_MS)
    }
    return () => {
      if (retryTimerRef.current) clearInterval(retryTimerRef.current)
    }
  }, [status, check])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retryTimerRef.current) clearInterval(retryTimerRef.current)
      if (countdownRef.current)  clearInterval(countdownRef.current)
    }
  }, [])

  return (
    <BackendStatusContext.Provider value={{
      status,
      lastChecked,
      attempts,
      errorCode,
      retry: check,
    }}>
      {/* Pass countdown via a separate context value or prop if needed */}
      {children}
    </BackendStatusContext.Provider>
  )
}
```

Also export countdown so OfflineScreen can show it.
Add countdown to the context value:

```tsx
// Add to BackendStatusValue interface:
countdown: number   // seconds until next auto-retry (0-10)

// Add to Provider value:
countdown,
```

Wrap App.tsx with the provider:

Open src/App.tsx. Import BackendStatusProvider and wrap the
BrowserRouter with it:

```tsx
import { BackendStatusProvider } from './context/BackendStatusContext'

export default function App() {
  return (
    <BackendStatusProvider>
      <BrowserRouter>
        <Routes>
          {/* existing routes unchanged */}
        </Routes>
      </BrowserRouter>
    </BackendStatusProvider>
  )
}
```


# ============================================================
# OF-2 — ConnectingScreen + OfflineScreen components
# ============================================================

Create src/components/BackendStatus/ConnectingScreen.tsx
Create src/components/BackendStatus/OfflineScreen.tsx

Both components replace the main content area only.
The sidebar and header are rendered by AppLayout as normal.
These components slot into the <main> area.

--- ConnectingScreen.tsx ---

Copied EXACTLY from Connecting.html body content:

```tsx
export default function ConnectingScreen() {
  return (
    <main className="ml-sidebar-width mt-[56px] min-h-[calc(100vh-56px)] bg-surface flex items-center justify-center p-lg">
      <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-xl max-w-[440px] w-full shadow-sm flex flex-col items-center text-center">

        {/* Spinning icon — exact Connecting.html */}
        <div className="relative w-[80px] h-[80px] rounded-full bg-surface-container flex items-center justify-center mb-lg">
          <div className="absolute inset-0 border-4 border-outline-variant/40 rounded-full" />
          <div className="absolute inset-0 border-4 border-t-primary border-transparent rounded-full animate-spin"
            style={{ animationDuration: '1.5s' }} />
          <span className="material-symbols-outlined text-outline text-[36px]"
            style={{ fontVariationSettings: "'FILL' 0" }}>
            cloud_sync
          </span>
        </div>

        {/* Text — exact Connecting.html */}
        <div className="space-y-sm mb-lg">
          <h3 className="font-page-title text-page-title text-on-surface">
            Connecting...
          </h3>
        </div>

        {/* Animated dots — exact Connecting.html */}
        <div className="flex items-center gap-2 mb-xl">
          <div className="w-2 h-2 rounded-full bg-primary" />
          <div className="w-2 h-2 rounded-full bg-outline-variant" />
          <div className="w-2 h-2 rounded-full bg-outline-variant" />
        </div>

        {/* Footer note — exact Connecting.html */}
        <footer className="mt-auto">
          <span className="font-meta text-meta text-outline">
            This usually takes less than a second
          </span>
        </footer>

      </div>
    </main>
  )
}
```

--- OfflineScreen.tsx ---

Copied EXACTLY from offline.html body content.
Uses useBackendStatus() to read live values.

```tsx
import { useBackendStatus } from '../../context/BackendStatusContext'

export default function OfflineScreen() {
  const { lastChecked, attempts, errorCode, retry, countdown } = useBackendStatus()

  return (
    <main className="ml-sidebar-width pt-[56px] h-screen bg-surface flex flex-col items-center justify-center p-lg gap-6 overflow-y-auto">

      {/* MAIN ERROR CARD — exact offline.html */}
      <div className="bg-white rounded-2xl border border-outline-variant p-xl max-w-[480px] w-full shadow-sm flex flex-col items-center text-center">

        {/* Cloud off icon — exact offline.html */}
        <div className="w-20 h-20 bg-error-container rounded-full flex items-center justify-center mb-md">
          <span className="material-symbols-outlined text-[40px] text-error"
            style={{ fontVariationSettings: "'FILL' 1" }}>
            cloud_off
          </span>
        </div>

        <h3 className="text-[22px] font-bold text-on-surface mb-xs">
          Backend is offline
        </h3>
        <p className="font-body text-on-surface-variant mb-xl">
          The automation server isn't running or isn't reachable.
        </p>

        {/* Action buttons — exact offline.html */}
        <div className="w-full flex flex-col gap-sm mt-xl">
          <button
            onClick={retry}
            className="h-10 bg-primary text-on-primary rounded-lg flex items-center justify-between px-md hover:brightness-110 active:scale-[0.98] transition-all"
          >
            <div className="flex items-center gap-sm font-medium">
              <span className="material-symbols-outlined">refresh</span>
              Try Again
            </div>
            {/* Auto-retry countdown chip — exact offline.html */}
            <div className="bg-primary-container/20 px-2 py-0.5 rounded text-[11px] font-medium">
              {countdown > 0 ? `Auto-retry in ${countdown}s` : 'Retrying...'}
            </div>
          </button>
        </div>
      </div>

      {/* STATUS STRIP — exact offline.html */}
      <div className="max-w-[480px] w-full bg-surface-container-low rounded-xl border border-outline-variant px-md py-sm flex items-center justify-between text-[12px]">
        <div className="flex items-center gap-md">
          {/* Pulsing red dot — uses custom animation from offline.html */}
          <div className="w-2 h-2 rounded-full bg-error animate-pulse-red" />
          <div className="flex items-center gap-sm">
            <span className="text-outline">Last checked:</span>
            <span className="font-mono text-on-surface font-medium">
              {lastChecked ?? '—'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-md border-l border-outline-variant pl-md">
          <span className="font-mono text-on-surface-variant">
            Attempts: {attempts}
          </span>
          <span className="font-mono text-error font-medium">
            {errorCode ?? 'ECONNREFUSED'}
          </span>
        </div>
      </div>

      {/* INFO NOTICE — exact offline.html */}
      <div className="max-w-[480px] w-full bg-primary-container/5 border border-primary/20 p-md rounded-xl flex gap-md">
        <span className="material-symbols-outlined text-primary">info</span>
        <div className="flex flex-col">
          <p className="font-medium text-on-primary-container text-body">
            Sidebar navigation is available
          </p>
          <p className="text-on-surface-variant text-[13px]">
            You can browse between pages. Data will load once the
            server is back online.
          </p>
        </div>
      </div>

    </main>
  )
}
```

Add the pulse-red animation from offline.html to src/index.css:

```css
/* Offline screen — pulsing red dot animation (from offline.html) */
@keyframes pulse-red {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}
.animate-pulse-red {
  animation: pulse-red 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```


# ============================================================
# OF-3 — Wire into AppLayout: swap content when offline
# ============================================================

Open src/components/Layout/AppLayout.tsx.

This is the file that renders the sidebar + header + page
content for every route. We intercept the content area here
so EVERY page gets the offline screen automatically without
touching any individual page file.

Current AppLayout (before change):
```tsx
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppLayout() {
  return (
    <div className="bg-background font-body text-on-surface antialiased flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col md:ml-[260px] h-full overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
```

Replace with:

```tsx
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import ConnectingScreen from '../BackendStatus/ConnectingScreen'
import OfflineScreen    from '../BackendStatus/OfflineScreen'
import { useBackendStatus } from '../../context/BackendStatusContext'
import { useLocation } from 'react-router-dom'

// Map route paths to page titles for the Header
const PAGE_TITLES: Record<string, string> = {
  '/dashboard':     'Dashboard',
  '/mailbox':       'Mailbox',
  '/new-task':      'New Task',
  '/tasks':         'All Tasks',
  '/scheduled':     'Scheduled Task',
  '/import-export': 'Import/Export',
  '/rules':         'Rules',
  '/logs':          'Logs',
  '/settings':      'Settings',
}

export default function AppLayout() {
  const { status } = useBackendStatus()
  const location   = useLocation()
  const title      = PAGE_TITLES[location.pathname] ?? 'Your Personal Assistant'

  return (
    <div className="bg-background font-body text-on-surface antialiased flex h-screen overflow-hidden">

      {/* Sidebar — always visible regardless of backend status */}
      <Sidebar />

      {/* Right side: header + content */}
      <div className="flex-1 flex flex-col md:ml-[260px] h-full overflow-hidden">

        {/* Header — always visible regardless of backend status */}
        <Header title={title} />

        {/* Content area — swapped based on backend status */}
        {status === 'checking' && <ConnectingScreen />}
        {status === 'offline'  && <OfflineScreen />}
        {status === 'online'   && (
          <div className="flex-1 overflow-hidden">
            <Outlet />
          </div>
        )}

      </div>
    </div>
  )
}
```

IMPORTANT: Because ConnectingScreen and OfflineScreen
already include ml-sidebar-width and mt-[56px] in their
own markup (copied from the Stitch HTML), remove those
offset classes from the wrapping div above. The screens
are self-contained and handle their own positioning.

Actually — re-read both Stitch HTML files.
ConnectingScreen has: ml-sidebar-width mt-[56px]
OfflineScreen has:    ml-sidebar-width pt-[56px]

These were written for a layout WITHOUT AppLayout wrapping them.
Since AppLayout now provides the sidebar offset (ml-[260px] on
the right-side div), REMOVE ml-sidebar-width from both screen
components. Keep only the top offset (mt-[56px] / pt-[56px])
since the header is still rendered above them.

Update ConnectingScreen.tsx main element:
  CHANGE: className="ml-sidebar-width mt-[56px] ..."
  TO:     className="mt-[56px] ..."   (remove ml-sidebar-width)

Update OfflineScreen.tsx main element:
  CHANGE: className="ml-sidebar-width pt-[56px] ..."
  TO:     className="pt-[56px] ..."   (remove ml-sidebar-width)

--- FINAL VERIFICATION ---

Run npm run dev with the backend NOT running.
Open http://localhost:5173

Expected behaviour:
  1. App loads — ConnectingScreen appears for ~5 seconds
     (the health check timeout duration)
     Spinner animates, dots show, "Connecting..." text visible

  2. Health check fails — OfflineScreen replaces ConnectingScreen
     - Sidebar visible with correct nav items
     - Header visible with "Dashboard" title + bell + avatar
     - Error card centered in content area:
         cloud_off icon in bg-error-container circle
         "Backend is offline" heading
         "Try Again" button with countdown chip counting down
     - Status strip below: pulsing red dot, last checked time,
       attempt count, ECONNREFUSED error code
     - Info notice below: "Sidebar navigation is available"

  3. Countdown chip counts down: "Auto-retry in 10s" → "9s" → ...
     At 0: automatically retries health check

  4. Clicking "Try Again": immediately retries health check,
     countdown resets to 10

  5. Click any sidebar link — page changes (title updates in header)
     but OfflineScreen content stays (no dummy data shown)

  6. Start the backend (uvicorn app.main:app --reload --port 8000)
     Within 10 seconds the auto-retry fires, health check succeeds,
     OfflineScreen disappears, Dashboard loads with real data.

  7. While backend IS running: ConnectingScreen shows for <1 second
     then immediately transitions to the real page content.

If dummy data appears at any point:
  - Check that status === 'online' is the ONLY condition that
    renders <Outlet /> in AppLayout.tsx
  - Check that individual pages do NOT call APIs before checking
    status (they shouldn't since they never render when offline).
