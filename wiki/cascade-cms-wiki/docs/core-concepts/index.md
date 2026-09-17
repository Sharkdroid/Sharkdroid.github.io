# Core Concepts

Building on the quick-start guide, this page explores the core mental model of the library: entering the wrapper, building operations, chaining callbacks, and submitting everything as a batch.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Results line up with the chains in the order they were created, returning values or errors directly without raising exceptions. This guarantees that API errors or callback failures are caught and handled gracefully per chain.

### Example

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError

env_vars = {"SERVER": "production", "API_KEY": "secret-token", "CASCADE_URL": "https://cascade.example.com"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Queue a read operation for an asset
    cascade.operations.read(identifier)
    
    # Execute all queued requests and retrieve the result list
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(f"Asset name: {result.get('name')}")
```

### Expected Output

```python
Asset
```

---

## Payload Models

Payload models are typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide type-safety, handle field aliasing (such as mapping Python snake_case to Cascade camelCase), and validate required parameters before any request hits the server.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation

env_vars = {"SERVER": "production", "API_KEY": "secret-token", "CASCADE_URL": "https://cascade.example.com"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog",
    )
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

Pydantic enforces required attributes and validates field types upon construction, ensuring malformed payloads are caught early. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import CascadeWrapperBase

env_vars = {"SERVER": "production", "API_KEY": "secret-token", "CASCADE_URL": "https://cascade.example.com"}

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, {}) as cascade:
        cascade.operations.read(id).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.5 -->
