# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization workflows before saving modified assets.
- Large-file parsing or heavy data transformations on asset payloads.
- Bulk regex searches and replacements across large HTML bodies.
- Light callbacks (title string replaces, simple metadata dict updates) do not need it and perform better running directly on the event loop via `ThreadPoolExecutor` or the default path.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a picklable module-level callback function
def optimize_image(asset):
    # Perform heavy CPU-bound image processing
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-bound tasks, but it requires all callbacks and arguments to be picklable and incurs higher startup overhead. `ThreadPoolExecutor` operates within shared memory with lower overhead and no pickling constraints, but remains subject to the Global Interpreter Lock (GIL), preventing true parallelism for CPU-heavy workloads. Use `ProcessPoolExecutor` for CPU-heavy transformations and `ThreadPoolExecutor` (the default) for I/O-bound work.

---

## Performance Considerations

Spawning separate worker processes incurs a one-time startup cost, meaning very fast callbacks might execute slower under a `ProcessPoolExecutor` due to IPC and serialization overhead than they would running synchronously. Additionally, choose your `max_workers` carefully (e.g., using `cpu_count()`) to avoid thread or process thrashing, keeping in mind that the underlying driver's request semaphore still governs HTTP concurrency independently of your callback executor choice.

<!-- synthesized-for: 3.1.6 -->
