# Logging & Diagnosis

cascade_cms features two distinct output modes: a normal mode for everyday operation, and a debug mode for diagnosing network or parsing failures. Both produce timestamped logfiles under the hood, but debug mode switches on a verbose pipeline log alongside a quieter console output.

---

## Normal Mode Output

In normal mode (`debug_config=None`), output is split between a minimal console feed showing lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`) and summary tallies, and a clean logfile. The logfile records one line per executed chain using the format `(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...`.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: my_migration_script.py
(uuid:12345, page) read -> edit -> release
3/4 succeeded
[DONE]: 4 assets processed in 1.2s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

Debug mode is activated by passing a `debug_config` dictionary (even an empty one) to the library, which switches `_is_debug` on.

```python
cascade = CascadeWrapperBase(
    server="myserver.com",
    api_key="123456",
    debug_config={"log_dir": "./logs"}
)
```

---

## Debug Configuration Options

The `debug_config` dictionary accepts specific keys to control verbose output behavior, with default values falling back if omitted.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

When debug mode is active, `OperationLogger` names the logfile following the pattern `{SERVER}_debug_{timestamp}.log`. It outputs quieter console information while writing comprehensive pipeline segments, individual network request URLs via `[METHOD] URL`, and separate request/response JSON payload files into the log directory.

### Sample Debug Log

```text
>>>> START REQUEST <<<
(uuid:12345, page) read -> edit -> release
[GET] https://myserver.com/api/v1/read/page/uuid:12345
[POST] https://myservers.com/api/v1/edit/page/uuid:12345 | payload: uuid:12345_request.json
3/4 succeeded
>>>> END REQUEST <<<<<
```

---

## Interpreting Errors in Debug Mode

When a chain fails, `OperationLogger` captures the failure at the exact `failing_step_index`, rendering a `v` alignment marker directly under the failing segment's column, followed by an `!ERROR:` block containing the multi-line message and source file location (`@{file}:{line}`). Standalone exceptions outside of a chain context are routed through `log_cascade_error` or `log_python_error`, logging the exception type, message, and local file/line number without an enclosing pipeline line.

<!-- synthesized-for: 3.1.3 -->
