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
with CascadeWrapperBase(url="...", username="...", password="...") as cascade:
    # Build a Path identifier referencing the site and path
    identifier = Path(asset_type="page", siteName="Default", path="/index")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Execute the queued operations concurrently
    results = cascade.submit_requests()
    result = results[0]

    # Check if the operation resulted in an error
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access asset properties on the returned Asset wrapper
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings` — and returns a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase(url="...", username="...", password="...") as cascade:
    identifier = Path(asset_type="page", siteName="Default", path="/old-page")
    
    # Build delete parameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations_identifiers=[],
        unpublish=True
    )
    
    cascade.operations.delete(identifier, payload=payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

`delete` and other mutating operations like `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation only rather than the modified asset, so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase(url="...", username="...", password="...") as cascade:
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
        # Iterate over the flat list of matched elements
        for item in result.flat:
            print(item)
```

`search` requires a typed payload object without a bare identifier shortcut, following the same pattern used by operations like `readAudits` with `auditParameters` and `editWorkflowSettings`.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase(url="...", username="...", password="...") as cascade:
    # Queue three independent chains in a single block
    path_id = Path(asset_type="page", siteName="Default", path="/index")
    cascade.operations.read(path_id)
    
    del_path = Path(asset_type="page", siteName="Default", path="/old-page")
    cascade.operations.delete(del_path)
    
    search_payload = SearchInformation(siteName="Default", searchTerms="test")
    cascade.operations.search(search_payload)
    
    # All three chains run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.6 -->
