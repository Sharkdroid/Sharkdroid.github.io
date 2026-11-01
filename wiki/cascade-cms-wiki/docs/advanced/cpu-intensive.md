# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or other heavy graphical transformations
- Parsing and manipulating very large files or payloads
- Performing heavy data transformation or cryptographic hashing across multiple records
- Running bulk regular expressions or heavy string analysis on large HTML bodies
- *Contrast with light callbacks:* Title string replacements, simple metadata dictionary updates, or minor logging additions execute quickly and do not need offloading.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, but requires all callbacks and arguments to be picklable and carries a higher task-spawning overhead. `ThreadPoolExecutor` shares memory space and incurs lower task overhead, but remains bound by the Global Interpreter Lock (GIL) and is best suited for I/O-bound work. Use `ProcessPoolExecutor` for CPU-heavy transformations and `ThreadPoolExecutor` (the default) for lighter or mixed workloads.

---

## Performance Considerations

Spawning and communicating with worker processes incurs a startup overhead; for very fast callbacks, this overhead can exceed the performance gain of parallel execution. Note that the driver's underlying semaphore (`MAX_REQUESTS`) continues to govern HTTP request concurrency regardless of which executor is selected for callbacks.

<!-- synthesized-for: 3.9.2 -->
