"""
diagnostics.py - drop-in runtime diagnostics for a PyQt6 app (works in a windowed PyInstaller exe).

Usage in your entry point:

    from diagnostics import install_diagnostics, start_ui_watchdog

    install_diagnostics("MyApp")          # BEFORE creating QApplication
    app = QApplication(sys.argv)
    start_ui_watchdog(stall_seconds=3.0)  # AFTER creating QApplication
    ...
    sys.exit(app.exec())

Logs go to %LOCALAPPDATA%\\<AppName>\\logs\\ (falls back to the home directory):
    app.log         rotating application log (includes UI-stall stack dumps)
    faulthandler.log  hard-crash tracebacks (segfaults, fatal Qt errors)

When the UI thread is blocked for longer than `stall_seconds`, the main thread's
stack is written to app.log. That line tells you exactly which call is blocking.
"""
from __future__ import annotations

import faulthandler
import logging
import logging.handlers
import os
import platform
import sys
import threading
import time
import traceback
from pathlib import Path

from PyQt6.QtCore import (
    PYQT_VERSION_STR,
    QT_VERSION_STR,
    QTimer,
    QtMsgType,
    qInstallMessageHandler,
)

log = logging.getLogger("diag")

_fault_file = None  # keep a reference so the file isn't closed/garbage collected
_watchdog = None    # keep a reference to the watchdog


def _log_dir(app_name: str) -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    path = Path(base) / app_name / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _format_all_thread_stacks() -> str:
    names = {t.ident: t.name for t in threading.enumerate()}
    parts = []
    for ident, frame in sys._current_frames().items():
        parts.append(f"--- Thread {names.get(ident, '?')} (id={ident}) ---")
        parts.append("".join(traceback.format_stack(frame)))
    return "\n".join(parts)


def _qt_message_handler(msg_type, context, message):
    level = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }.get(msg_type, logging.INFO)
    log.log(level, "Qt: %s (%s:%s)", message, getattr(context, "file", ""), getattr(context, "line", ""))


def install_diagnostics(app_name: str, level: int = logging.INFO) -> Path:
    """Set up file logging, exception hooks, faulthandler and a Qt message handler."""
    global _fault_file
    logs = _log_dir(app_name)

    handler = logging.handlers.RotatingFileHandler(
        logs / "app.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # Windowed exes have sys.stdout / sys.stderr == None; faulthandler needs a real file.
    _fault_file = open(logs / "faulthandler.log", "a", buffering=1, encoding="utf-8")
    faulthandler.enable(file=_fault_file, all_threads=True)

    def _excepthook(exc_type, exc, tb):
        log.critical("Unhandled exception", exc_info=(exc_type, exc, tb))

    def _thread_excepthook(args):
        log.critical(
            "Unhandled exception in thread %s",
            getattr(args.thread, "name", "?"),
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    def _unraisable_hook(unraisable):
        log.error("Unraisable exception: %s (object=%r)", unraisable.exc_value, unraisable.object)

    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook
    sys.unraisablehook = _unraisable_hook
    qInstallMessageHandler(_qt_message_handler)

    log.info("=== %s starting ===", app_name)
    log.info(
        "OS=%s | Python=%s | PyQt6=%s | Qt=%s | frozen=%s | exe=%s",
        platform.platform(), platform.python_version(), PYQT_VERSION_STR, QT_VERSION_STR,
        getattr(sys, "frozen", False), sys.executable,
    )
    log.info(
        "Proxy env set: HTTP_PROXY=%s HTTPS_PROXY=%s NO_PROXY=%s",
        bool(os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")),
        bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")),
        bool(os.environ.get("NO_PROXY") or os.environ.get("no_proxy")),
    )
    return logs


class _UiWatchdog:
    """A QTimer on the UI thread updates a heartbeat; a background thread checks it."""

    def __init__(self, stall_seconds: float, beat_ms: int = 250):
        self._stall = stall_seconds
        self._last_beat = time.monotonic()
        self._main_ident = threading.main_thread().ident
        self._timer = QTimer()
        self._timer.setInterval(beat_ms)
        self._timer.timeout.connect(self._beat)
        self._thread = threading.Thread(target=self._run, name="ui-watchdog", daemon=True)

    def start(self):
        self._timer.start()
        self._thread.start()

    def _beat(self):
        self._last_beat = time.monotonic()

    def _run(self):
        reporting = False
        stall_start = 0.0
        while True:
            time.sleep(0.5)
            stalled_for = time.monotonic() - self._last_beat
            if stalled_for >= self._stall and not reporting:
                reporting = True
                stall_start = time.monotonic() - stalled_for
                frame = sys._current_frames().get(self._main_ident)
                main_stack = "".join(traceback.format_stack(frame)) if frame else "<unavailable>"
                log.error(
                    "UI THREAD STALLED for >= %.1fs. Main thread stack:\n%s\nAll threads:\n%s",
                    stalled_for, main_stack, _format_all_thread_stacks(),
                )
            elif stalled_for < self._stall and reporting:
                reporting = False
                log.warning("UI thread recovered after ~%.1fs", time.monotonic() - stall_start)


def start_ui_watchdog(stall_seconds: float = 3.0) -> None:
    """Call from the main thread after QApplication exists."""
    global _watchdog
    _watchdog = _UiWatchdog(stall_seconds)
    _watchdog.start()
