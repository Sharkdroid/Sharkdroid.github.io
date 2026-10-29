# Core Concepts

Building on the quick-start guide, this page explores the library's mental model: managing connections via the context wrapper, building queues with the operations builder, chaining steps into independent execution units, and dispatching batches concurrently.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. The operations builder returns independent `OperationChain` instances that run strictly in order, while `submit_requests()` handles concurrent execution across the driver's shared session.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for an asset
    cascade.operations.read(identifier)
    
    # Submit all queued operations as a batch
    results = cascade.submit_requests()
    
    # Check if the result is an API-level error response
    if isinstance(results[0], CascadeError):
        print(results[0].message)
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={'id': UUID('...'), 'name': 'index', 'path': '/index', ...}
)
```

---

## Payload Models

Payload models are typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the expected fields and correct data types. They provide compile-time type safety and runtime validation, eliminating guesswork when constructing complex request bodies.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload with required fields
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)

# Pass the payload to the search operation
cascade.operations.search(payload)
```

Payload models enforce strict schema validation, ensuring that missing or misnamed attributes raise errors before requests hit the wire, unlike raw dictionaries which would fail silently on the server. Other operations follow the same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

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
