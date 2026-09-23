# Logging & Grade-Level Debugging

The `cascade_cms` library provides two output modes: normal mode for everyday use, and debug mode for diagnosing failures. Both produce logfiles; debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

In normal mode, the logger produces lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a normal logfile named after the server and timestamp with one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver
[RUNNING]: my_script.py
[READ]: mySite/blog/post-1
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver
```

---

## Enabling Debug Mode

```python
wrapper = CascadeWrapperBase(server="myserver", debug_config={"log_dir": "./logs"})
```

---

## Debug Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile is named following the pattern `{SERVER}_debug_{timestamp}.log` and captures the verbose execution flow, including nested call chains and per-request files.

### Sample Debug Log

```text
>>>> START REQUEST <<+
[READ] https://myserver.com/api/v1/read/site/mySite/blog/post-1
(mySite/blog/post-1, page) READ -> TRANSFORM
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Errors in debug mode present alignment markers (`v`) pointing directly to the failing step in the pipeline along with `!ERROR:` detail blocks. CascadeError captures API-level failures with step-index context, while Python errors record exception types and message details outside of the chain context.

<!-- synthesized-for: 3.1.6 -->
