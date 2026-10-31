# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization
- Large-file parsing and heavy data transformation
- Bulk regular expression operations on large HTML bodies
- For light callbacks (such as a simple title string replacement or metadata dictionary update), the default `ThreadPoolExecutor` or standard loop execution is preferred since they avoid process-spawning overhead.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

# Module-level function for pickling compatibility
def optimize_image(asset):
    # CPU-heavy image processing logic here
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

`ProcessPoolExecutor` provides true parallelism by running tasks in separate Python processes with isolated memory spaces, making it ideal for CPU-bound tasks, though it requires functions to be picklable and introduces process-spawning overhead. `ThreadPoolExecutor` runs tasks concurrently within the same process sharing memory, which is faster for I/O-bound operations and does not require pickling, but remains restricted by the Global Interpreter Lock (GIL) for CPU-bound execution.

---

## Performance Considerations

Spawning and managing worker processes carries a startup cost, so for very fast callbacks the serialization overhead can outweigh the parallel execution benefits. Additionally, network request concurrency remains governed by the driver's underlying semaphore limit regardless of which executor is selected for callbacks.

<!-- synthesized-for: 3.9.2 -->
