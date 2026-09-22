# Logging & Debugging

The `cascade_cms` library provides two distinct output modes: a normal mode for everyday use and a debug mode designed for diagnosing failures. Both modes produce logfiles, while debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode writes minimal console output and a simple logfile. It records session lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a logfile containing one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: myscript.py
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeClient(
    url="https://cascade.example.com",
    api_key="12345",
    site="Default",
    debug_config={"log_dir": "./logs"}
)
```

---

## Debug Configuration Options

Recognized `debug_config` keys control verbose logging behavior and file destinations.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str / Path | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile is named according to the `{SERVER}_debug_{timestamp}.log` convention in the configured `log_dir` folder. It records a quiet console output, a verbose logfile, and per-request JSON files.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error blocks in debug mode use a `v` alignment marker and an `!ERROR:` block where the column aligns under the first character of the failing step. A `CascadeError` represents an API-level failure logged via `log_cascade_error`, whereas Python exceptions are logged via `log_python_error` with the exception type, message, and `@{file}:{line}` location appended to the last line of the message.

<!-- synthesized-for: 3.1.6 -->
