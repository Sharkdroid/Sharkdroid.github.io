---
layout: default
title: ID vs. Path Addressing
parent: Examples & Patterns
nav_order: 1
---

# Reading assets: IdentifierType vs Path

Two types can address any Cascade asset. This example reads the same page both ways and then uses `get_data_structure()` and `get_page_configuration()` to navigate its content.

## IdentifierType — UUID-based addressing

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

id_ref = IdentifierType(
    identifier=UUID("8b320f55ac1001062545a6d2562cee4b"),
    asset_type="page",
)

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(id_ref)
    results = cascade.submit_requests(Asset)

asset = results[0]
print(asset.get("name"))
```

## Path — location-based addressing

`Path` references the same asset by site and path string instead of UUID. The operations API is identical.

```python
from cascade_cms.cmstypes import Asset, Path

path_ref = Path(
    asset_type="page",
    siteName="www.example.edu",
    path="/about/leadership",
)

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(path_ref)
    results = cascade.submit_requests(Asset)
```

**When to use which:**
- `IdentifierType` is faster — UUID lookups are direct. Use it when you have IDs from API responses or database records.
- `Path` is human-readable — ideal for scripts targeting known folder structures or when you don't have the UUID.

## Navigating asset content

Once you have an `Asset`, two utility methods let you navigate structured content.

### `get_data_structure(group, identifier)`

Finds nodes matching an identifier inside a structured data group. Returns a list of matching nodes **by reference** — mutations you make to nodes persist when you later call `edit()`.

```python
# Find all "body-text" nodes inside "main-content" groups
nodes = asset.get_data_structure("main-content", "body-text")

if nodes:
    for node in nodes:
        print(node.get("text", ""))
        # Mutate in place — changes persist on edit
        node["text"] = "<p>Updated content</p>"
```

### `get_page_configuration(name, region=None)`

Finds a page configuration by name, and optionally a specific region within it. Returns `PageConfiguration` or `PageRegion` objects **by reference**.

```python
# Get the full configuration
config = asset.get_page_configuration("ASPX")
if config:
    print(config.name)
    print([r.name for r in config.pageRegions])

# Get a specific region directly
region = asset.get_page_configuration("ASPX", "DEFAULT")
if region:
    print(region.content)
    region.content = "<p>New default region content</p>"
```

---

See also: [Iterating results](./pattern-read-iterate/) · [Edit in-place](./pattern-edit-in-place/)
