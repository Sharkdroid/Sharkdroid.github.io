# Logging & Debugging

The cascade_cms library provides two output modes: normal mode for everyday use and debug mode for diagnosing failures. Both produce logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode uses a minimal console and a simple logfile, logging lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a normal logfile named with the server and timestamp containing one line per completed operation.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver
[RUNNING]: myscript.py
(mySite/blog/post-1, page) read -> read_asset
(mySite/blog/post-2, page) read -> read_asset
1/2 succeeded
[DONE]: 2 assets processed in 0.5s
[EXIT]: Disconnecting from myserver
```

---

## Enabling Debug Mode

```python
wrapper = CascadeWrapperBase(
    server="myserver",
    debug_config={
        "log_dir": "./logs",
        "show_network_headers": True
    }
)
```

---

## Debug Configuration Options

Recognized `debug_config` keys: `log_dir` controls the directory for the logfile and verbose mode request/response JSON files (default `./logs`), and `show_network_headers` logs request and response HTTP headers in verbose mode.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `log_dir` | str | `"./logs"` | Directory for the logfile and request/response JSON files. |
| `show_network_headers` | bool | `False` | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile follows the naming convention `{SERVER}_debug_{timestamp}.log` and contains quiet console output alongside a verbose logfile plus per-request JSON files.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(mySite/blog/post-1, page) read -> read_asset
[GET] https://myserver/api/v1/read/page/mySite/blog/post-1
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error blocks appear in debug mode with a `v` alignment marker pointing directly to the character column where the error occurred, followed by an `!ERROR:` block indicating the failure message and file/line reference. Chain-level failures go through `flush_chain_error` with step-index context, while standalone API-level failures are logged via `log_cascade_error` or Python exceptions via `log_python_error`.

<!-- synthesized-for: 3.1.6 -->
