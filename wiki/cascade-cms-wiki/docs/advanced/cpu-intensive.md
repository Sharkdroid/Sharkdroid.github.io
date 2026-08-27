# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization tasks.
- Parsing large files or heavy data transformation.
- Running bulk regular expressions across large HTML bodies.
- Light callbacks (like title string replacement or metadata dictionary updates) do not need it and perform better on the default executor.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a picklable module-level callback function
def optimize_image(asset):
    # CPU-heavy image processing logic here
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

`ProcessPoolExecutor` provides true parallelism in separate memory spaces, making it ideal for CPU-bound work, though it requires functions to be picklable and incurs higher task overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling constraints, but remains subject to the Python GIL, making it suitable for mixed I/O and lightweight operations rather than heavy computation.

---

## Performance Considerations

Spawning worker processes carries a startup cost, so for very fast callbacks the process overhead may outweigh any performance benefit. Additionally, the driver's underlying request semaphore (`MAX_REQUESTS`) still governs HTTP concurrency across your batch regardless of which executor you choose for your callbacks.

<!-- synthesized-for: 3.1.1 -->
