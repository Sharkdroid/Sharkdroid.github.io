# Core Patterns: `read`, `delete`, `search`

Every script that uses `cascade_cms` follows the same shape: open the wrapper as
a context manager, queue up one or or more operations on `cascade.operations`, then
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
from cascade_cms.cmstypes import CascadeError, Path

with CascadeWrapperBase("my-site") as cascade:
    # Build a Path identifier referencing the asset
    identifier = Path(path="index", asset_type="page", siteName="Default")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Run the queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]

    # Check for API-level failures
    if isinstance(result, CascadeError):
        print(f"Failed: {result.message}")
    else:
        # Access structured asset data
        print(result.displayName)
        print(result.metadata)
```

The `read` operation returns a structured `Asset` wrapper containing the full object definition returned by Cascade CMS. This is the same response shape followed by other asset-fetching operations like `readAccessRights`, `readWorkflowSettings`, and `listSubscribers`.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError, Path, deleteParameters

with CascadeWrapperBase("my-site") as cascade:
    # Build a Path identifier
    identifier = Path(path="old-page", asset_type="page", siteName="Default")
    
    # Define delete parameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # Queue the delete operation
    cascade.operations.delete(identifier, payload=payload)
    
    # Run requests
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a confirmation wrapper (`CascadeSuccess`) rather than the modified asset data itself. Callers should inspect the success flag or error message instead of expecting asset fields back.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError, SearchInformation

with CascadeWrapperBase("my-site") as cascade:
    # Construct the required search information payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    # Run requests
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of matched elements
        for element in result.flat:
            print(element)
```

Searching requires a fully typed `SearchInformation` payload object rather than a bare identifier shortcut. Operations such as `readAudits` follow the same pattern by requiring specific parameter payloads (`auditParameters`) to shape their requests.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("my-site") as cascade:
    cascade.operations.read(path_identifier)
    cascade.operations.delete(other_path_identifier, payload=delete_params)
    cascade.operations.search(search_info_payload)
    
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.1 -->
