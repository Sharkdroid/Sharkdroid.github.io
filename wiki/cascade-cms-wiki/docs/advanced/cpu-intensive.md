# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

* Image resizing, optimization, and generation
* Parsing and processing large XML/HTML payloads or documents
* Heavy data transformation and number-crunching pipelines
* Running bulk regular expressions across large text bodies
* *Contrast with:* Light callbacks such as minor string replacement or simple metadata dictionary updates, which have minimal overhead and run efficiently on the default thread pool or main event loop.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

# Callback must be defined at module level for pickling
def optimize_image(asset):
    # CPU-heavy image optimization logic here
    return asset

env_vars = {
    "SERVER": "Production",
    "API_KEY": "your-api-key",
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-bound tasks, though it requires picklable functions and incurs higher task dispatch overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling restrictions, but remains limited by Python's Global Interpreter Lock (GIL) for CPU-bound computations. Use `ProcessPoolExecutor` for heavy processing tasks, and `ThreadPoolExecutor` (or the default) for I/O-bound work.

---

## Performance Considerations

Spawning and communicating with worker processes incurs a small startup and serialization overhead, so extremely fast callbacks may run slower in a process pool than synchronously. Additionally, choosing an executor only governs callback execution; HTTP request concurrency remains managed separately by the driver's request semaphore.

<!-- synthesized-for: 3.1.5 -->
