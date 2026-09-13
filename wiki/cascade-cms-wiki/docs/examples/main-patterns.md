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
from cascade_cms.cmstypes import CascadeError, Path

with CascadeWrapperBase() as cascade:
    # Build a Path identifier for the asset
    path = Path(asset_type="page", path="/index", siteName="Default")
    
    # Queue the read operation
    chain = cascade.operations.read(path)
    
    # Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]

    # Check for errors before working with the result
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
from cascade_cms.cmstypes import CascadeError, Path, deleteParameters, IdentifierType

with CascadeWrapperBase() as cascade:
    path = Path(asset_type="page", path="/old-page", siteName="Default")
    payload = deleteParameters(
        do_workflow=False,
        destinations_identifiers=[IdentifierType(id="12345678123456781234567812345678", type="destination")],
        unpublish=True
    )
    
    cascade.operations.delete(path, payload=payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset successfully deleted.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError, SearchInformation

with CascadeWrapperBase() as cascade:
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    cascade.operations.search(payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
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
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import Path, SearchInformation, deleteParameters, IdentifierType

with CascadeWrapperBase() as cascade:
    path1 = Path(asset_type="page", path="/about", siteName="Default")
    path2 = Path(asset_type="page", path="/old-page", siteName="Default")
    del_payload = deleteParameters(
        do_workflow=False,
        destinations_identifiers=[IdentifierType(id="12345678123456781234567812345678", type="destination")],
        unpublish=True
    )
    search_payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )

    cascade.operations.read(path1)
    cascade.operations.delete(path2, payload=del_payload)
    cascade.operations.search(search_payload)

    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.5 -->
