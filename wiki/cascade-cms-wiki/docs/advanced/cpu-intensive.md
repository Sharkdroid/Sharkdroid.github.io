# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization tasks.
- Parsing large files or heavy data transformation.
- Running bulk regular expressions across large HTML bodies.
- Light callbacks (like title string replacement or metadata dictionary updates) do not need it and perform better on the default executor.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Initialize the process pool with workers matching the CPU count
with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    with CascadeWrapperBase(env_vars, config_vars) as cascade:
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

`ProcessPoolExecutor` provides true parallelism across separate memory spaces, making it ideal for CPU-bound tasks, but it requires picklable functions and carries higher startup overhead. `ThreadPoolExecutor` shares memory with no pickling overhead, making it great for I/O-bound work, though it remains bound by the GIL for CPU-heavy workloads. Use `ProcessPoolExecutor` for heavy processing and `ThreadPoolExecutor` or the default settings for mixed or I/O-heavy operations.

---

## Performance Considerations

Spawning worker processes incurs a one-time startup cost, meaning very fast callbacks might run slower due to inter-process communication overhead than they would synchronously. Additionally, the driver's underlying HTTP concurrency is still strictly governed by the request semaphore limits regardless of whether a process or thread pool executor is chosen for callbacks.

<!-- synthesized-for: 3.1.6 -->
