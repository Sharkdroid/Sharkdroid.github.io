# Logging & Debuuging

The `cascade_cms` library provides two distinct output modes managed by `OperationLogger`: normal mode for everyday use and debug mode for diagnosing failures. Both modes produce logfiles in a designated log directory; debug mode adds a verbose nested call-chain log alongside a quieter console output and per-request JSON files.

---

## Normal Mode Output

Normal mode (active when `debug_config=None`) provides a minimal console output and a simple logfile. It outputs lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines, and a logfile containing one line per chain in the format `(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...`.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.example.com
[LOG]: logs/myserver.example.com_20240101T000000-000000_1.log
[RUNNING]: my_script.py
(my-uuid, page) read -> edit -> release
1/1 succeeded
[DONE]: Disconnecting from myserver.example.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeClient(
    url="https://cascade.example.com:8443/api/v1",
    username="user",
    password="password",
    site_name="Default",
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
| log_dir | str / PathLike | "./logs" | Directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | Verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

The debug logfile is named using the format `_` joined parts containing `{SERVER}_debug_{timestamp}_{serial}.log`. It includes quiet console output, a verbose logfile, and per-request JSON files in the specified log directory.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(my-uuid, page) read -> edit -> release
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

When a chain fails, `flush_chain_error` writes the finished pipeline text followed by the alignment `v` marker and `!ERROR:` block. Network and library failures prepend `[NETWORK]` or `[CASCADE-REST-CMS]` to the error message, while Cascade and callback errors have no prefix. Unhandled or out-of-chain errors are logged via `log_cascade_error` or `log_python_error` with captured file names and line numbers (`@{file}:{line}`).

<!-- synthesized-for: 3.9.2 -->
