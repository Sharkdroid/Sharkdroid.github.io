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
    # 1. Define a Path identifier for the asset
    identifier = Path(asset_type="page", path="/index", site_name="default")
    
    # 2. Queue the read operation
    cascade.operations.read(identifier)
    
    # 3. Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]

    # 4. Handle failures before interacting with the asset object
    if isinstance(result, CascadeError):
        print(f"Failed to read asset: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` operation serves as the primary template for fetching existing assets and metadata from Cascade. Other methods like `readAudits`, `readAccessRights`, and `readWorkflowSettings` follow this exact pattern, returning structured objects specific to the requested endpoint.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Define the asset path and parameters for the deletion
    identifier = Path(asset_type="page", path="/old-page", site_name="default")
    payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    
    # 2. Queue the delete operation
    cascade.operations.delete(identifier, payload=payload)
    
    # 3. Execute the request
    results = cascade.submit_requests()
    result = results[0]

    # 4. Check for errors
    if isinstance(result, CascadeError):
        print(f"Deletion failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Mutating operations such as `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a confirmation status rather than the full asset object. Callers should inspect the success indicator or handle the resulting error object without expecting modified asset fields to be returned.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Construct the required SearchInformation payload
    payload = SearchInformation(siteName="default", searchTerms="blog")
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Execute and retrieve results
    results = cascade.submit_requests()
    result = results[0]

    # 4. Handle errors or iterate over elements
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        for item in result.flat:
            print(item)
```

Searching and audit logging operations mandate explicit payload configurations instead of bare identifier shortcuts. Methods like `readAudits` and `search` rely on dedicated parameter models to structure query criteria prior to execution.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Queue multiple independent operations in a single batch
    cascade.operations.read(Path(asset_type="page", path="/index", site_name="default"))
    cascade.operations.delete(Path(asset_type="page", path="/old-page", site_name="default"), payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="default", searchTerms="news"))
    
    # All three run concurrently, returning results in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
