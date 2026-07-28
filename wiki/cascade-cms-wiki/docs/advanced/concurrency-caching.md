---
layout: default
title: Concurrency & Caching
parent: Advanced Topics
nav_order: 1
---

# Concurrency & Caching

Internals for users who need to understand or tune how the library executes requests and manages the response cache.

---

## 1. The event loop

Each `CascadeWrapperBase` instance creates a dedicated `asyncio` event loop via `asyncio.new_event_loop()`. This loop is reused for the entire lifetime of the session — it is not created per request or per `submit_requests()` call.

All HTTP I/O, cache reads/writes, and async callback execution run on this loop. `submit_requests()` blocks the calling thread (via `eventLoop.run_until_complete()`) until the batch finishes.

---

## 2. Concurrency limit

`CascadeCMSRestDriver.MAX_REQUESTS = 50` is the maximum number of in-flight HTTP requests at one time. It is enforced with an `asyncio.Semaphore`:

```python
sem = asyncio.Semaphore(self.MAX_REQUESTS)
```

If you queue 500 requests, 50 execute immediately. Each time one completes, the semaphore releases and another starts. You do not need to batch requests manually — the semaphore manages the queue automatically.

Results arrive in **completion order** via `asyncio.as_completed()`, not submission order. If ordering matters for your processing logic, filter by asset type, identifier, or a field value rather than index position.

---

## 3. How a single request executes

Each `RequestExecutor.fetch()` call follows this path:

```
1. Acquire semaphore slot
2. Serialize payload (if any) → bytes
3. Build cache key from (method, url)
4. Check SQLite cache
   ├── HIT  → read raw bytes from cache → parse → release semaphore → return
   └── MISS → issue HTTP request via aiohttp
               → raise_for_status() (4xx/5xx raises immediately)
               → read response bytes
               → parse bytes with parser function
               ├── _cacheable=True  → write to SQLite cache
               └── _cacheable=False → skip cache write
               → release semaphore → return
```

A `CascadeError` response sets `_cacheable=False` — error responses are never written to the cache.

---

## 4. Cache internals

The cache is an `aiohttp-client-cache` `SQLiteBackend`. The database stores raw HTTP response bytes keyed by `(method, url)`.

**What is cached:**
- Only `GET` responses (enforced by `allowed_methods`)
- Only HTTP 200 responses (enforced by `allowed_codes`)
- Only responses where parsing succeeded (`_cacheable=True`)

**What is never cached:**
- `POST` and `PUT` requests
- `CascadeError` responses (API-level failures)
- Responses that raise Python exceptions during parsing

**Cache key collision:** If the same URL is read with different session headers (e.g., different API keys), the cached response from the first request may be returned for the second. The cache key does not include headers. Use separate cache files for separate API contexts.

**Clearing the cache:** Delete `./cache/cache.sqlite` (or wherever you pointed `cache_name`). There is no programmatic flush API exposed by the library.

---

## 5. Callback execution model

After HTTP results are collected, `submit_requests()` runs callbacks via a second `run_until_complete()` call on the same event loop.

```
submit_requests()
  └── _driver._submitRequests()         → HTTP batch
  └── _execute_all_callbacks(results)   → asyncio.gather over all results
       ├── result_1: [cb1, cb2, cb3]    → sequential per result
       ├── result_2: [cb1, cb2, cb3]    → concurrent across results
       └── result_3: [cb1, cb2, cb3]
```

- **Callbacks on a single result** run sequentially: `cb1` must finish before `cb2` starts.
- **Callbacks across results** run concurrently: `result_1` and `result_2` process their chains in parallel (bounded by the event loop and executor).

**Async callbacks** (`async def`) are awaited directly in the event loop.

**Sync callbacks** run in a `ThreadPoolExecutor` via `loop.run_in_executor()`, which returns a coroutine the event loop can await without blocking.

---

## 6. Tuning ProcessPoolExecutor

When passing a `ProcessPoolExecutor`, `max_workers` controls the worker pool size. `cpu_count()` is a reasonable default:

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

# Saturate all cores
executor = ProcessPoolExecutor(max_workers=cpu_count())

# Leave headroom for the main process and OS
executor = ProcessPoolExecutor(max_workers=max(1, cpu_count() - 2))
```

Each worker process imports your module. Avoid expensive module-level initialization that shouldn't run in workers.

---

## 7. Error propagation

**Python exceptions** (network timeouts, parse errors, unexpected response shapes) inside `fetch()` are caught in `process_executors()`, logged, and excluded from the returned results list. The batch continues.

**CascadeError** objects (API-level failures) are included in the returned results list alongside successes. Filter them explicitly if needed:

```python
from cascade_cms.cmstypes import CascadeError

results = cascade.submit_requests()
successes = [r for r in results if not isinstance(r, CascadeError)]
```

**Callback exceptions** are caught inside `_execute_callbacks_on_result()`. The exception is logged, and execution continues with the next callback in the chain. A failing callback does not skip remaining callbacks or stop processing other results.

---

## 8. Memory considerations for large batches

Parsed response objects are held in memory until `submit_requests()` returns. For very large batches:

- Queue no more than a few thousand requests per `submit_requests()` call
- Process results inside the `with` block before queuing the next batch
- The SQLite cache stores raw bytes separately from the in-memory parsed objects

```python
BATCH_SIZE = 200

with CascadeWrapperBase(env, config) as cascade:
    for i in range(0, len(all_ids), BATCH_SIZE):
        batch = all_ids[i : i + BATCH_SIZE]
        cascade.operations.read(batch)
        results = cascade.submit_requests(Asset)

        for asset in results:
            process(asset)  # process before next batch loads
```
