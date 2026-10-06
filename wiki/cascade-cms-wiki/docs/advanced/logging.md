# Logging & Debugging

Two output modes exist within the cascade_cms library: normal mode for everyday use and debug mode for diagnosing failures. Both produce logfiles, while debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

Normal mode provides minimal console output and a simple logfile. It records session lifecycle markers, per-operation progress lines, and logs each chain as one line using a write-once-per-chain rendering model.

### Normal Logfile Format

```
[INIT]: Connecting to myserver
[LOG]: ./logs/myserver_2023-10-27T12-00-00-000000_1.log
([2f8b5a, page) read -> edit -> release
[RESULT]: Success
```

---

## Enabling Debug Mode

```python
wrapper = Cascade(
    server="myserver",
    debug_config={
        "log_dir": "./logs",
        "show_network_headers": True
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

Debug mode uses quiet console output with a verbose logfile named `{SERVER}_debug_{timestamp}.log` plus per-request JSON files.

### Sample Debug Log

```
>>>> START REQUEST <<<<
([2f8b5a, page) read -> edit -> release
[GET] https://myserver/api/v1/sites/mySite/page/2f8b5a
3/3 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error blocks in debug mode display an alignment column pointing at the failing step index via a `v` marker followed by an `!ERROR:` block. Network and library failures prepend `[NETWORK]/[CASCADE-REST-CMS]` to the error message, while Cascade and callback errors do not include a prefix.

<!-- synthesized-for: 3.9.1 -->
