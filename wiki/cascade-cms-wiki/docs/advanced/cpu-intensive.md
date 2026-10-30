# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and pixel optimization
- Large-file parsing and heavy data transformation
- Bulk regular expression operations on large HTML bodies
- Complex schema validation or cryptographic hashing

Contrast with light callbacks (title string replacement, metadata dictionary updates) that execute instantly and do not need multi-processing.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

def optimize_image(asset):
    # CPU-heavy image optimization logic
    return asset

with Cascade(env_vars) as cascade:
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores with isolated memory spaces, but requires all tasks and functions to be picklable and incurs a higher startup overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling constraints, but remains constrained by the Global Interpreter Lock (GIL), making it ideal for mixed I/O and light tasks while ProcessPoolExecutor is suited for CPU-heavy work.

---

## Performance Considerations

Spawning and managing worker processes carries a distinct startup and serialization overhead; for very fast callbacks, this overhead can outweigh the performance benefit of parallelism. Note that the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency regardless of which executor is selected for callbacks.

<!-- synthesized-for: 3.9.2 -->
