# Core Concepts

This page explains the library's core architecture and mental model: how the `CascadeWrapperBase` context manager coordinates with `Operations`, `OperationChain`, and `submit_requests()` to manage API interactions.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design decouples request building from execution, letting you queue multiple independent or batched operations before firing them across the network in parallel.

### Example

```python
# Open the wrapper context manager
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Start a chain and queue a read operation
    cascade.operations.read(identifier)
    # Execute the queued chain and retrieve results
    results = cascade.submit_requests(Asset)
    
    for result in results:
        # Check for API-level failures
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(result)
```

### Expected Output

```python
Asset(_asset_type='page', _data={...}, _page_configs=[...])
```

---

## Payload Models

Payload models are typed Pydantic objects (inheriting from `SimplePayload`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type-safety and IDE autocompletion for complex request structures.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="Default",
    searchTerms="news",
    searchFields=["name", "title"],
    searchTypes=["page"]
)

cascade.operations.search(payload)
```

These models enforce required and optional fields at runtime, preventing malformed payloads from reaching the Cascade API. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

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
