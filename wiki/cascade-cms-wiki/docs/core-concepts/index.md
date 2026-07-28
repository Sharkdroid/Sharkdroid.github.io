---
layout: default
title: Core Concepts
nav_order: 3
---

# Core Concepts

This page explains the design decisions behind the library — why things work the way they do and what mental model to bring when writing scripts.

---

## 1. Design philosophy

The library is intentionally lean and explicit. It exposes the Cascade CMS REST API as clean Python calls. It does not abstract workflow complexity, make decisions about what to do with results, or automate orchestration that belongs in your script.

**Why?** Every script has unique business logic. A bulk-publish script, a workflow-advance script, and a content-migration script all use the same operations but chain them differently. If the library tried to abstract that chaining, it would either be too rigid or too complex. Instead, it exposes the REST operations cleanly and lets you compose them.

A concrete example: `performWorkflowTransition()` advances one workflow step. It does not auto-publish. It does not send notifications. It does not check whether the step is valid. Those decisions belong in your script:

```python
# Read current state
cascade.operations.readWorkflowInformation(asset_id)
wf_info = cascade.submit_requests(workflowInformation)[0]

# Your script validates
available = [a["action_identifier"] for step in wf_info.ordered_steps
             for a in step.get("actions", [])
             if step["step_identifier"] == wf_info.current_step]

if "approve" not in available:
    raise ValueError("Approval action not available in current step")

# Your script orchestrates
cascade.operations.performWorkflowTransition(asset_id, transition_payload)
cascade.submit_requests()
```

---

## 2. Payload and response models

Requests use **Pydantic dataclass models** derived from `SimplePayload`. Each operation takes a specific payload type that serializes itself to JSON automatically.

```python
# Payload types are validated at construction time
payload = SearchInformation(
    siteName="www.example.edu",
    searchTerms="annual report",
    searchTypes=["page"],
)
cascade.operations.search(payload)
```

Responses are deserialized into typed Python objects: `Asset`, `IdentifierType`, `ListElements`, `workflowInformation`, and so on. The type you pass to `submit_requests()` is what you get back in the list.

Some payload models serve double duty as response models — `accessRightsInformationPayload`, for example, serializes a request and deserializes its own response because the Cascade API mirrors the request structure in its reply.

`NewAsset` is a special case: it allows extra fields (`extra="allow"`) because Cascade silently ignores unknown fields and asset-type-specific properties vary per type:

```python
# Extra fields like "text" pass through to Cascade without validation errors
new_file = NewAsset(
    name="report.txt",
    asset_type="file",
    site_name="www.example.edu",
    parent_folder_path="/uploads",
    text="Hello World",  # asset-type-specific, not in the model schema
)
```

---

## 3. Identifiers: IdentifierType vs Path

Two types can address any Cascade asset.

**`IdentifierType`** references an asset by UUID and type:

```python
from uuid import UUID
from cascade_cms.cmstypes import IdentifierType

ref = IdentifierType(
    identifier=UUID("e868f539ac1001062cfa029c4c5df4d0"),
    asset_type="page",
)
```

**`Path`** references an asset by type, site name, and path string:

```python
from cascade_cms.cmstypes import Path

ref = Path(
    asset_type="page",
    siteName="www.example.edu",
    path="/about/leadership",
)
```

`resolve_identifier()` converts either into URL segments the REST driver appends to the endpoint path. Internally:
- `IdentifierType` → `(asset_type, uuid_hex)`
- `Path` → `(asset_type, siteName, path_string)`

**When to use which:**
- Use `IdentifierType` when you have UUIDs (from API responses, database records, etc.)
- Use `Path` when you're writing scripts against known folder structures or site layouts
- Both work with every operation that accepts an identifier argument

---

## 4. The Asset wrapper

`Asset` is a dict-backed wrapper around a raw Cascade JSON payload. Unlike the Pydantic models, `Asset` has no fixed schema — the inner fields vary by asset type.

```python
# Access fields with .get()
name = asset.get("name")
keywords = asset.get("keywords", "")

# Or with direct dict access
asset["displayName"] = "New Title"

# Type is enforced on reassignment
asset["name"] = 42  # TypeError: expected str, got int
```

`Asset` provides two utility methods for structured navigation:

**`get_data_structure(group, identifier)`** — finds nodes matching an identifier inside a structured data group. Returns a list of matching nodes by reference (mutations persist).

```python
nodes = asset.get_data_structure("main-content", "body-text")
if nodes:
    nodes[0]["text"] = "<p>Updated content</p>"
```

**`get_page_configuration(name, region=None)`** — looks up a named page configuration and optionally a specific region within it. Returns a `PageConfiguration` or `PageRegion` object by reference.

```python
config = asset.get_page_configuration("ASPX")          # → PageConfiguration
region = asset.get_page_configuration("ASPX", "DEFAULT")  # → PageRegion
if region:
    region.content = "<p>New region content</p>"
```

---

## 5. Callbacks

Callbacks are functions that run on each result after `submit_requests()` completes. They are optional and registered with `.then()`.

```python
def normalize(asset):
    keywords = asset.get("keywords", "")
    asset["keywords"] = keywords.strip().lower()

cascade.operations.read(ids).then(normalize)
results = cascade.submit_requests(Asset)
# normalize was called once per result, in order
```

**Execution model:** Callbacks run sequentially on each result. If result B finishes before result A (because they execute concurrently), callbacks still run in registration order on each individual result.

**Chaining:** `.then()` accepts a single function or a list. Both register in the same list.

```python
cascade.operations.read(ids).then([validate, normalize, log])
# Per result: validate → normalize → log
```

**Error handling:** If a callback raises an exception, it is logged and execution continues with the next callback. One failing callback does not stop the chain.

**Async callbacks:** If your callback is a coroutine function (`async def`), it is awaited directly. Sync callbacks run in a `ThreadPoolExecutor` by default to avoid blocking the event loop.

---

## 6. Executors: ThreadPoolExecutor vs ProcessPoolExecutor

By default, sync callbacks run in a `ThreadPoolExecutor` — safe for I/O-bound work like HTTP calls, file writes, or database inserts.

For CPU-bound work (image optimization, ML inference, PDF processing), use a `ProcessPoolExecutor`:

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Module-level function required (must be picklable)
def compress_image(asset):
    data = asset.get("blob")
    ...

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    cascade.operations.read(image_ids).then(compress_image)
    results = cascade.submit_requests(executor=executor)
```

`ProcessPoolExecutor` requires **module-level functions** — lambdas and nested functions cannot be pickled and will raise a `PicklingError`. This is a Python multiprocessing constraint, not a library constraint.

---

## 7. RequestExecutor and generic typing

`RequestExecutor[T]` holds one queued request. The generic `T` is the **response** type — what you expect to get back — not the payload type. This distinction matters for static analysis:

```python
# Correct: T is the response type
request = RequestExecutor[Asset](url, "GET", parser=parse_assets)
request = RequestExecutor[IdentifierType](url, "POST", payload=new_asset, parser=bound_parser)

# Not: T is not the payload type
request = RequestExecutor[NewAsset](...)  # misleading — NewAsset is sent, not returned
```

---

## 8. Caching

GET responses are cached in a local SQLite database. Repeated reads of the same asset skip the network entirely.

The cache configuration is passed as `configuration_variables` to `CascadeWrapperBase`. The dict is forwarded directly to `aiohttp-client-cache`'s `SQLiteBackend`:

```python
# Default: cache all 200 GET responses
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}

# Disable caching: pass empty allowed_methods
config_no_cache = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": (),  # empty — nothing is cached
}

# Short-lived cache: expire after 60 seconds
config_ttl = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
    "expire_after": 60,
}
```

POST and PUT requests are **never cached**, regardless of config. Only successfully parsed responses (`_cacheable=True`) are stored — error responses are never written to the cache.

See [Concurrency & Caching](../advanced/concurrency-caching/) for a deeper look at the caching internals.

---

## 9. Logging

The logger runs in one of two modes depending on whether a `debug` dict is passed to `CascadeWrapperBase`.

**Normal mode** (default, `debug=None`): minimal console output and a simple logfile.
```
[INIT]: Connecting to prod
[RUNNING]: my_script.py
Processed: 12/12
[DONE]: 12 assets processed in 1.4s
[EXIT]: Disconnecting from prod
```
Logfile: `./logs/prod_{timestamp}.log`

**Debug mode** (`debug={...}`): quiet console, verbose nested logfile with request URLs, payloads, response bodies, callback names, and variable snapshots on errors.
Logfile: `./logs/prod_debug_{timestamp}.log`

See [Logging & Debugging](../logging/) for how to read both modes and when to enable debug.
