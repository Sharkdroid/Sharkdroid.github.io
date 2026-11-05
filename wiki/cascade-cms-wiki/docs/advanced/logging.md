# Logging & Design

The `cascade_cms` library provides two distinct logging and execution modes: normal mode for everyday use and debug mode for diagnosing failures. Both produce detailed logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode outputs minimal console messages and a simple logfile. It handles initialization, progress reporting, and cleanup while writing one concise line per completed chain to the logfile.

### Normal Logfile Format

```text
[INIT]: Connecting to example.com
[LOG]: logs/example.com_2023-10-27T12-00-00-000000_1.log
[RUNNING]: my_script.py
3/3 succeeded
[DONE]: 3 assets processed in 0.5s
0 failed, 3 succeeded
[EXIT]: Disconnecting from example.com
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True,
}
wrapper = CascadeWrapperBase(server="example.com", debug_config=debug_config)
```

---

## Debug Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str / PathLike | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile is named using the pattern `{SERVER}_debug_{timestamp}_{serial}.log`. It contains a quiet console output, a verbose logfile, and per-request JSON files when `debug_config` is provided.

### Sample Debug Log

```text
>>>> START REQUEST <<^
(mySite/blog/post-1, page) READ -> read
[GET] https://example.com/api/v1/read/page/mySite/blog/post-1
3/3 succeeded
>>>> END REQUEST <<^
```

---

## Interpreting Errors in Debug Mode

When a failure occurs, `OperationLogger` records a `v` marker pointing directly to the column of the failing step, followed by an `!ERROR:` block that includes the error message and the source file and line number (`@{file}:{line}`). For network or library failures, category prefixes such as `[NETWORK]` or `[CASCADE-REST-CMS]` are prepended to the message.

<!-- synthesized-for: 3.9.2 -->
