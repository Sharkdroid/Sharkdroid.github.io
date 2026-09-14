# Core Concepts

This section establishes the core mental model of the library: a context-managed wrapper (`CascadeWrapperBase`) that exposes an operations builder (`Operations`), which in turn spawns individual operation chains (`OperationChain`) to be executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Operations run strictly in order, receiving the previous node's result, and each chain stops at its first failure. Results line up with the chains in the order they were created.

### Example

```python
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Start a chain reading an asset by identifier
    cascade.operations.read(identifier)
    
    # Submit all registered chains concurrently
    results = cascade.submit_requests()
    
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
[
    Asset(_asset_type='page', _data={'id': '...', 'name': 'index', ...})
]
```

---

## Payload Models

Payload models are typed Pydantic objects (`SimplePayload` subclasses) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide type safety and IDE autocompletion, validating parameters before any network request is ever dispatched.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search criteria with site name, search terms, and filters
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)

with CascadeWrapperBase(env_vars, config_vars) as cascade:
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce required and optional argument structures, ensuring that payload dictionaries are properly formatted and aliased before hitting the Cascade REST API. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `copyParameters`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, config_vars) as cascade:
        cascade.operations.read(identifier).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.5 -->
