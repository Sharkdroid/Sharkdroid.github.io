# Logging & Drafting

The cascade_cms library provides two output modes for tracing execution: normal mode for everyday use and debug mode for deep diagnostics. Both modes produce logfiles in a designated directory, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode writes minimal console information and a simple logfile. It outputs lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and generates a logfile named via the underlying logger setup with one line per chain operation.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[LOG]: logs/myserver.com_2023-10-27T12-00-00-000000_1.log
(mySite/blog/post-1, page) READ -> edit -> publish
[RESULT]: Success
(mySite/blog/post-2, page) READ -> edit
                         v
                         !ERROR: CascadeError — check log @operations.py:45
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True,
}
wrapper = CascadeWrapper(server="myserver.com", debug_config=debug_config)
```

---

## Debug Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str \| PathLike \| None | "./logs" | directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile uses the naming convention `{server}_debug_{timestamp}_{serial}.log` (with `debug` inserted into the filename parts) and records the verbose per-request JSON files, HTTP requests, and network headers.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
[GET] https://myserver.com/api/v1/read/page/mySite/blog/post-1 | payload: mySite/blog/post-1_request.json
(mySite/blog/post-1, page) READ -> edit -> publish
3/3 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error lines in debug mode feature a `v` alignment marker pointing directly to the failing step in the pipeline, followed by an `!ERROR:` block indicating the precise file and line number where the exception or API error originated. `CascadeError` entries include asset-level context, while Python errors record the exception type, message, and traceback details.

<!-- synthesized-for: 3.9.2 -->
