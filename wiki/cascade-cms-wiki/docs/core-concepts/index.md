# Core Concepts

This guide builds upon the quick-start by walking through the library's core mental model: initializing a `Cascade` context manager, building fluent operations, chaining sequential work, and executing batches via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. A chain stops at the first failure without affecting any other chain, pairing results and errors directly to the step that produced them.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for an asset
    cascade.operations.read(identifier)
    # Execute the registered chain and return results
    results = cascade.submit_requests()
    # inspect the result directly
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
```

### Expected Output

```python
# Returns a ChainResults object containing the successfully read Asset instance
[Asset(_asset_type='page', _data={'name': 'index', 'id': '...'})]
```

---

## Payload Models

Payload models are typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type safety, editor autocompletion, and guaranteed data shape serialization.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct a typed search payload
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
)

# Pass the typed payload to the search operation
cascade.operations.search(payload)
results = cascade.submit_requests()
```

These models enforce required arguments and handle field aliasing (such as `siteName` and `searchTerms`) automatically, preventing runtime serialization errors that raw dictionaries would introduce. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

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
