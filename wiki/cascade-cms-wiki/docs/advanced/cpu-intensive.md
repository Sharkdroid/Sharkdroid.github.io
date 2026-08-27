# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Heavy image resizing, compression, or format conversion pipelines.
- Large-scale HTML or XML payload parsing and DOM manipulation.
- Complex data transformation routines computing deep nested structures.
- Bulk regex matching or string replacement across large text blocks.
- Light callbacks (like a simple title string replacement or metadata dictionary update) do not need it and perform better on the default event loop or `ThreadPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import CascadeWrapperBase

# Define callback at module level so it is picklable
def optimize_image(asset):
    # Perform heavy CPU-bound processing here
    return asset

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-api-key",
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

The `ProcessPoolExecutor` provides true parallelism by running tasks in separate memory spaces, making it ideal for CPU-bound callbacks, though it requires picklable functions and incurs higher inter-process communication overhead. Conversely, `ThreadPoolExecutor` operates within shared memory with lower startup overhead and no pickling constraints, but remains constrained by Python's Global Interpreter Lock (GIL) for CPU-heavy tasks. Use `ProcessPoolExecutor` for heavy computational pipelines and `ThreadPoolExecutor` for general I/O-bound operations.

---

## Performance Considerations

Spawning and managing worker processes carries a startup overhead, meaning that extremely fast callbacks may run slower in a process pool due to serialization delays than they would on the main thread. Additionally, choosing an executor only affects sync callback execution; HTTP request concurrency to Cascade CMS is independently governed by the driver's request semaphore.

<!-- synthesized-for: 3.1.1 -->
