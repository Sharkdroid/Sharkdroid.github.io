# CPU-Intensive Tasks

[PLACEHOLDER: 2–3 sentence intro — by default `.then()` callbacks run on the async event loop, which is fine for I/O-bound work (string manipulation, dict transforms) but blocks the loop for CPU-heavy work. `ProcessPoolExecutor` offloads callbacks to separate worker processes to keep the event loop free.]

---

## When to Use `ProcessPoolExecutor`

[PLACEHOLDER: Bullet list of 3–4 scenarios where `ProcessPoolExecutor` is appropriate — e.g. image resizing/optimization, large-file parsing, heavy data transformation, bulk regex on large HTML bodies. Contrast with light callbacks (title string replace, metadata dict update) that don't need it.]

---

## Example

[PLACEHOLDER: Full code block showing the `ProcessPoolExecutor` wrapping a `CascadeWrapperBase` session, with a module-level callback function passed to `.then()`. Show the executor passed as a keyword argument (or however `CascadeWrapperBase`/`then` accepts it — source from wrapper.md or operations.md docstrings). Include inline comments explaining the pattern.]

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

[PLACEHOLDER: Short comparison table or paragraph — ProcessPool: true parallelism, separate memory, requires picklable functions, higher overhead per task; ThreadPool: shared memory, no pickling, lower overhead, still subject to GIL so not truly parallel for CPU-bound work. Recommend ProcessPool for CPU-heavy, ThreadPool for mixed I/O+CPU. 3–5 sentences or a small table.]

---

## Performance Considerations

[PLACEHOLDER: 2–3 sentences on overhead — spawning worker processes has startup cost; for very fast callbacks the overhead may outweigh the benefit. Mention that the existing 50-request semaphore still governs HTTP concurrency regardless of executor choice.]
