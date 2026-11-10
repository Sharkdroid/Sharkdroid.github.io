# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization
- Large-file parsing and processing
- Heavy data transformations
- Bulk regular expression operations on large HTML bodies
- Light callbacks (like title string replacement or a simple metadata dictionary update) do not need it and perform better with the default `ThreadPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a top-level function so it can be pickled
def optimize_image(asset):
    # Perform heavy CPU-bound processing
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

`ProcessPoolExecutor` provides true parallelism by running tasks in separate processes with separate memory spaces, but requires all callbacks and data to be picklable and incurs higher startup overhead. `ThreadPoolExecutor` (the default) shares memory and has lower overhead, making it ideal for I/O-bound work, but remains constrained by the Global Interpreter Lock (GIL) for CPU-bound tasks. Choose `ProcessPoolExecutor` for heavy CPU-bound tasks and `ThreadPoolExecutor` for general I/O-bound operations.

---

## Performance Considerations

Spawning worker processes has an upfront startup cost, so for very fast callbacks the IPC and pickling overhead may outweigh the concurrency benefit. Additionally, the driver's underlying request semaphore (`MAX_REQUESTS`) still governs HTTP concurrency independently of whichever executor you pass for your callbacks.

<!-- synthesized-for: 3.9.2 -->
