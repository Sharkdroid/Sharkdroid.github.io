# Core Concepts

This page bridges the quick-start guide by detailing the library's core mental model: a central wrapper (`CascadeWrapperBase`) manages state and connections, exposes an operations builder (`Operations`), which in turn spawns individual execution chains (`OperationChain`) that run concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Results line up with the chains in the order they were created, returning values or errors directly so failures flow downstream unless explicitly guarded.

### Example

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError

env = {"SERVER": "production", "API_KEY": "token", "CASCADE_URL": "http://cms.example.com"}

with CascadeWrapperBase(env, {}) as cascade:
    # Start a chain reading an asset by identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently
    results = cascade.submit_requests()
    
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(result)
```

### Expected Output

```python
Asset(id='1234567890abcdef...', type='page', ...)
```

---

## Payload Models

Payload models are typed objects (like `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type safety and clear documentation for complex operation parameters without relying on raw dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation

env = {"SERVER": "production", "API_KEY": "token", "CASCADE_URL": "http://cms.example.com"}

with CascadeWrapperBase(env, {}) as cascade:
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce required keys and aliases automatically before any request is dispatched, ensuring invalid parameters are caught early. Other operations follow the exact same validation pattern using models like `deleteParameters`, `auditParameters`, and `Comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import CascadeWrapperBase

env = {"SERVER": "production", "API_KEY": "token", "CASCADE_URL": "http://cms.example.com"}

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env, {}) as cascade:
        cascade.operations.read(id).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.3 -->
