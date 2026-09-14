# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, optimization, and format conversion
- Parsing large files or heavy data transformation
- Executing bulk regular expression matches on large HTML bodies
- Heavy computational tasks that would otherwise block the event loop

Light callbacks—such as a simple title string replacement or metadata dictionary update—run fast enough in memory that they do not need a process pool.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-api-key",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

def optimize_image(asset):
    # CPU-bound image optimization logic
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, making it ideal for CPU-heavy tasks, though it requires picklable functions and has higher startup overhead. `ThreadPoolExecutor` uses shared memory with no pickling overhead, but remains constrained by Python's Global Interpreter Lock (GIL), meaning it is better suited for I/O-bound work or mixed workloads. Use `ProcessPool` for heavy computation and `ThreadPool` (or the default executor) for standard requests and light operations.

---

## Performance Considerations

Spawning worker processes carries a startup and serialization overhead; for very fast callbacks, this inter-process communication cost can exceed the processing time gained. Additionally, regardless of whether you choose a thread pool or process pool for your callbacks, the driver's underlying `MAX_REQUESTS` semaphore continues to govern all concurrent HTTP request traffic sent to the Cascade CMS instance.

<!-- synthesized-for: 3.1.5 -->
