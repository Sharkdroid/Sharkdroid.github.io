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
from cascade_cms.cmstypes import Path, CascadeError, AssetTypes

# Open the wrapper as a context manager
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Build a Path identifier referencing a Page asset
    identifier = Path(asset_type=AssetTypes.PAGE, path="/index", site_name="default")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Run queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # Check if the operation returned an API error
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access properties on the parsed Asset object
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, CascadeError, AssetTypes, deleteParameters, IdentifierType

with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    identifier = Path(asset_type=AssetTypes.PAGE, path="/old-page", site_name="default")
    
    # Construct deleteParameters payload
    payload = deleteParameters(
        do_workflow=False,
        destinations_identifiers=[]
    )
    
    # Queue the delete operation with parameters
    cascade.operations.delete(identifier, payload=payload)
    
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation, CascadeError, AssetTypes

with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Construct the required SearchInformation payload
    payload = SearchInformation(
        site_name="default",
        search_terms="report",
        search_types=[AssetTypes.PAGE]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list elements returned
        for element in result.flat:
            print(element)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and naming the other operations that follow the same pattern: `readAudits` (`auditParameters`), `editWorkflowSettings`, etc.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    cascade.operations.read(Path(asset_type=AssetTypes.PAGE, path="/index", site_name="default"))
    cascade.operations.delete(Path(asset_type=AssetTypes.PAGE, path="/old-page", site_name="default"))
    cascade.operations.search(SearchInformation(site_name="default", search_terms="test"))
    
    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.1 -->
