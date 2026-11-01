# Core Concepts

This page bridges the quick-start guide to the library's core mental model: a single `Cascade` wrapper session containing an `Operations` builder that spawns independent `OperationChain` instances, executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. These operations are independent, ensuring that a failure in one chain never affects any other.

### Example

```python
with Cascade(env_vars) as cascade:
    # Queue a read operation for the given asset identifier
    cascade.operations.read(identifier)
    
    # Execute all queued chains concurrently
    results = cascade.submit_requests()
    
    # results[0] contains the result or error; inspect without isinstance checks
    result = results[0]
```

### Expected Output

```python
Asset(_data={'name': 'example', 'id': '1234567890abcdef...', ...})
```

---

## Payload Models

Payload models are typed Pydantic objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide type-safety, handle field aliasing (like camelCase conversion), and validate required parameters before any request ever reaches the server.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search parameters with site name, search terms, and optional fields/types
payload = SearchInformation(
    siteName="Default_Site",
    searchTerms="blog",
    searchFields=["name", "summary"],
    searchTypes=["page"]
)

with Cascade(env_vars) as cascade:
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce the exact schema required by Cascade CMS endpoints, preventing silent failures from malformed dictionaries. All write and query operations follow this exact pattern using dedicated payload classes like `deleteParameters`, `auditParameters`, and `copyParameters`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

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
