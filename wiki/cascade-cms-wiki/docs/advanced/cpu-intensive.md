# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and binary payload optimization before saving back to Cascade CMS.
- Large-file parsing or heavy structural data transformations on deeply nested asset metadata.
- Running complex regular expressions and text replacement over large HTML content bodies.
- Light callbacks (like title string replacement or simple metadata dict updates) run fast enough on the main thread and do not need a process pool.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "production",
    "API_KEY": "bearer-token-here",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

def optimize_image(asset):
    # CPU-bound work executed in a separate worker process
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by utilizing separate memory spaces, but requires all target callbacks to be picklable and introduces higher task-launch overhead. `ThreadPoolExecutor` (which is the default when using sync callbacks without an explicit executor) shares memory, requires no pickling, and has lower overhead, but remains bound by the Global Interpreter Lock (GIL) and cannot achieve true parallelism for heavy CPU work. Use `ProcessPoolExecutor` for CPU-intensive tasks, and rely on `ThreadPoolExecutor` (or default execution) for mixed I/O and light tasks.

---

## Performance Considerations

Spawning and managing worker processes incurs a measurable startup and serialization cost; for extremely fast callbacks, this overhead can outweigh the performance gains of parallelism. Additionally, keep in mind that the underlying HTTP request concurrency remains governed independently by the driver's request semaphore regardless of whether a process pool or thread pool is selected for callbacks.

<!-- synthesized-for: 3.1.5 -->
