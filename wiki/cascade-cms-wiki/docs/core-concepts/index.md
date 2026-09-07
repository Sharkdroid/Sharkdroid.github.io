# Core Concepts

This page bridges the quick-start guide and the full library reference by explaining the core mental model of `cascade-cms`: the wrapper ties together your credentials and logging, `cascade.operations` builds fluent query chains, and `submit_requests()` executes them concurrently.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Failures are captured as values rather than raised as exceptions, so you can inspect them safely after execution finishes.

### Example

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError

env_vars = {"SERVER": "myserver", "API_KEY": "mykey", "CASCADE_URL": "https://cascade.local/"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # 1. Start an operation chain by reading an asset
    cascade.operations.read(identifier)
    
    # 2. Submit the registered requests
    results = cascade.submit_requests()
    
    # 3. Inspect results without crashing on errors
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
# Returns an Asset wrapper around the raw JSON payload:
# Asset(
#     _asset_type='page',
#     _data={'id': '...', 'name': 'index', 'path': 'index', ...},
#     _page_configs[...]
# )
```

---

## Payload Models

Payload models are typed objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time clarity and validation, ensuring you never pass invalid parameters to an endpoint.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation

env_vars = {"SERVER": "myserver", "API_KEY": "mykey", "CASCADE_URL": "https://cascade.local/"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Build the payload for the search operation
    payload = SearchInformation(
        siteName="Default",
        searchTerms="about",
    )
    
    # Pass the payload model into the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce correct input structures before any HTTP request leaves your client, keeping your interaction with the Cascade REST API strictly typed. Other operations follow this exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {"SERVER": "myserver", "API_KEY": "mykey", "CASCADE_URL": "https://cascade.local/"}

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

<!-- synthesized-for: 3.1.3 -->
