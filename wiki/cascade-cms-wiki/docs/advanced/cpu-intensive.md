# CPU-Intensive Tasks

Synchronous callbacks run by default on the thread pool executor (or the main event loop context depending on how the executor is provided). Running CPU-heavy tasks directly in these callbacks can block execution threads and slow down the entire batch of concurrent requests. Using a `ProcessPoolExecutor` offloads this heavy computational work to separate worker processes, freeing up concurrency.

---

## When to Use `ProcessPoolExecutor`

* Resizing or transcoding binary asset attachments (like images or PDFs)
* Parsing very large XML/HTML data structures or files
* Executing heavy regular expression matching and data transformations over large text bodies
* Light callbacks (like simple property setting or logging) that execute instantly do not need a process pool and should remain on default threads.

---

## Example

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.wrapper import Cascade

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
# ✗ Raises a pickling error at runtime:
# cascade.operations.read(id).then(lambda asset: asset)

# ✓ Correct module-level function:
def my_callback(asset):
    return asset

cascade.operations.read(id).then(my_callback)
```

---

## `ProcessPoolExecutor` vs `ThreadPoolExecutor`

The `ThreadPoolExecutor` shares memory and requires no function pickling, making it lightweight and fast for I/O-bound tasks, but the Global Interpreter Lock (GIL) prevents CPU-bound work from running in true parallelism. Conversely, the `ProcessPoolExecutor` provides true multi-core parallelism and separate memory spaces, but demands picklable module-level code and incurs serialization overhead. By default, the library uses a thread pool for I/O-bound work. Use thread pools for network and I/O tasks, and process pools for heavy CPU transformations.

---

## Performance Considerations

Worker process start-up and IPC serialization costs can sometimes outweigh the computational benefits for very fast callbacks. Furthermore, overall network concurrency is bounded by the driver's request limit (`MAX_REQUESTS = 50`) regardless of which executor you choose.

<!-- synthesized-for: 3.10.1 -->
