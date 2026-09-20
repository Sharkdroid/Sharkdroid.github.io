# Logging & Deduplication

cascade_cms features two distinct operation output modes: a clean normal mode for everyday use, and a verbose debug mode designed for troubleshooting and diagnosing complex pipeline or network failures. Both modes generate dedicated logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

In normal mode, the logger produces lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress tallies, and a standard logfile containing one line per completed operation chain. The logfile captures minimal console output and simple log entries without verbose request payloads.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: myscript.py
(mySite/blog/post-1, page) READ -> READ
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeWrapperBase(
    url="https://cascade.example.com",
    api_key="12345",
    debug_config={"log_dir": "./logs"}
)
```

---

## Debug Configuration Options

The `debug_config` dictionary controls verbose behavior. Recognized keys, their defaults, and descriptions are detailed below:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

Debug mode generates a distinct logfile named `{SERVER}_debug_{timestamp}.log` inside the designated `log_dir`, along with individual per-request JSON payload files. It captures detailed request URLs, headers, and full step-by-step pipeline progression.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(mySite/blog/post-1, page) READ -> READ
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

When an error occurs, the logger records the failing step index and prints a `v` alignment marker directly beneath the pipeline step where the failure happened, followed by an `!ERROR:` block indicating the exact source file and line number. `CascadeError` covers API-level failures with asset identifiers, while general Python exceptions capture the exact exception type, message, and local frame info.

<!-- synthesized-for: 3.1.6 -->
