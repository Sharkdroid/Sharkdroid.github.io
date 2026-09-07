# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, and format optimization (e.g., optimizing heavy binary assets).
- Large-file parsing and heavy data transformations across extensive payload hierarchies.
- Bulk regular expression operations on large HTML bodies or rich text content.
- Light callbacks (title string replacement, metadata dictionary updates) do not need it and perform better running directly on the event loop or via the default `ThreadPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "production",
    "API_KEY": "bearer-token",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

def optimize_image(asset):
    # CPU-heavy image processing task
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by utilizing separate memory spaces, but requires all callbacks and data to be picklable and carries a higher task startup overhead. `ThreadPoolExecutor` uses shared memory with negligible overhead and requires no pickling, but remains limited by the Global Interpreter Lock (GIL), making it ineffective for heavy CPU-bound computation. Use `ProcessPoolExecutor` for CPU-heavy tasks and `ThreadPoolExecutor` (or the default executor behavior) for I/O-bound workflows.

---

## Performance Considerations

Spawning and managing worker processes incurs an initial startup cost, meaning very fast callbacks may execute slower under a process pool due to serialization overhead. Additionally, choosing an executor only affects sync callback execution; the driver's underlying HTTP concurrency remains strictly governed by the request semaphore limits.

<!-- synthesized-for: 3.1.3 -->
