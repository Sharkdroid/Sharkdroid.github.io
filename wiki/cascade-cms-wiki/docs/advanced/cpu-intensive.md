# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization
- Large-file parsing and heavy data transformation
- Bulk regex parsing or manipulation on large HTML bodies
- Light callbacks (title string replace, metadata dict update) that do not need offloading and run fast enough directly on the loop or thread pool.

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

ProcessPoolExecutor provides true parallelism in separate memory spaces for CPU-bound work, though it requires picklable functions and incurs higher overhead per task. ThreadPoolExecutor uses shared memory with lower overhead and no pickling requirements, but remains subject to the GIL, making it ideal for mixed I/O and CPU-bound work or standard I/O tasks.

---

## Performance Considerations

Spawning worker processes carries a startup and serialization cost, meaning that for very fast callbacks the overhead can outweigh the parallel performance benefit. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency independently of whichever executor is selected for callbacks.

<!-- synthesized-for: 3.9.2 -->
