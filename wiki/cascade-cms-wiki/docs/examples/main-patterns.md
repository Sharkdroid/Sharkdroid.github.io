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
    identifier = Path(asset_type=AssetTypes.PAGE, path="index", site_name="default")
    
    # 2. Queue the read operation
    cascade.operations.read(identifier)
    
    # 3. Execute all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]

    # 4. Check for API-level failures before using the result
    if isinstance(result, CascadeError):
        print(f"Failed to read asset: {result.message}")
    else:
        # Access structured asset data
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other "fetch" operations follow—such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to what was requested, allowing you to inspect detailed properties directly from the returned response.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Define a Path identifier for the asset to delete
    identifier = Path(asset_type=AssetTypes.PAGE, path="old-page", site_name="default")
    
    # 2. Construct delete parameters payload
    payload = deleteParameters(
        do_workflow=False,
        destinations_identifiers=[],
        unpublish=True
    )
    
    # 3. Queue the delete operation with parameters
    cascade.operations.delete(identifier, payload=payload)
    
    # 4. Execute requests and check the response
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded!")
```

The `delete` operation and other mutating actions like `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a confirmation status only rather than the modified asset data. Consequently, scripts should not expect asset attributes or body content back when invoking these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Construct the SearchInformation payload
    payload = SearchInformation(
        siteName="default",
        searchTerms="blog",
        searchFields=[FieldsSearchTypes.NAME],
        searchTypes=[AssetTypes.PAGE]
    )
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Execute the search request
    results = cascade.submit_requests()
    result = results[0]

    # 4. Handle errors and iterate over list elements via .flat
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        for element in result.flat:
            print(element.get_id, element.get_type)
```

The `search` operation requires a strongly-typed payload object rather than a bare identifier shortcut. Other library operations follow this exact payload-driven pattern, including `readAudits` (which uses `auditParameters`), `editWorkflowSettings`, and others.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Queue a read chain, a delete chain, and a search chain simultaneously
    read_id = Path(asset_type=AssetTypes.PAGE, path="about", site_name="default")
    delete_id = Path(asset_type=AssetTypes.PAGE, path="temp-page", site_name="default")
    search_payload = SearchInformation(siteName="default", searchTerms="news")

    cascade.operations.read(read_id)
    cascade.operations.delete(delete_id)
    cascade.operations.search(search_payload)

    # Run all three independent chains concurrently; results match creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
