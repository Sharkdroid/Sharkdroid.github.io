---
layout: default
title: Logging & Debugging
nav_order: 6
---

# Logging & Debugging

The library writes structured output to both the console and a logfile. Two modes exist: **normal** (minimal) and **debug** (verbose). Choosing between them is a single argument to `CascadeWrapperBase`.

---

## 1. Normal mode (default)

Pass no `debug` argument, or pass `debug=None`. Console is minimal; logfile captures operation names and errors.

```python
with CascadeWrapperBase(env, config) as cascade:
    ...
# debug=None is the default
```

**Console output:**
```
[INIT]: Connecting to prod
[RUNNING]: my_script.py
Processed: 1/12
Processed: 2/12
...
Processed: 12/12 (1 failed)
[ERROR]: CascadeError — check log
[DONE]: 12 assets processed in 1.4s
[ERRORS]: 1 failure — check prod_2025-01-15T09-30-00.log
[EXIT]: Disconnecting from prod
```

**Logfile** at `./logs/{SERVER}_{timestamp}.log`:
```
[READ]: mysite/blog/post-1
[READ]: mysite/blog/post-2
[ERROR]: mysite/blog/missing-page
  Error Type: CascadeError
  Error Message: Unable to identify an entity based on path 'mysite/blog/missing-page'
```

---

## 2. Debug mode

Pass a `debug` dict to `CascadeWrapperBase`. All keys are optional — any key you omit falls back to the default listed in [§3](#3-debug-config-keys-explained).

```python
debug_config = {
    "log_dir": "./logs",
    "log_operations": True,
    "log_callbacks": True,
    "log_responses": True,
    "show_payload_data": True,
    "show_network_headers": False,
    "show_error_variables": True,
    "response_line_limit": 8,   # lines of response body to include; -1 = full body
}

with CascadeWrapperBase(env, config, debug=debug_config) as cascade:
    ...
```

Every key above is shown at its default value — this example is for illustration only. In practice, pass just the keys you want to override, e.g. `debug={"response_line_limit": -1}`. Even an empty dict (`debug={}`) is enough to turn on debug mode with every key at its default.

**Console in debug mode:** Only `[INIT]`, `[DEBUG]`, progress counter, and errors. No operation details.

**Logfile** at `./logs/{SERVER}_debug_{timestamp}.log` — nested, structured blocks:

```
> READ:
|  [URL]: https://cascade.example.edu/api/v1/read/page/8b320f55...
|  [payload]: NONE
|  [parser]: parse_assets
|  [identifier]: mysite/blog/post-1
|  ========================= (RESPONSE) =========================
|  {"asset":{"page":{"id":"8b320f55...","name":"post-1",...
|  ... (truncated at 8 lines)
>>>>>>>>>>>>>>>>>>>>>> END OF REQUEST <<<<<<<<<<<<<<<<<<<<<<<
```

The pipe-indented nesting shows depth: top-level operations are prefixed with `> `, and their content is indented with `| `.

---

## 3. Debug config keys explained

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `log_dir` | `str` | `"./logs"` | Directory for logfiles. Created if it doesn't exist. |
| `log_operations` | `bool` | `True` | Write an operation block per request (URL, payload, parser, identifier). |
| `log_callbacks` | `bool` | `True` | Log callback chain `fn1 >> fn2 >> fn3` for each result. |
| `log_responses` | `bool` | `True` | Write the raw response body inside each operation block. |
| `show_payload_data` | `bool` | `True` | Include the serialized payload in operation blocks. |
| `show_network_headers` | `bool` | `False` | Write request and response HTTP headers. Useful for debugging caching and auth issues. |
| `show_error_variables` | `bool` | `True` | On Python exceptions, dump local variable names and values from the failing frame. |
| `response_line_limit` | `int` | `8` | Max lines of response body to include. `-1` dumps the full body. |

---

## 4. Reading a normal mode logfile

Each line in the normal logfile is one of:

**Operation record** — one line per queued request:
```
[READ]: mysite/blog/post-1
[SEARCH]: NONE
[CREATE]: NONE
```

The identifier shown is the asset path when available, otherwise the first 8 chars of the UUID plus asset type:
```
[READ]: a3f9bc12... (folder)
```

**Error record** — two lines per error:
```
[ERROR]: mysite/blog/missing-page
  Error Type: CascadeError
  Error Message: Unable to identify an entity...
```

```
[ERROR]: mysite/files/corrupted.jpg
  Error Type: ClientResponseError
  Error Message: 500 Internal Server Error
```

---

## 5. Reading a debug logfile

**Operation block structure:**

```
> OPERATION_NAME:               ← top-level operation header
|  [URL]: ...                   ← full request URL
|  [payload]: ...               ← serialized payload (if show_payload_data=True)
|  [parser]: parse_assets       ← parser function name
|  [identifier]: ...            ← identifier display string
|  === (RESPONSE) ===           ← response body (if log_responses=True)
|  line 1 of JSON...
|  ...
>>>>>>>>>>>>>> END OF REQUEST <<<<<<<<<<<   ← marks return to depth 0
```

**Nested operations** (e.g., callbacks queueing new operations):

```
> READ:
|  [URL]: ...
|  |---> READ (via follow_linked_asset):   ← callback-triggered sub-operation
|  |  [URL]: ...
|  |  [callbacks]: follow_linked_asset
>>>>>>>>>>>>>> END OF REQUEST <<<<<<<<<<<
```

**Error blocks in debug mode:**

```
|  
*!! CascadeError: Unable to identify entity...
  asset: mysite/blog/missing-page
!!
```

```
*!! ClientResponseError: 500 Internal Server Error
  origin:   driver.py
  function: fetch
  line 98:  response.raise_for_status()
  variables:
    self       = RequestExecutor(url='...', method='GET')  (RequestExecutor)
    response   = <ClientResponse ...>  (ClientResponse)
!!
```

---

## 6. When to enable debug mode

| Situation | Recommendation |
|-----------|---------------|
| Script fails silently (no console output) | Enable debug; check logfile for first error |
| Cascade returns unexpected data | Set `log_responses=True`, `response_line_limit=-1` |
| Callback not executing | Set `log_callbacks=True`; check if callback name appears |
| Performance seems slow | Set `show_network_headers=True`; check response times and cache status |
| Script crashes with a Python exception | Set `show_error_variables=True`; see local state at failure |
| Everything works but you want a full audit trail | Enable debug for the production run |

---

## 7. Logfile location and naming

| Mode | Filename pattern |
|------|-----------------|
| Normal | `./logs/{SERVER}_{timestamp}.log` |
| Debug | `./logs/{SERVER}_debug_{timestamp}.log` |

`timestamp` is formatted as `YYYY-MM-DDTHH-MM-SS`.

**Custom log directory:**
```python
debug_config = {
    "log_dir": "/var/log/cascade",
    ...
}
```

For normal mode, the log directory is always `./logs` and is not configurable.

**Cleanup:** Logfiles accumulate with each script run. Add `./logs/` to `.gitignore` and periodically archive or delete old logs. The library does not rotate or clean up logfiles automatically.
