---
layout: default
title: Dependent Callbacks
parent: Examples & Patterns
nav_order: 8
---

# Dependent callbacks

Callbacks have access to the full operations builder. This means a callback can inspect a result and queue new operations based on what it finds — then a second `submit_requests()` call executes them.

This example reads a set of pages, and for each one that has a linked asset ID in its structured data, queues a read of that linked asset.

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

parent_ids = [
    IdentifierType(identifier=UUID("aaa..."), asset_type="page"),
    IdentifierType(identifier=UUID("bbb..."), asset_type="page"),
    IdentifierType(identifier=UUID("ccc..."), asset_type="page"),
]

with CascadeWrapperBase(env, config) as cascade:

    def follow_linked_asset(asset: Asset):
        """
        If this page references a linked file, queue a read of that file.
        The callback has access to `cascade` via closure.
        """
        nodes = asset.get_data_structure("featured-content", "linked-file")
        if not nodes:
            return

        linked_id = nodes[0].get("fileId")
        linked_type = nodes[0].get("fileType", "file")

        if linked_id:
            print(f"  → queuing read of linked asset: {linked_id}")
            cascade.operations.read(
                IdentifierType(
                    identifier=UUID(linked_id),
                    asset_type=linked_type,
                )
            )

    # First pass: read parent pages, callback queues linked reads
    cascade.operations.read(parent_ids).then(follow_linked_asset)
    parents = cascade.submit_requests(Asset)
    print(f"Read {len(parents)} parent pages")

    # Second pass: execute whatever the callback queued
    linked_assets = cascade.submit_requests(Asset)
    print(f"Read {len(linked_assets)} linked assets")

for asset in linked_assets:
    print(f"  Linked: {asset.get('name')}")
```

## How it works

The callback is a closure — it captures `cascade` from the enclosing `with` block. When it calls `cascade.operations.read(...)`, it adds to the same pending queue. The second `submit_requests()` call picks up whatever the callback queued.

## When to use this

Use dependent callbacks when the set of operations you need to run depends on the content of earlier results — for example:
- Following relationships discovered inside structured data
- Reading the parent folder of every asset in a set
- Queueing edits only for assets that pass a content check

## What to be careful of

**Cycles:** If `follow_linked_asset` queues a read of an asset that itself triggers a callback that queues another read, you can build an infinite chain. Guard with a visited set if traversal depth is unbounded.

**Order:** The second `submit_requests()` only sees what was queued during the first pass. If callbacks queue operations asynchronously or conditionally, the queue may be empty on the second call.

---

See also: [Callback chain](./pattern-callback-chain.md) · [Workflow orchestration](./pattern-workflow-orchestration.md) for a structured multi-pass pattern
