# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or other pixel-level processing operations
- Heavy data transformations or bulk regex parsing on large HTML bodies
- Complex serialization or cryptographic hashing tasks
- Light callbacks (title string replace, metadata dict update) that don't need it and are faster on the default thread pool or main loop

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores with separate memory spaces, but requires all callback functions and data to be picklable and incurs higher task-dispatch overhead. `ThreadPoolExecutor` (which is the default) shares memory and has lower overhead, but is still bound by the Global Interpreter Lock (GIL) and cannot achieve true parallelism for CPU-bound tasks. Use `ProcessPoolExecutor` for CPU-heavy workflows and `ThreadPoolExecutor` for I/O-bound work.

---

## Performance Considerations

Spawning worker processes has a measurable startup cost, so for very fast callbacks the inter-process communication and pickling overhead may outweigh the parallel execution benefit. Additionally, the driver's underlying request concurrency semaphore still governs HTTP operations independently of whatever executor is chosen for synchronous callback functions.

<!-- synthesized-for: 3.9.2 -->
