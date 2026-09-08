# Logging & Drying

The cascade_cms library provides two output modes: normal mode for everyday use and debug mode for diagnosing failures. Both produce logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode uses a minimal console and a simple logfile to record session lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a logfile named `{server}_{timestamp}.log` containing one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver
[RUNNING]: myscript
(mySite/blog/post-1, page) READ -> EDIT -> PUBLISH
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True,
}
wrapper = CascadeWrapperBase(server="myserver", debug_config=debug_config)
```

---

## Debug Configuration Options

Recognized `debug_config` keys include:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `log_dir` | `str` | `"./logs"` | Directory for the logfile and (verbose mode) request/response JSON files. |
| `show_network_headers` | `bool` | `False` | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile is named `{server}_debug_{timestamp}.log` and contains a quiet console output, a verbose logfile, and per-request JSON files stored in the designated log directory.

### Sample Debug Log

```text
>>>> START REQUEST <<<
(mySite/blog/post-1, page) READ -> EDIT -> PUBLISH
1/1 succeeded
>>>> END REQUEST <<<<<
```

---

## Interpreting Errors in Debug Mode

When a chain fails, `OperationLogger` records the finished pipeline text followed by an alignment block containing the `v` marker and `!ERROR:` message with file and line locations. Non-chain API-level failures use `log_cascade_error`, while unexpected Python exceptions outside of chain context are captured via `log_python_error` with traceback file and line numbers.

<!-- synthesized-for: 3.1.3 -->
