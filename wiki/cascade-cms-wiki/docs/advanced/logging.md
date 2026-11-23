# Logging & Debugging

Cascade CMS REST provides two distinct output modes: a normal mode that records lifecycle markers and chain outcomes, and a debug mode that captures detailed requests, responses, and network payloads. The active mode is determined by the `debug` configuration dictionary passed when instantiating a `Cascade` session. Both modes write output to a structured log file in the configured logging directory.

---

## Normal Mode Output

In normal mode, the library writes lifecycle markers, per-chain execution lines, and batch tallies to both the console and the log file. Each session names its log file based on the configured environment and stores it in the designated `log_dir`.

### Normal Logfile Format

```text
[INIT] cascade_url=... script_name=...
[BATCH-START]
e868f539ac1001062cfa029c4c5df4d0 folder: read
[BATCH-END] succeeded=1 total=1 has_reportable_failure=false
[EXIT-CODE]: success
```

---

## Enabling Debug Mode

To turn debug mode on, pass a `debug_config` dictionary containing your debug settings to the `Cascade` constructor along with your environment variables. 

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

When debug mode is active, the logger captures granular request and response data, request payloads, and detailed error context according to the configuration keys provided.

---

## Debug Configuration Options

| Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `log_dir` | `str \| os.PathLike` | None | Directory where log files and per-request JSON files are stored. (Can also be set via the `log_dir` constructor parameter on `Cascade`, which takes precedence.) |
| `log_operations` | `bool` | — | Controls whether operations are logged in detail. |
| `log_callbacks` | `bool` | — | Controls whether callback executions are logged. |
| `log_responses` | `bool` | — | Controls whether responses are captured in the log. |
| `show_payload_data` | `bool` | — | Controls whether request payloads are displayed in output. |
| `show_network_headers` | `bool` | — | Controls whether network headers are included in the log output (requires verbose mode). |
| `show_error_variables` | `bool` | — | Controls whether error variables are surfaced during failures. |
| `show_response_line_limit` / `response_line_limit` | `int` | `8` | Limits response lines printed in logs (`-1` dumps the full response body). |

---

## Debug Logfile Format

The debug logfile captures detailed method invocations and URLs via `[METHOD] URL` entries, alongside per-request files written directly to the logs folder (such as `{uuid}_request.json` and `{uuid}_response.json` when verbose mode is enabled). Trivial successes or failures are skipped to avoid redundant file clutter.

### Sample Debug Log

```text
[INIT] cascade_url=... script_name=...
[BATCH-START]
[METHOD] GET /api/v1/read/folder/e868f539ac1001062cfa029c4c5df4d0
e868f539ac1001062cfa029c4c5df4d0 folder: read
[BATCH-END] succeeded=1 total=1 has_reportable_failure=false
[EXIT-CODE]: success
```

---

## Interpreting Errors in Debug Mode

When a chain fails, the log records the pipeline line followed by an alignment block indicating the failing step index, message, file, and line number. Failures are categorized using the `FailureCategory` enumeration: `CASCADE` (when the API rejects a request with a `CascadeError`), `NETWORK` (for network-layer exceptions), `LIBRARY` (for request building, parsing, or gather exceptions), and `CALLBACK` (for exceptions raised inside user-supplied callback code). For `NETWORK` and `LIBRARY` failures, the `!ERROR:` message is explicitly prefixed with `[NETWORK]` or `[CASCADE-REST-CMS]`, whereas `CASCADE` and `CALLBACK` errors do not carry this prefix. Check the failing step's category and accompanying error variables first when diagnosing issues.

<!-- synthesized-for: 3.10.1 -->
