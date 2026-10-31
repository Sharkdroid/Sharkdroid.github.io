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
    # Build a Path identifier pointing to a page asset
    identifier = Path(path="index", asset_type=AssetTypes.PAGE, site_name="Default")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Submit requests concurrently and retrieve results
    results = cascade.submit_requests()
    result = results[0]
    
    # Check for API-level failures before accessing asset properties
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other fetch operations follow—such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object tailored to the specific type of resource requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    identifier = Path(path="old-page", asset_type=AssetTypes.PAGE, site_name="Default")
    
    # Construct deleteParameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # Queue the delete operation
    cascade.operations.delete(identifier, payload=payload)
    
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Operations like `delete` and other mutating actions (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation responses rather than the modified asset data itself. Callers should not expect updated asset objects to be returned from these execution paths.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Construct SearchInformation payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog",
        searchFields=[FieldsSearchTypes.NAME],
        searchTypes=[AssetTypes.PAGE]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of matching elements
        for element in result.flat:
            print(element.get_id, element.get_type)
```

The `search` operation requires a typed payload object with no bare identifier shortcuts. Other operations such as `readAudits` (which uses `auditParameters`), `editWorkflowSettings`, and similar commands follow this exact payload-driven pattern.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    path_id = Path(path="index", asset_type=AssetTypes.PAGE, site_name="Default")
    delete_id = Path(path="old-page", asset_type=AssetTypes.PAGE, site_name="Default")
    del_payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="Default", searchTerms="blog")

    # Queue three independent chains; all run concurrently on submit_requests()
    cascade.operations.read(path_id)
    cascade.operations.delete(delete_id, payload=del_payload)
    cascade.operations.search(search_payload)

    # Results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
