# Logging & GradeDebugging

Cascade CMS provides two distinct output modes for tracking operation progress and diagnosing issues: a normal mode designed for everyday script execution, and a debug mode intended for deeper investigation and troubleshooting. Both modes write output to logfiles, but debug mode adds a verbose nested call-chain log alongside quieter console output.

---

## Normal Mode Output

Normal mode provides minimal console output and a simple logfile, driven by lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), operation progress lines, and a normal logfile named `{SERVER}_{timestamp}.log` containing one line per completed operation chain. Chains run concurrently, but their results are written once upon completion or stoppage to avoid interleaved lines in scrolling consoles or append-only logfiles.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.edu
[RUNNING]: my_script.py
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver.edu
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True,
}
wrapper = CascadeWrapperBase("myserver.edu", debug_config=debug_config)
```

---

## Debug Configuration Options

Recognized debug_config keys control output destinations and verbose request details:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

In debug mode, logfiles are named with the `debug` suffix (e.g., `{SERVER}_debug_{timestamp}.log`) and contain verbose per-request JSON files alongside the main log. Request and response detail lines as well as raw request/response JSON files are emitted in debug mode only, and payloads are never inlined directly.

### Sample Debug Log

```text
[INIT]: Connecting to myserver.edu
[DEBUG]: running in debug mode
>>>> START REQUEST <<<<
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
>>>> END REQUEST <<<<
[DONE]: 1 assets processed in 0.8s
[EXIT]: Disconnecting from myserver.edu
```

---

## Interpreting Errors in Debug Mode

When an operation fails or stops during a chain, `flush_chain_error` writes the completed pipeline text via `render_complete()` followed by a `v` alignment marker and an `!ERROR:` block. The failing step index aligns the `v` column directly under the first character of the failing step's label by reconstructing the preceding line length (accounting for 4-character ` -> ` separators). Multi-line messages maintain consistent indentation without progressive nesting, appending `@{file}:{line}` to the final line. Outside of chain context, `log_cascade_error` logs API-level `CascadeError` failures and `log_python_error` extracts tracebacks from general exceptions.

<!-- synthesized-for: 3.1.3 -->
