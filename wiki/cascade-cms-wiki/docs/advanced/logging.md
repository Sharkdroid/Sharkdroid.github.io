# Logging & Debugging

Operation logger owns all console, logfile, and (verbose mode) request/response file output for the cascade_cms library. Two output modes exist: normal mode for everyday use and debug mode for diagnosing failures, controlled solely by whether `debug_config` is `None`. Both produce logfiles; debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode produces minimal console output and a simple logfile. It logs lifecycle markers such as `[INIT]`, `[RUNNING]`, `[DONE]`, and `[EXIT]`, along with batch tallies and operation progress lines. The normal logfile is named `{SERVER}_{timestamp}.log` and records one line per chain.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: myscript.py
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeWrapperBase("myserver.com", debug_config={
    "log_dir": "./logs",
    "show_network_headers": True
})
```

---

## Debug Configuration Options

Recognized `debug_config` keys control the log directory and network header visibility.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile uses the naming convention `{SERVER}_debug_{timestamp}.log`. It features a quiet console, a verbose logfile, and per-request JSON files. There is no longer a separate "log operations vs. callbacks vs. responses" toggle — `_is_debug` is the single on/off switch for verbose behavior.

### Sample Debug Log

```text
>>>> START REQUEST <<+
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
[GET] https://myserver.com/api/v1/read/site/path
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error lines in debug mode utilize a `v` marker followed by an `!ERROR:` block indicating the failure at the specified step index. Chain-level failures go through `flush_chain_error` which has step-index context. `log_cascade_error` provides a thin wrapper to log a `CascadeError` (API-level failure) outside of chain context, while `log_python_error` logs an unhandled Python exception with traceback, file name, and line number.

<!-- synthesized-for: 3.1.1 -->
