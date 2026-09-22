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
    # Define a Path identifier with its asset type and site information
    identifier = Path(asset_type="page", siteName="Default", path="/index")
    
    # Queue the read operation chain
    cascade.operations.read(identifier)
    
    # Submit all queued operations concurrently
    result = cascade.submit_requests()

# Handle failure returned as a value
if isinstance(result, CascadeError):
    print(f"Error: {result.message}")
else:
    print(result.displayName)
    print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, deleteParameters, CascadeError, CascadeSuccess

with CascadeWrapperBase() as cascade:
    identifier = Path(asset_type="page", siteName="Default", path="/old-page")
    payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    
    cascade.operations.delete(identifier, payload=payload)
    result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Failed to delete: {result.message}")
elif isinstance(result, CascadeSuccess):
    print("Successfully deleted asset.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation, CascadeError, ListElements

with CascadeWrapperBase() as cascade:
    payload = SearchInformation(siteName="Default", searchTerms="report")
    
    cascade.operations.search(payload)
    result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Search failed: {result.message}")
elif isinstance(result, ListElements):
    for element in result.flat:
        print(element)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and other operations such as `readAudits` (`auditParameters`), `editWorkflowSettings`, etc., follow the same pattern.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, SearchInformation, deleteParameters

with CascadeWrapperBase() as cascade:
    # Queue three independent chains in a single batch
    cascade.operations.read(Path(asset_type="page", siteName="Default", path="/index"))
    cascade.operations.delete(Path(asset_type="page", siteName="Default", path="/old-page"), payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="Default", searchTerms="report"))
    
    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.6 -->
