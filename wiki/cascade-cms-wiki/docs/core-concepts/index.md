# Core Concepts

This page bridges the quick-start guide by detailing the core mental model behind Cascade CMS: the session wrapper coordinates everything, driving fluent operation queues that compile into independent execution chains before running concurrently via batch submission.

---

## Basic Operation Calls

Every script follows the same structural skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, attach sequential callbacks using `.then()`, and finally invoke `submit_requests()` to dispatch all accumulated chains concurrently. The wrapper manages the underlying REST driver and session lifecycle automatically.

### Example

```python
from cascade_cms import CascadeWrapperBase, CascadeError

env_vars = {"SERVER": "prod", "API_KEY": "secret", "CASCADE_URL": "https://cms.example.com"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Queue a read operation for an asset
    cascade.operations.read(identifier)
    
    # Submit the request batch
    results = cascade.submit_requests()
    
    for result in results:
        if isinstance(result, CascadeError):
            print(f"API Error: {result.message}")
        else:
            print(f"Success: {result}")
```

### Expected Output

```python
Asset(id='1234567890abcdef1234567890abcdef', type='page', path='index')
```

---

## Payload Models

Payload models are typed Pydantic objects (such as `SearchInformation`) that pair with specific operations to ensure API endpoints receive all expected and correctly formatted fields. They provide compile-time safety and clear input validation before any network request is ever sent.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search parameters using the dedicated payload model
payload = SearchInformation(
    siteName="Default",
    searchTerms="about",
    searchFields=["name"],
    searchTypes=["page"]
)

# Pass the payload directly to the search operation
cascade.operations.search(payload)
results = cascade.submit_requests()
```

Payload models enforce strict schemas and type checking; passing a raw dictionary directly to these operations would cause a validation failure. Other operations follow this exact structural pattern using dedicated models like `deleteParameters`, `auditParameters`, and `publishInformation`.

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
