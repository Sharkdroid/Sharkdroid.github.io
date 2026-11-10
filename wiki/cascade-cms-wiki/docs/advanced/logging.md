# Logging & Database

The `cascade_cms` library provides two distinct output modes: a normal mode for everyday use and a debug mode for diagnosing failures. Both modes produce logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode uses a minimal console and simple logfile to record session lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a logfile named `{SERVER}_{timestamp}.log` with one line per operation.

### Normal Logfile Format

```text
[INIT]: Connecting to my-server
[RUNning]: script.py
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
[DONE]: 1 assets processed in 1.0s
0 failed, 1 succeeded
[EXIT]: Disconnecting from my-server
```

---

## Enabling Debug Mode

```python
wrapper = CascadeWrapperBase(
    server="my-server",
    auth=("user", "pass"),
    debug_config={"log_dir": "./logs"}
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

Debug mode uses a quieter console and a verbose logfile named `{SERVER}_debug_{timestamp}.log` alongside per-request JSON files. The two modes are controlled solely by whether `debug_config` is `None`; `_is_debug` serves as the single on/off switch for verbose behavior.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error output utilizes a `v` marker and `!ERROR:` block positioned beneath the failing step. For NETWORK/LIBRARY failures, `[NETWORK]` or `[CASCADE-REST-CMS]` is prepended to the `!ERROR:` message, while CASCADE and CALLBACK failures get no prefix. The alignment column is computed by reconstructing the line's literal text up to (not including) the failing label and measuring its length, where each ` -> ` separator is counted as 4 characters.

<!-- synthesized-for: 3.9.2 -->
