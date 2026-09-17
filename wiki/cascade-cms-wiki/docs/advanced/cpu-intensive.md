# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and binary asset optimization.
- Parsing and validating large XML/JSON payloads or documents.
- Heavy data transformation and complex computational data crunching.
- Bulk regex searches and replacements across large HTML bodies.
- *Contrast:* Light callbacks like simple title string replacements or metadata dictionary updates execute instantly and do not require process offloading.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

def optimize_image(asset):
    # Perform heavy CPU-bound processing on worker process
    return asset

env_vars = {
    "SERVER": "my-server",
    "API_KEY": "my-api-key",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

with CascadeWrapperBase(env_vars, {}) as cascade:
    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        cascade.operations.read(id).then(optimize_image)
        results = cascade.submit_requests(executor=executor)
```

---

## Pickling Constraint

Callbacks executed in a `ProcessPoolExecutor` must be **defined at module level**. Python's `multiprocessing` serializes functions via `pickle`, which cannot handle:

- Lambda functions
- Nested/inner functions defined inside another function or class method
- Closures that capture local variables

```python
# ✗ Will raise PicklingError at runtime
cascade.operations.read(id).then(lambda asset: asset)

# ✓ Module-level function — safe to pickle
def transform(asset):
    asset.displayName = asset.displayName.upper()
    return asset

cascade.operations.read(id).then(transform)
```

---

## `ProcessPoolExecutor` vs `ThreadPoolExecutor`

`ProcessPoolExecutor` provides true parallelism in separate memory spaces, making it ideal for CPU-heavy tasks, though it requires picklable functions and incurs higher task overhead. `ThreadPoolExecutor` uses shared memory with minimal overhead and no pickling constraints, making it great for I/O-bound work, but it remains subject to the Python GIL. Use `ProcessPoolExecutor` for CPU-intensive tasks and `ThreadPoolExecutor` for standard I/O operations or mixed workloads.

---

## Performance Considerations

Spawning and communicating with worker processes incurs a startup cost, so very fast callbacks may execute slower under a process pool due to serialization overhead. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency independently from whichever executor is chosen for callbacks.

<!-- synthesized-for: 3.1.5 -->
