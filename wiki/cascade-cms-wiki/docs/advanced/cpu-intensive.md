# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization
- Large-file parsing and heavy data transformation
- Bulk regular expression operations on large HTML bodies
- Light callbacks (like title string replacement or simple metadata dictionary updates) do not need it and run efficiently on the default executor.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores with separate memory spaces, but requires all callbacks to be picklable and introduces higher task startup overhead. `ThreadPoolExecutor` runs in shared memory with virtually no overhead and requires no pickling, but is still bound by the Global Interpreter Lock (GIL) and cannot achieve true parallelism for CPU-bound tasks. Use `ProcessPoolExecutor` for heavy CPU computations, and `ThreadPoolExecutor` (the default) for I/O-bound or mixed operations.

---

## Performance Considerations

Spawning and communicating with worker processes incurs a measurable startup and serialization overhead; for very fast callbacks, this overhead can outweigh the parallel execution benefits. Additionally, the driver's underlying request concurrency semaphore (`MAX_REQUESTS`) still governs HTTP networking speed independently of the callback executor choice.

<!-- synthesized-for: 3.9.2 -->
