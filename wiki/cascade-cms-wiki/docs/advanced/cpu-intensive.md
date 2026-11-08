# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing, compression, or other heavy visual asset optimization.
- Parsing and manipulating very large XML/HTML bodies or files.
- Executing complex, compute-intensive data transformations on metadata.
- Running bulk regular expression operations across large text fields.
- Contrast with light callbacks (e.g., title string replacement, simple metadata dictionary updates), which execute quickly in-process and do not require `ProcessPoolExecutor`.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

def optimize_image(asset):
    # Perform heavy CPU-bound image processing here
    return asset

with Cascade(env_vars) as cascade:
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

`ProcessPoolExecutor` provides true parallelism by running callbacks in separate worker processes with independent memory spaces, making it ideal for CPU-bound tasks, though it incurs higher startup overhead and requires picklable functions. `ThreadPoolExecutor` runs tasks concurrently within the same process sharing memory with lower overhead, but Python's Global Interpreter Lock (GIL) prevents it from achieving true parallelism for CPU-bound work. Use `ProcessPoolExecutor` for heavy compute operations and `ThreadPoolExecutor` (the default) for standard I/O-bound tasks.

---

## Performance Considerations

Spawning and managing worker processes carries a startup cost, so for very fast, lightweight callbacks the inter-process serialization overhead may actually outweigh the performance benefit. Additionally, keep in mind that the driver's internal request semaphore still governs HTTP concurrency independently of whichever executor you choose for your synchronous callbacks.

<!-- synthesized-for: 3.9.2 -->
