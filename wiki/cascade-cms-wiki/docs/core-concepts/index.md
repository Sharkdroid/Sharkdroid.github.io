# Core Concepts

Building on the quick-start guide, this page explores the library's core mental model: a single context manager (`CascadeWrapperBase`) manages the lifecycle of your session, exposing an `Operations` builder that queues up independent or batched operation chains, which are then dispatched concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Individual chains stop at the first failure without affecting others, and results are returned as values rather than raised exceptions.

### Example

```python
# Open the Cascade wrapper session
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Start a read operation chain for the identifier
    cascade.operations.read(identifier)
    # Execute the queued chains concurrently and fetch results
    results = cascade.submit_requests()
    
    for result in results:
        # Check if the operation resulted in a CascadeError
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
Asset(asset_type='page', _data={'id': '...', 'name': 'index', 'path': '/index', 'siteName': 'default'})
```

---

## Payload Models

Payload models are typed objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type safety and runtime validation, preventing malformed requests before they ever touch the network.

### Example: `SearchInformation` paired with `search`

```python
# Construct search parameters using the typed model
payload = SearchInformation(
    siteName="default",
    searchTerms="about",
    searchFields=[FieldsSearchTypes.name],
    searchTypes=[AssetTypes.page]
)

# Pass the payload to the search operation builder
cascade.operations.search(payload)
results = cascade.submit_requests()
```

The `SearchInformation` model enforces that `siteName`, `searchTerms`, and optional filter fields are correctly typed and structured before sending. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, config_vars) as cascade:
        cascade.operations.read(id).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.1 -->
