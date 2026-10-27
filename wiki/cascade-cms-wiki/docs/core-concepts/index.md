# Core Concepts

Building on the quick-start guide, this page explores the core mental model of `cascade-cms`: the `Cascade` wrapper initializes your session and logger, exposes an `Operations` builder for queuing requests, and sequences work into independent `OperationChain` nodes that execute concurrently when `submit_requests()` is called.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design keeps your request definitions declarative while managing connection pooling and concurrency automatically under the hood.

### Example

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import CascadeError

with Cascade(env_vars) as cascade:
    # Queue a read operation for a specific asset identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently and retrieve the results container
    results = cascade.submit_requests()
    
    # Check if the result is an API-level error
    if isinstance(results[0], CascadeError):
        print(f"Failed: {results[0].message}")
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={
        'id': '1234567890abcdef1234567890abcdef',
        'name': 'index',
        'path': '/index',
        'siteName': 'default',
        ...
    }
)
```

---

## Payload Models

Payload models are strongly typed Pydantic classes (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the correct structure and field types. They provide clear autocompletion, validate required fields up front, and automatically serialize parameters into the exact shape Cascade expects.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import SearchInformation

with Cascade(env_vars) as cascade:
    # Construct a strongly typed search payload
    payload = SearchInformation(
        siteName="default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Pass the payload object to the search operation builder
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce required criteria and format options correctly before any HTTP request leaves your client. Other operations follow the exact same pattern using dedicated payload classes like `deleteParameters`, `auditParameters`, and `Comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

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
