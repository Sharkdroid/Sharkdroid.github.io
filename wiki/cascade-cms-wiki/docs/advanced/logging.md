# Logging & Data & Debugging

The `cascade_cms` library provides two output modes: normal mode for everyday use, and debug mode for diagnosing failures. Both produce logfiles; debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode provides minimal console output and a simple logfile. It records lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and writes a logfile containing one line per chain.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: my_script.py
(mySite/blog/post-1, page) read -> edit -> publish
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True,
}
wrapper = CascadeWrapperBase("myserver.com", debug_config=debug_config)
```

---

## Debug Configuration Options

Recognized `debug_config` keys:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

Debug mode uses a quiet console, a verbose logfile plus the per-request JSON files, and is controlled solely by whether `debug_config` is `None`. The file is named according to `{server}_debug_{timestamp}.log`.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
[GET] https://myserver.com/api/v1/read/page/mySite/blog/post-1
(mySite/blog/post-1, page) read -> edit -> publish
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

When a chain fails, `OperationLogger.flush_chain_error` writes the pipeline text via `render_complete()`, followed by the alignment `v` marker and `!ERROR:` block. Outside of chain context, `log_cascade_error` handles API-level `CascadeError` failures and `log_python_error` handles Python exceptions by extracting tracebacks and formatting the exception type, message, file name, and line number.

<!-- synthesized-for: 3.1.3 -->
