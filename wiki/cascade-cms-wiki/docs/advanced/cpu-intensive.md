# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, optimization, and format conversion
- Parsing large XML/HTML payloads or processing heavy data transformations
- Running bulk regular expression operations on large text bodies
- Light callbacks (such as a simple title string replacement or metadata dictionary update) do not need it and perform better on the default executor or event loop.

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by utilizing separate memory spaces, but requires picklable functions and incurs higher task-serialization overhead. `ThreadPoolExecutor` (the default) uses shared memory with lower overhead and no pickling restrictions, but remains limited by the Global Interpreter Lock (GIL) for CPU-bound tasks. Choose `ProcessPoolExecutor` for CPU-heavy tasks and `ThreadPoolExecutor` for I/O-bound work.

---

## Performance Considerations

Spawning and managing worker processes carries an initial startup overhead, so extremely fast callbacks may run slower under a `ProcessPoolExecutor` than in-thread. Additionally, the driver's underlying request concurrency remains governed by the semaphore, ensuring network requests are properly throttled regardless of which executor is handling synchronous callback execution.

<!-- synthesized-for: 3.2.1 -->
