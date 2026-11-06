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
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Build a Path identifier referencing a page in the site
    identifier = Path(asset_type="page", siteName="Default", path="/index")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Execute the request(s)
    results = cascade.submit_requests()
    result = results[0]
    
    # Failures are returned as values, not raised
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset data
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to what was requested, wrapping the server response into a typed Pydantic model or dynamic asset wrapper.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    identifier = Path(asset_type="page", siteName="Default", path="/old-page")
    
    # Construct delete parameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
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

The `delete` operation along with other mutating operations like `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a confirmation status rather than the modified asset itself. Callers should expect a `CascadeSuccess` object indicating success or a `CascadeError` on failure, so you should never expect asset data back from these methods.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Construct the required search information payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
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

The `search` operation requires a typed payload object (`SearchInformation`) rather than a bare identifier shortcut. Other operations like `readAudits` (which uses `auditParameters`), `editWorkflowSettings`, and `siteCopy` follow this same payload-driven pattern to supply criteria to the server.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    identifier = Path(asset_type="page", siteName="Default", path="/index")
    delete_payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="Default", searchTerms="report")

    # Queue three independent chains in a single wrapper block
    cascade.operations.read(identifier)
    cascade.operations.delete(identifier, payload=delete_payload)
    cascade.operations.search(search_payload)

    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
