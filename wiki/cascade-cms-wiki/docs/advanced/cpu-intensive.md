# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and pixel manipulation
- Large-file parsing or heavy data transformation
- Bulk regular expression operations on large HTML bodies
- Complex schema validation or cryptographic hashing

Light callbacks like title string replacements or simple metadata dictionary updates do not need `ProcessPoolExecutor` and run efficiently directly on the event loop or via the default `ThreadPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

# Module-level callback required for pickling
def optimize_image(asset):
    # Perform CPU-heavy image optimization here
    return asset

env_vars = {
    "SERVER": "production",
    "API_KEY": "your-api-key",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

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

`ProcessPoolExecutor` provides true parallelism in separate memory spaces, making it ideal for CPU-bound tasks, though it requires picklable functions and incurs higher task-startup overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling restrictions, but remains limited by the Global Interpreter Lock (GIL) for CPU-bound tasks. Use `ProcessPoolExecutor` for heavy computation, and `ThreadPoolExecutor` (the default) for I/O-bound work.

---

## Performance Considerations

Spawning worker processes carries a startup cost, so very fast callbacks may execute slower under a `ProcessPoolExecutor` due to inter-process communication overhead. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP concurrency independently of whichever executor is chosen for sync callbacks.

<!-- synthesized-for: 3.9.2 -->
