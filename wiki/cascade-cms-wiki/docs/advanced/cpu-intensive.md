# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or optimization
- Parsing large XML/JSON structures or heavy data transformation
- Running intensive regular expressions across large HTML bodies
- Light callbacks like simple string replacements or metadata dictionary updates do not need it and perform better on the default thread pool or event loop.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms import CascadeWrapperBase

env = {"SERVER": "prod", "API_KEY": "secret", "CASCADE_URL": "https://cascade.example.com"}

def optimize_image(asset):
    # CPU-bound image processing work here
    return asset

with CascadeWrapperBase(env, {}) as cascade:
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, but requires all callback functions and data to be picklable and incurs inter-process communication overhead. `ThreadPoolExecutor` uses shared memory with minimal overhead and no pickling restrictions, but remains limited by Python's Global Interpreter Lock (GIL) for CPU-bound tasks. Use `ProcessPoolExecutor` for heavy CPU computation, and stick with `ThreadPoolExecutor` (the default) for I/O-bound work.

---

## Performance Considerations

Spawning and managing worker processes carries an initialization overhead, meaning extremely fast callbacks may run slower in a process pool than synchronously due to serialization costs. Additionally, offloading CPU work via the executor does not change the network concurrency rules; the driver's underlying `MAX_REQUESTS` semaphore still governs HTTP request limits.

<!-- synthesized-for: 3.1.1 -->
