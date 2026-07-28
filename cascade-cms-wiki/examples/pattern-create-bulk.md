---
layout: default
title: Bulk Create
parent: Examples & Patterns
nav_order: 4
---

# Creating multiple assets in one batch

Queue all creates together and execute them concurrently. Cascade returns the new asset's ID only — if you need the full asset afterward, read it in a second call.

```python
import os
from uuid import UUID
from dotenv import load_dotenv
from cascade_cms.cmstypes import IdentifierType, NewAsset, Asset
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

# Build payloads for three new text files
assets_to_create = [
    NewAsset(
        name="report-q1.txt",
        asset_type="file",
        site_name="www.example.edu",
        parent_folder_path="/uploads/reports",
        text="Q1 Report placeholder",
    ),
    NewAsset(
        name="report-q2.txt",
        asset_type="file",
        site_name="www.example.edu",
        parent_folder_path="/uploads/reports",
        text="Q2 Report placeholder",
    ),
    NewAsset(
        name="report-q3.txt",
        asset_type="file",
        site_name="www.example.edu",
        parent_folder_path="/uploads/reports",
        text="Q3 Report placeholder",
    ),
]

with CascadeWrapperBase(env, config) as cascade:
    # Create all three concurrently
    cascade.operations.create(assets_to_create)
    new_ids = cascade.submit_requests(IdentifierType)

    for ref in new_ids:
        print(f"Created: {ref.get_id} ({ref.get_type})")

    # If you need the full asset, read it back
    cascade.operations.read(new_ids)
    created_assets = cascade.submit_requests(Asset)

for asset in created_assets:
    print(f"  Name: {asset.get('name')}, Path: {asset.get('path')}")
```

## Key points

**The response is `IdentifierType`, not `Asset`.** Cascade's create endpoint returns only the new UUID. If you need fields like `path` or `siteId`, do a second `read()` call with the returned identifiers.

**Extra fields are passed through.** `NewAsset` uses `extra="allow"` — any fields not in the model schema (like `text` for file assets, or data-definition-specific fields for pages) are serialized as-is. Cascade silently ignores fields it doesn't recognize for the given asset type.

**Either `site_name` or `site_id` is required, not both.** Same rule applies to `parent_folder_path` and `parent_folder_id`. The model validator enforces exactly one of each pair at construction time.

---

See also: [Edit in-place](./pattern-edit-in-place.md) · [Operations: create](../operations/all-operations/#create)
