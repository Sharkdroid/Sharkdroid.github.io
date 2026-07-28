---
layout: default
title: Iterating Results Three Ways
parent: Examples & Patterns
nav_order: 3
---

# Iterating results three ways

Reading five pages and doing something with the results. Three approaches — list comprehension, for-loop, and callback — on the same result set. Choose based on whether you want to collect output, branch on content, or trigger side effects.

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

ids = [
    IdentifierType(identifier=UUID("aaa..."), asset_type="page"),
    IdentifierType(identifier=UUID("bbb..."), asset_type="page"),
    IdentifierType(identifier=UUID("ccc..."), asset_type="page"),
    IdentifierType(identifier=UUID("ddd..."), asset_type="page"),
    IdentifierType(identifier=UUID("eee..."), asset_type="page"),
]
```

## Approach 1: List comprehension

Best when you want to collect a transformed value from every result.

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(ids)
    results = cascade.submit_requests(Asset)

# Collect display names
display_names = [asset.get("displayName", "") for asset in results]

# Collect page configurations for a specific template
aspx_configs = [
    asset.get_page_configuration("ASPX")
    for asset in results
    if asset.get_page_configuration("ASPX") is not None
]
```

## Approach 2: For-loop

Best when you need to branch, skip, or take action based on individual values.

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(ids)
    results = cascade.submit_requests(Asset)

for asset in results:
    name = asset.get("name", "")

    if name.startswith("draft-"):
        print(f"Skipping draft: {name}")
        continue

    # Navigate structured content
    nodes = asset.get_data_structure("main-content", "body-text")
    if nodes:
        text = nodes[0].get("text", "")
        print(f"{name}: {len(text)} chars")
    else:
        print(f"{name}: no body-text node found")
```

## Approach 3: Callback

Best when you want side effects (logging, writing, transforming) to run automatically on each result as part of the submit cycle.

```python
def report_page(asset):
    config = asset.get_page_configuration("ASPX", "DEFAULT")
    region_content = config.content if config else "(none)"
    print(f"{asset.get('name')}: DEFAULT region = {region_content[:80]}")

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(ids).then(report_page)
    results = cascade.submit_requests(Asset)
    # report_page was called once per result during submit
```

## Which to use?

| Approach | Good for |
|----------|---------|
| List comprehension | Collecting a uniform value from every result |
| For-loop | Branching logic, skipping, or mixed operations |
| Callback | Side effects that integrate with the submit cycle; chaining with other callbacks |

Callbacks do not replace the returned `results` list — `submit_requests()` still returns all results. Callbacks and comprehensions can coexist in the same script.

---

See also: [Callback chain](./pattern-callback-chain.md) · [ID vs. Path](./pattern-read-identifiers.md)
