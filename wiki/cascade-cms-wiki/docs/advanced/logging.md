# Logging & Definitions

The `cascade_cms` library provides two distinct output modes: a normal mode for everyday use and a debug mode for diagnosing failures. Both modes produce logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode uses a minimal console and a simple logfile to track execution, writing lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a normal logfile named `{SERVER}_{timestamp}.log` with one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to example.com
[LOG]: ./logs/example.com_2023-10-27T12-30-00-000000_1.log
(mySite/blog/post-1, page) READ -> edit -> publish
[DONE]: 1 assets processed in 0.5s
0 failed, 1 succeeded
[EXIT]: Disconnecting from example.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeClient(server="example.com", debug_config={})
```

---

## Debug Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile uses the naming convention `{SERVER}_debug_{timestamp}.log` and captures quiet console, verbose logfile output plus per-request JSON files.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
[GET] https://example.com/api/v1/read/page/mySite/blog/post-1
(mySite/blog/post-1, page) READ -> edit -> publish
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error blocks in debug mode render a `v` marker followed by a `!ERROR:` block aligned under the failing step's index. Network and library failures prepend `[NETWORK]` or `[CASCADE-REST-CMS]` to the error message, while cascade and callback errors receive no prefix, appending `@{file}:{line}` to the last line of the message.

<!-- synthesized-for: 3.9.2 -->
