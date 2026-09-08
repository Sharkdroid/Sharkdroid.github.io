# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization tasks before writing back via `.edit()`
- Large-file parsing or extensive content restructuring
- Heavy data transformation and complex computations on asset bodies
- Bulk regular expression operations on large HTML bodies
- Contrast with light callbacks like title string replacements or metadata dict updates, which execute quickly in-process and do not need a process pool.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

# Define callback at module level so it can be pickled
def optimize_image(asset):
    # Perform CPU-heavy image optimization here
    return asset

env_vars = {
    "SERVER": "prod",
    "API_KEY": "bearer-token",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for heavy computational work, though it requires picklable functions and incurs task-spawning overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling restrictions, making it ideal for I/O-bound work, but it remains constrained by the Global Interpreter Lock (GIL) for CPU-bound tasks. Choose `ProcessPoolExecutor` for heavy CPU processing and `ThreadPoolExecutor` (the default) for standard I/O operations or mixed workloads.

---

## Performance Considerations

Spawning worker processes carries a startup and serialization overhead; for extremely fast callbacks, this overhead may outweigh the benefits of parallel execution. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency independently of the callback executor choice.

<!-- synthesized-for: 3.1.3 -->
