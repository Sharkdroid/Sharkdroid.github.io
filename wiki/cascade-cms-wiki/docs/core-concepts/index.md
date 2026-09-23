# Core Concepts

This guide builds upon the quick-start guide by breaking down the library's mental model: tying together the wrapper, operations builder, operation chains, and batch execution into a cohesive execution flow.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. The library handles the asynchronous plumbing internally while letting you build operations with a clean, fluent syntax.

### Example

```python
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for an asset identifier
    cascade.operations.read(identifier)
    
    # Submit all queued requests and retrieve results
    results = cascade.submit_requests()
    
    # Inspect the result, guarding against CascadeError responses
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
        else:
            print(f"Successfully read asset: {result}")
```

### Expected Output

```python
[Asset(_asset_type='page', _data={'id': '1234567890abcdef1234567890abcdef', 'name': 'index', 'path': '/index', ...})]
```

---

## Payload Models

Payload models are typed objects (subclasses of `SimplePayload`) that pair with specific operations to ensure the API endpoint receives the expected fields and correct data types. They provide compile-time safety and self-documenting parameters through Pydantic without requiring raw dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload with required and optional parameters
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name", "summary"],
    searchTypes=["page", "file"]
)

with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Pass the payload model directly into the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

Payload models enforce strict typing and field-level validation, preventing subtle payload mismatch errors before any HTTP requests are dispatched to Cascade. Other operations follow this exact pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, config_vars) as cascade:
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
