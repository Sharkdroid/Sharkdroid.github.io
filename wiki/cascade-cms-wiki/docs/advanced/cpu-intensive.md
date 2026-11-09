# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, conversion, or heavy graphical optimization.
- Parsing and manipulating very large XML/HTML payloads or files.
- Executing complex data transformations or intensive calculations on asset metadata.
- Running bulk regular expressions across large text bodies.
- Light callbacks (such as a simple title string replacement or metadata dictionary update) do not need `ProcessPoolExecutor` and run efficiently on the default executor or event loop.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define a module-level helper function for the callback
def optimize_image(asset):
    # Perform CPU-intensive processing here
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores by utilizing separate memory spaces, making it ideal for CPU-bound tasks, though it requires all callbacks and arguments to be picklable and incurs higher task overhead. `ThreadPoolExecutor` uses shared memory with lower overhead and no pickling restrictions, making it great for I/O-bound work, but it remains subject to the Python GIL and is not truly parallel for CPU-heavy processing. Use `ProcessPoolExecutor` for heavy compute operations and `ThreadPoolExecutor` (or the default) for network-bound or mixed I/O and light processing workflows.

---

## Performance Considerations

Spawning and communicating with worker processes incurs a startup and serialization cost; for very fast callbacks, this overhead can outweigh the parallel execution benefits. Additionally, the driver's underlying `MAX_REQUESTS` semaphore continues to govern HTTP concurrency independently of whether you use a thread or process pool for your callback functions.

<!-- synthesized-for: 3.9.2 -->
