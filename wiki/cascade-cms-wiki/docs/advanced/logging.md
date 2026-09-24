# Logging & Debugging

The `cascade_cms` library provides two distinct output modes: a normal mode for everyday use and a debug mode for diagnosing failures. Both modes produce logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode provides minimal console output and a simple logfile. It outputs lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a normal logfile named `{SERVER}_{timestamp}.log` with one line per operation.

### Normal LogfileFormat

```text
[INIT]: Connecting to myserver.example.com
[RUNNING]: myscript.py
(mySite/blog/post-1, page) read -> edit -> publish
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
0 failed, 1 succeeded
[EXIT]: Disconnecting from myserver.example.com
```

---

## Enabling Debug Mode

To activate debug mode, pass the `debug_config` dictionary when instantiating your wrapper class. For example:

```python
wrapper = CascadeWrapperBase(
    server="myserver.example.com",
    site="mySite",
    debug_config={"log_dir": "./logs"}
)
```

---

## Debug Configuration Options

The recognized `debug_config` keys control logging directories and verbose behaviors:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `log_dir` | `str` | `"./logs"` | Directory for the logfile and (verbose mode) request/response JSON files. |
| `show_network_headers` | `bool` | `False` | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

Debug mode uses a quiet console, a verbose logfile named `{SERVER}_debug_{timestamp}.log`, and per-request JSON files. The logfile records detailed pipeline execution steps, HTTP request details, and headers when configured.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
[GET] https://myserver.example.com/api/v1/read/page/mySite/blog/post-1
(mySite/blog/post-1, page) read -> edit -> publish
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

In debug mode, chain failures use `flush_chain_error` to write the completed pipeline text followed by an alignment `v` marker and an `!ERROR:` block. Network and library failures prepend `[NETWORK]` or `[CASCADE-REST-CMS]` to the error message, while standalone errors like `log_cascade_error` and `log_python_error` log API-level failures or unexpected exceptions outside of chain context with file and line annotations.

<!-- synthesized-for: 3.2.1 -->
