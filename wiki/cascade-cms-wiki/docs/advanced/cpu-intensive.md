# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or format conversion
- Parsing and manipulating very large files or JSON structures
- Heavy data transformations and bulk regex operations on large HTML bodies
- Light callbacks (title string replacement, metadata dict updates) should stay on the default thread pool or event loop since they do not need separate process overhead.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

def optimize_image(asset):
    # CPU-heavy image processing here
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, but requires all tasks and callbacks to be picklable and incurs a higher startup overhead per task. `ThreadPoolExecutor` shares memory space with no pickling restrictions and has lower overhead, but remains subject to the Global Interpreter Lock (GIL) and thus cannot achieve true parallelism for CPU-bound work. Use `ProcessPoolExecutor` for CPU-heavy tasks and `ThreadPoolExecutor` for I/O-bound operations.

---

## Performance Considerations

Spawning and managing worker processes carries a startup cost, so for very fast callbacks the serialization overhead can outweigh the performance benefit. Additionally, the driver's underlying request concurrency semaphore (`MAX_REQUESTS`) still governs HTTP networking concurrency independently of whether you choose a thread or process pool for your callbacks.

<!-- synthesized-for: 3.9.2 -->
