# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or heavy media optimization.
- Parsing or indexing very large JSON, XML, or HTML document trees.
- Executing heavy data transformation pipelines or complex regex operations across large text bodies.
- *Contrast with light callbacks:* Simple operations like string replacements on title fields or metadata dictionary updates execute instantly in-process and do not need a process pool.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

# Module-level callback required for pickling
def optimize_image(asset):
    # Perform CPU-intensive processing here
    return asset

env_vars = {
    "SERVER": "prod",
    "API_KEY": "bearer_token",
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by running tasks in separate memory spaces, but requires all callbacks and arguments to be picklable and incurs inter-process communication overhead. `ThreadPoolExecutor` (the default) runs tasks concurrently within the same process using shared memory with minimal overhead, but is restricted by the Global Interpreter Lock (GIL) and cannot achieve true parallel CPU execution. Use `ProcessPoolExecutor` for CPU-heavy data manipulation tasks, and `ThreadPoolExecutor` for I/O-bound or mixed workloads.

---

## Performance Considerations

Spawning and communicating across worker processes introduces a startup and serialization overhead; for very fast callbacks, this overhead can exceed the time saved by parallelism. Additionally, while the executor manages the concurrency of your CPU-bound Python callbacks, the underlying network requests remain bounded by the driver's request semaphore and connection pool limits.

<!-- synthesized-for: 3.1.3 -->
