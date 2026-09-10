# Core Concepts

This page bridges the quick-start guide by detailing the core mental model behind `cascade-cms`: a structured pipeline where the `CascadeWrapperBase` context manager orchestrates `Operations` builders, which in turn spawn and chain `OperationChain` units executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Results are returned in the exact order the chains were created, matching your flow. Failures are returned as values rather than raised, giving you clean control over API errors and exceptions.

### Example

```python
from cascade_cms import CascadeWrapperBase, CascadeError

env_vars = {"SERVER": "myserver", "API_KEY": "secret", "CASCADE_URL": "https://cascade.domain.edu/api/v1"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Start an operation chain to read an asset by its identifier
    cascade.operations.read(identifier)
    
    # Submit all registered chains and unpack the single result
    results = cascade.submit_requests()
    result = results[0]

    # Guard against API-level failures
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result)
```

### Expected Output

```python
Asset(asset={'page': {'id': '4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d', 'name': 'index', 'path': 'index', 'siteName': 'default', ...}})
```

---

## Payload Models

Payload models are typed objects (inheriting from `SimplePayload`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide full type-safety and IDE autocompletion for complex request parameters without requiring raw dictionary manipulation.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload specifying the site and search criteria
payload = SearchInformation(
    siteName="default",
    searchTerms="index",
    searchFields=["name", "title"],
    searchTypes=["page", "folder"]
)

# Pass the payload to the search operation
cascade.operations.search(payload)
results = cascade.submit_requests()
```

Payload models enforce required fields and structured validation before any HTTP request is ever sent to the REST API, replacing error-prone raw dictionaries. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, `copyParameters`, and `moveParameters`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import CascadeWrapperBase

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, {}) as cascade:
        cascade.operations.read(identifier).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.3 -->
