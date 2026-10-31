# Core Concepts

This page breaks down the library’s mental model: everything flows from the context-manager wrapper down to fluent operations, sequential chains, and concurrent execution.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for the asset
    cascade.operations.read(identifier)
    # Execute the queued batch of chains concurrently
    results = cascade.submit_requests()
    # Check if the result is an API-level failure
    if isinstance(results[0], CascadeError):
        print(f"Failed: {results[0].message}")
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={
        'id': '1234567890abcdef1234567890abcdef',
        'name': 'index',
        'path': '/index',
        'displayName': 'Home Page'
    }
)
```

---

## Payload Models

Payload models are typed objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type safety, clear autocomplete support, and correct serialization formats without requiring manual dictionary construction.

### Example: `SearchInformation` paired with `search`

```python
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)
cascade.operations.search(payload)
```

The `SearchInformation` model enforces that `siteName`, `searchTerms`, `searchFields`, and `searchTypes` are correctly typed and structured before any network request is attempted. Passing a raw dictionary instead of the model fails validation, and all other write/query operations follow this exact typed pattern (`deleteParameters`, `auditParameters`, `copyParameters`, etc.).

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with Cascade(env_vars) as cascade:
        cascade.operations.read(identifier).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: debug logging and CPU-intensive workload patterns.

<!-- synthesized-for: 3.9.2 -->
