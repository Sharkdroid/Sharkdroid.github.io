# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

* Image resizing, compression, or heavy media optimization.
* Parsing extremely large XML or JSON file payloads.
* Complex, heavy data transformations across large batches of assets.
* Intensive regular expression matching or text replacement across large HTML bodies.
* Note: Light callbacks such as simple title string replacements or metadata dictionary updates do not need `ProcessPoolExecutor` and should use the default execution context.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-api-key",
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

`ProcessPoolExecutor` provides true parallelism with separate memory spaces, making it ideal for CPU-bound work, though it requires picklable functions and incurs higher startup overhead. `ThreadPoolExecutor` uses shared memory and lower overhead with no pickling constraints, but remains subject to the Global Interpreter Lock (GIL) and cannot achieve true parallelism for CPU-heavy tasks. Use `ProcessPoolExecutor` for heavy data processing workloads, and `ThreadPoolExecutor` (or the default) for mixed I/O and lightweight tasks.

---

## Performance Considerations

Spawning worker processes has a measurable startup and serialization cost; for extremely fast callbacks, this overhead may outweigh the concurrency benefit. Additionally, the driver's underlying request semaphore (`MAX_REQUESTS`) continues to govern HTTP request concurrency independently from whichever executor is chosen for callbacks.

<!-- synthesized-for: 3.1.6 -->
