# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

* Image resizing, compression, or other heavy visual optimization tasks.
* Parsing very large files or extensive asset data structures.
* Heavy data transformation or complex numerical analysis on asset metadata.
* Running bulk regular expressions across large HTML bodies.
* Note: Light callbacks such as simple title string replacements or metadata dictionary updates do not need `ProcessPoolExecutor` and should use the default thread pool or synchronous execution.

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores with separate memory spaces, making it ideal for heavy computational workloads, though it requires all task functions to be picklable and carries a higher overhead per task. `ThreadPoolExecutor` uses shared memory with lower startup overhead and no pickling constraints, but remains subject to the Global Interpreter Lock (GIL) and is thus best suited for I/O-bound operations or mixed workloads where true CPU parallelism is unnecessary.

---

## Performance Considerations

Spawning and managing worker processes involves initialization and serialization overhead, so for extremely fast callbacks, the inter-process communication cost may outweigh the parallelism benefits. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP request concurrency regardless of which executor is selected for callbacks.

<!-- synthesized-for: 3.1.5 -->
