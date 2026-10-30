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
    # Build a Path identifier pointing to a page asset
    identifier = Path(asset_type=AssetTypes.PAGE, site_name="default", path="/index")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Execute all queued operations concurrently
    result = cascade.submit_requests()[0]

    # Always check if the result is a CascadeError before using it
    if isinstance(result, CascadeError):
        print(f"Failed to read asset: {result.message}")
    else:
        # Access structured properties on the returned Asset object
        print(result.displayName)
        print(result.metadata)
```

`read` represents the core fetch pattern used by the library. Other methods like `readAudits`, `readAccessRights`, and `readWorkflowSettings` follow this same convention, returning structured domain objects specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    identifier = Path(asset_type=AssetTypes.PAGE, site_name="default", path="/old-page")
    
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    cascade.operations.delete(identifier, payload=payload)
    result = cascade.submit_requests()[0]

    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a simple success indicator rather than the updated asset data. Callers should not expect asset attributes back from these actions.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    payload = SearchInformation(
        siteName="default",
        searchTerms="news",
        searchFields=[FieldsSearchTypes.NAME],
        searchTypes=[AssetTypes.PAGE]
    )
    
    cascade.operations.search(payload)
    result = cascade.submit_requests()[0]

    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of matching elements
        for item in result.flat:
            print(item)
```

`search` requires a structured payload object rather than a simple identifier. Operations like `readAudits` and `editWorkflowSettings` adopt this same pattern, requiring explicit parameters to filter or describe the request.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Queue multiple independent chains
    cascade.operations.read(Path(asset_type=AssetTypes.PAGE, site_name="default", path="/index"))
    cascade.operations.delete(Path(asset_type=AssetTypes.PAGE, site_name="default", path="/old-page"), payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="default", searchTerms="report"))
    
    # Run them all concurrently; results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
