# CPU-Intensive Tasks

By default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.

---

## When to Use `ProcessPoolExecutor`

* Image resizing, compression, or optimization
* Large-file parsing and heavy data transformation
* Bulk regular expression matching across large HTML bodies
* Light callbacks (title string replace, metadata dict update) that do not require process separation and run efficiently on the default executor

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Wrap the Cascade session and pass a ProcessPoolExecutor to submit_requests()
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

`ProcessPoolExecutor` provides true parallelism across multiple CPU cores in separate memory spaces, but requires picklable functions and incurs higher inter-process communication overhead. `ThreadPoolExecutor` shares memory and has lower task overhead, but remains bound by the Global Interpreter Lock (GIL), preventing true parallelism for CPU-heavy work. Use `ProcessPoolExecutor` for CPU-intensive tasks and `ThreadPoolExecutor` (the default) for I/O-bound tasks.

---

## Performance Considerations

Spawning and maintaining worker processes introduces an initial startup overhead, meaning very fast callbacks may execute slower under a process pool than in the main thread. Additionally, the driver's underlying request limits and semaphores continue to govern HTTP concurrency independently of the callback executor choice.

<!-- synthesized-for: 3.1.3 -->
