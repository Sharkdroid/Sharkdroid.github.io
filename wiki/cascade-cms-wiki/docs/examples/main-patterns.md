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
    # 1. Define a Path identifier for the asset
    path = Path(path="/index", siteName="default", asset_type="page")
    
    # 2. Queue the read operation
    cascade.operations.read(path)
    
    # 3. Execute all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # 4. Check for errors before inspecting the asset
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` pattern represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — returning a structured object specific to what was requested. Because `read` returns an `Asset` wrapper around the underlying Cascade JSON, you can access asset-specific properties directly from the result once verified.

---

## Pattern 2 — `delete`: a simple success response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, deleteParameters, CascadeError, IdentifierType

with CascadeWrapperBase() as cascade:
    # 1. Define a Path identifier for the asset to delete
    path = Path(path="/old-page", siteName="default", asset_type="page")
    
    # 2. Create the delete parameters payload
    # Note: destinations_identifiers requires a list of IdentifierType objects
    params = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # 3. Queue the delete operation with parameters
    cascade.operations.delete(path, payload=params)
    
    # 4. Submit and inspect the result
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Deletion failed: {result.message}")
    else:
        print("Asset successfully deleted!")
```

The `delete` operation and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation, CascadeError

with CascadeWrapperBase() as cascade:
    # 1. Construct the SearchInformation payload
    payload = SearchInformation(
        siteName="default",
        searchTerms="blog",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Submit and inspect the result container
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # 4. Iterate over the flat list of matched elements
        for element in result.flat:
            print(element)
```

The `search` operation requires a typed payload object — there is no bare identifier shortcut — and follows the same payload-driven pattern as operations like `readAudits` (`auditParameters`), `editWorkflowSettings`, and others.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, SearchInformation, deleteParameters

with CascadeWrapperBase() as cascade:
    # Queue three independent chains
    cascade.operations.read(Path(path="/about", siteName="default", asset_type="page"))
    cascade.operations.delete(Path(path="/temp", siteName="default", asset_type="page"), payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="default", searchTerms="news"))
    
    # All three run concurrently, and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.3 -->
