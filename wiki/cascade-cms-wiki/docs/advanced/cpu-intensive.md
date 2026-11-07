# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization
- Large-file parsing
- Heavy data transformation
- Bulk regex on large HTML bodies
- *Contrast with light callbacks (title string replace, metadata dict update) that don't need it and run efficiently on the default thread pool or event loop.*

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores with separate memory spaces, but requires picklable module-level functions and has higher startup overhead per task. `ThreadPoolExecutor` uses shared memory with lower overhead, but remains bound by Python's Global Interpreter Lock (GIL), making it unsuitable for heavy CPU computations. Use `ProcessPoolExecutor` for CPU-heavy processing, and `ThreadPoolExecutor` (or the default) for I/O-bound or mixed workloads.

---

## Performance Considerations

Spawning worker processes incurs a one-time startup cost, so very fast callbacks may execute slower under a `ProcessPoolExecutor` than in the main process due to serialization overhead. Additionally, note that the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency regardless of which executor is selected for callbacks.

<!-- synthesized-for: 3.9.2 -->
