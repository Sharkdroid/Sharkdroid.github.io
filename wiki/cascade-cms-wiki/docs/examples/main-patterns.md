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
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Build a Path identifier pointing to the page asset
    identifier = Path(path="about-us", site_name="Default", asset_type="page")
    
    # Queue a read operation and submit the batch
    cascade.operations.read(identifier)
    results = cascade.submit_requests()
    result = results[0]

    # Guard against API-level failures
    if isinstance(result, CascadeError):
        print(f"Failed: {result.message}")
    else:
        # Access structured asset data
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    identifier = Path(path="old-page", site_name="Default", asset_type="page")
    
    # Construct delete parameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    cascade.operations.delete(identifier, payload=payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Successfully deleted asset.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Construct the required search payload
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
        # Iterate over the flat list of matched elements
        for element in result.flat:
            print(element.get_id, element.get_path)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and naming the other operations that follow the same pattern: `readAudits` (`auditParameters`), `editWorkflowSettings`, etc.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Queue three independent chains
    cascade.operations.read(Path(path="home", site_name="Default", asset_type="page"))
    cascade.operations.delete(Path(path="temp-file", site_name="Default", asset_type="file"))
    cascade.operations.search(SearchInformation(siteName="Default", searchTerms="report"))

    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
