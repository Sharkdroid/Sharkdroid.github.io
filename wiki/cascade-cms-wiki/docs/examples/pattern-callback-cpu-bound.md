---
layout: default
title: CPU-Bound Callbacks
parent: Examples & Patterns
nav_order: 9
---

# CPU-bound callbacks with ProcessPoolExecutor

By default, sync callbacks run in a `ThreadPoolExecutor` — appropriate for I/O-bound work. For CPU-intensive processing (image compression, PDF generation, ML inference), use `ProcessPoolExecutor` for true parallelism that bypasses the Python GIL.

## Requirements

**Callbacks must be module-level functions.** `ProcessPoolExecutor` pickles functions to send them to worker processes. Lambdas, closures, and nested functions cannot be pickled and will raise a `PicklingError`. Define callbacks at the top level of your module.

## Example: parallel image optimization

```python
import os
from uuid import UUID
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count
from cascade_cms.cmstypes import Asset, IdentifierType
from cascade_cms.wrapper import CascadeWrapperBase

load_dotenv()

env = {
    "API_KEY": os.environ["CASCADE_API_KEY"],
    "CASCADE_URL": os.environ["CASCADE_URL"],
    "SERVER": os.environ["SERVER"],
}
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}


# Must be at module level — not inside a function, class, or lambda
def optimize_image(asset: Asset):
    """
    CPU-bound: compress binary image data in-place.
    This runs in a separate worker process, not the main thread.
    """
    blob = asset.get("blob")
    if not blob:
        return

    # Replace with your actual image processing logic
    # e.g., Pillow, OpenCV, wand, etc.
    # optimized = compress(blob, quality=75)
    # asset["blob"] = optimized

    name = asset.get("name", "unknown")
    size = len(blob)
    print(f"Optimized {name}: {size} bytes → (compressed)")


def log_result(asset: Asset):
    """Secondary callback: runs after optimize_image on each asset."""
    print(f"Done: {asset.get('name')}")


if __name__ == "__main__":
    image_ids = [
        IdentifierType(identifier=UUID("aaa..."), asset_type="file"),
        IdentifierType(identifier=UUID("bbb..."), asset_type="file"),
        IdentifierType(identifier=UUID("ccc..."), asset_type="file"),
        IdentifierType(identifier=UUID("ddd..."), asset_type="file"),
    ]

    # ProcessPoolExecutor: true parallelism across CPU cores
    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        with CascadeWrapperBase(env, config) as cascade:
            cascade.operations.read(image_ids).then([optimize_image, log_result])
            results = cascade.submit_requests(executor=executor)

    print(f"Processed {len(results)} images")
```

## ThreadPoolExecutor vs ProcessPoolExecutor

| | ThreadPoolExecutor | ProcessPoolExecutor |
|--|---|---|
| **Parallelism** | Concurrent (I/O overlap) | True parallel (separate processes) |
| **GIL** | Shared — CPU-bound tasks block each other | Bypassed — each worker has its own GIL |
| **Use for** | HTTP calls, file writes, database inserts | Image processing, ML inference, PDF rendering |
| **Function requirement** | Any callable | Module-level only (must be picklable) |
| **Default** | Yes (when no executor passed) | Opt-in via `submit_requests(executor=...)` |

## The `if __name__ == "__main__"` guard

This guard is **required** when using `ProcessPoolExecutor` on Windows and recommended on all platforms. Without it, worker processes import the script and trigger recursive process spawning.

## Combining with non-CPU callbacks

You can chain CPU-bound and non-CPU-bound callbacks. The executor applies to all sync callbacks:

```python
cascade.operations.read(ids).then([optimize_image, log_result])
# Both optimize_image and log_result run in the ProcessPoolExecutor workers
```

If you need one callback to run in the main thread, separate the submit calls:

```python
# First pass: CPU work in workers
with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    cascade.operations.read(ids).then(optimize_image)
    results = cascade.submit_requests(executor=executor)

# Second pass: I/O work in default ThreadPoolExecutor
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.edit(results).then(log_result)
    cascade.submit_requests()
```

---

See also: [Core Concepts: Executors](../core-concepts/index.md#6-executors-threadpoolexecutor-vs-processpoolexecutor) · [Callback chain](./pattern-callback-chain.md)
