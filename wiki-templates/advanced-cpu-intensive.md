<!-- purpose: Show when and how to run CPU-heavy callbacks in worker processes instead of on the event loop, the pickling rule that comes with it, and the trade-offs. The reader knows chains and callbacks from Core Concepts. -->
<!-- focus: Cascade, submit_requests, then, execute, execute_async, MAX_REQUESTS, ProcessPoolExecutor, ThreadPoolExecutor, executor -->
# CPU-Intensive Tasks

[PLACEHOLDER: 2–3 sentence intro: where synchronous callbacks run by default (state this exactly as the code facts' docstrings describe it), why CPU-heavy work there slows the whole batch, and that a process pool moves it to worker processes.]

---

## When to Use `ProcessPoolExecutor`

[PLACEHOLDER: Bullet list of 3–4 CPU-heavy callback jobs (e.g. image resizing, parsing large files, heavy regex over big HTML bodies), then one bullet contrasting light callbacks that don't need it.]

---

## Example

[PLACEHOLDER: Full code block: a module-level CPU-bound callback attached to a chain, a `ProcessPoolExecutor` created with a worker count, and the executor handed to the library exactly where the code facts show it is accepted (that method and keyword name). Inline comments explain each step.]

---

## Pickling Constraint

Callbacks executed in a `ProcessPoolExecutor` must be **defined at module level**. Python's `multiprocessing` serializes functions via `pickle`, which cannot handle:

- Lambda functions
- Nested/inner functions defined inside another function or class method
- Closures that capture local variables

[PLACEHOLDER: Short code block contrasting a lambda callback (marked ✗, raises a pickling error at runtime) with an equivalent module-level function (marked ✓), both attached to a chain the way the code facts show.]

---

## `ProcessPoolExecutor` vs `ThreadPoolExecutor`

[PLACEHOLDER: Small table or 3–5 sentences: process pool gives true parallelism and separate memory, needs picklable callbacks and costs more per task; thread pool shares memory, needs no pickling and is cheaper, but the GIL keeps CPU-bound work from running in parallel. Say which one the library uses when none is given, if the code facts state it, and recommend each for its case.]

---

## Performance Considerations

[PLACEHOLDER: 2–3 sentences: worker start-up cost can outweigh the benefit for fast callbacks, and HTTP concurrency is capped by the driver's request limit whichever executor you use (give the number from the code facts).]
