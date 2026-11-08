# Core Concepts

This page unpacks the mental model behind Cascade CMS: the `Cascade` context manager ties together a REST driver, an operation logger, and an `Operations` builder that yields independent `OperationChain` instances, all executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design keeps network requests clean, isolates failures per asset, and eliminates boilerplate.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for a specific asset identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently
    results = cascade.submit_requests()
    
    # Check results for API-level errors
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
```

### Expected Output

```python
Asset(_asset_type='page', _data={...})
```

---

## Payload Models

Payload models are strongly typed Pydantic objects (inheriting from `SimplePayload`) that pair with specific REST operations to ensure the API endpoint receives the expected fields. They provide type safety, autocomplete, and proper serialization aliases (like converting Python snake_case to Cascade camelCase) without requiring raw dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the payload with search criteria
payload = SearchInformation(
    siteName="Default",
    searchTerms="article",
    searchFields=["name"],
    searchTypes=["page"]
)

with Cascade(env_vars) as cascade:
    # Pass the typed payload to the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce required arguments at validation time, preventing malformed requests from ever hitting the wire. Other operations follow the exact same pattern using models like `deleteParameters`, `auditParameters`, and `publishInformation`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

def optimize_image(asset):
    # Heavy CPU-bound image processing
    return asset

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
