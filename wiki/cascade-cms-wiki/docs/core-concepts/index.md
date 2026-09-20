# Core Concepts

This page details the library's core mental model, building on the quick-start guide by examining how the wrapper, operations builder, execution chains, and request submission work together under the hood.

---

## Basic Operation Calls

Every automation script follows the same structural skeleton: instantiate or open the wrapper as a context manager, queue one or more operations on `cascade.operations`, chain post-processing callbacks with `.then()`, and finally invoke `submit_requests()` to execute all queued chains concurrently. This design keeps API calls declarative while managing network I/O and batching transparently.

### Example

```python
# Open the wrapper context manager
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation on an asset identifier
    cascade.operations.read(identifier)
    
    # Execute the request and retrieve results
    results = cascade.submit_requests()
    
    # Guard against API-level failures returned as values
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
```

### Expected Output

```python
[
    Asset(
        _asset_type='page',
        _data={'id': 'abc123uuid...', 'name': 'index', 'path': '/index', ...}
    )
]
```

---

## Payload Models

Payload models are typed, Pydantic-backed classes (inheriting from `SimplePayload`) that pair with specific API operations to ensure endpoints receive properly structured and validated input fields. They enforce schema compliance and catch configuration errors early without relying on raw, error-prone dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload using the typed model
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name", "title"],
    searchTypes=["page"]
)

# Pass the payload directly into the search operation
cascade.operations.search(payload)
```

The `SearchInformation` model validates required fields (`siteName`, `searchTerms`) and handles serialization defaults for optional fields like `searchFields` and `searchTypes`. Other operations use equivalent models (such as `deleteParameters`, `auditParameters`, and `copyParameters`) to guarantee strict API compatibility.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    cascade.operations.read(identifier).then(optimize_image)
    results = cascade.submit_requests(executor=executor)
```

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.

<!-- synthesized-for: 3.1.6 -->
