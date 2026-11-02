# Core Concepts

Building on the quick-start guide, this page explores the library's underlying mental model: the top-level wrapper (`Cascade`) coordinates operations and chains, executing them concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design keeps network round-trips batched and predictable while letting you compose custom transformation logic right on top of API responses.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation on an asset
    cascade.operations.read(identifier)
    # Submit all queued operations in a single concurrent batch
    results = cascade.submit_requests()
    
    for result in results:
        # Check if a specific chain returned an API error
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={'id': '12345678123456781234567812345678', 'name': 'index', 'path': '/index'}
)
```

---

## Payload Models

Payload models are typed objects (inheriting from `SimplePayload`) that pair with specific write or query operations to ensure the API endpoint receives the exact structure it expects. They provide type safety and auto-serialization, replacing error-prone raw dictionaries with validated classes.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)

with Cascade(env_vars) as cascade:
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

The `SearchInformation` model enforces required endpoint fields like `siteName` and `searchTerms` with proper serialization aliases (`siteName`, `searchTerms`, `searchFields`, `searchTypes`), ensuring that raw dictionary structure mismatches are caught before a request ever hits Cascade. Other operations follow this exact typed pattern, using classes like `deleteParameters`, `auditParameters`, `copyParameters`, and `moveParameters`.

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
