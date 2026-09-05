# Core Concepts

This page bridges the quick-start guide by detailing the library's mental model: tying together the context-manager wrapper, operations builder, sequential operation chains, and concurrent batch execution.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design keeps network requests organized and transparently separates the fluent building phase from the execution phase.

### Example

```python
# Open the wrapper context manager with required environment variables
with CascadeWrapperBase(env_vars, {}) as cascade:
    # Queue a read operation on the specified identifier
    cascade.operations.read(identifier)
    
    # Execute the registered chain and return the results list
    results = cascade.submit_requests()
    
    # Check if the result encountered an API-level error
    if isinstance(results[0], CascadeError):
        print(results[0].message)
```

### Expected Output

```python
Asset(_asset_type='page', _data={'id': '12345', 'name': 'index', 'path': 'index', 'siteName': 'default'})
```

---

## Payload Models

Payload models are typed objects (subclasses of `SimplePayload`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time type safety and clear documentation of required fields without needing raw dictionary constructions.

### Example: `SearchInformation` paired with `search`

```python
# Construct the search payload with required site name and search terms
payload = SearchInformation(
    siteName="default",
    searchTerms="about",
)

# Pass the payload model directly to the search operation
cascade.operations.search(payload)
results = cascade.submit_requests()
```

The payload model enforces that required attributes (`siteName`, `searchTerms`) are present and valid, preventing malformed requests from reaching the CMS and making other operations like `deleteParameters`, `auditParameters`, and `publishInformation` follow the exact same consistent pattern.

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

<!-- synthesized-for: 3.1.3 -->
