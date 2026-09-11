# Core Concepts

This page bridges the gap between quick-start usage and full mastery of the library by explaining its core mental model: a context manager wrapper containing an Operations builder, which generates independent operation chains executed concurrently upon submission.

---

## Basic Operation Calls

Every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. This design decouples request building from execution, allowing you to queue arbitrary combinations of reads, edits, and custom transformation callbacks before dispatching them as a batch.

### Example

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import CascadeError

env_vars = {"SERVER": "myserver", "API_KEY": "my-token", "CASCADE_URL": "https://cms.example.com"}

# Open the wrapper context manager
with CascadeWrapperBase(env_vars, {}) as cascade:
    # Queue a read operation on the identifier
    cascade.operations.read(identifier)
    
    # Submit requests and capture the results list
    results = cascade.submit_requests()
    
    # Check if the result encountered an API error
    if isinstance(results[0], CascadeError):
        print(f"Error: {results[0].message}")
    else:
        asset = results[0]
```

### Expected Output

```python
# Returns an Asset instance wrapping the raw JSON response:
# Asset(_asset_type='page', _data={...})
```

---

## Payload Models

Payload models are typed Pydantic objects (such as `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. They enforce schema validation up front so you never have to guess at the structure required by a particular Cascade REST endpoint.

### Example: `SearchInformation` paired with `search`

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import SearchInformation

env_vars = {"SERVER": "myserver", "API_KEY": "my-token", "CASCADE_URL": "https://cms.example.com"}

with CascadeWrapperBase(env_vars, {}) as cascade:
    # Construct the SearchInformation payload with required search criteria
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Pass the payload model into the search operation
    cascade.operations.search(payload)
    results = cascade.submit_requests()
```

These models enforce required keys and valid types through Pydantic validators, meaning raw dictionaries are rejected where structured payloads are expected. Other operations follow this exact pattern using dedicated parameter classes like `deleteParameters`, `auditParameters`, `copyParameters`, and `moveParameters`.

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {"SERVER": "myserver", "API_KEY": "my-token", "CASCADE_URL": "https://cms.example.com"}

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, {}) as cascade:
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
