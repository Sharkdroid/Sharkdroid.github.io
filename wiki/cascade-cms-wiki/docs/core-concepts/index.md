# Core Concepts

This page bridges the quick-start guide by detailing the core mental model of `cascade-cms`: the `Cascade` wrapper orchestrates a session, tying together the REST driver and `Operations` builder to manage execution. Individual operations queue into independent `OperationChain` structures that execute concurrently when `submit_requests()` is invoked.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. A chain stops at the first failure without affecting any other chain, pairing each result with the operation that produced it.

### Example

```python
from cascade_cms import Cascade

# Open the Cascade wrapper context manager
with Cascade(env_vars) as cascade:
    # Queue a read operation on the operations builder
    cascade.operations.read(identifier)
    
    # Submit all registered operation chains for concurrent execution
    results = cascade.submit_requests()
    
    # Check if the result returned a CascadeError
    if isinstance(results[0], CascadeError):
        print("Operation failed.")
```

### Expected Output

```python
# Returns a ChainResults object containing the parsed Asset object wrapper
Asset(asset={'page': {'id': '1234567890abcdef...', 'name': 'index', ...}})
```

---

## Payload Models

Payload models are typed objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time safety and clarity, replacing raw dictionaries with validated structures.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct the search payload with site name and search terms
payload = SearchInformation(
    site_name="default",
    search_terms="news"
)

# Pass the payload to the search operation
cascade.operations.search(payload)
```

These models enforce required fields and structural constraints through Pydantic validators before requests ever reach the driver, ensuring API correctness across all operations (`deleteParameters`, `auditParameters`, etc.).

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

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
