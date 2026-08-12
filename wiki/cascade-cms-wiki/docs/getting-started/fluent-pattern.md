---
layout: default
title: The Fluent Pattern
parent: Getting Started
nav_order: 3
---

# The Fluent Pattern

Every script using this library follows the same three-step cycle:

1. **Queue** operations on `cascade.operations`
2. **Submit** all queued operations at once with `cascade.submit_requests()`
3. **Collect** and use the results

This means HTTP requests are batched and executed concurrently — you queue everything first, then fire them all together.

## The context manager

```python
with CascadeWrapperBase(env, config) as cascade:
    # Step 1: queue
    cascade.operations.read(identifier)

    # Step 2: submit (executes all queued requests)
    results = cascade.submit_requests(Asset)

# Session is closed automatically on exit
```

`CascadeWrapperBase` handles the HTTP session, event loop, cache, and logger. The `with` block ensures everything closes cleanly even if an exception occurs.

## Queuing multiple operations

Operations accumulate until `submit_requests()` is called. They all execute concurrently.

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(id_a)
    cascade.operations.read(id_b)
    cascade.operations.read(id_c)

    # All three fire concurrently
    results = cascade.submit_requests(Asset)
    # results has up to 3 Asset objects
```

## Calling submit_requests() multiple times

You can call `submit_requests()` multiple times in one session. Each call executes whatever has been queued since the last call.

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(page_id)
    pages = cascade.submit_requests(Asset)

    # Use the results to queue more work
    page = pages[0]
    page["displayName"] = "Updated title"
    cascade.operations.edit(page)
    cascade.submit_requests()
```

## The type hint on submit_requests()

The `result_type` argument is a type hint for static analysis tools (Pylance, mypy). It does not change runtime behavior — it tells your editor what type to expect in the returned list.

```python
results = cascade.submit_requests(Asset)      # type: List[Asset]
results = cascade.submit_requests(IdentifierType)  # type: List[IdentifierType]
results = cascade.submit_requests()           # type: List[CascadeObjects]
```

## Adding callbacks

The `.then()` method on operations registers functions to run on each result after `submit_requests()` completes.

```python
def print_name(asset):
    print(asset.get("name"))

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(identifiers).then(print_name)
    cascade.submit_requests(Asset)
    # print_name is called once per result
```

Callbacks are optional. See [Examples & Patterns](../examples/index.md) for all the ways to use them.

## Controlling callback execution with executor

`submit_requests()` also takes an optional, keyword-only `executor` argument. It controls how *synchronous* callbacks (registered via `.then()`) are run.

```python
results = cascade.submit_requests(Asset)  # executor defaults to None
```

By default (`executor=None`), sync callbacks run on the event loop's default `ThreadPoolExecutor` — lightweight, and fine for I/O-bound callbacks. For CPU-bound callbacks (image optimization, etc.), pass a `ProcessPoolExecutor` for true parallelism:

```python
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    cascade.operations.read(identifiers).then(optimize_image)
    results = cascade.submit_requests(Asset, executor=executor)
```

Async callbacks (`async def`) ignore `executor` entirely — they're awaited directly on the event loop regardless of what's passed.

---

Next: [Core Concepts](../core-concepts/index.md) — the design philosophy behind these patterns, or jump to [Examples](../examples/index.md) to see the library in action.
