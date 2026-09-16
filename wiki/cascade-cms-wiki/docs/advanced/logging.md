# Logging & Data & Debugging

The `cascade_cms` library provides two output modes: a normal mode for everyday use and a debug mode for diagnosing failures. Both produce logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode provides minimal console output and a simple logfile. It tracks session lifecycle markers (`log_init`, `log_batch_start`, `log_batch_end`, `log_exit`), batch tallies, and basic operation progress lines without verbose network details or payload files.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver
[RUNNING]: myscript
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver
```

---

## Enabling Debug Mode

```python
debug_config = {
    "log_dir": "./logs",
    "show_network_headers": True
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

The debug logfile is named according to the pattern `{SERVER}_debug_{timestamp}.log` and contains a quiet console, a verbose logfile, plus per-request JSON files in the designated log directory.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

When failures occur, `OperationLogger` captures step-by-step context using `flush_chain_error`, `log_cascade_error`, or `log_python_error`. A `v` alignment marker and an `!ERROR:` block point directly to the failing step index or display standard traceback info alongside `@{file}:{line}` references.

<!-- synthesized-for: 3.1.5 -->
