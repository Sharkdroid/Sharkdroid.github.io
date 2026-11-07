# Core Concepts

This page unpacks the mental model behind Cascade CMS: the `Cascade` wrapper initializes your session and logger, which exposes the `Operations` builder to queue chains of work (`OperationChain`), culminating in concurrent execution via `submit_requests()`.

---

## Basic Operation Calls

Every script follows a consistent skeleton: you open the wrapper as a context manager, queue your operations on `cascade.operations`, attach any desired processing via `.then()`, and finally invoke `submit_requests()` to dispatch every registered chain concurrently. Chains run strictly in order, and each node receives the previous result. A failure stops only the chain it occurred on without interrupting the rest of the batch.

### Example

```python
from cascade_cms import Cascade

# Initialize the context manager with your environment variables
with Cascade(env_vars) as cascade:
    # Queue a read operation for a specific asset identifier
    cascade.operations.read(identifier)
    
    # Submit all queued operation chains concurrently
    results = cascade.submit_requests()
    
    # Check the result of the first chain
    result = results[0]
    if isinstance(result, CascadeError):
        print(f"Operation failed: {result.message}")
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={
        'id': UUID('...'),
        'name': 'index',
        'path': '/index',
        'displayName': 'Home Page',
        ...
    }
)
```

---

## Payload Models

Payload models are typed objects (subclasses of `SimplePayload`) that pair with specific operations to ensure API endpoints receive all expected fields with proper typing. They provide structural clarity and type safety, catching validation errors before requests ever hit the server.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import SearchInformation

with Cascade(env_vars) as cascade:
    # Construct a typed payload for the search endpoint
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Pass the payload model directly into the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce that required fields like `siteName` and `searchTerms` are present and properly typed, preventing common mistakes that occur when passing raw dictionaries. Other operations follow this exact pattern using dedicated models such as `deleteParameters`, `auditParameters`, and `comment`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

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
