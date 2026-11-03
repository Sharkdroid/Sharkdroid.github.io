# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or other heavy visual asset optimization.
- Parsing extremely large JSON, XML, or HTML document trees.
- Heavy data transformations involving extensive mathematical calculations or complex business logic.
- Running intensive regular expressions or bulk text processing on massive content bodies.
- *Contrast:* Light callbacks like a simple title string replacement, tag appending, or metadata dictionary update are fast enough to run directly on the event loop (using the default `ThreadPoolExecutor` or inline) without the serialization overhead of a `ProcessPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Module-level callback required for pickling
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-bound tasks, but it requires picklable functions and incurs higher task startup overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling constraints, but it remains bound by Python's Global Interpreter Lock (GIL), meaning it cannot achieve true parallelism for CPU-heavy computations. Use `ProcessPoolExecutor` for heavy CPU workloads and `ThreadPoolExecutor` (the default) for I/O-bound or lightweight work.

---

## Performance Considerations

Spawning and communicating with separate worker processes introduces serialization and inter-process communication overhead, so very fast callbacks may execute slower under a `ProcessPoolExecutor` than in the default thread pool. Additionally, the driver's `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency independently of whichever executor is chosen for synchronous callbacks.

<!-- synthesized-for: 3.9.2 -->
