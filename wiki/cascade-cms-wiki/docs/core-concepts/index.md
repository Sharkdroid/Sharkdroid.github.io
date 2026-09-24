# Core Concepts

Building on the quick-start guide, this page explores the library's foundational mental model: the wrapper manages the session, which hands off to the operations builder, which spawns independent operation chains before executing them concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Keep it to 3–4 sentences.

### Example

```python
from cascade_cms import CascadeWrapperBase, CascadeError

# Open the wrapper context manager with required environment and config variables
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for an asset identifier
    cascade.operations.read(identifier)
    
    # Submit all queued requests and retrieve the ChainResults container
    results = cascade.submit_requests()
    
    # Inspect the result using the first entry in ChainResults
    result = results[0]
    if isinstance(result, CascadeError):
        print(f"Operation failed: {result.message}")
    else:
        print(f"Success! Asset type: {result.internal_type}")
```

### Expected Output

```python
# Output from a successful read operation returning the wrapped Asset object:
Asset(internal_type='page', _data={'id': '1234567890abcdef...', 'name': 'index', 'path': 'index'})
```

---

## Payload Models

Payload models are strongly typed Pydantic objects (inheriting from `SimplePayload`) that pair with specific operations to ensure API endpoints receive expected parameters with correct aliasing. They provide type safety and IDE autocomplete while managing serialization format rules under the hood.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct SearchInformation payload with required search criteria
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name", "metadata"],
    searchTypes=["page", "file"]
)

# Pass the payload directly to the operations builder search method
cascade.operations.search(payload)
```

Passing a raw dictionary directly to operations requiring these models will fail validation; every operation expects its corresponding typed parameter class (such as `deleteParameters`, `auditParameters`, or `SearchInformation`) to guarantee correct request body generation.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import CascadeWrapperBase

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, config_vars) as cascade:
        cascade.operations.read(identifier).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.2.1 -->
