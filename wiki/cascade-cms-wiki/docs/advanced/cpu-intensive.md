# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

* Image resizing, optimization, and compression tasks on binary asset data.
* Heavy data transformation, deep tree-walking, or complex schema mapping on large assets.
* Bulk regular expression replacement or parsing over large HTML/text bodies.
* Light callbacks (title string replacement, small metadata dictionary updates) do not need it and perform better running directly on the event loop or via the default executor.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a top-level function so it can be pickled
def optimize_image(asset):
    # CPU-bound processing on asset data
    return asset

# Initialize the wrapper context and pass a ProcessPoolExecutor to submit_requests
with CascadeWrapperBase(env_vars, config_vars) as cascade:
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-bound tasks, though it requires all task functions to be picklable and introduces higher task startup overhead. `ThreadPoolExecutor` operates within shared memory with lower overhead, making it great for I/O-bound operations, but it remains limited by the Global Interpreter Lock (GIL) and cannot achieve true parallelism for heavy CPU work. Use `ProcessPoolExecutor` for CPU-heavy workloads and stick to `ThreadPoolExecutor` (the default) or direct execution for mixed or I/O-bound work.

---

## Performance Considerations

Spawning and managing worker processes carries a startup cost, so for extremely fast callbacks, the serialization overhead may outweigh the concurrency benefit. Additionally, keep in mind that the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency independently of the executor choice used for sync callbacks.

<!-- synthesized-for: 3.1.3 -->
