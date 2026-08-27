# Core Concepts

This page bridges the quick-start guide by walking through the library's core mental model: a wrapper context manager that orchestrates a REST driver and operations builder, collecting fluent operation chains into a batch that runs concurrently upon submission.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Each chain runs strictly in order, stopping at the first failure so results and errors are cleanly preserved.

### Example

```python
# Open the wrapper context manager
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation on the operations builder
    cascade.operations.read(identifier)
    
    # Execute the registered chain(s) and capture results
    results = cascade.submit_requests()
    
    # Guard against API failures returned as values
    if isinstance(results[0], CascadeError):
        print(f"Failed: {results[0].message}")
```

### Expected Output

```python
# Returns a ResponseParser wrapping an Asset object
Asset(
    asset_type='page',
    _data={'id': '...', 'name': 'index', 'path': 'index', 'siteName': 'default'}
)
```

---

## Payload Models

Payload models are typed objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type-safety and structural clarity, ensuring all required properties are present before a request is ever dispatched to Cascade.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the payload with search criteria
payload = SearchInformation(
    siteName="default",
    searchTerms="blog",
    searchFields=["name", "metadata"],
    searchTypes=["page"]
)

# Pass the payload to the search operation
cascade.operations.search(payload)
```

The payload model ensures that fields like `siteName`, `searchTerms`, `searchFields`, and `searchTypes` conform to the strict schema expected by Cascade's REST API. Passing a raw dict would bypass this validation; other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `Comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
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
