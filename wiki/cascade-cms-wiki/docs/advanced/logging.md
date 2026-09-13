# Logging & Debugging

The cascade_cms library provides two distinct logging and output modes: normal mode for everyday use and debug mode for diagnosing failures. Both produce logfiles; debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode provides minimal console output and a simple logfile. It outputs lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a normal logfile named based on the server and timestamp with one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to myServer
[RUNNING]: my_script
[READ]: mySite/blog/post-1
[ERROR]: CascadeError — check log
(mySite/blog/post-1)
v
!ERROR: API failure
(mySite/blog/post-2)
v
!ERROR: ZeroDivisionError: division by zero @script.py:42
[DONE]: 2 assets processed in 1.2s
[EXIT]: Disconnecting from myServer
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

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

Debug mode uses a quiet console, a verbose logfile named `{SERVER}_debug_{timestamp}.log`, and per-request JSON files. It features one line per chain built via `ChainLineBuilder` and produced by `OperationLogger.flush_chain` or `flush_chain_error`.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(mySite/blog/post-1, page) read -> edit -> release
[GET] https://myserver/api/v1/read/page/mySite/blog/post-1
2/2 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Errors in debug mode are rendered using a `v` alignment marker and an `!ERROR:` block. The failing step index points to the specific segment in the chain line where the failure occurred, aligning vertically beneath its first character, followed by the error message and the file and line number where it originated.

<!-- synthesized-for: 3.1.5 -->
