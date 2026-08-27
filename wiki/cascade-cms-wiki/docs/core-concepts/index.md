# Core Concepts

This guide builds on the quick-start by walking through the library's core mental model: a single-script session is managed by a wrapper, which exposes an operations builder that queues up independent operation chains, executed concurrently when submitted.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. These operations are non-blocking until submitted, and each chain maintains its own sequential execution order. Failures are captured individually per chain rather than crashing the batch.

### Example

```python
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for an asset
    cascade.operations.read(identifier)
    
    # Submit the request and retrieve results
    results = cascade.submit_requests()
    
    # Check for API-level errors
    if isinstance(results[0], CascadeError):
        print(f"Error: {results[0].message}")
```

### Expected Output

```python
# Returns an Asset wrapper containing the resource data
Asset(asset={'page': {'id': '12345678...', 'name': 'index', ...}})
```

---

## Payload Models

Payload models are structured Pydantic objects subclassing `SimplePayload` (e.g. `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide strict type-safety, handle field aliasing, and wrap requests in the exact dictionary structure Cascade expects.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="Default",
    searchTerms="test",
    searchFields=["name"],
    searchTypes=["page"]
)

cascade.operations.search(payload)
results = cascade.submit_requests()
```

These models enforce required arguments and ensure schema validation before any request leaves the client, preventing silent API rejections. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `Comment`.

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
