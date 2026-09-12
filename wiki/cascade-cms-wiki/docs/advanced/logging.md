# Logging & Debugging

Operation logger owns all console, logfile, and (verbose mode) request/response file output for the cascade_cms library. Two output modes exist: a normal mode for everyday use and a debug mode for diagnosing failures. Both produce logfiles, while debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Operation logger owns all console and logfile output for the cascade_cms library. Normal (debug_config=None) features minimal console and simple logfile output, writing one line per chain via `flush_chain` and `flush_chain_error`.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: my_script.py
([INIT]: Connecting to myserver.com)
v
!ERROR: CascadeError — check log
1/1 succeeded
[DONE]: 1 assets processed in 0.1s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True,
}
```

---

## Debug Configuration Options

Debug (debug_config=dict) features a quiet console, verbose logfile plus the per-request JSON files. Recognized `debug_config` keys are detailed below:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile is named following the pattern `{self._server}_debug_{timestamp}.log` and captures the complete execution flow, request/response details, and per-request JSON files when enabled.

### Sample Debug Log

```text
>>>> START REQUEST <<++
([uuid_or_path, asset_type]) OP1 -> fn_name: Type -> ...
[GET] https://myserver.com/api/v1/...
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error blocks appear in debug mode using a `v` alignment marker pointing to the failing step index followed by an `!ERROR:` block that includes the message, file, and line number `@{file}:{line}`. `CascadeError` covers API-level failures outside or inside chain context, while Python errors capture the exception type, message, and extracted traceback frame info.

<!-- synthesized-for: 3.1.5 -->
