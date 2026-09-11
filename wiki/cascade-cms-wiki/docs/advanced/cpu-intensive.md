# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and optimization workflows before saving modified assets.
- Large-file parsing or complex DOM/HTML manipulation on returned asset content.
- Heavy data transformation pipelines that consume significant CPU cycles.
- Bulk regular expression operations executed over large body content.
- Contrast these with light callbacks (such as a simple title string replacement or metadata dictionary update) which execute quickly and do not require offloading.

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

`ProcessPoolExecutor` provides true parallelism with separate memory spaces, making it ideal for CPU-bound tasks, though it requires picklable functions and has a higher task overhead. `ThreadPoolExecutor` (the default) uses shared memory with lower overhead and no pickling constraints, making it great for I/O-bound work, but it remains subject to the GIL and cannot achieve true parallelism for heavy CPU tasks. Use `ProcessPoolExecutor` for CPU-heavy callbacks and `ThreadPoolExecutor` for standard workloads.

---

## Performance Considerations

Spawning worker processes carries a one-time startup and serialization overhead; for very fast callbacks, this overhead may outweigh the concurrency benefit. Additionally, the driver's underlying request concurrency remains governed by its semaphore limits regardless of whether a thread or process executor is chosen for callbacks.

<!-- synthesized-for: 3.1.3 -->
