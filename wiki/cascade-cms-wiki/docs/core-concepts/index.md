# Core Concepts

This section establishes the foundational mental model for interacting with the Cascade CMS REST API. By moving from the quick-start wrapper setup to fluent operation chains, you can build, chain, and concurrently execute complex requests against your CMS instance.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. The library handles all underlying REST communication, session pooling, and error interception. Each chain runs independently, stopping at the first failure without disrupting other active requests.

### Example

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError

env_vars = {"SERVER": "my-server", "API_KEY": "token", "CASCADE_URL": "https://cascade.example.com/api/v1"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Start a chain reading an asset by identifier
    cascade.operations.read(identifier)
    
    # Submit all queued operation chains concurrently
    results = cascade.submit_requests()
    
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            # Result is an Asset wrapper
            print(result)
```

### Expected Output

```python
Asset(_asset_type='page', _data={'id': '1234567890abcdef', 'name': 'index', 'path': '/index', 'siteName': 'default'})
```

---

## Payload Models

Payload models are typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide strict validation and autocompletion support, preventing malformed requests before they hit the network.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search criteria using the SearchInformation payload model
payload = SearchInformation(
    siteName="default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)

# Pass the payload to the search operation
cascade.operations.search(payload)
results = cascade.submit_requests()
```

These models enforce required arguments and structure parameters correctly before transmission, ensuring type safety where passing a raw dictionary would fail validation. Other operations follow this exact pattern using models like `deleteParameters`, `auditParameters`, and `Comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

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

<!-- synthesized-for: 3.1.5 -->
