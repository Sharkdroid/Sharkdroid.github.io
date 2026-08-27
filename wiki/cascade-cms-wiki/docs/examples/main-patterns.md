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
with CascadeWrapperBase("config.json") as cascade:
    # Build a Path identifier referencing a page in a site
    path = Path(asset_type="page", path="/index", siteName="Default")
    
    # Queue a read operation
    cascade.operations.read(path)
    
    # Execute the request queue concurrently
    result = cascade.submit_requests()
    
    # Check for API-level failures
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
with CascadeWrapperBase("config.json") as cascade:
    path = Path(asset_type="page", path="/old-page", siteName="Default")
    
    # Build delete parameters
    params = deleteParameters(
        doWorkflow=False,
        destinations_identifiers=[],
        unpublish=True
    )
    
    # Queue a delete operation
    cascade.operations.delete(path, payload=params)
    
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset successfully deleted.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Build the required SearchInformation payload
    search_info = SearchInformation(
        siteName="Default",
        searchTerms="blog",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue a search operation
    cascade.operations.search(search_info)
    
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of elements returned
        for item in result.flat:
            print(item)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and other operations that follow the same pattern include `readAudits` (taking `auditParameters`), `editWorkflowSettings`, and others.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("config.json") as cascade:
    # Queue three independent operation chains
    cascade.operations.read(Path(asset_type="page", path="/index", siteName="Default"))
    cascade.operations.delete(Path(asset_type="page", path="/old-page", siteName="Default"))
    cascade.operations.search(SearchInformation(siteName="Default", searchTerms="test"))
    
    # Run all queued chains concurrently and return their results in order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.1 -->
