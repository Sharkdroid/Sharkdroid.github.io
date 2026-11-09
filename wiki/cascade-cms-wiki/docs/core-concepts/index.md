# Core Concepts

This page breaks down the library's core mental model: wrapping your session with `Cascade`, queueing operations through `Operations`, building sequential workflows via `OperationChain`, and executing them concurrently with `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for an asset
    chain = cascade.operations.read(identifier)
    
    # Submit all queued operations in a batch
    results = cascade.submit_requests()
    
    # Check the result
    result = results[0]
    if isinstance(result, CascadeError):
        print(f"Operation failed: {result.message}")
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={
        'id': '1234567890abcdef1234567890abcdef',
        'name': 'index',
        'path': '/index',
        'siteName': 'default',
        'displayName': 'Home Page',
        ...
    }
)
```

---

## Payload Models

Payload models are typed objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide type-safety, validation, and clarity by structuring inputs correctly before they reach the REST driver.

### Example: `SearchInformation` paired with `search`

```python
payload = SearchInformation(
    siteName="default",
    searchTerms="blog",
    searchFields=["name", "summary"],
    searchTypes=["page", "file"]
)
cascade.operations.search(payload)
```

These models enforce required attributes and validation rules via Pydantic before requests are dispatched. Passing raw dictionaries is generally not supported for complex operations, and this pattern is shared across all parameter models like `deleteParameters`, `auditParameters`, and `copyParameters`.

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
