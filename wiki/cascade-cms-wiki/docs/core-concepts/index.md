# Core Concepts

Building on the quick-start guide, this page explores the library's core mental model: a single context manager wrapper (`CascadeWrapperBase`) manages the lifecycle and connection, exposes a fluent `Operations` builder, produces independent `OperationChain` instances, and executes them in concurrent batches via `submit_requests()`.

---

## Basic Operation Calls

Every automation script follows the same structural pattern: open the wrapper as a context manager, queue one or more operation chains on `cascade.operations`, chain post-processing callbacks with `.then()`, and finally invoke `submit_requests()` to execute everything concurrently. Chains run independently, so a failure in one asset's chain never interrupts the others.

### Example

```python
with CascadeWrapperBase(env_vars, config_vars) as cascade:
    # Queue a read operation for a specific asset identifier
    cascade.operations.read(identifier)
    
    # Submit requests and receive results in the order chains were created
    results = cascade.submit_requests()
    
    # Check for API-level failures returned as values rather than raised
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
Success: Asset(_asset_type='page', _data={'id': '...', 'name': 'index', ...})
```

---

## Payload Models

Payload models are typed Pydantic objects (inheriting from `SimplePayload`) that pair with specific operations to ensure the underlying API endpoints receive structurally valid fields. They provide compile-time type safety, editor autocompletion, and automatic field aliasing (`by_alias=True`) to match Cascade's expected JSON payload keys without requiring manual dictionaries.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search criteria using the SearchInformation payload model
payload = SearchInformation(
    siteName="Default_Site",     # The target site name to search within
    searchTerms="blog",          # The term or query string to search for
    searchFields=["name"],       # Specific fields to scan (e.g., name, path)
    searchTypes=["page"]         # Asset types to include in search results
)

# Pass the typed payload to cascade.operations.search()
cascade.operations.search(payload)
results = cascade.submit_requests()
```

The `SearchInformation` model enforces that all required parameters are present and properly formatted before the request is executed, preventing malformed requests from hitting the Cascade API. Other operations follow this exact structural pattern using dedicated payload classes like `deleteParameters`, `auditParameters`, and `copyParameters`.

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

<!-- synthesized-for: 3.1.5 -->
