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
    # Define a path to a page asset on a specific site
    path = Path(path="index", siteName="Default", asset_type="page")
    
    # Queue the read operation
    cascade.operations.read(path)
    
    # Submit all queued operations concurrently
    result = cascade.submit_requests()

# Check whether the operation succeeded or returned an API-level error
if isinstance(result, CascadeError):
    print(f"Error: {result.message}")
else:
    # Access structured asset fields
    print(result.displayName)
    print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and all of them return a structured object specific to what was requested. Because failures are captured rather than raised, verifying the result type is always required before processing.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, deleteParameters, CascadeError, IdentifierType
import uuid

with CascadeWrapperBase() as cascade:
    # Define the path of the asset to delete
    path = Path(path="old-page", siteName="Default", asset_type="page")
    
    # Configure delete parameters
    payload = deleteParameters(
        doWorkflow=False,
        destinations_identifiers=[
            IdentifierType(id=uuid.UUID("1234567890abcdef1234567890abcdef"), type="destination")
        ],
        unpublish=True
    )
    
    # Queue the delete operation with parameters
    cascade.operations.delete(path, payload=payload)
    
    # Submit requests
    result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Failed to delete: {result.message}")
else:
    print("Asset deleted successfully.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations. Instead, they return minimal success or failure responses indicating whether the action completed.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation, CascadeError

with CascadeWrapperBase() as cascade:
    # Construct the required search payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    # Submit requests
    result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Search failed: {result.message}")
else:
    # Iterate over the flat list of matched elements
    for element in result.flat:
        print(element)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and names the other operations that follow the same pattern: `readAudits` (`auditParameters`), `editWorkflowSettings`, etc. These operations rely on dedicated parameter models to package query criteria before execution.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, SearchInformation

with CascadeWrapperBase() as cascade:
    path = Path(path="index", siteName="Default", asset_type="page")
    search_payload = SearchInformation(siteName="Default", searchTerms="news")

    # Queue three independent chains; all run concurrently when submitted
    cascade.operations.read(path)
    cascade.operations.delete(path)
    cascade.operations.search(search_payload)

    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.6 -->
