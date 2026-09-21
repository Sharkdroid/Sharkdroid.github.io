# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, watermarking, or heavy media optimization where processing bytes consumes significant CPU cycles.
- Parsing very large XML/HTML payloads or executing complex regular expressions across extensive text bodies.
- Heavy data transformations and computational aggregations on large asset structures.
- Light callbacks (title string replace, metadata dict update) do not need it and perform better with default execution or a `ThreadPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "production",
    "API_KEY": "bearer_token_123",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

def optimize_image(asset):
    # CPU-heavy image processing task
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by utilizing separate memory spaces, making it ideal for heavy computational tasks, though it requires picklable functions and incurs higher task overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling constraints, but remains bound by the Global Interpreter Lock (GIL), preventing true parallelism for CPU-bound tasks. Use `ProcessPoolExecutor` for CPU-heavy workloads and `ThreadPoolExecutor` for I/O-bound tasks.

---

## Performance Considerations

Spawning worker processes introduces a startup overhead cost, meaning extremely fast callbacks may run slower in a process pool than in the main thread or thread pool. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern concurrent HTTP request execution regardless of which executor is selected for callbacks.

<!-- synthesized-for: 3.1.6 -->
