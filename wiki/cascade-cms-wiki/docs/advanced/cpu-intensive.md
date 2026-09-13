# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or optimization pipelines.
- Parsing very large XML/HTML payloads or unstructured files.
- Heavy cryptographic hashing, serialization, or data transformation.
- Bulk regular expression matching across large text bodies.
- Light callbacks (like title string replacements or simple metadata updates) do not need it and perform better on the default thread pool or event loop.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-token",
    "CASCADE_URL": "https://cascade.example.com/api/v1"
}

def optimize_image(asset):
    # CPU-bound image processing task defined at module level
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by running tasks in separate memory spaces, but it requires all callbacks and data to be picklable and incurs inter-process communication overhead. `ThreadPoolExecutor` uses shared memory with lower startup overhead and no pickling constraints, but it remains bound by Python's Global Interpreter Lock (GIL) and cannot achieve true parallelism for CPU-bound tasks. Use `ProcessPoolExecutor` exclusively for CPU-heavy workloads, and rely on `ThreadPoolExecutor` (or the default runner) for I/O-bound or mixed operations.

---

## Performance Considerations

Spawning and managing worker processes carries a startup cost, so very short or lightweight callbacks may run faster with standard threading or inline execution where process initialization overhead outweighs the parallelism benefit. Additionally, while the executor manages callback concurrency, the underlying driver's request semaphore (`MAX_REQUESTS`) still governs HTTP network concurrency independently.

<!-- synthesized-for: 3.1.5 -->
