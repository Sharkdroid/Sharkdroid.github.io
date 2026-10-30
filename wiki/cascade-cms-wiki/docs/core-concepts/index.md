# Core Concepts

Building on the quick-start guide, this page explores the library's mental model: tying together the context manager wrapper, the fluent operations builder, method-chained execution units, and concurrent dispatch via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design keeps your request definitions declarative and separates network orchestration from business logic.

### Example

```python
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import CascadeError

# Open the Cascade context manager
with Cascade(env_vars) as cascade:
    # Queue a read operation and chain a processing callback
    cascade.operations.read(identifier).then(rewrite)
    
    # Execute all queued chains concurrently
    results = cascade.submit_requests()
```

### Expected Output

```python
# Returns a ChainResults collection containing the resolved Asset wrapper object
# (or a CascadeError if the operation failed at the API level).
```

---

## Payload Models

Payload models are typed Pydantic-based objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time safety and automatic serialization (including camelCase alias mapping via `SimplePayload`), preventing malformed requests before they hit the network.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.cmstypes import SearchInformation

# Construct search parameters with required site and terms
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
)

# Pass the payload model into the search operation
results = cascade.operations.search(payload)
```

Other operations follow the exact same pattern, using dedicated request models like `deleteParameters`, `auditParameters`, `copyParameters`, and `moveParameters` to enforce correct schemas.

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

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: debug logging and CPU-intensive workload patterns.

<!-- synthesized-for: 3.9.2 -->
