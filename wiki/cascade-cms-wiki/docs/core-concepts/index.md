# Core Concepts

This page explains the library's core mental model: how the context manager ties together drivers, operation builders, and individual request chains. You'll learn how to construct basic queries, manage strongly-typed payloads, and offload CPU-bound work.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Individual request chains run sequentially, but batches of chains run in parallel while respecting server limits. Failures are captured as values instead of raising exceptions, allowing your script to inspect partial successes safely.

### Example

```python
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for a specific asset identifier
    cascade.operations.read(identifier)
    
    # Submit all queued requests and retrieve the result list
    results = cascade.submit_requests()
    
    # Check if the result encountered an API-level error
    if isinstance(results[0], CascadeError):
        print(f"Error: {results[0].message}")
```

### Expected Output

```python
[
    Asset(
        _asset_type="page",
        _data={
            "id": "abc123...",
            "path": "/index",
            "siteName": "default",
            "displayName": "Home",
            ...
        }
    )
]
```

---

## Payload Models

Payload models are typed objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide full type safety and catch missing parameters before any requests are ever dispatched to the server.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="default",            # Name of the site to search within
    searchTerms="blog",            # Query terms to match against assets
    searchFields=["name", "path"],   # Fields to inspect during the search
    searchTypes=["page", "file"]     # Asset types to include in results
)

with CascadeWrapperBase(env_vars, config_vars) as cascade:
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These Pydantic-backed models enforce validation at runtime and automatically wrap outgoing payloads in the expected REST format. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `copyParameters`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

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

<!-- synthesized-for: 3.1.5 -->
