# ============================================================
# NEW FEATURE PROMPTS — Part 1 of 2
# Feature A: Response Consolidation  (FA1-FA2 frontend, BA1-BA2 backend)
# Feature B: Calendar Event Creation (FB1-FB2 frontend, BB1-BB2 backend)
# Feature C: Multi-job Run Selection (FC1 frontend,    BC1 backend)
# ============================================================
# Run order: BA1 → BA2 → BB1 → BB2 → BC1 first (backend)
#            then FA1 → FA2 → FB1 → FB2 → FC1 (frontend)
# ============================================================


# ============================================================
# BA1 — Response Consolidation: service layer
# ============================================================

Create app/services/consolidation_service.py

Context: A user sends a draft mail to many people asking them
to fill in data in a particular Excel format. When tracking
those responses, the user wants to consolidate all the reply
attachments (which share the same Excel format/columns) into
one single merged Excel file.

This service handles that merging logic.

```python
"""
Consolidation Service

When email tracking finds responses to a draft mail, each
respondent may have attached an Excel file with the same
column structure. This service:
  1. Reads all attachment files from a given folder
  2. Validates they share the same column headers
  3. Merges all rows into a single output Excel file
  4. Adds a "Source" column showing which file each row came from
  5. Writes the merged file to the configured output path
"""
import logging
from pathlib import Path
from typing import Optional
import openpyxl
from openpyxl import Workbook

logger = logging.getLogger(__name__)


class ConsolidationResult:
    def __init__(self):
        self.merged_rows: int = 0
        self.source_files: list[str] = []
        self.skipped_files: list[str] = []
        self.errors: list[str] = []
        self.output_path: str = ''
        self.success: bool = False


def consolidate_responses(
    input_folder: str,
    output_path: str,
    file_pattern: str = '*.xlsx',
    sheet_name: Optional[str] = None,   # None = first sheet
    header_row: int = 1,
    add_source_column: bool = True,
) -> ConsolidationResult:
    """
    Merge all Excel files in input_folder into a single output file.

    Args:
        input_folder:      Folder containing the response files
        output_path:       Full path for the merged output file
        file_pattern:      Glob pattern to match files (default *.xlsx)
        sheet_name:        Sheet to read from each file (None = first sheet)
        header_row:        Row number of the header (default 1)
        add_source_column: Add a "Source File" column to merged output

    Returns:
        ConsolidationResult with counts, paths, and any errors
    """
    result = ConsolidationResult()
    folder = Path(input_folder)

    if not folder.exists():
        result.errors.append(f"Input folder does not exist: {input_folder}")
        return result

    files = sorted(folder.glob(file_pattern))
    if not files:
        result.errors.append(f"No files matching '{file_pattern}' in {input_folder}")
        return result

    # --- Pass 1: read headers from all files, validate consistency ---
    reference_headers: list[str] = []
    file_data: list[tuple[Path, list[str], list[list]]] = []

    for file in files:
        try:
            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            ws = wb[sheet_name] if sheet_name and sheet_name in wb.sheetnames else wb.active

            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                result.skipped_files.append(f"{file.name}: empty sheet")
                wb.close()
                continue

            headers = [str(h).strip() if h is not None else '' for h in rows[header_row - 1]]
            data_rows = [list(r) for r in rows[header_row:] if any(c is not None for c in r)]
            wb.close()

            if not reference_headers:
                reference_headers = headers
            else:
                # Validate headers match
                if headers != reference_headers:
                    mismatches = [
                        f"col {i+1}: expected '{reference_headers[i] if i < len(reference_headers) else '(missing)'}' "
                        f"got '{headers[i] if i < len(headers) else '(missing)'}'"
                        for i in range(max(len(headers), len(reference_headers)))
                        if i >= len(headers) or i >= len(reference_headers) or headers[i] != reference_headers[i]
                    ]
                    result.skipped_files.append(
                        f"{file.name}: header mismatch — {'; '.join(mismatches[:3])}"
                    )
                    continue

            file_data.append((file, headers, data_rows))
            result.source_files.append(file.name)

        except Exception as e:
            result.skipped_files.append(f"{file.name}: error reading — {e}")
            logger.warning(f"Skipped {file.name}: {e}")

    if not file_data:
        result.errors.append("No valid files could be read — check file formats and folder path")
        return result

    # --- Pass 2: write merged output ---
    try:
        out_wb = Workbook()
        out_ws = out_wb.active
        out_ws.title = 'Consolidated'

        # Write header row
        header_out = reference_headers.copy()
        if add_source_column:
            header_out.append('Source File')
        out_ws.append(header_out)

        # Style header row
        from openpyxl.styles import Font, PatternFill, Alignment
        header_fill = PatternFill(start_color='2A49DF', end_color='2A49DF', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        for cell in out_ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        # Write data rows
        for file_path, _, data_rows in file_data:
            for row in data_rows:
                row_out = row.copy()
                if add_source_column:
                    row_out.append(file_path.name)
                out_ws.append(row_out)
                result.merged_rows += 1

        # Auto-fit column widths (approximate)
        for col in out_ws.columns:
            max_len = max(
                (len(str(cell.value)) if cell.value else 0 for cell in col),
                default=10
            )
            out_ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

        # Add summary sheet
        summary_ws = out_wb.create_sheet('Summary')
        summary_ws.append(['Consolidation Summary'])
        summary_ws.append(['Total rows merged', result.merged_rows])
        summary_ws.append(['Source files', len(result.source_files)])
        summary_ws.append(['Skipped files', len(result.skipped_files)])
        summary_ws.append([])
        summary_ws.append(['Source Files Included:'])
        for f in result.source_files:
            summary_ws.append([f])
        if result.skipped_files:
            summary_ws.append([])
            summary_ws.append(['Skipped Files:'])
            for f in result.skipped_files:
                summary_ws.append([f])

        # Ensure output directory exists
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_wb.save(out_path)

        result.output_path = str(out_path)
        result.success = True
        logger.info(
            f"Consolidation complete: {result.merged_rows} rows from "
            f"{len(result.source_files)} files → {output_path}"
        )

    except Exception as e:
        result.errors.append(f"Failed to write output: {e}")
        logger.error(f"Consolidation write failed: {e}")

    return result
```

After writing, add openpyxl to requirements.txt if not present.

Write a quick test (no server needed):
```python
# test_consolidation.py
from app.services.consolidation_service import consolidate_responses
import tempfile, os
from pathlib import Path
import openpyxl

# Create two test Excel files with same columns
tmp = Path(tempfile.mkdtemp())
for i, name in enumerate(['alice.xlsx', 'bob.xlsx']):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Name', 'Value', 'Date'])
    ws.append([f'Person {i}', i * 10, '2024-01-01'])
    wb.save(tmp / name)

result = consolidate_responses(
    input_folder=str(tmp),
    output_path=str(tmp / 'merged.xlsx'),
)
print('Success:', result.success)
print('Rows merged:', result.merged_rows)
print('Source files:', result.source_files)
print('Output:', result.output_path)
```
Expected: success=True, merged_rows=2, two source files listed.


# ============================================================
# BA2 — Response Consolidation: router + task type integration
# ============================================================

Step 1 — Add consolidation fields to the task models.
Open app/models/task.py (from B2).
Add a new optional config class for consolidation settings:

```python
class ConsolidationConfig(BaseModel):
    """
    Attached to EmailTracking tasks when the user wants to
    consolidate response attachments after tracking.
    """
    enabled: bool = False
    input_folder: str = ''        # folder where attachments land
    output_path: str = ''         # path for merged output file
    file_pattern: str = '*.xlsx'  # glob pattern for response files
    sheet_name: Optional[str] = None
    add_source_column: bool = True
```

In EmailTrackingConfig, add an optional field:
```python
consolidation: Optional[ConsolidationConfig] = None
```

Step 2 — Add consolidation execution to the task executor.
Open app/tasks/executor.py.
In the _call_tracking method, after the tracking worker runs
successfully, check if consolidation is enabled and run it:

```python
def _call_tracking(self, args: dict, is_shared: bool):
    if is_shared:
        from shared_routes.track_mail import main as run_tracking
    else:
        from personal_routes.track_mail import main as run_tracking
    run_tracking(args)

    # After tracking, run consolidation if configured
    config = self.task.get('config', {})
    consolidation = config.get('consolidation', {})
    if consolidation and consolidation.get('enabled'):
        self._log('INFO', 'Consolidation enabled — merging response files')
        from app.services.consolidation_service import consolidate_responses
        result = consolidate_responses(
            input_folder=consolidation.get('input_folder', ''),
            output_path=consolidation.get('output_path', ''),
            file_pattern=consolidation.get('file_pattern', '*.xlsx'),
            sheet_name=consolidation.get('sheet_name'),
            add_source_column=consolidation.get('add_source_column', True),
        )
        if result.success:
            self._log('INFO',
                f"Consolidated {result.merged_rows} rows from "
                f"{len(result.source_files)} files → {result.output_path}"
            )
        else:
            self._log('WARNING',
                f"Consolidation finished with issues: {'; '.join(result.errors)}"
            )
        for skipped in result.skipped_files:
            self._log('WARNING', f"Skipped: {skipped}")
```

Step 3 — Add a standalone consolidation API endpoint.
Open app/routers/tasks.py and add:

```python
from app.services.consolidation_service import consolidate_responses
from pydantic import BaseModel as PydanticBase

class ConsolidationRequest(PydanticBase):
    input_folder: str
    output_path: str
    file_pattern: str = '*.xlsx'
    sheet_name: str = ''
    add_source_column: bool = True

@router.post('/{task_id}/consolidate')
def run_consolidation(task_id: str, body: ConsolidationRequest):
    """
    Manually trigger consolidation for a specific tracking task.
    Returns the result immediately (synchronous — not a background job).
    """
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    if task.get('task_type') not in ('email_tracking',):
        raise HTTPException(
            status_code=400,
            detail='Consolidation only applies to Email Tracking tasks'
        )

    result = consolidate_responses(
        input_folder=body.input_folder,
        output_path=body.output_path,
        file_pattern=body.file_pattern,
        sheet_name=body.sheet_name or None,
        add_source_column=body.add_source_column,
    )

    return {
        'success':      result.success,
        'merged_rows':  result.merged_rows,
        'source_files': result.source_files,
        'skipped_files':result.skipped_files,
        'output_path':  result.output_path,
        'errors':       result.errors,
    }
```

Test with curl after server is running:
  curl -X POST http://localhost:8000/api/tasks/{id}/consolidate \
    -H "Content-Type: application/json" \
    -d '{"input_folder":"C:\\Responses","output_path":"C:\\Output\\merged.xlsx"}'


# ============================================================
# BB1 — Calendar Event Creation: service layer
# ============================================================

Create app/services/calendar_service.py

Context: The user has a list of email addresses and wants
to book Outlook calendar events — either one single event
for all attendees, or separate events with individual
time/date for each attendee — all in a single task.

The corporate Graph API proxy is used:
  https://o365-graph-proxy-ms6.gaiacloud.jpmchase.net

Graph API endpoint for creating calendar events:
  Personal:  POST /me/events
  Shared:    POST /users/{mailbox}/events

```python
"""
Calendar Service — creates Outlook calendar events via the
corporate Graph API proxy.

Two modes:
  single:   one event with all attendees invited
  separate: one event per attendee with individual time/date
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

logger = logging.getLogger(__name__)
GRAPH_PROXY_BASE = 'https://o365-graph-proxy-ms6.gaiacloud.jpmchase.net'


def _get_headers() -> dict:
    """Reuse fetch_token.py from existing src/helpers/"""
    from helpers.fetch_token import fetch_token   # adjust if function name differs
    token = fetch_token()
    if isinstance(token, dict):
        return token
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


def _build_event_body(
    subject: str,
    body_content: str,
    start_dt: str,       # ISO format: 2024-11-15T09:00:00
    end_dt: str,         # ISO format: 2024-11-15T10:00:00
    timezone: str,       # e.g. "GMT Standard Time"
    attendees: list[str],
    location: str = '',
    is_online: bool = False,
    reminder_minutes: int = 15,
) -> dict:
    """Build the Graph API event request body."""
    attendee_list = [
        {
            'emailAddress': {'address': email.strip(), 'name': email.strip()},
            'type': 'required'
        }
        for email in attendees if email.strip()
    ]

    event = {
        'subject': subject,
        'body': {
            'contentType': 'HTML',
            'content': body_content or subject,
        },
        'start': {
            'dateTime': start_dt,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_dt,
            'timeZone': timezone,
        },
        'attendees': attendee_list,
        'reminderMinutesBeforeStart': reminder_minutes,
        'isReminderOn': True,
    }

    if location:
        event['location'] = {'displayName': location}

    if is_online:
        event['isOnlineMeeting'] = True
        event['onlineMeetingProvider'] = 'teamsForBusiness'

    return event


def _post_event(
    event_body: dict,
    is_shared: bool,
    mailbox: str,
) -> dict:
    """POST a single event to Graph API. Returns the created event."""
    headers = _get_headers()

    if is_shared:
        url = f'{GRAPH_PROXY_BASE}/users/{mailbox}/events'
    else:
        url = f'{GRAPH_PROXY_BASE}/me/events'

    response = httpx.post(
        url,
        headers=headers,
        json=event_body,
        timeout=15.0,
        verify=False,
    )
    response.raise_for_status()
    return response.json()


class EventResult:
    def __init__(self, attendee: str):
        self.attendee = attendee
        self.success = False
        self.event_id = ''
        self.event_url = ''
        self.error = ''


def create_single_event(
    subject: str,
    body_content: str,
    start_dt: str,
    end_dt: str,
    timezone: str,
    attendees: list[str],
    location: str = '',
    is_online: bool = False,
    reminder_minutes: int = 15,
    is_shared: bool = False,
    mailbox: str = '',
) -> list[EventResult]:
    """
    Create ONE event with ALL attendees invited.
    Returns a list with a single EventResult covering all attendees.
    """
    result = EventResult('all')
    try:
        event_body = _build_event_body(
            subject, body_content, start_dt, end_dt,
            timezone, attendees, location, is_online, reminder_minutes,
        )
        created = _post_event(event_body, is_shared, mailbox)
        result.success = True
        result.event_id = created.get('id', '')
        result.event_url = created.get('webLink', '')
        logger.info(
            f"Single event created: '{subject}' "
            f"for {len(attendees)} attendees — id={result.event_id}"
        )
    except Exception as e:
        result.error = str(e)
        logger.error(f"Failed to create single event: {e}")
    return [result]


def create_separate_events(
    subject: str,
    body_content: str,
    timezone: str,
    attendee_schedule: list[dict],
    # Each dict: {email, start_dt, end_dt, location (opt)}
    location: str = '',
    is_online: bool = False,
    reminder_minutes: int = 15,
    is_shared: bool = False,
    mailbox: str = '',
) -> list[EventResult]:
    """
    Create ONE event PER ATTENDEE with individual time/date.
    attendee_schedule: list of {email, start_dt, end_dt, location}
    Returns a list of EventResult, one per attendee.
    """
    results = []
    for entry in attendee_schedule:
        email = entry.get('email', '').strip()
        if not email:
            continue
        result = EventResult(email)
        try:
            event_body = _build_event_body(
                subject=subject,
                body_content=body_content,
                start_dt=entry.get('start_dt', ''),
                end_dt=entry.get('end_dt', ''),
                timezone=timezone,
                attendees=[email],
                location=entry.get('location', location),
                is_online=is_online,
                reminder_minutes=reminder_minutes,
            )
            created = _post_event(event_body, is_shared, mailbox)
            result.success = True
            result.event_id = created.get('id', '')
            result.event_url = created.get('webLink', '')
            logger.info(
                f"Separate event created for {email}: "
                f"'{subject}' at {entry.get('start_dt')} — id={result.event_id}"
            )
        except Exception as e:
            result.error = str(e)
            logger.error(f"Failed to create event for {email}: {e}")
        results.append(result)

    return results
```


# ============================================================
# BB2 — Calendar Event Creation: task type + router
# ============================================================

Step 1 — Add Calendar as a task type.
Open app/models/task.py.
Add 'calendar' to the TaskType enum:
```python
class TaskType(str, Enum):
    draft_send     = 'draft_send'
    reminder       = 'reminder'
    email_tracking = 'email_tracking'
    download       = 'download'
    calendar       = 'calendar'       # NEW
```

Add a CalendarConfig model:
```python
class AttendeeSchedule(BaseModel):
    email: str
    start_dt: str   # ISO: 2024-11-15T09:00:00
    end_dt: str     # ISO: 2024-11-15T10:00:00
    location: str = ''

class CalendarConfig(BaseModel):
    event_mode: str = 'single'          # 'single' or 'separate'
    subject: str
    body_content: str = ''
    timezone: str = 'GMT Standard Time'
    location: str = ''
    is_online: bool = False
    reminder_minutes: int = 15

    # For single mode: one time for all
    start_dt: str = ''
    end_dt: str = ''
    attendees: list[str] = []           # plain email list

    # For separate mode: one schedule per attendee
    attendee_schedule: list[AttendeeSchedule] = []
```

Step 2 — Add calendar execution to the task executor.
Open app/tasks/executor.py.
In _dispatch(), add:
```python
elif task_type == 'calendar':
    self._run_with_capture(self._call_calendar, worker_args, is_shared)
```

Add the _call_calendar method:
```python
def _call_calendar(self, args: dict, is_shared: bool):
    """
    Create Outlook calendar events via Graph API.
    Does not call src/workers/ — uses calendar_service directly.
    """
    from app.services.calendar_service import (
        create_single_event,
        create_separate_events,
    )
    config = self.task.get('config', {})
    mode = config.get('event_mode', 'single')
    mailbox = self.task.get('mailbox', '')

    if mode == 'single':
        results = create_single_event(
            subject=config.get('subject', ''),
            body_content=config.get('body_content', ''),
            start_dt=config.get('start_dt', ''),
            end_dt=config.get('end_dt', ''),
            timezone=config.get('timezone', 'GMT Standard Time'),
            attendees=config.get('attendees', []),
            location=config.get('location', ''),
            is_online=config.get('is_online', False),
            reminder_minutes=config.get('reminder_minutes', 15),
            is_shared=is_shared,
            mailbox=mailbox,
        )
    else:
        results = create_separate_events(
            subject=config.get('subject', ''),
            body_content=config.get('body_content', ''),
            timezone=config.get('timezone', 'GMT Standard Time'),
            attendee_schedule=[
                s if isinstance(s, dict) else s.dict()
                for s in config.get('attendee_schedule', [])
            ],
            location=config.get('location', ''),
            is_online=config.get('is_online', False),
            reminder_minutes=config.get('reminder_minutes', 15),
            is_shared=is_shared,
            mailbox=mailbox,
        )

    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    self._log('INFO', f"Calendar: {successful} events created, {failed} failed")
    for r in results:
        if r.success:
            self._log('INFO', f"  ✓ {r.attendee} — event id: {r.event_id}")
        else:
            self._log('ERROR', f"  ✗ {r.attendee} — {r.error}")
```

Step 3 — Add a calendar preview/validate endpoint.
Open app/routers/tasks.py and add:

```python
from app.models.task import CalendarConfig

@router.post('/calendar/preview')
def preview_calendar_events(config: CalendarConfig):
    """
    Validate and preview what events will be created
    without actually posting to the Graph API.
    Returns a list of event summaries for the user to review.
    """
    if config.event_mode == 'single':
        attendees = config.attendees
        events = [{
            'mode': 'single',
            'subject': config.subject,
            'attendees': attendees,
            'attendee_count': len(attendees),
            'start_dt': config.start_dt,
            'end_dt': config.end_dt,
            'location': config.location,
            'is_online': config.is_online,
        }]
    else:
        events = [
            {
                'mode': 'separate',
                'subject': config.subject,
                'attendee': s.email,
                'start_dt': s.start_dt,
                'end_dt': s.end_dt,
                'location': s.location or config.location,
                'is_online': config.is_online,
            }
            for s in config.attendee_schedule
        ]

    return {
        'event_count': len(events),
        'mode': config.event_mode,
        'events': events,
    }
```


# ============================================================
# BC1 — Multi-job Run: bulk run endpoint
# ============================================================

Open app/routers/tasks.py.
Add a bulk-run endpoint that accepts multiple task IDs and
triggers them all, returning individual run IDs for each.

```python
from pydantic import BaseModel as PydanticBase
from typing import List

class BulkRunRequest(PydanticBase):
    task_ids: List[str]
    run_mode: str = 'parallel'   # 'parallel' or 'sequential'

class BulkRunResult(PydanticBase):
    task_id: str
    task_name: str
    status: str          # 'triggered' or 'error'
    run_id: str = ''
    error: str = ''

@router.post('/bulk-run')
def bulk_run_tasks(body: BulkRunRequest):
    """
    Trigger multiple tasks at once.

    run_mode:
      'parallel':   all tasks start simultaneously in separate threads
      'sequential': tasks run one after another in a single thread

    Returns immediately with a list of run IDs.
    The actual execution happens in the background.
    """
    if not body.task_ids:
        raise HTTPException(status_code=400, detail='No task IDs provided')
    if len(body.task_ids) > 20:
        raise HTTPException(
            status_code=400,
            detail='Maximum 20 tasks per bulk run'
        )

    from app.tasks.scheduler import trigger_now
    results = []

    for task_id in body.task_ids:
        task = get_task_by_id(task_id)
        if not task:
            results.append(BulkRunResult(
                task_id=task_id,
                task_name='Unknown',
                status='error',
                error='Task not found',
            ))
            continue

        if not task.get('enabled', True):
            results.append(BulkRunResult(
                task_id=task_id,
                task_name=task.get('process_name', ''),
                status='error',
                error='Task is disabled',
            ))
            continue

        try:
            if body.run_mode == 'sequential':
                # Run synchronously in this thread (blocks until each completes)
                from app.tasks.executor import TaskExecutor
                executor = TaskExecutor(task)
                result = executor.run()
                results.append(BulkRunResult(
                    task_id=task_id,
                    task_name=task.get('process_name', ''),
                    status='completed',
                    run_id=result['run_id'],
                ))
            else:
                # Parallel: fire and forget in a background thread
                provisional_run_id = trigger_now(task)
                results.append(BulkRunResult(
                    task_id=task_id,
                    task_name=task.get('process_name', ''),
                    status='triggered',
                    run_id=provisional_run_id,
                ))
        except Exception as e:
            results.append(BulkRunResult(
                task_id=task_id,
                task_name=task.get('process_name', ''),
                status='error',
                error=str(e),
            ))

    triggered = sum(1 for r in results if r.status in ('triggered', 'completed'))
    failed = sum(1 for r in results if r.status == 'error')

    return {
        'run_mode':  body.run_mode,
        'total':     len(body.task_ids),
        'triggered': triggered,
        'failed':    failed,
        'results':   [r.dict() for r in results],
    }
```

Test with curl:
  curl -X POST http://localhost:8000/api/tasks/bulk-run \
    -H "Content-Type: application/json" \
    -d '{"task_ids": ["task-id-1", "task-id-2"], "run_mode": "parallel"}'

Expected response:
  {
    "run_mode": "parallel",
    "total": 2,
    "triggered": 2,
    "failed": 0,
    "results": [...]
  }
