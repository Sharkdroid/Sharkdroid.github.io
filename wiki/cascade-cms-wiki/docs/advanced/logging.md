# Logging & Details

The cascade_cms library provides two distinct output modes for console and logfile generation: a normal mode for everyday use and a debug mode for deep troubleshooting. Both modes produce dedicated logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.

---

## Normal Mode Output

In normal mode, the logger produces minimal console output and a simple logfile. It tracks session lifecycle markers such as `[INIT]`, `[RUNNING]`, `[DONE]`, and `[EXIT]`, reports per-batch request progress, and writes a logfile named `{SERVER}_{timestamp}.log` containing one line per completed operation chain.

### Normal Logfile Format

```text
[INIT]: Connecting to myserver.com
[RUNNING]: myscript.py
(uuid:123, asset) read -> write
1/1 succeeded
[DONE]: 1 assets processed in 0.5s
[EXIT]: Disconnecting from myserver.com
```

---

## Enabling Debug Mode

```python
wrapper = CascadeWrapperBase(
    url="http://cascade.example.com",
    api_key="12345",
    site="Default",
    debug_config={"log_dir": "./logs"}
)
```

---

## Debug Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| log_dir | str | "./logs" | directory for the logfile and (verbose mode) request/response JSON files. |
| show_network_headers | bool | False | verbose mode only: also log request/response HTTP headers. |

---

## Debug Logfile Format

In debug mode, the logfile is named `{SERVER}_debug_{timestamp}.log` and captures verbose per-request details, cache hits, network headers (when enabled), and individual request/response JSON payloads written to the specified log directory.

### Sample Debug Log

```text
>>>> START REQUEST <<<<
(uuid:123, asset) read -> write
1/1 succeeded
>>>> END REQUEST <<<<
```

---

## Interpreting Errors in Debug Mode

Error blocks in debug mode render a `v` alignment marker below the pipeline step where the failure occurred, followed by an `!ERROR:` block detailing the message and its source file and line number. Chain-level failures go through `flush_chain_error` with step-index context, while API-level errors use `log_cascade_error` and unexpected Python exceptions are captured via `log_python_error`.

<!-- synthesized-for: 3.1.5 -->
