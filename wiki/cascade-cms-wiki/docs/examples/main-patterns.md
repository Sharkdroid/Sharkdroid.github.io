# Core Patterns: `read`, `delete`, `search`

Every script that uses `cascade_cms` follows the same shape: open the wrapper as
a context manager, queue up one or more operations on `cascade.operations`, then
call `submit_requests()` once to run them all concurrently.

The three examples below use the same skeleton but highlight the **three
distinct response shapes** you'll see across the library:

| Operation | Returns | Why it's shown |
|-----------|---------|----------------|
| `read` | A large, structured `Asset` object | Most operations that touch an existing asset return this shape |
| `delete` | A simple success object (`CascadeSuccess`) | Mutating operations that don't return data use this minimal shape |
| `search` | A list result, driven by a required `SearchInformation` payload | Shows the "operation needs a payload object" pattern |

All three also demonstrate the same failure-handling rule: **failures are
returned as values, not raised.** Always check `isinstance(result, CascadeError)`
before using a result.

---

## Pattern 1 — `read`: fetching a structured asset

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, CascadeError

with CascadeWrapperBase() as cascade:
    # Build a Path identifier for the asset
    path = Path(asset_type="page", path="/index", siteName="Default")
    
    # Queue a read operation
    cascade.operations.read(path)
    
    # Execute the queued request(s) concurrently
    results = cascade.submit_requests()
    result = results[0]

    # Check for API-level failures
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset fields
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. All of these operations return a structured object specific to what was requested, which can then be inspected or transformed further down the line.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, deleteParameters, CascadeError, CascadeSuccess

with CascadeWrapperBase() as cascade:
    path = Path(asset_type="page", path="/old-page", siteName="Default")
    
    # Configure delete parameters
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True,
    )
    
    cascade.operations.delete(path, payload=payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    elif isinstance(result, CascadeSuccess):
        print("Asset successfully deleted.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation only rather than the modified asset data. Callers should check for a `CascadeSuccess` response rather than expecting structured asset fields back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation, CascadeError, ListElements

with CascadeWrapperBase() as cascade:
    # Construct the required search payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog",
    )
    
    cascade.operations.search(payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list elements returned
        for item in result.flat:
            print(item)
```

Searching requires a typed payload object such as `SearchInformation` — there is no bare identifier shortcut. Other operations that follow this same payload-driven pattern include `readAudits` (using `auditParameters`) and `editWorkflowSettings`.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, SearchInformation

with CascadeWrapperBase() as cascade:
    path = Path(asset_type="page", path="/index", siteName="Default")
    search_payload = SearchInformation(siteName="Default", searchTerms="test")

    # Queue multiple independent chains
    cascade.operations.read(path)
    cascade.operations.delete(path)
    cascade.operations.search(search_payload)

    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.5 -->
