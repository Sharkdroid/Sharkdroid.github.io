# Logging & Data & Debugging

Two output modes exist within `cascade_cms` for monitoring operations: normal mode for everyday use, and debug mode for diagnosing failures. Both produce logfiles; debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Owns all console, logfile, and (verbose mode) request/response file output for the cascade_cms library. Normal mode (`debug_config=None`) provides a minimal console and a simple logfile, logging session lifecycle events, per-operation progress, and one line per chain.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver
[LOG]: logs/myserver_20231024T120000_1.log
(mySite/blog/post-1, page) read -> read_metadata -> get_asset
[RESULT]: Success
(mySite/blog/missing, page) read -> get_asset
v
!ERROR: CascadeError — asset not found @ operations.py:42
[DONE]: 1 assets processed in 0.5s
1 failed, 0 succeeded
[EXIT]: Disconnecting from myserver
```

---

## Enabling Debug Mode

```python
wrapper = CascadeClient(
    server="myserver",
    username="user",
    password="password",
    debug_config={
        "log_dir": "./logs",
        "show_network_headers": True,
    }
)
```

---

## Debug Configuration Options

Recognized `debug_config` keys:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `log_dir` | `str` | `"./logs"` | Directory for the logfile and (verbose mode) request/response JSON files. |
| `show_network_headers` | `bool` | `False` | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The logfile is named using the format `{server}_debug_{timestamp}_{serial}.log` (or without the `debug` suffix in normal mode), stored inside the configured `log_dir`. It owns all console, logfile, and verbose request/response file output, recording the sequence of steps per chain as built incrementally via `ChainLineBuilder`.

### Sample Debug Log

```text
>>>> START REQUEST <<
(mySite/blog/post-1, page) read -> read_metadata -> get_asset
[GET] https://myserver.example.com/api/v1/read/page/mySite/blog/post-1
[request-headers]:
  authorization: Bearer mask_token(...)
[response-headers]:
  content-type: application/json
1/1 succeeded
>>>> END REQUEST <<
```

---

## Interpreting Errors in Debug Mode

Error blocks in debug mode are flushed via `flush_chain_error` or handled via standalone functions like `log_cascade_error` and `log_python_error`. A failure displays a `v` marker pointing directly to an `!ERROR:` block that aligns under the failing step's column, along with the source file and line number (`@{file}:{line}`). For network or library failures, error categories prepend `[NETWORK]/[CASCADE-REST-CMS]` to the message, while callback-only failures omit this prefix.

<!-- synthesized-for: 3.9.2 -->
