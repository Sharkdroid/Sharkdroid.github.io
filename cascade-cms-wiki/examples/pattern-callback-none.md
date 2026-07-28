---
layout: default
title: No Callbacks
parent: Examples & Patterns
nav_order: 6
---

# Multiple operations with no callbacks

Queue several different operations together and collect all results at once. No callbacks, no post-processing — just the raw result list. This is the simplest baseline and a good starting point for any script.

```python
import os
from uuid import UUID
from dotenv import load_dotenv
from cascade_cms.cmstypes import (
    Asset,
    IdentifierType,
    ListElements,
    SearchInformation,
)
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

page_id = IdentifierType(identifier=UUID("aaa..."), asset_type="page")
folder_id = IdentifierType(identifier=UUID("bbb..."), asset_type="folder")
file_id = IdentifierType(identifier=UUID("ccc..."), asset_type="file")

search_payload = SearchInformation(
    siteName="www.example.edu",
    searchTerms="annual report",
    searchTypes=["page"],
)

with CascadeWrapperBase(env, config) as cascade:
    # Queue four different operations
    cascade.operations.read(page_id)
    cascade.operations.read(folder_id)
    cascade.operations.read(file_id)
    cascade.operations.search(search_payload)

    # All four execute concurrently
    results = cascade.submit_requests()

# results contains up to 4 objects in completion order (not queue order)
for result in results:
    if isinstance(result, Asset):
        print(f"Asset: {result.get('name')} ({result._asset_type})")
    elif isinstance(result, ListElements):
        print(f"Search: {len(result.elements)} matches")
```

## What to expect

Results are returned in **completion order**, not queue order. The network is fast and the differences are usually negligible, but don't rely on `results[0]` corresponding to the first queued operation. If order matters, use the `identifier` attached to each result or filter by type.

## Checking for errors

`CascadeError` objects appear in `results` alongside successful responses when an operation fails at the API level (asset not found, permission denied, etc.). Filter them out if you only want successes:

```python
from cascade_cms.cmstypes import CascadeError

successes = [r for r in results if not isinstance(r, CascadeError)]
errors    = [r for r in results if isinstance(r, CascadeError)]

for e in errors:
    print(f"Failed: {e.message}")
```

---

See also: [Callback chain](./pattern-callback-chain/) to add post-processing · [Iterating results](./pattern-read-iterate/) for more result-handling patterns
