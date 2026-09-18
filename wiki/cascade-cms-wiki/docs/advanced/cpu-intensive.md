# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization workflows before saving modified assets.
- Large-file parsing or heavy data transformations on asset content.
- Bulk regular expression operations on large HTML bodies or rendered blocks.
- Light callbacks (such as a title string replacement or metadata dict update) do not need it and perform better without process-spawning overhead.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-bearer-token",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

def optimize_image(asset):
    # CPU-bound image transformation logic here
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

`ProcessPoolExecutor` provides true parallelism using separate memory spaces, but requires picklable functions and incurs higher startup overhead per task. `ThreadPoolExecutor` uses shared memory with no pickling restrictions and lower overhead, but remains constrained by the Global Interpreter Lock (GIL) for CPU-bound computations. Use `ProcessPoolExecutor` for heavy CPU workloads, and `ThreadPoolExecutor` for I/O-bound or mixed workloads.

---

## Performance Considerations

Spawning worker processes carries a one-time startup cost, meaning very fast callbacks may execute slower under a process pool than in the main thread due to inter-process communication overhead. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP concurrency independently of whether a thread or process executor handles the callback stage.

<!-- synthesized-for: 3.1.6 -->
