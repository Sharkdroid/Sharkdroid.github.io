# Core Concepts

This page bridges the quick-start guide by examining the library's core mental model: a top-level `Cascade` wrapper orchestrating fluent `Operations` builders, which spawn single-asset `OperationChain` singly-linked lists executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Each chain stops at the first failure, pairing results precisely with the operation that produced them.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for the given identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently and get results
    results = cascade.submit_requests()
    
    # Check the result of the first chain
    result = results[0]
    if isinstance(result, CascadeError):
        print(f"Operation failed: {result.message}")
```

### Expected Output

```python
# Returns a ResponseParser holding an Asset wrapper or a CascadeError
ResponseParser(_content=Asset(...))
```

---

## Payload Models

Payload models are strongly typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the exact structure it expects. They eliminate guesswork and provide IDE auto-completion while validating parameters before any network requests are sent.

### Example: `SearchInformation` paired with `search`

```python
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=[FieldsSearchTypes.NAME],
    searchTypes=[AssetTypes.PAGE]
)
cascade.operations.search(payload)
```

The `SearchInformation` model enforces valid parameters for site name, search terms, and search fields. Similar dedicated payloads exist across the SDK, such as `deleteParameters`, `auditParameters`, and `copyParameters`.

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

<!-- synthesized-for: 3.9.1 -->
