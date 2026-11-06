# Core Concepts

Building on the quick-start guide, this section details the library's core mental model: a `Cascade` context manager owns the session and error lifecycle, `cascade.operations` starts fluent builders, `OperationChain` sequences work per asset, and `submit_requests()` executes everything concurrently.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Three to four sentences are all it takes to wire up a complete session.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for an asset identifier
    cascade.operations.read(identifier)
    
    # Execute the queued batch concurrently and capture results
    results = cascade.submit_requests()
    
    # Inspect the result, handling potential API errors
    result = results[0]
    if isinstance(result, CascadeError):
        print(f"API Error: {result.message}")
```

### Expected Output

```python
# Returns an Asset instance wrapping the raw JSON payload
Asset(_asset_type='page', _data={'id': '...', 'name': 'index', ...})
```

---

## Payload Models

Payload models are typed objects (e.g. `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide type-safety, validation, and auto-aliasing for JSON serialization without requiring manual dictionary construction.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)

cascade.operations.search(payload)
```

The model enforces that required parameters are correctly typed and structured before any network requests are dispatched, ensuring malformed payloads are caught locally. Other write and query operations follow this exact pattern using models like `deleteParameters`, `auditParameters`, and `Comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with Cascade(env_vars) as cascade:
        cascade.operations.read(id).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: debug logging and CPU-intensive workload patterns.

<!-- synthesized-for: 3.9.2 -->
