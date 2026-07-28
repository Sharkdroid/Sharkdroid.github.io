---
layout: default
title: Edit In-Place
parent: Examples & Patterns
nav_order: 5
---

# Editing an asset in-place

Read an asset, modify its fields in memory, then queue the edit. Changes are local until `edit()` is queued and `submit_requests()` is called.

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

ref = IdentifierType(
    identifier=UUID("8b320f55ac1001062545a6d2562cee4b"),
    asset_type="page",
)

with CascadeWrapperBase(env, config) as cascade:
    # Step 1: Read
    cascade.operations.read(ref)
    results = cascade.submit_requests(Asset)
    asset = results[0]

    # Step 2: Modify in memory
    asset["displayName"] = "Annual Report 2025"
    asset["teaser"] = "Overview of the year's performance."

    # Modify structured data by reference
    nodes = asset.get_data_structure("main-content", "body-text")
    if nodes:
        nodes[0]["text"] = "<p>Updated body content.</p>"

    # Modify a page region by reference
    region = asset.get_page_configuration("ASPX", "DEFAULT")
    if region:
        region.content = updated_block_id  # reference to a content block

    # Step 3: Queue the edit and submit
    cascade.operations.edit(asset)
    cascade.submit_requests()

print("Edit complete.")
```

## Type enforcement on reassignment

`Asset` enforces that a field keeps its original Python type when reassigned. Assigning the wrong type raises a `TypeError` immediately, before any network call is made.

```python
# Allowed: same type
asset["name"] = "new-name"    # str → str ✓

# Not allowed: type mismatch
asset["name"] = 42            # str → int → TypeError
```

## Bulk in-place edits

Read many assets, modify each one, then submit all edits concurrently:

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(ids)
    results = cascade.submit_requests(Asset)

    for asset in results:
        asset["keywords"] = asset.get("keywords", "").strip().lower()

    cascade.operations.edit(results)  # pass the full list
    cascade.submit_requests()
```

---

See also: [Callback chain](./pattern-callback-chain.md) for callbacks that modify in-place · [Operations: edit](../operations/all-operations.md#editpayload)
