# Core Concepts

Building on the quick-start guide, this page explores the library's mental model: the top-level `Cascade` wrapper acts as a context manager coordinating the REST driver and logger, while `cascade.operations` starts fluent builder chains of requests and callbacks that execute concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. These operations form a singly linked list via `next` where each node carries its prepared requests or wraps a result-processing function. The chain stops at the first failure so results and errors map directly to their exact step.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation on the operations builder
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently and get results
    results = cascade.submit_requests(Asset)
    
    # Each entry in results corresponds to a queued chain
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
Asset(_asset_type='page', _data={'id': '1234567890abcdef...', 'name': 'index', ...})
```

---

## Payload Models

Payload models are typed objects (subclasses of `SimplePayload`) that pair with specific operations to ensure the API endpoint receives the expected fields and headers. They provide type safety and structural clarity by wrapping raw data structures in validated Pydantic models before serialization.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the payload model specifying search criteria
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name", "summary"],
    searchTypes=["page"]
)

with Cascade(env_vars) as cascade:
    # Pass the payload model directly to the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

The model enforces required fields and formatting at runtime, preventing invalid requests from hitting the REST API. Other operations follow the exact same typed parameter pattern, such as `deleteParameters`, `auditParameters`, and `copyParameters`.

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
