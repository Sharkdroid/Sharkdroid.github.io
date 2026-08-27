# Core Concepts

Building on the quick-start guide, this page explores the library's core mental model: a single-script session is managed by a wrapper (`CascadeWrapperBase`), which exposes an operations builder (`Operations`) to construct fluent operation chains (`OperationChain`), executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same structural skeleton: open the wrapper as a context manager, queue one or more operations on `cascade.operations`, attach optional callbacks with `.then()`, and finally invoke `submit_requests()` to execute all queued chains concurrently. Chains run independently, so a failure in one operation chain does not affect any other.

### Example

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError

env = {"SERVER": "myserver", "API_KEY": "my-token", "CASCADE_URL": "https://cascade.example.com"}

with CascadeWrapperBase(env, {}) as cascade:
    # Start a chain to read an asset by its identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains and return results in the order they were created
    results = cascade.submit_requests()
    
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
# Success returns an Asset object wrapping the requested resource:
Success: Asset(_asset_type='page', _data={...})
```

---

## Payload Models

Payload models are typed Pydantic objects (inheriting from `SimplePayload`) that pair with specific operations to ensure the Cascade CMS API endpoint receives the exact structure and fields it expects. They provide input validation, type safety, and automatic serialization via aliases.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation

env = {"SERVER": "myserver", "API_KEY": "my-token", "CASCADE_URL": "https://cascade.example.com"}

with CascadeWrapperBase(env, {}) as cascade:
    # Construct the payload model specifying search criteria
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Pass the payload model directly to the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

Payload models enforce strict validation rules on required fields and field types before any request is sent to the API, and other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `Comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env = {"SERVER": "myserver", "API_KEY": "my-token", "CASCADE_URL": "https://cascade.example.com"}

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env, {}) as cascade:
        cascade.operations.read(id).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.1 -->
