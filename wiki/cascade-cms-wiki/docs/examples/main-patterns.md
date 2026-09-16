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
    # Build a path identifier for a page in a site
    path_ident = Path(asset_type="page", path="/index", siteName="Default")
    
    # Queue the read operation
    cascade.operations.read(path_ident)
    
    # Execute all queued operations concurrently
    result = cascade.submit_requests()[0]

# Check if the operation resulted in a CascadeError
if isinstance(result, CascadeError):
    print(f"Error: {result.message}")
else:
    # Access asset fields via the underlying dict wrapper
    print(result.displayName)
    print(result.metadata)
```

The `read` operation represents the response shape that most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. All of these operations return a structured object specific to what was requested, which can be inspected directly after checking that no `CascadeError` occurred.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, deleteParameters, CascadeError, IdentifierType
import uuid

with CascadeWrapperBase() as cascade:
    # Build a path identifier for the asset to delete
    path_ident = Path(asset_type="page", path="/old-page", siteName="Default")
    
    # Build the delete parameters payload
    params = deleteParameters(
        doWorkflow=False,
        destinations=[IdentifierType(id=uuid.uuid4(), type="destination")],
        unpublish=True
    )
    
    # Queue the delete operation
    cascade.operations.delete(path_ident, payload=params)
    
    # Execute all queued operations
    result = cascade.submit_requests()[0]

if isinstance(result, CascadeError):
    print(f"Delete failed: {result.message}")
else:
    print("Asset deleted successfully.")
```

Operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation status only rather than the modified asset data. Callers should expect a success object or a `CascadeError` rather than asset fields back from these mutating calls.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation, CascadeError

with CascadeWrapperBase() as cascade:
    # Build the required SearchInformation payload
    search_info = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
    cascade.operations.search(search_info)
    
    # Execute requests
    result = cascade.submit_requests()[0]

if isinstance(result, CascadeError):
    print(f"Search failed: {result.message}")
else:
    # Iterate over the flat list of matching elements
    for element in result.flat:
        print(element)
```

The `search` operation requires a typed payload object rather than a bare identifier shortcut. Other operations that follow this same payload-driven pattern include `readAudits` (using `auditParameters`) and `editWorkflowSettings`.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, SearchInformation, deleteParameters, IdentifierType
import uuid

with CascadeWrapperBase() as cascade:
    page_path = Path(asset_type="page", path="/index", siteName="Default")
    old_page_path = Path(asset_type="page", path="/old-page", siteName="Default")
    
    # Queue a read chain
    cascade.operations.read(page_path)
    
    # Queue a delete chain with parameters
    delete_params = deleteParameters(
        doWorkflow=False,
        destinations=[IdentifierType(id=uuid.uuid4(), type="destination")],
        unpublish=True
    )
    cascade.operations.delete(old_page_path, payload=delete_params)
    
    # Queue a search chain
    search_info = SearchInformation(
        siteName="Default",
        searchTerms="blog",
        searchFields=["name"],
        searchTypes=["page"]
    )
    cascade.operations.search(search_info)
    
    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.5 -->
