# Core Concepts

This page bridges the quick-start guide by detailing the core mental model of `cascade-cms`: everything flows through a `CascadeWrapperBase` wrapper instance that exposes an `Operations` builder, which constructs independent `OperationChain` pipelines executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Failures are captured as values rather than raised exceptions, allowing clean error checks per result.

### Example

```python
from cascade_cms import CascadeWrapperBase, CascadeError

env_vars = {"SERVER": "dev", "API_KEY": "token", "CASCADE_URL": "https://cascade.example.com"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Queue a read operation on an asset identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently
    results = cascade.submit_requests()
    
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Asset read successfully: {result.internal_type}")
```

### Expected Output

```python
# Returns a list containing the parsed Asset wrapper for the requested identifier
[Asset(_asset_type='page', _data={...})]
```

---

## Payload Models

Payload models are typed Pydantic objects (`SimplePayload` subclasses) that pair with specific operations to ensure the API endpoint receives the exact structure Cascade expects. They provide autocomplete, type validation, and automatic serialization (such as aliasing pythonic snake_case fields to camelCase).

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload with required criteria
payload = SearchInformation(
    siteName="Default",
    searchTerms="index",
    searchFields=["name"],
    searchTypes=["page"]
)

# Pass the typed payload to the search operation
cascade.operations.search(payload)
results = cascade.submit_requests()
```

Payload models enforce strict schema validation at runtime before any HTTP request leaves the client, preventing malformed requests to the API. Other operations follow this exact pattern using models like `deleteParameters`, `auditParameters`, and `copyParameters`.

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
