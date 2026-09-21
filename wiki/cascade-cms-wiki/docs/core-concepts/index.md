# Core Concepts

This page bridges the quick-start guide by walking through the library's foundational mental model: the wrapper orchestrating a session, the operations builder dispatching requests, operation chains executing sequentially per asset, and batch submission running everything concurrently.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Failures are returned as values rather than raised exceptions, allowing scripts to handle partial drops safely without aborting the entire batch.

### Example

```python
# Open the wrapper session
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for an asset identifier
    cascade.operations.read(identifier)
    
    # Submit all queued requests and retrieve the results list
    results = cascade.submit_requests(Asset)
    
    # Check for API-level failures
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(result)
```

### Expected Output

```python
Asset(internal_type='page', _data={'name': 'index', 'path': '/index', 'id': '...'})
```

---

## Payload Models

Payload models are typed Pydantic objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the exact expected fields. They provide compile-time safety and clear structure over raw dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search criteria using the payload model
search_payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name", "summary"],
    searchTypes=["page"]
)

# Pass the payload directly to the search operation
cascade.operations.search(search_payload)
results = cascade.submit_requests()
```

These models enforce required arguments and ensure that field names map correctly via aliases before the request executes. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

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
