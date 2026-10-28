# Core Concepts

This page details the library's mental model, building on the quick-start guide by explaining how the `Cascade` wrapper, fluent `Operations` builder, `OperationChain` nodes, and `submit_requests()` work together.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, and then call `submit_requests()` once to execute all chains concurrently. Individual chains run strictly in order, while multiple chains execute in parallel across the driver's shared session.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for an asset
    chain = cascade.operations.read(identifier)
    # Execute all queued operations concurrently
    results = cascade.submit_requests()
    # Check the result of the first chain
    result = results[0]
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
```

### Expected Output

```python
Asset(_asset_type='page', _data={...})
```

---

## Payload Models

Payload models are typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the expected fields and types. They provide type safety and IDE autocompletion, preventing malformed requests from reaching the CMS.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)
cascade.operations.search(payload)
```

These models enforce the required fields and aliases that the Cascade API expects. Passing a raw dictionary instead of the typed model would fail validation; other operations follow the same pattern using models like `deleteParameters`, `auditParameters`, and `copyParameters`.

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
