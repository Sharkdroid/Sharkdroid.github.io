# Core Concepts

This page bridges the quick-start guide and the full library reference by explaining the core mental model of `cascade-cms`: the wrapper ties everything together, exposing an `Operations` builder that spawns individual chains, which are executed concurrently when you submit requests.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Each chain runs its operations and callbacks strictly in order, stopping immediately at the first failure without disrupting other concurrent chains.

### Example

```python
# Open the wrapper context manager
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Start an operation chain by reading an asset
    cascade.operations.read(identifier)
    
    # Submit all registered chains and capture their results
    results = cascade.submit_requests(Asset)
    
    # Check for errors returned as values in the result list
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Successfully read asset: {result.get('name')}")
```

### Expected Output

```python
Asset(_asset_type='page', _data={'id': '1234567890abcdef', 'name': 'index', 'path': '/index', 'siteName': 'default'})
```

---

## Payload Models

Payload models are typed Pydantic objects that pair with specific operations to ensure API endpoints receive the exact expected fields. They provide compile-time type safety, editor autocompletion, and robust validation before any network request is ever dispatched.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation, FieldsSearchTypes, AssetTypes

# Construct a typed payload for the search endpoint
payload = SearchInformation(
    siteName="default",
    searchTerms="about-us",
    searchFields=[FieldsSearchTypes.name],
    searchTypes=[AssetTypes.page]
)

# Pass the typed payload to the search operation builder
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

Passing raw dictionaries instead of these classes will fail validation; all other write and query operations follow this exact pattern using models like `deleteParameters`, `auditParameters`, and `copyParameters`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

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
