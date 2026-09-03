# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization tasks before writing back via `edit()`.
- Parsing large files or heavy data transformation.
- Running bulk regular expression operations on large HTML bodies.
- Light callbacks (such as a title string replacement or metadata dictionary update) do not need it and run efficiently on the default executor.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Module-level callback function (required for pickling)
def optimize_image(asset):
    # Perform heavy CPU-bound image processing here
    return asset

with CascadeWrapperBase(env_vars, config_vars) as cascade:
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores with separate memory spaces, but requires all functions and data to be picklable and carries a higher overhead per task. `ThreadPoolExecutor` uses shared memory, avoids pickling restrictions, and features lower overhead, but remains restricted by Python's Global Interpreter Lock (GIL) and cannot achieve true parallelism for CPU-bound tasks. Use `ProcessPoolExecutor` for heavy CPU workloads, while `ThreadPoolExecutor` is the default and works fine for I/O-bound work.

---

## Performance Considerations

Spawning worker processes introduces startup and inter-process communication overhead; for very fast callbacks, this overhead may outweigh the parallelism benefits. Note that the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency independently of whichever executor is chosen for callbacks.

<!-- synthesized-for: 3.1.3 -->
