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
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    # Build a Path identifier pointing to a page asset
    identifier = Path(asset_type=AssetTypes.PAGE, path="/index", site_name="default-site")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Submit requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # Check if the operation resulted in an error
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset properties
        print(result.displayName)
        print(result.metadata)
```

`read` represents the core response pattern used by asset-fetching endpoints across the library, such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these endpoints returns a specialized, structured object corresponding directly to the entity requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    identifier = Path(asset_type=AssetTypes.PAGE, path="/old-page", site_name="default-site")
    
    # Construct delete parameters payload
    payload = deleteParameters(
        do_workflow=False,
        destinations_identifiers=[],
        unpublish=True
    )
    
    # Queue the delete operation with the identifier and payload
    cascade.operations.delete(identifier, payload=payload)
    
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Deletion failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a minimal success confirmation rather than the modified asset itself. Because these endpoints omit the updated asset data, scripts should not attempt to read back asset properties directly from the result of a mutation.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    # Construct the SearchInformation payload
    payload = SearchInformation(
        site_name="default-site",
        search_terms="about",
        search_fields=[FieldsSearchTypes.NAME],
        search_types=[AssetTypes.PAGE]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of matched elements
        for element in result.flat:
            print(element)
```

The `search` operation requires a structured payload object rather than a bare identifier shortcut. Other endpoints in the library follow this exact payload-driven model, including `readAudits` (which takes `auditParameters`), `editWorkflowSettings`, and others.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    path_id = Path(asset_type=AssetTypes.PAGE, path="/index", site_name="default-site")
    del_id = Path(asset_type=AssetTypes.PAGE, path="/old-page", site_name="default-site")
    del_payload = deleteParameters(do_workflow=False, destinations_identifiers=[], unpublish=True)
    search_payload = SearchInformation(site_name="default-site", search_terms="about")

    # Queue multiple independent chains of different operation types
    cascade.operations.read(path_id)
    cascade.operations.delete(del_id, payload=del_payload)
    cascade.operations.search(search_payload)

    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
