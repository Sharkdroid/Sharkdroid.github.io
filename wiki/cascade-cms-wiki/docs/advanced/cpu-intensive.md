# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, optimization, and format conversion
- Parsing large XML/JSON structures or bulky asset payloads
- Heavy data transformation and computational analysis on asset content
- Bulk regular expression operations on large HTML bodies
- *Contrast with light callbacks (title string replace, simple metadata dict updates)* that run instantly in memory and do not need a separate process.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import Cascade

def optimize_image(asset):
    # CPU-heavy image processing task defined at module level
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-bound tasks, though it requires picklable functions and incurs higher startup overhead. `ThreadPoolExecutor` uses shared memory with lower task overhead, making it well-suited for I/O-bound operations, but it remains bound by Python's Global Interpreter Lock (GIL) and cannot achieve true parallelism for CPU-heavy workloads. Use `ProcessPoolExecutor` for heavy computational tasks and `ThreadPoolExecutor` (the default) for standard I/O-bound tasks.

---

## Performance Considerations

Spawning worker processes introduces startup and inter-process communication overhead; for very fast callbacks, this overhead can outweigh the parallel execution benefits. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP concurrency independently of whether a synchronous callback executor is provided.

<!-- synthesized-for: 3.9.2 -->
