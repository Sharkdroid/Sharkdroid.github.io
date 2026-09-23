# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

- Image resizing and binary asset optimization
- Parsing large XML or JSON file payloads
- Heavy data transformations and complex business logic processing
- Bulk regular expression operations on large HTML bodies
- Light callbacks (like simple title string replacements or metadata dictionary updates) run fast enough on the main thread and do not need a process pool.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Define the CPU-bound callback at module level for pickling support
def optimize_image(asset):
    # Perform heavy image optimization work here
    return asset

env_vars = {
    "SERVER": "myserver",
    "API_KEY": "my-token",
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

`ProcessPoolExecutor` provides true parallelism across separate memory spaces, making it ideal for CPU-bound tasks, though it requires functions to be picklable and incurs higher task overhead. `ThreadPoolExecutor` uses shared memory with lower overhead, but because of Python's Global Interpreter Lock (GIL), threads cannot run CPU-heavy Python bytecode in parallel. Use `ProcessPoolExecutor` for heavy computational tasks and `ThreadPoolExecutor` (the default) for I/O-bound work.

---

## Performance Considerations

Spawning worker processes has a startup and IPC cost; for very fast callbacks, this overhead may outweigh the concurrency benefit. Additionally, keep in mind that the driver's underlying request concurrency semaphore still governs HTTP interactions independently of the chosen callback executor.

<!-- synthesized-for: 3.1.6 -->
