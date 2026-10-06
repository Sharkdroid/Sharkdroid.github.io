# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or optimization
- Parsing very large XML/HTML payloads or files
- Heavy data transformations and structural recalculations
- Bulk regular expression operations across large text bodies

For light callbacks like title string replacements or minor metadata dictionary updates, the default thread pool or standard execution is sufficient and avoids process-spawning overhead.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a picklable, module-level function for CPU-bound work
def optimize_image(asset):
    # Heavy image processing logic here
    return asset

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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by utilizing separate memory spaces, making it ideal for CPU-bound work, though it requires picklable functions and incurs higher task overhead. `ThreadPoolExecutor` (the default) uses shared memory with minimal overhead and no pickling requirements, but remains constrained by the Global Interpreter Lock (GIL) for CPU-bound tasks. Use `ProcessPoolExecutor` for heavy computation, and `ThreadPoolExecutor` for I/O-bound operations or mixed workflows.

---

## Performance Considerations

Spawning and managing worker processes carries a one-time startup cost, meaning that for extremely fast callbacks the inter-process serialization overhead may actually outweigh the performance benefits. Additionally, note that the driver's underlying 50-request concurrency semaphore continues to govern HTTP request limits independently of whichever executor you choose for your synchronous callbacks.

<!-- synthesized-for: 3.9.1 -->
