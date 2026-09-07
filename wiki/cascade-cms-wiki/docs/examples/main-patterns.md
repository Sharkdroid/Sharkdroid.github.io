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
    # 1. Define a Path identifier for the asset
    identifier = Path(asset_type="page", path="index", siteName="default")
    
    # 2. Queue the read operation
    cascade.operations.read(identifier)
    
    # 3. Submit requests concurrently and grab the first result
    results = cascade.submit_requests()
    result = results[0]
    
    # 4. Check for API errors before accessing asset fields
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    # 1. Define the Path identifier and deleteParameters payload
    identifier = Path(asset_type="page", path="old-page", siteName="default")
    payload = deleteParameters(doWorkflow=False, destinations_identifiers=[], unpublish=True)
    
    # 2. Queue the delete operation
    cascade.operations.delete(identifier, payload=payload)
    
    # 3. Submit and evaluate the result
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset successfully deleted.")
```

The `delete` operation and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    # 1. Construct the required SearchInformation payload
    payload = SearchInformation(siteName="default", searchTerms="report")
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Submit and check for errors
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        for element in result.flat:
            print(element)
```

The `search` operation requires a typed payload object — there is no bare identifier shortcut — and the other operations that follow the same pattern include `readAudits` (`auditParameters`), `editWorkflowSettings`, etc.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default") as cascade:
    # Queue three independent chains in a single wrapper block
    cascade.operations.read(Path(asset_type="page", path="index", siteName="default"))
    cascade.operations.delete(Path(asset_type="page", path="old-page", siteName="default"), payload=deleteParameters(doWorkflow=False, destinations_identifiers=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="default", searchTerms="report"))
    
    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.3 -->
