# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, and format optimization where CPU cycles are heavily consumed.
- Large-file parsing and heavy structured data transformation on retrieved assets.
- Running complex regular expression matching or parsing across large HTML bodies.
- Light callbacks (such as a simple title string replacement or metadata dictionary update) do not need it and should rely on the default executor.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a picklable module-level callback function
def optimize_image(asset):
    # Perform CPU-bound image optimization here
    return asset

with CascadeWrapperBase(env_vars, config_vars) as cascade:
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

| Feature | `ProcessPoolExecutor` | `ThreadPoolExecutor` |
| :--- | :--- | :--- |
| **Concurrency Type** | True parallelism via separate worker processes | Concurrent threads within the same process |
| **Memory Space** | Separate memory space (requires pickling) | Shared memory space (no pickling required) |
| **GIL Impact** | Bypasses the Global Interpreter Lock (GIL) | Subject to the GIL (not truly parallel for CPU-bound work) |
| **Overhead** | Higher overhead per task due to process startup/serialization | Lower overhead; well-suited for I/O-bound tasks |

Use `ProcessPoolExecutor` for CPU-heavy processing, and `ThreadPoolExecutor` (or the default) for I/O-bound or mixed workloads.

---

## Performance Considerations

Spawning worker processes carries a startup cost, so for very fast callbacks the serialization overhead may outweigh the concurrency benefit. Additionally, keep in mind that the driver's request-level concurrency remains governed independently by its internal semaphore limits.

<!-- synthesized-for: 3.1.3 -->
