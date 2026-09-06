# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

* Image resizing, compression, or optimization
* Large-file parsing and heavy data transformation
* Bulk regular expression matching across large HTML bodies
* Light callbacks (title string replace, metadata dict update) do not need it and perform better running directly on the thread/event loop without serialization overhead.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-api-key",
    "CASCADE_URL": "https://cascade.example.com:8443/api/v1",
}

def optimize_image(asset):
    # CPU-heavy image optimization logic here
    return asset

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-bound tasks, but it requires functions to be picklable and introduces process communication overhead. `ThreadPoolExecutor` uses shared memory with lower task overhead, but it is bounded by Python's Global Interpreter Lock (GIL), meaning it cannot execute CPU-bound work in parallel. Use `ProcessPoolExecutor` for heavy computations and `ThreadPoolExecutor` (or the default executor) for mixed or I/O-bound work.

---

## Performance Considerations

Spawning and communicating with worker processes carries a startup cost, so very fast callbacks may run slower under a `ProcessPoolExecutor` due to serialization overhead. Additionally, the driver's underlying request semaphore continues to govern HTTP request concurrency independently of whichever executor is chosen for synchronous callback execution.

<!-- synthesized-for: 3.1.3 -->
