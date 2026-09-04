# Logging & Deployment

The cascade_cms library provides two distinct output modes: a clean normal mode for everyday use, and a verbose debug mode designed for diagnosing pipeline failures. Both modes produce dedicated logfiles, while debug mode additionally outputs a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

In normal mode, output is minimal on the console and clean in the logfile. It outputs lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a normal logfile named with `{server}_{timestamp}.log` containing one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to cms.example.com
[RUNNING]: batch_script.py
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
10/10 succeeded
[DONE]: 10 assets processed in 1.2s
[EXIT]: Disconnecting from cms.example.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeClient(
    url="https://cms.example.com",
    api_key="your-api-key",
    debug_config={
        "log_dir": "./logs",
        "show_network_headers": True,
    }
)
```

---

## Debug Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile follows the naming convention `{server}_debug_{timestamp}.log`, outputting quiet console logs and a verbose logfile plus per-request JSON files.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error lines in debug mode output a `v` marker followed by an `!ERROR:` block indicating the exact point of failure, utilizing the `failing_step_index` to align under the failing operation's first character. `CascadeError` covers API-level failures with step-index context, whereas Python exceptions handled by `log_python_error` extract traceback information to log the exception type, message, file name, and line number.

<!-- synthesized-for: 3.1.3 -->
