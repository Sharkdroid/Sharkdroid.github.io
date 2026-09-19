# Core Concepts

This section covers the library's core mental model—how `CascadeWrapperBase`, the `Operations` builder, `OperationChain`, and `submit_requests()` fit together to manage API communication. Building on the quick-start guide, you will learn how requests are structured, chained, and executed concurrently.

---

## Basic Operation Calls

Every script follows the same structural pattern: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, and then call `submit_requests()` once to execute all chains concurrently. This design keeps your code clean and allows multiple independent API operations to run as a single optimized batch.

### Example

```python
# Open the Cascade wrapper as a context manager
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for an asset
    cascade.operations.read(identifier)
    # Submit all queued requests and retrieve the results list
    results = cascade.submit_requests()
    
    for result in results:
        # Check if the operation resulted in a CascadeError
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Successfully read asset: {result}")
```

### Expected Output

```python
# Returns an Asset object wrapping the raw Cascade JSON response for the requested asset:
# Asset(_asset_type='page', _data={'id': '...', 'name': 'index', ...})
```

---

## Payload Models

Payload models are typed objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide full type-safety, validation, and auto-completion benefits while abstracting away the raw JSON structure required by Cascade.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload with required criteria
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name", "displayName"],
    searchTypes=["page"]
)

# Pass the payload directly to the search operation builder
cascade.operations.search(payload)
results = cascade.submit_requests()
```

Payload models enforce the exact schema required by each REST endpoint. Passing a raw dictionary will fail validation; using typed payloads (`deleteParameters`, `auditParameters`, `SearchInformation`, etc.) guarantees your request parameters are correctly formatted and serialized.

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

<!-- synthesized-for: 3.1.6 -->
