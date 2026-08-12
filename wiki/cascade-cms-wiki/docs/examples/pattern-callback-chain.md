---
layout: default
title: Callback Chain
parent: Examples & Patterns
nav_order: 7
---

# Callback chain with in-place modification

Register multiple callbacks with `.then()`. Each callback runs sequentially on every result. This example chains three functions that validate, normalize, and log each asset — modifying it in place along the way.

```python
import os
from uuid import UUID
from dotenv import load_dotenv
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

# --- Callback definitions ---

def validate_metadata(asset: Asset):
    """Warn if required metadata fields are empty."""
    for field in ("displayName", "description", "keywords"):
        if not asset.get(field, "").strip():
            print(f"[WARN] {asset.get('name')}: missing '{field}'")

def normalize_keywords(asset: Asset):
    """Strip whitespace and lowercase all keywords in-place."""
    raw = asset.get("keywords", "")
    cleaned = ", ".join(k.strip().lower() for k in raw.split(",") if k.strip())
    asset.keywords = cleaned

def log_asset(asset: Asset):
    """Print a summary line for each processed asset."""
    print(f"[OK] {asset.get('name')} — keywords: {asset.get('keywords', '(none)')}")

# --- Script ---

ids = [
    IdentifierType(identifier=UUID("aaa..."), asset_type="page"),
    IdentifierType(identifier=UUID("bbb..."), asset_type="page"),
    IdentifierType(identifier=UUID("ccc..."), asset_type="page"),
]

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(ids).then([
        validate_metadata,
        normalize_keywords,
        log_asset,
    ])
    results = cascade.submit_requests(Asset)

# At this point, each asset's keywords field has been normalized in memory.
# Queue an edit pass to persist the changes:
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.edit(results)
    cascade.submit_requests()
```

## Execution model

For each result, all three callbacks run in order before moving to the next result:

```
result_1 → validate_metadata → normalize_keywords → log_asset
result_2 → validate_metadata → normalize_keywords → log_asset
result_3 → validate_metadata → normalize_keywords → log_asset
```

If `normalize_keywords` raises an exception on `result_2`, `log_asset` is skipped for that result but execution continues with `result_3`. The exception is logged; the script does not crash.

## Passing a single callback vs. a list

Both are equivalent:

```python
# Single function
cascade.operations.read(ids).then(validate_metadata)

# List of functions
cascade.operations.read(ids).then([validate_metadata, normalize_keywords, log_asset])

# Chained .then() calls — same result
cascade.operations.read(ids).then(validate_metadata).then(normalize_keywords).then(log_asset)
```

---

See also: [Dependent callbacks](./pattern-callback-dependent.md) · [No callbacks](./pattern-callback-none.md) for the baseline
