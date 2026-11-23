# Logging & Debugging

The library operates in two distinct output modes: normal mode and debug mode. The active mode is determined by the presence and contents of the `debug` dictionary passed to the session. Both modes record a persistent record of the session's execution in a logfile.

---

## Normal Mode Output

In normal mode, the library prints lifecycle markers, a summary line for each executed operation chain, and a batch tally once requests are submitted. These details are written to a logfile located in the configured log directory (defaulting to the path specified in the debug configuration or context manager).

### Normal Logfile Format

```text
[INIT] ...
[BATCH-START]
[RESULT]: ...
v
!ERROR: ...
[BATCH-END]
[EXIT-CODE]: success
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "log_operations": True,
    "log_callbacks": True,
    "log_responses": True,
    "show_payload_data": True,
    "show_network_headers": False,
    "show_error_variables": True,
    "response_line_limit": 8,
}

with Cascade(environment_variables, debug=debug_config) as cascade:
    ...
```

Enabling debug mode activates verbose request tracking, writes individual request and response files for operations, and includes payload data in the logs according to the active configuration flags.

---

## Debug Configuration Options

| Key | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `log_dir` | str / os.PathLike | None | The directory where log files and request/response payloads are written. |
| `log_operations` | bool | - | Toggles logging of operation steps. |
| `log_callbacks` | bool | - | Toggles logging of user callbacks. |
| `log_responses` | bool | - | Toggles logging of response bodies. |
| `show_payload_data` | bool | - | Controls whether payload data is included in the log output. |
| `show_network_headers` | bool | - | Controls whether network request and response headers are logged. |
| `show_error_variables` | bool | - | Controls whether error variables are exposed in error logs. |
| `response_line_limit` | int | - | Maximum lines of response body to log (-1 dumps the full response). |

---

## Debug Logfile Format

The debug logfile captures the full pipeline progression of each chain along with detailed method calls, request URLs, and network headers when enabled. Additionally, verbose mode writes `{uuid}_request.json` and `{uuid}_response.json` files to the logs folder for non-trivial operations.

### Sample Debug Log

```text
[METHOD] GET ...
[RESULT]: Read asset e868f539ac1001062cfa029c4c5df4d0
```

---

## Interpreting Errors in Debug Mode

When a chain fails, the log records the exact step that encountered the issue accompanied by its failure category: `CASCADE` (when the API rejects a request with a `CascadeError`), `NETWORK` (for network-layer exceptions), `LIBRARY` (for internal parsing, request building, or gathering exceptions), or `CALLBACK` (for exceptions raised by user callback code). Examine the step index, the accompanying message, and the associated error details to trace the root cause.

<!-- synthesized-for: 3.10.1 -->
