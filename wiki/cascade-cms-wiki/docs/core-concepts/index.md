# Core Concepts

This guide builds on the quick-start guide by walking through the library's core mental model: binding an API session via the wrapper, starting operations builders, chaining work into self-contained operation chains, and batch-executing them with request submission.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Failures are returned as values rather than raised, allowing individual chains to stop at the exact step they failed without affecting others.

### Example

```python
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Start a chain for the given asset identifier
    cascade.operations.read(identifier)
    
    # Submit all registered chains concurrently and retrieve results
    results = cascade.submit_requests()
    
    for result in results:
        # Guard against API-level errors or exceptions returned as values
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(result)
```

### Expected Output

```python
# Returns an Asset instance wrapping the raw Cascade JSON payload
Asset(_asset_type='page', _data={...})
```

---

## Payload Models

Payload models are typed objects—such as `SearchInformation`—that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time safety and self-documenting parameters without requiring raw dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload specifying site name, terms, fields, and types
payload = SearchInformation(
    siteName="Default",
    searchTerms="index",
    searchFields=["name", "path"],
    searchTypes=["page"]
)

with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Pass the typed payload to the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

The payload model enforces validation rules and serialization mapping automatically via Pydantic, ensuring that invalid fields or omitted required values are caught early. Other operations follow this identical pattern using specialized models like `deleteParameters`, `auditParameters`, and `Comment`.

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

<!-- synthesized-for: 3.1.3 -->
