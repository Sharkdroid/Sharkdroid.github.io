# Core Concepts

This page unpacks the mental model behind Cascade CMS Python: a context manager wrapper (`Cascade`) coordinates a fluent builder (`Operations`) that constructs singly-linked operation chains (`OperationChain`), executed concurrently via `submit_requests()`.

---

## Basic Operation Calls

Every script follows the same skeleton: open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Individual chains run their steps strictly in order, stopping at the first failure without affecting others.

### Example

```python
# Open the Cascade context manager with your environment variables
with Cascade(env_vars) as cascade:
    # Queue a read operation on an identifier
    cascade.operations.read(identifier)
    
    # Submit all queued operations concurrently
    results = cascade.submit_requests()
    
    # Check if the result is a CascadeError
    for result in results:
        if isinstance(result, CascadeError):
            print(f"Error: {result.message}")
```

### Expected Output

```python
Asset(
    _asset_type='page',
    _data={
        'id': '1234567890abcdef1234567890abcdef',
        'name': 'index',
        'path': '/index',
        'displayName': 'Home Page',
        ...
    }
)
```

---

## Payload Models

Payload models are strongly typed Pydantic objects that pair with specific operations to ensure the API endpoint receives the expected fields. They provide compile-time safety and self-documenting structure compared to unstructured dictionaries.

### Example: `SearchInformation` paired with `search`

```python
# Construct a SearchInformation payload specifying site name, terms, fields, and types
payload = SearchInformation(
    siteName="Default",
    searchTerms="blog",
    searchFields=["name"],
    searchTypes=["page"]
)

# Pass the payload to the search operation
cascade.operations.search(payload)
```

The `SearchInformation` model enforces valid parameters before any HTTP request leaves the library, guaranteeing that required fields are present and properly aliased (`siteName`, `searchTerms`, `searchFields`, `searchTypes`). Other operations follow this exact pattern using corresponding payload models like `deleteParameters`, `auditParameters`, and `copyParameters`.

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
