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
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    # 1. Build a Path identifier specifying the asset type and site-relative path
    identifier = Path(asset_type=AssetTypes.PAGE, path="/index", site_name="default")
    
    # 2. Queue the read operation
    cascade.operations.read(identifier)
    
    # 3. Submit all queued operations concurrently
    result = cascade.submit_requests()
    
    # 4. Check for failure before using the result
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset fields
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    identifier = Path(asset_type=AssetTypes.PAGE, path="/old-page", site_name="default")
    
    # Provide deleteParameters payload for the delete operation
    payload = deleteParameters(
        do_workflow=False,
        destinations=[],
        unpublish=True
    )
    
    cascade.operations.delete(identifier, payload=payload)
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset deleted successfully.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    # Construct a SearchInformation payload specifying site and search terms
    payload = SearchInformation(
        siteName="default",
        searchTerms="blog",
        searchFields=[FieldsSearchTypes.NAME],
        searchTypes=[AssetTypes.PAGE]
    )
    
    cascade.operations.search(payload)
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of elements returned in the search results
        for item in result.flat:
            print(item.get_id, item.get_type)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and names the other operations that follow the same pattern: `readAudits` (`auditParameters`), `editWorkflowSettings`, etc.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    path_id = Path(asset_type=AssetTypes.PAGE, path="/index", site_name="default")
    delete_path = Path(asset_type=AssetTypes.PAGE, path="/old-page", site_name="default")
    del_params = deleteParameters(do_workflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="default", searchTerms="blog")

    # Queue multiple independent chains
    cascade.operations.read(path_id)
    cascade.operations.delete(delete_path, payload=del_params)
    cascade.operations.search(search_payload)

    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
    for res in results:
        if isinstance(res, CascadeError):
            print(f"Chain failed: {res.message}")
        else:
            print(f"Success result: {res}")
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
