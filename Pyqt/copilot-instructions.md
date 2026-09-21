# Copilot instructions: PyQt6 desktop app (SharePoint + network share, PyInstaller exe)

Place at `.github/copilot-instructions.md` in the repo.

## Project context
- Python + PyQt6 desktop app for Windows, shipped as a PyInstaller exe.
- Talks to SharePoint (behind a corporate proxy, NTLM/Kerberos auth) and to SMB/UNC shared drives.
- Priority: the UI must never freeze, show "Not Responding", or crash silently.

## Hard rules for every change
1. **The GUI thread does UI work only.** Never run these on the main thread: HTTP/SharePoint calls, auth/token acquisition, file or folder I/O (including `os.listdir`, `os.path.exists`, `os.stat`, `shutil`, `open`) on UNC/mapped/OneDrive paths, `time.sleep`, `subprocess.run`, thread `.join()`, or heavy pandas/Excel/JSON processing.
2. **Use one threading pattern consistently:** `QThreadPool` + `QRunnable` with a `WorkerSignals(QObject)` (`finished`, `error`, `progress`, `result`), or a `QObject` worker moved to a `QThread`. Do not mix in raw `threading.Thread` that touches widgets.
3. **Never touch widgets from a worker thread.** Communicate only through signals (queued connections). Pass plain data (dict, dataclass, str), never QWidgets or QModelIndex.
4. **Every network and share call gets an explicit timeout** (connect + read) and a cancel path. No unbounded retries; use bounded retry with backoff.
5. **Keep worker objects alive.** Hold a reference (attribute on the window, or the pool) until `finished`; a garbage-collected QThread/QRunnable causes random crashes.
6. **Shut down cleanly.** On `closeEvent`: stop timers, request cancellation, `quit()` + `wait(timeout)` threads, then accept. Never `wait()` without a timeout on the UI thread.
7. **Guard slots.** Wrap slot bodies that can fail in try/except and log with `logging.exception`. An unhandled exception in a slot can abort the app in PyQt6.
8. **Large data goes through a model**, not widget-by-widget: `QAbstractTableModel` / `QStandardItemModel`, batched updates, `setUpdatesEnabled(False)` or `blockSignals(True)` around bulk changes. Do not use `QApplication.processEvents()` to "fix" freezes.
9. **Prevent double-triggering:** disable the button or show a busy state while a task runs; ignore re-entrant clicks.
10. **No `print()` for diagnostics.** Windowed exes have `sys.stdout`/`sys.stderr` set to `None`. Use `logging` to a rotating file.
11. **Paths:** prefer UNC (`\\server\share\...`) over mapped drive letters (mapped letters are per-session and missing in elevated or scheduled contexts). Use `pathlib`. Resolve bundled resources via `sys._MEIPASS` when frozen.
12. **Secrets/credentials:** never hardcode; never log tokens, cookies, or full URLs with query strings.

## When asked to fix a bug
- First reproduce or reason about it from the log (`%LOCALAPPDATA%\<AppName>\logs\`), including the watchdog's "UI thread stalled" stack dump.
- Prefer the smallest change that removes the blocking call or race. Explain the root cause in one or two sentences.
- Do not rewrite unrelated code.

## Runtime/system-specific causes to consider
Slow or offline share, VPN/proxy state, expired Kerberos ticket, SharePoint throttling (HTTP 429/503), OneDrive/AV file locks, antivirus scanning the exe, DPI scaling or multi-monitor differences, missing VC++ runtime, locale/encoding differences, Windows long paths, different Python/PyQt6/Qt versions between dev and build machine, PyInstaller missing hidden imports or Qt plugins.
